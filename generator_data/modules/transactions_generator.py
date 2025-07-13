# generator_data/modules/transactions_generator.py
import random
from ..utils import fake, TRANSACTION_CATEGORIES


def generate_transactions(cursor, clients, num_per_client, start_date, end_date):
    """
    Генерирует транзакции для клиентов в заданном диапазоне дат.
    """
    print(f"Генерация транзакций с {start_date.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')}...")
    transactions_data = []

    for client_id, reg_date in clients:
        # Транзакции не могут быть раньше даты регистрации
        effective_start_date = max(reg_date, start_date.date())

        # Если клиент зарегистрировался после периода генерации, пропускаем его
        if effective_start_date > end_date.date():
            continue

        for _ in range(random.randint(1, num_per_client)):
            transactions_data.append((
                client_id,
                fake.date_time_between(start_date=effective_start_date, end_date=end_date, tzinfo=None),
                round(random.uniform(50.0, 20000.0), 2),
                random.choice(TRANSACTION_CATEGORIES),
                random.choice([True, False])
            ))

    cursor.executemany(
        "INSERT INTO transactions (client_id, transaction_date, amount, category, is_ecosystem_partner) VALUES (%s, %s, %s, %s, %s)",
        transactions_data
    )