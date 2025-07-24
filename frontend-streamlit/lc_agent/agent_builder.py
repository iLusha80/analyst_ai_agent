# frontend-streamlit/lc_agent/agent_builder.py (ФИНАЛЬНАЯ ВЕРСИЯ С УНИВЕРСАЛЬНЫМ ОБРАБОТЧИКОМ)

from langchain_community.agent_toolkits import create_sql_agent, SQLDatabaseToolkit
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.tools import Tool
from typing import List

# УБИРАЕМ ЛИШНИЕ ИМПОРТЫ
from langchain_core.agents import AgentFinish
from langchain_core.exceptions import OutputParserException

from core.db_connect import get_engine
from .prompts import LC_AGENT_PROMPT_PREFIX
from tools.custom_tools import get_table_schema_description


def display_table(data: str) -> str:
    """Пустышка. Используется как сигнал для UI, чтобы отобразить таблицу."""
    return "Таблица была успешно передана для отображения."


# --- НОВЫЙ, УНИВЕРСАЛЬНЫЙ ОБРАБОТЧИК ОШИБОК ---
def _handle_parsing_error(error: OutputParserException) -> AgentFinish:
    """
    Эта функция вызывается, когда агент не может разобрать ответ от LLM.
    Она берет "сырой" ответ LLM из объекта ошибки и превращает его
    в финальный ответ агента, предотвращая падение.
    """
    # Объект OutputParserException содержит "сырой" ответ в атрибуте 'llm_output'
    response = error.llm_output

    print(f"ПОЙМАНА ОШИБКА ПАРСИНГА. Возвращаем 'сырой' текст: {response}")

    # Возвращаем объект AgentFinish, который корректно завершает работу агента
    return AgentFinish({"output": response}, log=str(error))


def create_lc_agent() -> AgentExecutor:
    """
    Создает LangChain SQL Agent с кастомными инструментами и
    универсальным обработчиком ошибок парсинга.
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
        # Передаем нашу новую, более надежную функцию
        handle_parsing_errors=_handle_parsing_error,
        extra_tools=custom_tools
    )