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

# --- Логика кнопок ---
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
    if cols[i].button(query, key=f"query_btn_{i}"):
        # Просто сохраняем значение. Streamlit сам перезапустит скрипт.
        st.session_state.user_input = query
        # Немедленно перезапускаем скрипт, чтобы обработать ввод от кнопки
        # Это важно, чтобы кнопка вела себя так же, как поле ввода
        st.rerun() 

# --- Унифицированная обработка ввода ---

# Сначала получаем ввод из поля чата
chat_prompt = st.chat_input("Например: Покажи первых 5 клиентов")

# Проверяем, был ли ввод из чата ИЛИ от кнопки (сохраненный в session_state)
prompt_to_process = chat_prompt or st.session_state.get("user_input")

if prompt_to_process:
    # Важно: Сразу сбрасываем значение от кнопки, чтобы оно не сработало повторно
    if "user_input" in st.session_state:
        del st.session_state.user_input

    # Добавляем сообщение пользователя в историю и отображаем его
    st.session_state.messages.append({"role": "user", "content": prompt_to_process})
    
    # ПЕРЕЗАПУСКАЕМ СТРАНИЦУ, ЧТОБЫ СРАЗУ ПОКАЗАТЬ СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЯ
    # Этот rerun нужен, чтобы пользователь увидел свой вопрос до того, как агент начнет думать.
    # Это создает более отзывчивый интерфейс.
    st.rerun()

# --- Блок вызова агента теперь запускается ПОСЛЕ отображения сообщения пользователя ---
# Мы ищем последнее сообщение от пользователя, которое еще не обработано.
last_message = st.session_state.messages[-1]
if last_message["role"] == "user" and st.session_state.get("last_processed_message") != last_message["content"]:
    
    with st.chat_message("assistant"):
        with st.spinner("🤖 Думаю..."):
            try:
                prompt = last_message["content"]
                st.session_state.last_processed_message = prompt

                agent_input = {"input": prompt}
                response_dict = agent_executor.invoke(agent_input)
                
                if 'intermediate_steps' in response_dict and response_dict['intermediate_steps']:
                    for action, result in reversed(response_dict['intermediate_steps']):
                        if action.tool == 'display_table' and isinstance(action.tool_input, dict):
                            tool_input = action.tool_input
                            df = pd.DataFrame(tool_input.get('data', []), columns=tool_input.get('columns', []))
                            st.dataframe(df)
                            st.session_state.messages.append({"role": "assistant", "content": df})
                            break
                
                response_content = response_dict.get('output', 'Нет текстового ответа.')
                if response_content:
                    st.markdown(response_content)
                    st.session_state.messages.append({"role": "assistant", "content": response_content})

            except Exception as e:
                import traceback
                error_message = traceback.format_exc()
                print(error_message)
                response_content = f"Произошла ошибка: {e}"
                st.error(response_content)
                st.session_state.messages.append({"role": "assistant", "content": response_content})
    
    # Финальный rerun, чтобы обновить всю страницу после ответа ассистента
    st.rerun()