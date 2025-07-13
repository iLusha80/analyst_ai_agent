# generator_data/utils.py

from faker import Faker

# --- СПРАВОЧНИКИ ДАННЫХ ---
CITIES = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Казань']
GENDERS = ['Мужской', 'Женский']
CHANNELS = ['mobile_app', 'web', 'partner_bank', 'office']
TRANSACTION_CATEGORIES = ['Продукты', 'Такси', 'Кино', 'АЗС', 'Одежда', 'Рестораны']
SERVICES = ['Онлайн-кинотеатр', 'Доставка продуктов', 'Музыка', 'Кешбэк на АЗС']
SUBSCRIPTION_PLANS = {
    1: {'price': 299.00, 'is_trial': False},
    3: {'price': 799.00, 'is_trial': False},
    12: {'price': 2990.00, 'is_trial': False},
    0: {'price': 0.00, 'is_trial': True} # Триальная подписка
}

# Инициализация Faker
fake = Faker('ru_RU')