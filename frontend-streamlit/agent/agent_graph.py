# frontend-streamlit/agent/agent_graph.py (НОВАЯ, ПРАВИЛЬНАЯ ВЕРСИЯ)

import os
import operator
from typing import TypedDict, Annotated, List

from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# create_tool_calling_executor - это новый, более удобный способ сборки
from langgraph.prebuilt import create_tool_calling_executor

from .tools import get_agent_tools
from .prompts import SYSTEM_PROMPT


def _initialize_gemini_llm():
    """Инициализирует и возвращает LLM от Google."""
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("Переменная окружения GOOGLE_API_KEY не установлена!")

    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        # convert_system_message_to_human больше не рекомендуется,
        # Gemini сам хорошо обрабатывает системные промпты.
    )


def get_agent_executor():
    """
    Создает и компилирует LangGraph агент на базе Google Gemini,
    используя современный и рекомендованный способ.
    """
    tools = get_agent_tools()
    llm = _initialize_gemini_llm()

    # Добавляем системное сообщение к модели.
    # Это более надежный способ, чем передача через MessagesPlaceholder.
    llm_with_system_prompt = llm.with_structured_output(
        method="tool_calling",
        include_raw=True,
    ).bind(
        tools=tools,
        system_instruction=SYSTEM_PROMPT,
    )

    # create_tool_calling_executor - это готовый граф, который делает всё то,
    # что мы пытались построить вручную: вызывает модель, затем инструменты, и так по циклу.
    # Это самый простой и надежный способ.
    agent_executor = create_tool_calling_executor(
        llm_with_system_prompt,
        tools,
    )

    return agent_executor