# frontend-streamlit/core/db_connect.py

import os
from sqlalchemy import create_engine, Engine
import streamlit as st
from dotenv import load_dotenv


def get_db_uri() -> str:
    """
    Собирает URI для подключения к базе данных из переменных окружения.
    """
    # Загружаем переменные из .env файла, который находится в корне проекта
    # Путь '../../.env' означает "подняться на два уровня вверх от текущего файла"
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)

    # Получаем учетные данные из переменных окружения
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB")
    # Хост 'db' - это имя сервиса в docker-compose.yml
    # При запуске вне докера, можно использовать 'localhost'
    host = os.getenv("DB_HOST", "localhost")
    # Порт 5433 мы пробрасывали на хост-машину для локальной отладки
    # Внутри Docker-сети сервисы общаются по стандартным портам
    port = os.getenv("DB_PORT", "5433")

    if not all([user, password, db, host, port]):
        raise ValueError("Одна или несколько переменных окружения для БД не установлены.")

    # Формат URI для SQLAlchemy: postgresql+драйвер://user:password@host:port/dbname
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


@st.cache_resource
def get_engine() -> Engine:
    """
    Создает и кэширует объект SQLAlchemy Engine.

    Декоратор @st.cache_resource гарантирует, что функция выполнится только один раз,
    а результат (объект Engine) будет сохранен и переиспользован при последующих
    запусках скрипта (например, при нажатии на кнопку в UI).

    Returns:
        sqlalchemy.engine.Engine: Объект для взаимодействия с БД.
    """
    try:
        uri = get_db_uri()
        print("Создание нового подключения к БД (Engine)...")  # Это сообщение появится в консоли только один раз
        engine = create_engine(uri)
        # Простая проверка соединения
        with engine.connect() as connection:
            print("Соединение с БД успешно установлено.")
        return engine
    except Exception as e:
        st.error(f"Не удалось подключиться к базе данных: {e}")
        # Возвращаем None или прерываем выполнение, чтобы приложение не упало
        return None