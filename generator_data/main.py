# generator_data/main.py

import argparse
from datetime import datetime, timedelta
import random

# --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
# Используем относительные импорты с точкой, чтобы Python
# искал модули внутри текущего пакета 'generator_data'.
from .config import get_db_connection
from .modules import (
    generate_clients,
    generate_subscriptions,
    generate_transactions,
    generate_service_usage,
    populate_metadata,
)


def clear_data(cursor, tables):
    """Очищает указанные таблицы."""
    if not tables:
        print("Не указаны таблицы для очистки.")
        return
    print(f"Очистка таблиц: {', '.join(tables)}...")
    for table in tables:
        cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
    print("Очистка завершена.")


def main():
    parser = argparse.ArgumentParser(description="Генератор тестовых данных для AI-агента.")
    parser.add_argument('--full-fresh', action='store_true', help='Полная очистка и генерация всех данных.')

    parser.add_argument('--add-transactions', choices=['today', 'yesterday'],
                        help='Добавить транзакции за сегодня или вчера.')
    parser.add_argument('--num-clients', type=int, default=10000,
                        help='Количество клиентов для генерации (используется с --full-fresh).')
    parser.add_argument('--subscription-ratio', type=float, default=0.6,
                        help='Доля клиентов с подпиской (от 0.0 до 1.0).')

    args = parser.parse_args()

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            if args.full_fresh:
                clear_data(cur, ['clients', 'subscriptions', 'transactions', 'service_usage', 'table_metadata'])

                populate_metadata(cur)
                clients = generate_clients(cur, args.num_clients)
                subscriptions = generate_subscriptions(cur, clients, args.subscription_ratio)

                start_date_transactions = datetime(2023, 1, 1)
                end_date_transactions = datetime(2025, 6, 30)
                generate_transactions(cur, clients, 50, start_date_transactions, end_date_transactions)
                generate_service_usage(cur, subscriptions)

                print("\nПолная генерация данных успешно завершена!")

            elif args.add_transactions:
                cur.execute("SELECT client_id, registration_date FROM clients")
                clients = cur.fetchall()
                if not clients:
                    print("В базе нет клиентов. Сначала выполните полную генерацию с флагом --full-fresh.")
                    return

                today = datetime.now()
                if args.add_transactions == 'today':
                    start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = today
                else:  # yesterday
                    yesterday = today - timedelta(days=1)
                    start_date = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
                    end_date = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

                generate_transactions(cur, clients, random.randint(1, 5), start_date, end_date)
                print(f"\nТранзакции за '{args.add_transactions}' успешно добавлены!")

            else:
                print("Не выбрано ни одного действия. Используйте --help для просмотра опций.")

            conn.commit()
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()