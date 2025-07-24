# frontend-streamlit/lc_agent/agent_builder.py (ВЕРСИЯ С ПРАВИЛЬНЫМ ИМПОРТОМ)

from langchain_community.agent_toolkits import create_sql_agent, SQLDatabaseToolkit
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.tools import Tool
from typing import List

# --- ИСПРАВЛЕННЫЙ ИМПОРТ ---
from langchain_core.agents import AgentFinish

from core.db_connect import get_engine
from .prompts import LC_AGENT_PROMPT_PREFIX
from agent.tools import get_table_schema_description


def display_table(data: str) -> str:
    """Пустышка. Используется как сигнал для UI, чтобы отобразить таблицу."""
    return "Таблица была успешно передана для отображения."


def _handle_parsing_error(error: Exception) -> AgentFinish:
    """
    Эта функция вызывается, когда агент не может разобрать ответ от LLM.
    Она "ловит" некорректный текстовый ответ и превращает его в финальный
    ответ агента, предотвращая падение.
    """
    error_str = str(error)
    # Извлекаем "сырой" ответ LLM из текста ошибки
    try:
        response = error_str.split("Could not parse LLM output: `")[1].strip().replace("`", "")
    except IndexError:
        # Если формат ошибки другой, возвращаем текст ошибки как есть
        response = error_str

    print(f"ПОЙМАНА ОШИБКА ПАРСИНГА. Возвращаем текст: {response}")

    # Возвращаем объект AgentFinish, который корректно завершает работу агента
    return AgentFinish({"output": response}, log=error_str)


def create_lc_agent() -> AgentExecutor:
    """
    Создает LangChain SQL Agent, дополненный кастомными инструментами и
    устойчивостью к ошибкам парсинга.
    """
    engine = get_engine()
    db = SQLDatabase(engine)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    custom_tools: List[Tool] = [
        Tool(
            name="database_schema_description",
            func=lambda _: get_table_schema_description(engine),
            description="ОБЯЗАТЕЛЬНО используй этот инструмент В ПЕРВУЮ ОЧЕРЕДЬ..."
        ),
        Tool(
            name="display_table",
            func=display_table,
            description="Используй этот инструмент, чтобы отобразить табличные данные пользователю..."
        )
    ]

    return create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        prefix=LC_AGENT_PROMPT_PREFIX,
        handle_parsing_errors=_handle_parsing_error,
        extra_tools=custom_tools
    )