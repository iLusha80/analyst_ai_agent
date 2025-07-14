# frontend-streamlit/agent/agent_graph.py (АКТУАЛЬНАЯ ВЕРСИЯ)

import os
from typing import List, TypedDict, Union

from langchain_core.messages import BaseMessage
from langchain_core.agents import AgentAction, AgentFinish
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

# ИЗМЕНЕНИЕ 1: Импортируем ToolNode вместо ToolExecutor
from langgraph.prebuilt import ToolNode

from langchain.agents import create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .tools import get_agent_tools
from .promts import SYSTEM_PROMPT


# --- Класс состояния графа остается без изменений ---
class AgentState(TypedDict):
    question: str
    chat_history: List[BaseMessage]
    agent_outcome: Union[AgentAction, AgentFinish, None]
    intermediate_steps: List[tuple[AgentAction, str]]


def _initialize_gemini_llm():
    """Инициализирует и возвращает LLM от Google."""
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("Переменная окружения GOOGLE_API_KEY не установлена!")

    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        convert_system_message_to_human=True
    )


def get_agent_executor():
    """
    Создает и компилирует LangGraph агент на базе Google Gemini.
    """
    tools = get_agent_tools()
    llm = _initialize_gemini_llm()

    # --- Мозг агента остается без изменений ---
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent_runnable = create_openai_tools_agent(llm, tools, prompt)

    # --- Определение узлов графа (Nodes) ---

    def run_agent_node(state: AgentState):
        """Вызывает LLM для принятия решения о следующем шаге."""
        agent_outcome = agent_runnable.invoke({
            "question": state["question"],
            "chat_history": state["chat_history"],
            "intermediate_steps": state["intermediate_steps"]
        })
        # Важно: Для ToolNode нужно, чтобы результат был списком
        if isinstance(agent_outcome, AgentAction):
            state['agent_outcome'] = [agent_outcome]
        else:
            state['agent_outcome'] = agent_outcome
        return state

    # ИЗМЕНЕНИЕ 2: Используем готовый ToolNode вместо самописной функции
    # Он автоматически выполняет инструменты, которые решил вызвать агент.
    tool_node = ToolNode(tools)

    # --- Определение условных переходов (Edges) ---
    def should_continue_router(state: AgentState):
        """Определяет, куда двигаться дальше."""
        # В предыдущем шаге мы обернули AgentAction в список, поэтому проверяем первый элемент
        last_message = state["agent_outcome"]
        if isinstance(last_message, AgentFinish):
            return "end"
        else:
            return "continue"

    # --- Сборка графа ---
    workflow = StateGraph(AgentState)

    workflow.add_node("agent", run_agent_node)
    # Добавляем наш новый, более простой узел
    workflow.add_node("action", tool_node)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue_router,
        {
            "continue": "action",
            "end": END,
        },
    )

    workflow.add_edge("action", "agent")

    return workflow.compile()