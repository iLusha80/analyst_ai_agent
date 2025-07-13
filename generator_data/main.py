# generator-data/main.py

import argparse
from datetime import datetime, timedelta
import sys

# Добавляем родительскую директорию в sys.path, чтобы корректно работали импорты при запуске через python generator-data/main.py (но лучше запускать через -m)
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импорты из нашего пакета generator-data
from config import get_db_connection
# Импортируем функции напрямую из пакета modules (благодаря __init__.py внутри modules)
from modules import (
    generate_clients,
    generate_subscriptions,
    generate_transactions,
    generate_service_usage,
    populate_metadata
)


def clear_data(cursor, tables):
    """Очищает указанные таблицы."""
    if not tables:
        return
    print(f"Очистка таблиц: {', '.join(tables)}...")
    # TRUNCATE удаляет все данные и сбрасывает счетчики (RESTART IDENTITY)
    # CASCADE удаляет связанные данные в зависимых таблицах
    # Мы объединяем все таблицы в одну команду TRUNCATE для скорости
    try:
        tables_str = ", ".join(tables)
        cursor.execute(f"TRUNCATE TABLE {tables_str} RESTART IDENTITY CASCADE;")
        print("Очистка завершена.")
    except Exception as e:
        print(f"Ошибка при очистке таблиц: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(description="Генератор тестовых данных для AI-агента.")

    # Группа аргументов для полной генерации
    parser.add_argument('--full-fresh', action='store_true', help='Полная очистка и генерация всех данных.')
    parser.add_argument('--num-clients', type=int, default=200,
                        help='Количество клиентов для генерации (используется с --full-fresh). По умолчанию: 200.')
    parser.add_argument('--subscription-ratio', type=float, default=0.6,
                        help='Доля клиентов с подпиской (0.0-1.0). По умолчанию: 0.6 (60%).')

    # Группа аргументов для добавления данных
    parser.add_argument('--add-transactions', choices=['today', 'yesterday', 'week'],
                        help='Добавить транзакции за определенный период (не очищая старые данные).')

    args = parser.parse_args()

    # Подключение к БД
    try:
        conn = get_db_connection()
    except Exception as e:
        print(f"Не удалось подключиться к БД. Убедитесь, что Docker-контейнер запущен. Ошибка: {e}")
        return

    try:
        with conn.cursor() as cur:

            # --- Логика для --full-fresh ---
            if args.full_fresh:
                print("\n--- ЗАПУЩЕНА ПОЛНАЯ ГЕНЕРАЦИЯ ДАННЫХ ---")
                # Порядок важен из-за зависимостей (CASCADE позаботится об удалении, но лучше указывать все)
                tables_to_clear = ['clients', 'subscriptions', 'transactions', 'service_usage', 'table_metadata']
                clear_data(cur, tables_to_clear)

                # 1. Метаданные
                populate_metadata(cur)

                # 2. Клиенты
                clients = generate_clients(cur, args.num_clients)

                # 3. Подписки
                subscriptions = generate_subscriptions(cur, clients, args.subscription_ratio)

                # 4. Транзакции (генерируем за последний год)
                today = datetime.now()
                one_year_ago = today - timedelta(days=365)
                # Генерируем в среднем 30 транзакций на клиента за год
                generate_transactions(cur, clients, 30, one_year_ago, today)

                # 5. Использование сервисов
                generate_service_usage(cur, subscriptions)

                print("\n--- Полная генерация данных успешно завершена! ---")

            # --- Логика для --add-transactions ---
            elif args.add_transactions:
                print(f"\n--- ДОБАВЛЕНИЕ ТРАНЗАКЦИЙ ЗА: {args.add_transactions.upper()} ---")

                # Получаем существующих клиентов
                cur.execute("SELECT client_id, registration_date FROM clients")
                clients = cur.fetchall()
                if not clients:
                    print("Ошибка: В базе нет клиентов. Сначала выполните полную генерацию с флагом --full-fresh.")
                    return

                today = datetime.now()

                if args.add_transactions == 'today':
                    start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = today
                    num_tx = 2  # Добавляем 1-2 транзакции на клиента
                elif args.add_transactions == 'yesterday':
                    yesterday = today - timedelta(days=1)
                    start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
                    num_tx = 3
                elif args.add_transactions == 'week':
                    start_date = (today - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = today
                    num_tx = 10

                generate_transactions(cur, clients, num_tx, start_date, end_date)
                print(f"\n--- Транзакции успешно добавлены! ---")

            else:
                print("Не выбрано ни одного действия. Используйте --help для просмотра опций.")

            # Фиксируем изменения в базе данных
            conn.commit()

    except Exception as e:
        print(f"\nПроизошла ошибка во время генерации данных: {e}")
        if conn:
            conn.rollback()  # Откатываем транзакцию в случае ошибки
    finally:
        if conn:
            conn.close()
            print("Соединение с базой данных закрыто.")


# Этот блок позволяет запускать файл как скрипт
if __name__ == "__main__":
    # При запуске из корневой папки проекта используйте:
    # python -m generator-data.main [аргументы]
    main()