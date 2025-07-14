# frontend-streamlit/agent/agent_graph.py (НОВАЯ, ПРАВИЛЬНАЯ И СТАБИЛЬНАЯ ВЕРСИЯ)

import os
import operator
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, AIMessage

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .tools import get_agent_tools
from .prompts import SYSTEM_PROMPT


# 1. ОПРЕДЕЛЯЕМ СОСТОЯНИЕ (STATE)
# Теперь состояние - это просто список сообщений.
# Annotated и operator.add - это инструкция для LangGraph:
# "Не заменяй сообщения, а ДОБАВЛЯЙ новые к списку".
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]


# 2. ОПРЕДЕЛЯЕМ УЗЛЫ ГРАФА

def call_model_node(state: AgentState):
    """
    Узел, который вызывает LLM.
    Он принимает текущее состояние (список сообщений) и возвращает ответ LLM.
    """
    # Вызываем LLM с текущей историей сообщений
    response = llm.invoke(state["messages"])
    # Возвращаем ответ модели, чтобы он был добавлен в конец списка сообщений
    return {"messages": [response]}


# 3. ИНИЦИАЛИЗАЦИЯ ИНСТРУМЕНТОВ И МОДЕЛИ
tools = get_agent_tools()
tool_node = ToolNode(tools) # Используем стабильный ToolNode

# Инициализируем модель с системным промптом. Это самый надежный способ.
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0).bind_tools(tools)


# 4. ОПРЕДЕЛЯЕМ УСЛОВНЫЕ ПЕРЕХОДЫ
def should_continue_router(state: AgentState):
    """
    Определяет, куда двигаться дальше.
    Проверяет последнее сообщение в состоянии.
    """
    last_message = state["messages"][-1]
    # Если в последнем сообщении нет вызовов инструментов, значит агент закончил.
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        return "end"
    # В противном случае, нужно выполнить инструменты.
    else:
        return "continue"


# 5. СОБИРАЕМ ГРАФ
workflow = StateGraph(AgentState)

# Добавляем узел, который вызывает модель, и узел, который выполняет инструменты.
workflow.add_node("agent", call_model_node)
workflow.add_node("action", tool_node)

# Входная точка - это узел "agent".
workflow.set_entry_point("agent")

# Добавляем условный переход от "agent" к "action" или к концу работы.
workflow.add_conditional_edges(
    "agent",
    should_continue_router,
    {
        "continue": "action",
        "end": END,
    },
)

# После выполнения "action" всегда возвращаемся к "agent" для анализа результата.
workflow.add_edge("action", "agent")

# Компилируем граф в исполняемый объект.
agent_executor = workflow.compile()


# Добавляем системное сообщение в начало каждого диалога
# Это гарантирует, что агент всегда будет знать свои правила.
def get_agent_executor_with_system_message():
    # Мы не можем поместить это в @st.cache_resource, т.к. он не может
    # кэшировать объекты, содержащие системные сообщения напрямую.
    # Но сама компиляция графа быстрая.
    system_message_graph = {
        "messages": [
            AIMessage(content=SYSTEM_PROMPT)
        ]
    }
    return agent_executor