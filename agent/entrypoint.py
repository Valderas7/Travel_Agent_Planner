# Librerías
import logging
from agent.runtime.graph_runtime import get_graph
from state import create_travel_state
from typing import Any, Dict

# Se obtiene logger del módulo
logger = logging.getLogger(__name__)


async def travel_agent(
    user_message: str,
    thread_id: str
) -> Dict[str, Any]:
    """
    Agente principal de planificación de viajes basado en LangGraph + MCP.

    Este agente:
    - Inicializa el estado del viaje
    - Conecta con un servidor MCP de herramientas
    - Construye y ejecuta un grafo de ejecución
    - Devuelve vuelos, estado y resultados de herramientas

    Args:
        user_message (str): Mensaje del usuario en lenguaje natural.
        thread_id (str): Identificador único que se utiliza para gestionar la
            memoria y el contexto de una conversación

    Returns:
        Dict[str, Any]: Resultado final del agente con:
            - response: Respuesta final generada
            - flights: Lista de vuelos encontrados
            - state: Estado completo del grafo
            - tool_results: Resultados de herramientas ejecutadas
    """
    # Se construye el grafo de ejecución
    graph = await get_graph()

    # Se crea un grafo de estado inicial con la consulta del usuario
    state = {
        "user_message": user_message,
        "messages": [],
        "travel_state": create_travel_state(None),
        "tool_results": [],
        "response": ""
    }

    # Se ejecuta el grafo pasando un identificador de memoria
    final_state = await graph.ainvoke(
        input=state,
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    # Se devuelve un diccionario con la respuesta, los vuelos y los resultados
    # de las herramientas
    return {
        "response": final_state["response"],
        "flights": final_state["travel_state"].flights,
        "tool_results": final_state["tool_results"]
    }
    