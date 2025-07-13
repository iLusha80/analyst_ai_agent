# frontend-streamlit/app.py

import streamlit as st
import pandas as pd
from sqlalchemy.engine import Engine

# Импортируем наши кастомные модули
from core import init_session_state, get_engine


# --- Функции для отображения страниц ---

@st.cache_data(ttl=3600)  # Кэшируем данные на 1 час
def load_metadata(_engine: Engine) -> pd.DataFrame:
    """
    Загружает метаданные из таблицы table_metadata с помощью pandas.
    Декоратор @st.cache_data кэширует результат, чтобы не делать лишних запросов к БД.
    """
    if _engine is None:
        return pd.DataFrame()

    try:
        query = "SELECT table_name, column_name, description FROM table_metadata ORDER BY table_name, id;"
        df = pd.read_sql(query, _engine)
        return df
    except Exception as e:
        st.error(f"Ошибка при загрузке метаданных: {e}")
        return pd.DataFrame()


def show_data_schema_page(engine: Engine):
    """
    Отрисовывает страницу 'Описание данных'.
    """
    st.title("📄 Описание данных")
    st.markdown("""
    Здесь представлено описание таблиц и полей, доступных для анализа.
    AI-агент использует эту информацию для построения корректных SQL-запросов.
    """)

    metadata_df = load_metadata(engine)

    if metadata_df.empty:
        st.warning("Не удалось загрузить описание таблиц. Возможно, база данных пуста или недоступна.")
        return

    # Группируем данные по имени таблицы для красивого вывода
    for table_name, group in metadata_df.groupby('table_name'):
        with st.expander(f"Таблица: `{table_name}`", expanded=True):
            # Показываем отфильтрованный DataFrame без колонки table_name
            st.table(group[['column_name', 'description']].rename(columns={
                'column_name': 'Поле',
                'description': 'Описание'
            }).set_index('Поле'))


def show_main_chat_page():
    """
    Отрисовывает главную страницу с чатом.
    (Пока что это заглушка, но уже с отрисовкой истории)
    """
    st.title("💬 Аналитический чат")
    st.markdown("Задайте ваш вопрос на естественном языке, и я постараюсь найти ответ в данных.")

    # Отображаем историю сообщений, которая хранится в st.session_state
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Поле для ввода нового сообщения
    if prompt := st.chat_input("Например: Сколько у нас всего клиентов?"):
        # Добавляем и отображаем сообщение пользователя
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Здесь будет логика вызова AI-агента
        # --- НАЧАЛО ЗАГЛУШКИ ---
        with st.chat_message("assistant"):
            with st.spinner("Думаю..."):
                response = "🤖 *Это заглушка.* На следующем шаге я научусь отвечать на вопросы."
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        # --- КОНЕЦ ЗАГЛУШКИ ---


# --- Основная логика приложения ---

def main():
    """
    Главная функция, запускающая приложение.
    """
    # Настройка страницы (должна быть вызвана первой)
    st.set_page_config(
        page_title="Insight Agent",
        page_icon="💡",
        layout="wide"
    )

    # Инициализация состояния сессии для хранения истории чата
    init_session_state()

    # Получаем (из кэша) подключение к БД
    engine = get_engine()

    # Боковая панель для навигации и статуса
    with st.sidebar:
        st.title("💡 Insight Agent")

        if engine:
            st.success("✅ Подключение к БД: OK")
        else:
            st.error("❌ Подключение к БД: Ошибка")
            st.stop()  # Останавливаем выполнение, если нет БД

        # Меню навигации
        page = st.radio(
            "Выберите страницу:",
            ["Аналитический чат", "Описание данных"],
            label_visibility="collapsed"  # Скрываем заголовок "Выберите страницу"
        )
        st.markdown("---")
        st.info("Прототип AI-агента для анализа данных. Создан с использованием LangChain и Streamlit.")

    # Роутинг по страницам
    if page == "Аналитический чат":
        show_main_chat_page()
    elif page == "Описание данных":
        show_data_schema_page(engine)


if __name__ == "__main__":
    main()