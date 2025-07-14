# frontend-streamlit/agent/tools.py (ФИНАЛЬНАЯ ВЕРСИЯ, основанная на DeprecationWarning)

from typing import List
from sqlalchemy.engine import Engine
from sqlalchemy import text # Добавляем импорт text

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
    print("DEBUG: Вызов get_table_schema_description().") # Отладочный вывод
    try:
        with engine.connect() as connection:
            # Оборачиваем SQL-запрос в text() для явного указания SQLAlchemy
            query = text("SELECT table_name, column_name, description FROM table_metadata ORDER BY table_name, id;")
            print(f"DEBUG: get_table_schema_description - Выполнение запроса: {query}") # Отладочный вывод
            results = connection.execute(query).fetchall()
            print(f"DEBUG: get_table_schema_description - Результаты запроса: {results}") # Отладочный вывод

        schema_description = "Вот схема и описание доступных таблиц:\n\n"
        current_table = ""
        for row in results:
            table, column, description = row
            if table != current_table:
                current_table = table
                schema_description += f"Таблица `{current_table}`:\n"
            schema_description += f"- Поле `{column}`: {description}\n"

        print("DEBUG: get_table_schema_description - Схема успешно получена.") # Отладочный вывод
        return schema_description

    except Exception as e:
        print(f"DEBUG: get_table_schema_description - Произошла ошибка: {e}") # Отладочный вывод
        return f"Произошла ошибка при получении схемы базы данных: {e}"


def get_agent_tools() -> List[Tool]:
    """
    Фабричная функция для создания и получения списка всех инструментов,
    доступных для AI-агента.
    """
    print("DEBUG: Вызов get_agent_tools().") # Отладочный вывод
    engine = get_engine()
    if engine is None:
        print("DEBUG: get_agent_tools() - Не удалось получить подключение к базе данных.") # Отладочный вывод
        raise ValueError("Не удалось получить подключение к базе данных. Инструменты не могут быть созданы.")

    db = SQLDatabase(engine)
    print("DEBUG: get_agent_tools() - SQLDatabase инициализирован.") # Отладочный вывод

    # ИЗМЕНЕНИЕ 2: ИСПОЛЬЗУЕМ ПРАВИЛЬНЫЙ КЛАСС С ПРАВИЛЬНЫМ ИМЕНЕМ
    sql_query_tool = QuerySQLDatabaseTool(db=db)
    print("DEBUG: get_agent_tools() - QuerySQLDatabaseTool инициализирован.") # Отладочный вывод

    # "Заворачиваем" стандартный инструмент в наш Tool, чтобы дать ему понятное описание
    sql_tool = Tool(
        name="sql_query_tool",
        func=sql_query_tool.run,
        description="Полезен для выполнения SQL-запросов к базе данных для получения конкретных данных. Принимает на вход полноценный SQL-запрос."
    )
    print("DEBUG: get_agent_tools() - sql_tool создан.") # Отладочный вывод

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
    print("DEBUG: get_agent_tools() - schema_tool создан.") # Отладочный вывод

    print("DEBUG: get_agent_tools() - Возвращаем список инструментов.") # Отладочный вывод
    return [schema_tool, sql_tool]