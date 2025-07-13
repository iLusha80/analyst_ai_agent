# generator_data/modules/subscriptions_generator.py
import random
from datetime import datetime, timedelta
from ..utils import fake, SUBSCRIPTION_PLANS


def generate_subscriptions(cursor, clients, subscription_ratio):
    """
    Генерирует подписки для заданной доли клиентов.
    """
    print("Генерация подписок...")
    subscriptions_data = []

    num_subscribed_clients = int(len(clients) * subscription_ratio)
    subscribed_clients = random.sample(clients, num_subscribed_clients)

    for client_id, reg_date in subscribed_clients:
        start_date = fake.date_between(start_date=reg_date, end_date='today')

        # 0 = trial, 1, 3, 12 = paid
        duration_key = random.choice(list(SUBSCRIPTION_PLANS.keys()))
        plan = SUBSCRIPTION_PLANS[duration_key]

        end_date = None
        is_recurring = False
        duration_months = duration_key if duration_key != 0 else 1

        if plan['is_trial']:
            end_date = start_date + timedelta(days=30)
        else:
            end_date_candidate = start_date + timedelta(days=duration_months * 30)
            # 50% шанс, что подписка уже закончилась (если это было в прошлом)
            if end_date_candidate <= datetime.now().date() and random.random() < 0.5:
                end_date = end_date_candidate
            else:  # Подписка активна
                is_recurring = random.choice([True, False])

        subscriptions_data.append((
            client_id,
            start_date,
            end_date,
            plan['price'],
            is_recurring,
            duration_months,
            plan['is_trial']
        ))

    cursor.executemany(
        "INSERT INTO subscriptions (client_id, start_date, end_date, price, is_recurring, duration_months, is_trial) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        subscriptions_data
    )

    # Возвращаем ID и даты для генератора использований сервисов
    cursor.execute("SELECT subscription_id, start_date, end_date FROM subscriptions ORDER BY subscription_id")
    return cursor.fetchall()
