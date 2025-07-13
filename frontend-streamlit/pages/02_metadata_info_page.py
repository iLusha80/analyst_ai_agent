import streamlit as st
import pandas as pd
from sqlalchemy.engine import Engine

from core import get_engine # Импортируем нашу функцию для подключения

st.set_page_config(page_title="Описание данных",
                   page_icon="📄",
                   layout="wide")


# Используем @st.cache_data, чтобы не загружать данные при каждом действии
@st.cache_data(ttl=3600)
def load_metadata(_engine: Engine) -> pd.DataFrame:
    """Загружает метаданные из таблицы table_metadata."""
    if _engine is None:
        return pd.DataFrame()
    try:
        query = "SELECT table_name, column_name, description FROM table_metadata ORDER BY table_name, id;"
        return pd.read_sql(query, _engine)
    except Exception as e:
        st.error(f"Ошибка при загрузке метаданных: {e}")
        return pd.DataFrame()

# --- Основная логика страницы ---

# Заголовок страницы

st.title("📄 Описание данных")
st.markdown("""
Здесь представлено описание таблиц и полей, доступных для анализа.
AI-агент использует эту информацию для построения корректных SQL-запросов.
""")

# Получаем подключение к БД
engine = get_engine()

# Проверка подключения
if engine is None:
    st.error("❌ Не удалось подключиться к базе данных. Проверьте настройки и статус Docker-контейнера.")
    st.stop()

metadata_df = load_metadata(engine)

if metadata_df.empty:
    st.warning("Не удалось загрузить описание таблиц. Возможно, база данных пуста. Запустите генератор данных.")
else:
    # Группируем данные по имени таблицы для красивого вывода
    for table_name, group in metadata_df.groupby('table_name'):
        with st.expander(f"Таблица: `{table_name}`", expanded=True):
            st.table(group[['column_name', 'description']].rename(columns={
                'column_name': 'Поле',
                'description': 'Описание'
            }).set_index('Поле'))