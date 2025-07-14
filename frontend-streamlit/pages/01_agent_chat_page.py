# frontend-streamlit/pages/01_chat.py (ВЕРСИЯ ДЛЯ СТАБИЛЬНОГО ГРАФА)

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from agent.agent_graph import agent_executor
from core import init_session_state  # Промпт импортировать больше не нужно

st.set_page_config(page_title="Аналитический чат", page_icon="💬", layout="wide")

# init_session_state теперь просто создает пустой список
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("💬 Аналитический чат")
st.markdown("Задайте ваш вопрос на естественном языке.")

# Отображаем историю
if not st.session_state.messages:
    # Приветственное сообщение для первого запуска
    st.session_state.messages.append(
        {"role": "assistant", "content": "Здравствуйте! Я Insight Agent. Задайте мне вопрос."}
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Например: Сколько у нас всего клиентов?"):
    # Добавляем сообщение пользователя в нашу локальную историю
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 Думаю и анализирую данные..."):

            # Собираем историю для агента (БЕЗ системного промпта)
            chat_history_for_agent = []
            # Берем все сообщения, кроме первого приветственного
            for msg in st.session_state.messages[1:]:
                if msg["role"] == "user":
                    chat_history_for_agent.append(HumanMessage(content=msg["content"]))
                else:
                    chat_history_for_agent.append(AIMessage(content=msg["content"]))

            # Входные данные - это история сообщений
            agent_input = {"messages": chat_history_for_agent}

            try:
                response_dict = agent_executor.invoke(agent_input)
                response_content = response_dict['messages'][-1].content
            except Exception as e:
                import traceback

                print(traceback.format_exc())
                response_content = f"Произошла ошибка при обработке вашего запроса: {e}"
                st.error(response_content)

            st.markdown(response_content)
            # Добавляем финальный ответ агента в локальную историю
            st.session_state.messages.append({"role": "assistant", "content": response_content})