# core/chat_history.py

import json
from typing import List, Dict, Any, Optional
from uuid import UUID

from sqlalchemy.engine import Engine
from sqlalchemy import text

# --- ФУНКЦИИ ДЛЯ РАБОТЫ С СЕССИЯМИ (ЗАДАЧАМИ) ---

def create_new_session(engine: Engine, title: str, user_id: Optional[str] = None) -> UUID:
    """
    Создает новую сессию (задачу) в базе данных.

    Args:
        engine: SQLAlchemy Engine для подключения к БД.
        title: Заголовок для новой задачи.
        user_id: (Опционально) ID пользователя.

    Returns:
        UUID новой созданной сессии.
    """
    query = text(
        """
        INSERT INTO chat_sessions (title, user_id)
        VALUES (:title, :user_id)
        RETURNING id;
        """
    )
    with engine.connect() as connection:
        result = connection.execute(query, {"title": title, "user_id": user_id})
        session_id = result.scalar_one()
        connection.commit()
    return session_id


def get_all_sessions(engine: Engine, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Получает список всех сессий, отсортированных по дате создания.

    Args:
        engine: SQLAlchemy Engine.
        user_id: (Опционально) Фильтрует сессии по ID пользователя.

    Returns:
        Список словарей, где каждый словарь представляет одну сессию.
    """
    # Пока у нас нет системы пользователей, мы будем выбирать все сессии.
    # В будущем здесь будет фильтрация по user_id.
    # ORDER BY created_at DESC показывает самые новые задачи сверху.
    # TODO: Когда появится система пользователей, раскомментировать и адаптировать фильтр.
    query = text(
        """
        SELECT id, title, status, created_at
        FROM chat_sessions
        /* WHERE user_id = :user_id OR user_id IS NULL */
        ORDER BY created_at DESC;
        """
    )
    with engine.connect() as connection:
        # params = {"user_id": user_id}
        result = connection.execute(query)
        # .mappings().all() удобно преобразует результат в список словарей
        sessions = result.mappings().all()
    return sessions


def update_session_status(engine: Engine, session_id: UUID, status: str):
    """
    Обновляет статус указанной сессии.

    Args:
        engine: SQLAlchemy Engine.
        session_id: ID сессии для обновления.
        status: Новый статус ('in_progress', 'resolved', 'archived').
    """
    query = text(
        """
        UPDATE chat_sessions
        SET status = :status
        WHERE id = :session_id;
        """
    )
    with engine.connect() as connection:
        connection.execute(query, {"session_id": session_id, "status": status})
        connection.commit()


# --- ФУНКЦИИ ДЛЯ РАБОТЫ С СООБЩЕНИЯМИ ---

def add_message(
    engine: Engine,
    session_id: UUID,
    role: str,
    content_type: str,
    content: Any
):
    """
    Добавляет новое сообщение в указанную сессию.

    Args:
        engine: SQLAlchemy Engine.
        session_id: ID сессии, к которой относится сообщение.
        role: Роль отправителя ('user' или 'assistant').
        content_type: Тип контента ('text', 'dataframe', 'sql', 'error').
        content: Содержимое сообщения. Если это не строка, будет преобразовано в JSON.
    """
    # Если контент - не строка (например, dict или list для dataframe),
    # преобразуем его в JSON-строку для хранения в БД.
    if not isinstance(content, str):
        content = json.dumps(content, ensure_ascii=False)

    query = text(
        """
        INSERT INTO chat_messages (session_id, role, content_type, content)
        VALUES (:session_id, :role, :content_type, :content);
        """
    )
    with engine.connect() as connection:
        connection.execute(
            query,
            {
                "session_id": session_id,
                "role": role,
                "content_type": content_type,
                "content": content,
            },
        )
        connection.commit()


def get_messages_for_session(engine: Engine, session_id: UUID) -> List[Dict[str, Any]]:
    """
    Получает все сообщения для указанной сессии в хронологическом порядке.

    Args:
        engine: SQLAlchemy Engine.
        session_id: ID сессии, для которой нужно получить сообщения.

    Returns:
        Список словарей, представляющих сообщения.
    """
    if not session_id:
        return []

    query = text(
        """
        SELECT id, role, content_type, content, created_at
        FROM chat_messages
        WHERE session_id = :session_id
        ORDER BY created_at ASC;
        """
    )
    with engine.connect() as connection:
        result = connection.execute(query, {"session_id": session_id})
        messages = result.mappings().all()

    # Попытка распарсить JSON-контент для удобства пр
    for msg in messages:
        if msg['content_type'] == 'dataframe':
            try:
                msg['content'] = json.loads(msg['content'])
            except json.JSONDecodeError:
                # Если не получилось, оставляем как есть
                pass
    return messages
