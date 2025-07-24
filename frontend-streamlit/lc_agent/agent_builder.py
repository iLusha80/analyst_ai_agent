# frontend-streamlit/lc_agent/agent_builder.py

from langchain_community.agent_toolkits import create_sql_agent, SQLDatabaseToolkit
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor
from langchain_community.utilities.sql_database import SQLDatabase

from core.db_connect import get_engine
from .prompts import LC_AGENT_PROMPT_PREFIX

def create_lc_agent() -> AgentExecutor:
    """
    Создает и возвращает готовый к использованию LangChain SQL Agent.
    """
    # Получаем подключение к БД (так же, как и раньше)
    engine = get_engine()
    db = SQLDatabase(engine)

    # Инициализируем LLM
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

    # SQLDatabaseToolkit - это ГОТОВЫЙ НАБОР инструментов.
    # Он автоматически включает в себя:
    # - Инструмент для выполнения запросов
    # - Инструмент для получения схемы
    # - Инструмент для получения списка таблиц
    # Нам не нужно создавать их вручную, как в LangGraph!
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    # create_sql_agent - это высокоуровневая "фабрика", которая
    # собирает всё вместе: LLM, toolkit и правильный промпт.
    return create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,  # Включаем логирование "мыслей" агента в консоль
        prefix=LC_AGENT_PROMPT_PREFIX,
        # Это очень важный параметр для стабильности.
        # Он помогает агенту не падать, если LLM сгенерировала некорректный ответ.
        handle_parsing_errors=True,
    )