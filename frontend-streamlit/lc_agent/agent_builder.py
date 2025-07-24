# frontend-streamlit/lc_agent/agent_builder.py (ВЕРСИЯ С КАСТОМНЫМ ИНСТРУМЕНТОМ)

from langchain_community.agent_toolkits import create_sql_agent, SQLDatabaseToolkit
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.tools import Tool

from core.db_connect import get_engine
from .prompts import LC_AGENT_PROMPT_PREFIX

# ИМПОРТИРУЕМ НАШУ УМНУЮ ФУНКЦИЮ ИЗ ПАПКИ ДРУГОГО АГЕНТА!
# Это нормально для прототипа, т.к. функция универсальна.
from agent.tools import get_table_schema_description


def create_lc_agent() -> AgentExecutor:
    """
    Создает и возвращает LangChain SQL Agent, дополненный нашим кастомным
    инструментом для получения описания схемы.
    """
    engine = get_engine()
    db = SQLDatabase(engine)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    # Стандартный набор инструментов (выполнение SQL, проверка схемы и т.д.)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    # --- СОЗДАНИЕ НАШЕГО КАСТОМНОГО ИНСТРУМЕНТА ---
    # Мы "заворачиваем" нашу функцию в объект Tool, чтобы агент мог ее видеть.
    schema_description_tool = Tool(
        name="database_schema_description",
        func=lambda _: get_table_schema_description(engine),
        description=(
            "ОБЯЗАТЕЛЬНО используй этот инструмент В ПЕРВУЮ ОЧЕРЕДЬ, чтобы получить "
            "полное и понятное описание всех таблиц и полей в базе данных."
        )
    )

    # --- ГЛАВНОЕ ИЗМЕНЕНИЕ ---
    # Мы передаем наш кастомный инструмент в агент через параметр `extra_tools`.
    return create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        prefix=LC_AGENT_PROMPT_PREFIX,
        handle_parsing_errors=True,
        # Добавляем наш инструмент в "арсенал" агента
        extra_tools=[schema_description_tool]
    )
