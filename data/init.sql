-- data/init.sql (обновленный)

-- Удаляем таблицы, если они существуют, чтобы избежать ошибок при перезапуске
DROP TABLE IF EXISTS table_metadata;
DROP TABLE IF EXISTS service_usage;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS subscriptions;
DROP TABLE IF EXISTS clients;

-- Основные таблицы
CREATE TABLE clients (
    client_id SERIAL PRIMARY KEY,
    age INT,
    city VARCHAR(100),
    gender VARCHAR(10),
    registration_date DATE NOT NULL,
    registration_channel VARCHAR(50)
);

CREATE TABLE subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    client_id INT REFERENCES clients(client_id) ON DELETE CASCADE,
    start_date DATE NOT NULL,
    end_date DATE,
    price NUMERIC(10, 2),
    is_recurring BOOLEAN,
    duration_months INT,
    is_trial BOOLEAN
);

CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    client_id INT REFERENCES clients(client_id) ON DELETE CASCADE,
    transaction_date TIMESTAMP NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    category VARCHAR(100),
    is_ecosystem_partner BOOLEAN
);

CREATE TABLE service_usage (
    usage_id SERIAL PRIMARY KEY,
    subscription_id INT REFERENCES subscriptions(subscription_id) ON DELETE CASCADE,
    service_name VARCHAR(100),
    usage_datetime TIMESTAMP NOT NULL,
    benefit_amount NUMERIC(10, 2)
);

-- Таблица с метаданными
CREATE TABLE table_metadata (
    id SERIAL PRIMARY KEY,
    table_name VARCHAR(255) NOT NULL,
    column_name VARCHAR(255) NOT NULL,
    description TEXT,
    UNIQUE(table_name, column_name)
);