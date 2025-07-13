# frontend-streamlit/pages/1_💬_Аналитический_чат.py

import streamlit as st
from core import init_session_state

# Настройка страницы
st.set_page_config(
    page_title="Аналитический чат", # Это будет и в заголовке вкладки, и в меню
    page_icon="💬",                # Это будет иконкой
    layout="wide"
)

# Инициализация истории чата
init_session_state()

# Заголовок страницы
st.title("💬 Аналитический чат")
st.markdown("Задайте ваш вопрос на естественном языке, и я постараюсь найти ответ в данных.")

# Отображаем историю сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле для ввода нового сообщения
if prompt := st.chat_input("Например: Сколько у нас всего клиентов?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- ЗАГЛУШКА ДЛЯ AI-АГЕНТА ---
    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            response = "🤖 *Это заглушка.* На следующем шаге я научусь отвечать на вопросы."
            st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})