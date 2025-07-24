# frontend-streamlit/pages/03_lc_agent_chat.py

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from lc_agent.agent_builder import create_lc_agent

# Задаем имя и иконку для страницы
st.set_page_config(
    page_title="Чат с LangChain Агентом",
    page_icon="🔗",
    layout="wide"
)


# Кэшируем создание агента для производительности
@st.cache_resource
def load_agent():
    return create_lc_agent()


# Инициализируем историю чата для этой страницы
# Используем другой ключ, чтобы истории не смешивались
if "lc_messages" not in st.session_state:
    st.session_state.lc_messages = [
        {"role": "assistant", "content": "Здравствуйте! Я стандартный LangChain SQL агент. Задайте мне вопрос."}
    ]

st.title("🔗 Чат с LangChain Агентом (Стабильная версия)")
st.info("Эта версия использует высокоуровневую функцию `create_sql_agent` из LangChain для повышенной стабильности.")

# Отображаем историю
for message in st.session_state.lc_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Загружаем агента
agent_executor = load_agent()

if prompt := st.chat_input("Например: Какие у нас есть таблицы?"):
    st.session_state.lc_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 Думаю... (LangChain)"):
            try:
                # Вход для стандартного агента - это просто словарь с ключом 'input'
                agent_input = {"input": prompt}

                # Вызываем агент
                response_dict = agent_executor.invoke(agent_input)

                # Ответ находится в ключе 'output'
                response_content = response_dict['output']

            except Exception as e:
                import traceback

                print(traceback.format_exc())
                response_content = f"Произошла ошибка: {e}"
                st.error(response_content)

            st.markdown(response_content)
            st.session_state.lc_messages.append({"role": "assistant", "content": response_content})
