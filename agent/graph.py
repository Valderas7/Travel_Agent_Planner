# Librerías
from agent.nodes.planner import planner_node
from agent.nodes.tools import tool_node
from agent.nodes.response import response_node
from agent.nodes.update import update_node
from agent.router import should_call_tools
from agent.state import GraphState
from functools import partial
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from typing import Any, Callable


def build_graph(
    llm_with_tools: Any,
    tools: list[Any],
    process_tool_calls_fn: Callable[..., Any],
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
            - Genera observations

        3. update_node:
            - Actualiza estado del viaje

        4. response_node:
            - Genera respuesta final al usuario

    Args:
        llm_with_tools (Any):
            Modelo de lenguaje con herramientas enlazadas (bind_tools).

        tools (list[Any]):
            Lista de herramientas disponibles del servidor MCP.

        process_tool_calls_fn (Callable[..., Any]):
            Función encargada de ejecutar y procesar tool calls.

    Returns:
        CompiledStateGraph:
            Grafo compilado listo para ejecución.
    """
    # Se construye el grafo con estado tipado
    graph = StateGraph(GraphState)

    # Se añaden cuatro nodos al grafo
    graph.add_node(
        "planner",
        partial(planner_node, llm_with_tools=llm_with_tools)
    )
    graph.add_node(
        "tools",
        partial(tool_node, tools, process_tool_calls_fn)
    )
    graph.add_node("response", response_node)
    graph.add_node("update", update_node)

    # Se especifica el primer nodo a ser llamado en el grafo
    graph.set_entry_point("planner")

    # Se añade una bifurcación después del nodo 'planner'. Si se necesitan
    # herramientas MCP se ejecuta el nodo 'tools'; y si no, se ejecuta el
    # nodo 'response'
    graph.add_conditional_edges(
        "planner",
        should_call_tools,
        {
            True: "tools",
            False: "response"
        }
    )

    # Después del nodo 'tools' se pasa al nodo 'update', y posteriormente
    # al nodo 'planner'
    graph.add_edge("tools", "update")
    graph.add_edge("update", "planner")

    # Después del nodo 'response', se termina el grafo
    graph.add_edge("response", END)

    # Se compila el grafo y se devuelve
    return graph.compile()