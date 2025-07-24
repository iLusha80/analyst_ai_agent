# frontend-streamlit/tools/custom_tools.py

from sqlalchemy.engine import Engine
from sqlalchemy import text


def get_table_schema_description(engine: Engine) -> str:
    """
    Кастомная функция для получения описания всех таблиц и их полей
    из нашей специальной таблицы 'table_metadata'.

    Это гораздо информативнее для LLM, чем стандартный метод,
    так как содержит описания на естественном языке.
    """
    try:
        with engine.connect() as connection:
            query = text("SELECT table_name, column_name, description FROM table_metadata ORDER BY table_name, id;")
            results = connection.execute(query).fetchall()

        if not results:
            return "В базе данных не найдена таблица 'table_metadata' с описанием схемы. Агент не может продолжить работу без нее."

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
