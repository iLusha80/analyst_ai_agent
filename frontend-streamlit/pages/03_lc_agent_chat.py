# frontend-streamlit/pages/03_lc_agent_chat.py (ВЕРСИЯ С РЕНДЕРИНГОМ ТАБЛИЦ)

import streamlit as st
import pandas as pd
import ast  # Для безопасного преобразования строки в Python-объект

from lc_agent.agent_builder import create_lc_agent

st.set_page_config(
    page_title="Чат с LangChain Агентом",
    page_icon="🔗",
    layout="wide"
)


@st.cache_resource
def load_agent():
    return create_lc_agent()


if "lc_messages" not in st.session_state:
    st.session_state.lc_messages = [
        {"role": "assistant", "content": "Здравствуйте! Я стандартный LangChain SQL агент. Задайте мне вопрос."}
    ]

st.title("🔗 Чат с LangChain Агентом (Стабильная версия)")
st.info("Эта версия использует высокоуровневую функцию `create_sql_agent` из LangChain для повышенной стабильности.")

for message in st.session_state.lc_messages:
    with st.chat_message(message["role"]):
        # Проверяем, является ли контент DataFrame-ом (для рендеринга из истории)
        if isinstance(message["content"], pd.DataFrame):
            st.dataframe(message["content"])
        else:
            st.markdown(message["content"])

agent_executor = load_agent()

if prompt := st.chat_input("Например: Покажи первых 5 клиентов"):
    st.session_state.lc_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 Думаю... (LangChain)"):
            try:
                agent_input = {"input": prompt}
                response_dict = agent_executor.invoke(agent_input)

                # --- ГЛАВНОЕ ИЗМЕНЕНИЕ: ПЕРЕХВАТ И РЕНДЕРИНГ ТАБЛИЦ ---
                table_displayed = False
                # Проверяем промежуточные шаги агента
                if 'intermediate_steps' in response_dict:
                    for action, result in response_dict['intermediate_steps']:
                        # Ищем вызов нашего инструмента
                        if action.tool == 'display_table':
                            try:
                                # Преобразуем строковое представление данных в Python-объект
                                data = ast.literal_eval(action.tool_input)
                                df = pd.DataFrame(data)

                                # Отображаем DataFrame в чате
                                st.dataframe(df)
                                # Сохраняем сам DataFrame в историю для корректного отображения при перезагрузке
                                st.session_state.lc_messages.append({"role": "assistant", "content": df})
                                table_displayed = True
                            except Exception as e:
                                st.warning(f"Не удалось отобразить таблицу: {e}")

                # Отображаем и сохраняем финальный текстовый ответ агента
                response_content = response_dict['output']
                if table_displayed:
                    st.markdown(response_content)  # Если таблица была, текст будет дополнением
                else:
                    st.markdown(response_content)  # Если таблицы не было, это основной ответ

                # Сохраняем текстовую часть в любом случае
                st.session_state.lc_messages.append({"role": "assistant", "content": response_content})

            except Exception as e:
                import traceback

                print(traceback.format_exc())
                response_content = f"Произошла ошибка: {e}"
                st.error(response_content)
                st.session_state.lc_messages.append({"role": "assistant", "content": response_content})