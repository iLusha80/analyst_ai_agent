-- data/init.sql (обновленный)

-- Удаляем таблицы в обратном порядке зависимостей, чтобы избежать ошибок
DROP TABLE IF EXISTS table_metadata;
DROP TABLE IF EXISTS service_usage;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS subscriptions;
DROP TABLE IF EXISTS clients;

-- Добавляем удаление новых таблиц, если они уже существуют
DROP TABLE IF EXISTS chat_messages;
DROP TABLE IF EXISTS chat_sessions;

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

-- =================================================================
-- НОВЫЕ ТАБЛИЦЫ ДЛЯ ХРАНЕНИЯ ИСТОРИИ ЧАТОВ (ЗАДАЧА 1)
-- =================================================================

-- Таблица для хранения "задач" или "сессий" чата
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), -- Используем UUID для уникальных, непоследовательных ID
    user_id VARCHAR(255), -- ID пользователя, пока может быть NULL
    title VARCHAR(255) NOT NULL, -- Заголовок задачи, например, первый вопрос пользователя
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- Время создания с таймзоной
    status VARCHAR(50) NOT NULL DEFAULT 'in_progress' -- Статус: in_progress, resolved, archived
);

-- Таблица для хранения сообщений внутри каждой задачи
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE, -- Связь с задачей, удаляется вместе с ней
    role VARCHAR(50) NOT NULL, -- 'user' или 'assistant'
    content_type VARCHAR(50) NOT NULL, -- 'text', 'dataframe', 'sql', 'error'
    content TEXT NOT NULL, -- Содержимое. Для структурированных данных (dataframe) будем хранить как JSON-строку.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Добавляем индексы для ускорения частых запросов
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);