# frontend-streamlit/app.py (ВЕРСИЯ ДЛЯ ПРИЕМА СТРУКТУРИРОВАННЫХ ДАННЫХ)

import streamlit as st
import pandas as pd

from lc_agent.agent_builder import create_lc_agent

st.set_page_config(page_title="Insight Agent", page_icon="💡", layout="wide")

@st.cache_resource
def load_agent():
    return create_lc_agent()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Здравствуйте! Я Insight Agent. Задайте мне вопрос по данным."}
    ]

with st.sidebar:
    st.title("💡 Insight Agent")
    st.info("Прототип AI-агента для анализа данных.")
    st.markdown("---")
    st.markdown("Перейдите на страницу 'Описание данных', чтобы увидеть доступные таблицы.")

st.title("💬 Аналитический чат")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], pd.DataFrame):
            st.dataframe(message["content"])
        else:
            st.markdown(message["content"])

agent_executor = load_agent()

# Предопределенные запросы
predefined_queries = [
    "Сколько всего клиентов?",
    "Покажи средний возраст клиентов.",
    "Сколько активных подписок на данный момент?",
    "Покажи топ-5 городов по количеству транзакций за последний месяц.",
    "Какой средний доход от подписок на одного клиента в разрезе каналов регистрации за последний год?"
]

st.markdown("---")
st.subheader("Быстрые запросы:")
cols = st.columns(5)
for i, query in enumerate(predefined_queries):
    with cols[i]:
        if st.button(query):
            st.session_state.chat_input_value = query
            st.session_state.send_message_flag = True

# Инициализация chat_input_value, если его нет
if "chat_input_value" not in st.session_state:
    st.session_state.chat_input_value = ""

# Поле ввода чата всегда отображается
prompt = st.chat_input("Например: Покажи первых 5 клиентов", value=st.session_state.chat_input_value, key="chat_input")

# Если сообщение нужно отправить (из кнопки или из поля ввода)
if prompt or st.session_state.get("send_message_flag"):
    # Сбрасываем флаг
    st.session_state.send_message_flag = False
    # Сбрасываем значение поля ввода после отправки
    st.session_state.chat_input_value = ""

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤖 Думаю..."):
            try:
                agent_input = {"input": prompt}
                response_dict = agent_executor.invoke(agent_input)
                
                # --- ЛОГИКА ПЕРЕХВАТА СТРУКТУРИРОВАННОЙ ТАБЛИЦЫ ---
                if 'intermediate_steps' in response_dict:
                    for action, result in response_dict['intermediate_steps']:
                        if action.tool == 'display_table':
                            # action.tool_input теперь - это словарь, а не строка
                            tool_input = action.tool_input
                            df = pd.DataFrame(tool_input['data'], columns=tool_input['columns'])
                            st.dataframe(df)
                            st.session_state.messages.append({"role": "assistant", "content": df})
                
                response_content = response_dict['output']
                st.markdown(response_content)
                st.session_state.messages.append({"role": "assistant", "content": response_content})

            except Exception as e:
                import traceback
                print(traceback.format_exc())
                response_content = f"Произошла ошибка: {e}"
                st.error(response_content)
                st.session_state.messages.append({"role": "assistant", "content": response_content})