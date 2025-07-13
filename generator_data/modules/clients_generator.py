# generator_data/modules/clients_generator.py
import random
from ..utils import fake, CITIES, GENDERS, CHANNELS


def generate_clients(cursor, num_clients):
    """
    Генерирует заданное количество клиентов и возвращает их ID и даты регистрации.
    """
    print(f"Генерация {num_clients} клиентов...")
    clients_data = []
    for _ in range(num_clients):
        clients_data.append((
            fake.random_int(min=18, max=70),
            random.choice(CITIES),
            random.choice(GENDERS),
            fake.date_between(start_date='-3y', end_date='today'),
            random.choice(CHANNELS)
        ))

    # executemany для быстрой вставки
    cursor.executemany(
        "INSERT INTO clients (age, city, gender, registration_date, registration_channel) VALUES (%s, %s, %s, %s, %s)",
        clients_data
    )

    # Возвращаем ID и даты регистрации для использования в других генераторах
    cursor.execute("SELECT client_id, registration_date FROM clients ORDER BY client_id")
    return cursor.fetchall()
