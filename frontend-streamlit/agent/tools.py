# frontend-streamlit/agent/tools.py (ФИНАЛЬНАЯ ВЕРСИЯ, основанная на DeprecationWarning)

from typing import List
from sqlalchemy.engine import Engine

# ИЗМЕНЕНИЕ 1: ИСПОЛЬЗУЕМ САМЫЙ АКТУАЛЬНЫЙ ИМПОРТ, ПРЕДЛОЖЕННЫЙ БИБЛИОТЕКОЙ
from langchain_community.tools import QuerySQLDatabaseTool

from langchain_community.utilities.sql_database import SQLDatabase
from langchain.tools import Tool

# Импортируем нашу функцию для подключения к БД
from core import get_engine


def get_table_schema_description(engine: Engine) -> str:
    """
    Кастомная функция для получения описания всех таблиц и их полей
    из нашей специальной таблицы 'table_metadata'.
    """
    try:
        with engine.connect() as connection:
            query = "SELECT table_name, column_name, description FROM table_metadata ORDER BY table_name, id;"
            results = connection.execute(query).fetchall()

        schema_description = "Вот схема и описание доступных таблиц:\n\n"
        current_table = ""
        for row in results:
            table, column, description = row
            if table != current_table:
                current_table = table
                schema_description += f"Таблица `{current_table}`:\n"
            schema_description += f"- Поле `{column}`: {description}\n"

        return schema_description

    except Exception as e:
        return f"Произошла ошибка при получении схемы базы данных: {e}"


def get_agent_tools() -> List[Tool]:
    """
    Фабричная функция для создания и получения списка всех инструментов,
    доступных для AI-агента.
    """
    engine = get_engine()
    if engine is None:
        raise ValueError("Не удалось получить подключение к базе данных. Инструменты не могут быть созданы.")

    db = SQLDatabase(engine)

    # ИЗМЕНЕНИЕ 2: ИСПОЛЬЗУЕМ ПРАВИЛЬНЫЙ КЛАСС С ПРАВИЛЬНЫМ ИМЕНЕМ
    sql_query_tool = QuerySQLDatabaseTool(db=db)

    # "Заворачиваем" стандартный инструмент в наш Tool, чтобы дать ему понятное описание
    sql_tool = Tool(
        name="sql_query_tool",
        func=sql_query_tool.run,
        description="Полезен для выполнения SQL-запросов к базе данных для получения конкретных данных. Принимает на вход полноценный SQL-запрос."
    )

    # Наш кастомный инструмент для получения описания схемы
    schema_tool = Tool(
        name="get_schema_description",
        func=lambda _: get_table_schema_description(engine),
        description=(
            "Очень важный инструмент! Полезен для получения описания всех таблиц и их полей на человеческом языке. "
            "Используй этот инструмент **в первую очередь**, чтобы понять, какие данные доступны, "
            "прежде чем составлять сложный SQL-запрос."
        )
    )

    return [schema_tool, sql_tool]