# generator_data/modules/metadata_generator.py

METADATA = {
    'clients': {
        'client_id': 'Уникальный идентификатор клиента',
        'age': 'Возраст клиента',
        'city': 'Город проживания клиента',
        'gender': 'Пол клиента (Мужской/Женский)',
        'registration_date': 'Дата регистрации клиента в системе',
        'registration_channel': 'Канал привлечения клиента (mobile_app, web и т.д.)'
    },
    'subscriptions': {
        'subscription_id': 'Уникальный идентификатор подписки',
        'client_id': 'Идентификатор клиента, оформившего подписку',
        'start_date': 'Дата начала действия подписки',
        'end_date': 'Дата окончания действия подписки (NULL, если активна)',
        'price': 'Стоимость подписки в рублях',
        'is_recurring': 'Признак автоматического продления (True/False)',
        'duration_months': 'Длительность подписки в месяцах',
        'is_trial': 'Признак пробной подписки (True/False)'
    },
    'transactions': {
        'transaction_id': 'Уникальный идентификатор транзакции',
        'client_id': 'Идентификатор клиента, совершившего транзакцию',
        'transaction_date': 'Дата и время совершения транзакции',
        'amount': 'Сумма транзакции в рублях',
        'category': 'Категория покупки (Продукты, Такси и т.д.)',
        'is_ecosystem_partner': 'Проведена ли транзакция у партнера экосистемы (True/False)'
    },
    'service_usage': {
        'usage_id': 'Уникальный идентификатор использования сервиса',
        'subscription_id': 'Идентификатор подписки, в рамках которой использован сервис',
        'service_name': 'Название использованного сервиса (Онлайн-кинотеатр, Музыка и т.д.)',
        'usage_datetime': 'Дата и время использования сервиса',
        'benefit_amount': 'Сумма полученной выгоды/скидки в рублях'
    }
}


def populate_metadata(cursor):
    """Наполняет таблицу с описанием полей."""
    print("Наполнение таблицы метаданных...")
    metadata_records = []
    for table_name, columns in METADATA.items():
        for column_name, description in columns.items():
            metadata_records.append((table_name, column_name, description))

    cursor.executemany(
        """INSERT INTO table_metadata (table_name, column_name, description)
           VALUES (%s, %s, %s)
           ON CONFLICT (table_name, column_name) DO NOTHING""",
        metadata_records
    )
    print(f"Добавлено/проверено {len(metadata_records)} записей в метаданные.")
