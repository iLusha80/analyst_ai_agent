# frontend-streamlit/core/__init__.py

from .db_connect import get_engine, get_db_uri
from .session_state import init_session_state

# __all__ - это список имен, которые будут импортированы,
# когда кто-то выполнит 'from core import *'. Это хорошая практика.
__all__ = [
    'get_engine',
    'get_db_uri',
    'init_session_state'
]
