# generator_data/modules/service_usage_generator.py
import random
from datetime import datetime
from ..utils import fake, SERVICES


def generate_service_usage(cursor, subscriptions):
    """
    Генерирует использования сервисов для активных или истёкших подписок.
    """
    print("Генерация использования сервисов...")
    service_usage_data = []
    if not subscriptions:
        print("Нет подписок для генерации использования сервисов.")
        return

    for sub_id, start_date, end_date in subscriptions:
        # Конечная дата для генерации - либо дата окончания, либо сегодня, если подписка активна
        effective_end_date = end_date if end_date else datetime.now().date()

        # Проверка, что есть временной интервал для генерации
        if start_date < effective_end_date:
            # Генерируем от 1 до 20 использований на подписку
            for _ in range(random.randint(1, 20)):
                usage_date = fake.date_time_between(start_date=start_date, end_date=effective_end_date, tzinfo=None)
                service_usage_data.append((
                    sub_id,
                    random.choice(SERVICES),
                    usage_date,
                    round(random.uniform(50.0, 500.0), 2)  # "Выгода"
                ))

    if not service_usage_data:
        print("Не сгенерировано ни одного использования сервиса.")
        return

    cursor.executemany(
        "INSERT INTO service_usage (subscription_id, service_name, usage_datetime, benefit_amount) VALUES (%s, %s, %s, %s)",
        service_usage_data
    )