# frontend-streamlit/core/session_state.py

import streamlit as st


def init_session_state():
    """
    Инициализирует состояние сессии Streamlit, если оно еще не было создано.

    Создает ключ 'messages' для хранения истории чата.
    Это предотвращает потерю истории при каждом взаимодействии с виджетами.
    """

    # Проверяем, есть ли ключ 'messages' в состоянии сессии
    if "messages" not in st.session_state:
        # Если нет, создаем его и добавляем первое сообщение от ассистента
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Здравствуйте! Я Insight Agent. Задайте мне вопрос по данным о клиентах, подписках или транзакциях."
            }
        ]
