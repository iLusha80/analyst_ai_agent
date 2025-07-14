# frontend-streamlit/pages/01_chat.py (ВЕРСИЯ ДЛЯ НОВОГО ГРАФА)

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

# ИЗМЕНЕНИЕ: Импортируем сам исполняемый объект agent_executor
from agent.agent_graph import agent_executor, SYSTEM_PROMPT

from core import init_session_state

# --- Основная логика страницы ---
st.set_page_config(page_title="Аналитический чат", page_icon="💬", layout="wide")

# ИЗМЕНЕНИЕ: Переопределяем init_session_state, чтобы он добавлял системный промпт
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": SYSTEM_PROMPT}  # Первое сообщение - это правила для агента
    ]
    st.session_state.messages.append(
        {"role": "assistant", "content": "Здравствуйте! Я Insight Agent. Задайте мне вопрос."}
    )

st.title("💬 Аналитический чат")
st.markdown("Задайте ваш вопрос на естественном языке.")

# Отображаем историю, пропуская первое системное сообщение
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Например: Сколько у нас всего клиентов из Москвы?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 Думаю и анализирую данные..."):

            # Собираем историю для агента (включая системный промпт)
            chat_history_for_agent = []
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    chat_history_for_agent.append(HumanMessage(content=msg["content"]))
                else:  # assistant
                    chat_history_for_agent.append(AIMessage(content=msg["content"]))

            # Входные данные - это просто список сообщений
            agent_input = {"messages": chat_history_for_agent}

            try:
                # Вызываем агент
                response_dict = agent_executor.invoke(agent_input)
                # Извлекаем контент из последнего сообщения
                response_content = response_dict['messages'][-1].content
            except Exception as e:
                import traceback

                print(traceback.format_exc())
                response_content = f"Произошла ошибка при обработке вашего запроса: {e}"
                st.error(response_content)

            st.markdown(response_content)
            st.session_state.messages.append({"role": "assistant", "content": response_content})