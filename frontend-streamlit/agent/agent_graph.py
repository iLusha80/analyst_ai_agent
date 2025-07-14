import os
import operator
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, AIMessage

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .tools import get_agent_tools
from .prompts import SYSTEM_PROMPT


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]


def call_model_node(state: AgentState):
    """Вызывает LLM и добавляет отладочный вывод."""
    print("---[ ВЫЗОВ МОДЕЛИ ]---")
    print(f"Сообщения на входе: {[msg.pretty_repr() for msg in state['messages']]}")

    response = llm.invoke(state["messages"])

    print(f"Ответ модели: {response.pretty_repr()}")
    print("---[ КОНЕЦ ВЫЗОВА МОДЕЛИ ]---\n")
    return {"messages": [response]}


# Инициализация инструментов и модели
tools = get_agent_tools()
tool_node = ToolNode(tools)

# ИЗМЕНЕНИЕ: Используем правильное и актуальное имя модели
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0).bind_tools(tools)


def should_continue_router(state: AgentState):
    """Определяет, куда двигаться дальше, и добавляет отладочный вывод."""
    print("---[ РОУТЕР ]---")
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
        print("Решение: ЗАВЕРШИТЬ (нет вызовов инструментов)")
        print("---[ КОНЕЦ РОУТЕРА ]---\n")
        return "end"
    else:
        print("Решение: ПРОДОЛЖИТЬ (обработать инструменты)")
        print("---[ КОНЕЦ РОУТЕРА ]---\n")
        return "continue"


# Сборка графа
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