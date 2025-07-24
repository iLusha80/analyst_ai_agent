# frontend-streamlit/lc_agent/agent_builder.py (ФИНАЛЬНАЯ ВЕРСИЯ С ПРАВИЛЬНЫМ ПРИЕМОМ АРГУМЕНТОВ)

import json
from langchain_community.agent_toolkits import create_sql_agent, SQLDatabaseToolkit
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.tools import Tool
from typing import List
from pydantic.v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from langchain_core.agents import AgentFinish
from langchain_core.exceptions import OutputParserException

from core.db_connect import get_engine
from .prompts import LC_AGENT_PROMPT_PREFIX
from tools.custom_tools import get_table_schema_description

class TableDisplayArgs(BaseModel):
    json_input: str = Field(description="JSON-строка, содержащая данные для отображения в виде списка словарей и список названий колонок.")

class DisplayTableTool(BaseTool):
    """Инструмент, который служит сигналом для UI для отображения таблицы."""
    name: str = "display_table"
    description: str = (
        "Используй этот инструмент, чтобы отобразить табличные данные пользователю. "
        "Передай ему данные и названия колонок."
    )
    args_schema: type[BaseModel] = TableDisplayArgs

    # --- ГЛАВНОЕ ИЗМЕНЕНИЕ ЗДЕСЬ ---
    # Мы явно указываем, что метод принимает аргументы 'data' и 'columns'.
    # Это позволяет LangChain правильно передать в них значения из JSON.
    def _run(self, json_input: str) -> str:
        # Парсим json_input как JSON-строку
        try:
            parsed_input = json.loads(json_input)
            data = parsed_input.get("data")
            columns = parsed_input.get("columns")

            if data is None or columns is None:
                return f"Ошибка: Отсутствуют 'data' или 'columns' в json_input: {json_input}"

            # Этот инструмент по-прежнему не выполняет никакой логики,
            # но теперь он корректно принимает структурированные данные.
            return "Таблица была успешно передана для отображения."
        except json.JSONDecodeError as e:
            return f"Ошибка парсинга JSON: {e}. Получено: {json_input}"

def _handle_parsing_error(error: OutputParserException) -> AgentFinish:
    """Обработчик ошибок парсинга ответа LLM."""
    response = error.llm_output
    print(f"ПОЙМАНА ОШИБКА ПАРСИНГА. Возвращаем 'сырой' текст: {response}")
    return AgentFinish({"output": response}, log=str(error))

def create_lc_agent() -> AgentExecutor:
    """Создает LangChain SQL Agent."""
    engine = get_engine()
    db = SQLDatabase(engine)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    custom_tools: List[BaseTool] = [
        Tool(
            name="database_schema_description",
            func=lambda _: get_table_schema_description(engine),
            description="ОБЯЗАТЕЛЬНО используй этот инструмент В ПЕРВУЮ ОЧЕРЕДЬ..."
        ),
        DisplayTableTool()
    ]

    return create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        handle_parsing_errors=_handle_parsing_error,
        extra_tools=custom_tools,
        agent_kwargs={"prefix": LC_AGENT_PROMPT_PREFIX}
    )
