import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from agent.agent_graph import agent_executor
from agent.prompts import SYSTEM_PROMPT  # Импортируем промпт
from core import init_session_state

# --- Основная логика страницы ---
st.set_page_config(page_title="Аналитический чат", page_icon="💬", layout="wide")

# init_session_state теперь просто создает пустой список, если его нет
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("💬 Аналитический чат")
st.markdown("Задайте ваш вопрос на естественном языке.")

# Отображаем историю сообщений, если она есть
if not st.session_state.messages:
    st.info("История чата пуста. Начните диалог!")
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Например: Сколько у нас всего клиентов?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 Думаю и анализирую данные..."):

            # Собираем историю для агента
            chat_history_for_agent = [SystemMessage(content=SYSTEM_PROMPT)]
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    chat_history_for_agent.append(HumanMessage(content=msg["content"]))
                else:
                    chat_history_for_agent.append(AIMessage(content=msg["content"]))

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
            # Добавляем в историю только финальный ответ агента
            st.session_state.messages.append({"role": "assistant", "content": response_content})