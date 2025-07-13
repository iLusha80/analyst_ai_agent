# generator_data/config.py

import os
import psycopg2
from dotenv import load_dotenv

# Идем на уровень выше, чтобы найти .env файл
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

DB_SETTINGS = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': 'localhost',
    'port': '5433'
}

def get_db_connection():
    """Устанавливает соединение с базой данных."""
    try:
        conn = psycopg2.connect(**DB_SETTINGS)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
        raise