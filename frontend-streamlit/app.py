# frontend-streamlit/app.py (НОВАЯ ГЛАВНАЯ СТРАНИЦА)

import streamlit as st
import pandas as pd
import ast

# Импортируем нашу стабильную "фабрику" агентов
from lc_agent.agent_builder import create_lc_agent

# --- Основная логика приложения ---

st.set_page_config(
    page_title="Insight Agent",
    page_icon="💡",
    layout="wide"
)


# Кэшируем создание агента для производительности
@st.cache_resource
def load_agent():
    return create_lc_agent()


# Инициализируем историю чата прямо здесь
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Здравствуйте! Я Insight Agent. Задайте мне вопрос по данным."}
    ]

# --- Боковая панель (Sidebar) ---
with st.sidebar:
    st.title("💡 Insight Agent")
    st.info("Прототип AI-агента для анализа данных. Эта версия использует стабильный SQL-агент LangChain.")
    st.markdown("---")
    st.markdown("Перейдите на страницу 'Описание данных', чтобы увидеть доступные таблицы.")

# --- Основной интерфейс чата ---
st.title("💬 Аналитический чат")

# Отображаем историю сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], pd.DataFrame):
            st.dataframe(message["content"])
        else:
            st.markdown(message["content"])

# Загружаем агента
agent_executor = load_agent()

# Поле для ввода вопроса
if prompt := st.chat_input("Например: Покажи первых 5 клиентов"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 Думаю..."):
            try:
                agent_input = {"input": prompt}
                response_dict = agent_executor.invoke(agent_input)

                table_displayed = False
                if 'intermediate_steps' in response_dict:
                    for action, result in response_dict['intermediate_steps']:
                        if action.tool == 'display_table':
                            try:
                                data = ast.literal_eval(action.tool_input)
                                df = pd.DataFrame(data)
                                st.dataframe(df)
                                st.session_state.messages.append({"role": "assistant", "content": df})
                                table_displayed = True
                            except Exception as e:
                                st.warning(f"Не удалось отобразить таблицу: {e}")

                response_content = response_dict['output']
                st.markdown(response_content)
                st.session_state.messages.append({"role": "assistant", "content": response_content})

            except Exception as e:
                import traceback

                print(traceback.format_exc())
                response_content = f"Произошла ошибка: {e}"
                st.error(response_content)
                st.session_state.messages.append({"role": "assistant", "content": response_content})