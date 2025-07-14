# frontend-streamlit/pages/01_chat.py (ИСПРАВЛЕННАЯ ВЕРСИЯ)

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from core import init_session_state
from agent.agent_graph import get_agent_executor


@st.cache_resource
def load_agent_executor():
    """Загружает и кэширует исполняемый объект агента."""
    return get_agent_executor()


# --- Основная логика страницы ---

st.set_page_config(page_title="Аналитический чат", page_icon="💬", layout="wide")
init_session_state()

st.title("💬 Аналитический чат")
st.markdown("Задайте ваш вопрос на естественном языке, и я постараюсь найти ответ в данных.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

try:
    agent_executor = load_agent_executor()
except ValueError as e:
    st.error(f"Ошибка инициализации агента: {e}")
    st.stop()

if prompt := st.chat_input("Например: Сколько у нас всего клиентов из Москвы?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 Думаю и анализирую данные..."):

            chat_history_for_agent = []
            for msg in st.session_state.messages[1:-1]:
                if msg["role"] == "user":
                    chat_history_for_agent.append(HumanMessage(content=msg["content"]))
                else:
                    chat_history_for_agent.append(AIMessage(content=msg["content"]))

            # --- ИЗМЕНЕНИЕ ЗДЕСЬ ---
            # Мы должны передавать полный объект состояния, который ожидает граф,
            # включая пустой список для intermediate_steps.
            agent_input = {
                "question": prompt,
                "chat_history": chat_history_for_agent,
                "intermediate_steps": []  # <--- ЭТОТ КЛЮЧ РЕШАЕТ ПРОБЛЕМУ
            }

            try:
                # В agent_graph.py теперь возвращается финальное состояние целиком
                final_state = agent_executor.invoke(agent_input)
                # Извлекаем финальный ответ из словаря
                response_content = final_state['agent_outcome'].return_values['output']
            except Exception as e:
                # Добавим traceback для более удобной отладки в консоли
                import traceback

                print(traceback.format_exc())
                response_content = f"Произошла ошибка при обработке вашего запроса: {e}"
                st.error(response_content)

            st.markdown(response_content)
            st.session_state.messages.append({"role": "assistant", "content": response_content})