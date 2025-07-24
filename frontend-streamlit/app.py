import streamlit as st
import pandas as pd
import json

from lc_agent.agent_builder import create_lc_agent

st.set_page_config(page_title="Insight Agent", page_icon="💡", layout="wide")

# --- ФУНКЦИИ С КЭШИРОВАНИЕМ ---

@st.cache_data
def load_quick_queries(file_path="frontend-streamlit/queries.json"):
    """Загружает быстрые запросы из JSON-файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        st.error(f"Ошибка загрузки файла с запросами: {e}")
        return []

@st.cache_resource
def load_agent():
    """Загружает и кэширует экземпляр AI-агента."""
    return create_lc_agent()

# --- ИНИЦИАЛИЗАЦИЯ SESSION STATE ---

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Здравствуйте! Я Insight Agent. Задайте мне вопрос по данным."}
    ]

if "last_processed_message" not in st.session_state:
    st.session_state.last_processed_message = None


# --- БОКОВАЯ ПАНЕЛЬ (SIDEBAR) ---

with st.sidebar:
    st.title("💡 Insight Agent")
    st.info("Прототип AI-агента для анализа данных.")
    st.markdown("---")
    st.markdown("Перейдите на страницу 'Описание данных', чтобы увидеть доступные таблицы.")

# --- ОСНОВНОЙ ИНТЕРФЕЙС ЧАТА ---

st.title("💬 Аналитический чат")

# Отображение истории сообщений из session_state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if isinstance(message["content"], pd.DataFrame):
            st.dataframe(message["content"])
        else:
            st.markdown(message["content"])

# Загрузка агента
agent_executor = load_agent()

# --- БЛОК БЫСТРЫХ ЗАПРОСОВ (ВНУТРИ СВОРАЧИВАЕМОГО st.expander) ---

st.markdown("---")

predefined_queries = load_quick_queries()

if predefined_queries:
    # ### ГЛАВНОЕ ИЗМЕНЕНИЕ ###
    # Весь блок с кнопками теперь обернут в st.expander.
    # Он будет по умолчанию свернут (expanded=False). 
    # Можете поставить True, если хотите, чтобы он был открыт при загрузке страницы.
    with st.expander("🚀 Показать быстрые запросы", expanded=False):
        # Определяем, сколько кнопок будет в одном ряду
        COLS_PER_ROW = 3

        # Разбиваем список запросов на "ряды"
        for i in range(0, len(predefined_queries), COLS_PER_ROW):
            chunk = predefined_queries[i:i + COLS_PER_ROW]
            cols = st.columns(COLS_PER_ROW)

            for j, query in enumerate(chunk):
                if cols[j].button(query, key=query, use_container_width=True):
                    st.session_state.user_input = query
                    st.rerun()

# --- ЛОГИКА ОБРАБОТКИ ВВОДА И ВЫЗОВА АГЕНТА (БЕЗ ИЗМЕНЕНИЙ) ---

chat_prompt = st.chat_input("Например: Покажи первых 5 клиентов")
prompt_to_process = chat_prompt or st.session_state.get("user_input")

if prompt_to_process:
    if "user_input" in st.session_state:
        del st.session_state.user_input

    st.session_state.messages.append({"role": "user", "content": prompt_to_process})
    st.rerun()

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
    
    st.rerun()