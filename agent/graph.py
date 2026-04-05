# Librerías
from agent.nodes.planner import planner_node
from agent.nodes.tools import tool_node
from agent.nodes.response import response_node
from agent.nodes.update import update_node
from agent.router import should_call_tools
from agent.runtime.checkpointer import checkpointer
from agent.state import GraphState
from functools import partial
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from typing import Any


def build_graph(
    llm_with_tools: Any,
    tools: list[Any]
) -> CompiledStateGraph:
    """
    Construye y compila el grafo de ejecución del agente de viajes. Sigue
    una arquitectura tipo LangGraph con nodos explícitos:

    Flujo:
        1. planner_node:
            - Invoca el LLM con herramientas
            - Decide si necesita tools
        2. tools_node:
            - Ejecuta herramientas MCP
        3. update_node:
            - Actualiza estado del viaje
        4. response_node:
            - Genera respuesta final al usuario

    Args:
        llm_with_tools (Any):
            Modelo de lenguaje con herramientas enlazadas (bind_tools).
        tools (list[Any]):
            Lista de herramientas disponibles del servidor MCP.

    Returns:
        CompiledStateGraph:
            Grafo compilado listo para ejecución.
    """
    # Se construye el grafo con estado tipado
    graph = StateGraph(GraphState)

    # Se añaden cuatro nodos al grafo
    graph.add_node(
        "planner",
        partial(
            planner_node,
            llm_with_tools=llm_with_tools
        )
    )
    graph.add_node(
        "tools",
        partial(
            tool_node,
            tools=tools,
        )
    )
    graph.add_node(
        "response",
        partial(response_node)
    )
    graph.add_node("update", update_node)

    # Se especifica el primer nodo a ser llamado en el grafo
    graph.set_entry_point("planner")

    # Se añade una bifurcación después del nodo 'planner'. Se llama al
    # enrutador que comprueba si debe llamarse a alguna herramienta MCP. Si
    # éste devuelve True, se pasa al nodo 'tools, si por el contrario devuelve
    # False, se pasa al nodo 'response'
    graph.add_conditional_edges(
        "planner",
        should_call_tools,
        {
            True: "tools",
            False: "response"
        }
    )

    # Después del nodo 'tools' se pasa al nodo 'update'
    graph.add_edge("tools", "update")

    # Después de nodo 'update' se pasa al nodo 'response'
    graph.add_edge("update", "response")

    # Después del nodo 'response', se termina el grafo
    graph.add_edge("response", END)

    # Se compila el grafo con la memoria a corto plazo importada
    return graph.compile(checkpointer=checkpointer)