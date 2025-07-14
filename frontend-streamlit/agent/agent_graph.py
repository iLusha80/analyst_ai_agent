# frontend-streamlit/agent/agent_graph.py (СТАБИЛЬНАЯ И ПРОВЕРЕННАЯ ВЕРСИЯ)

import os
import operator
from typing import TypedDict, Annotated, List

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .tools import get_agent_tools
from .prompts import SYSTEM_PROMPT

# 1. ОПРЕДЕЛЯЕМ СОСТОЯНИЕ (STATE)
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# 2. ИНИЦИАЛИЗАЦИЯ ИНСТРУМЕНТОВ И МОДЕЛИ
tools = get_agent_tools()
tool_node = ToolNode(tools)

# Инициализируем модель Gemini
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# Привязываем инструменты к модели. Это стандартный и правильный способ.
llm_with_tools = llm.bind_tools(tools)

# 3. СОЗДАЕМ ПРОМПТ И "МОЗГ" АГЕНТА
# Мы явно указываем, где системный промпт, а где история чата.
# Это самый надежный способ.
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# Соединяем промпт и модель с инструментами в единую цепочку
agent_runnable = prompt | llm_with_tools


# 4. ОПРЕДЕЛЯЕМ УЗЛЫ И ЛОГИКУ ГРАФА
def call_model_node(state: AgentState):
    """Вызывает LLM для принятия решения."""
    print(f"DEBUG: call_model_node - State: {state}") # Отладочный вывод
    response = agent_runnable.invoke(state)
    print(f"DEBUG: call_model_node - Response from LLM: {response}") # Отладочный вывод
    return {"messages": [response]}

def should_continue_router(state: AgentState):
    """Определяет, нужно ли вызывать инструменты."""
    print(f"DEBUG: should_continue_router - State: {state}") # Отладочный вывод
    last_message = state["messages"][-1]
    print(f"DEBUG: should_continue_router - Last message: {last_message}") # Отладочный вывод
    if last_message.tool_calls:
        print("DEBUG: should_continue_router - Tool calls detected, continuing to action.") # Отладочный вывод
        return "continue"
    print("DEBUG: should_continue_router - No tool calls, ending.") # Отладочный вывод
    return "end"

# 5. СОБИРАЕМ ГРАФ
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model_node)
workflow.add_node("action", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue_router,
    {"continue": "action", "end": END},
)
workflow.add_edge("action", "agent")
agent_executor = workflow.compile()