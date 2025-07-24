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

if prompt := st.chat_input("Например: Покажи первых 5 клиентов"):
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