# Librerías
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableBinding
from prompts.flight_prompts import FlightPrompts
from typing import Dict, Any


async def planner_node(
    state: Dict[str, Any],
    llm_with_tools: RunnableBinding
) -> Dict[str, Any]:
    """
    Planner node del agente de viajes.

    Este nodo construye el prompt del LLM usando el estado del viaje
    (TravelState), ejecuta el modelo con herramientas (tool calling)
    y actualiza el estado del grafo con la respuesta y posibles tool calls.

    Args:
        state (Dict[str, Any]):
            Estado del grafo (GraphState). Debe contener:
            - user_message (str): mensaje del usuario
            - travel_state (TravelState): estado semántico del viaje
            - messages (list, optional): historial de mensajes

        llm_with_tools (RunnableBinding):
            Modelo de lenguaje con herramientas enlazadas mediante bind_tools.

    Returns:
        Dict[str, Any]:
            Estado actualizado del grafo con:
            - messages: historial actualizado con la respuesta del LLM
            - tool_calls: llamadas a herramientas detectadas (si existen)
    """
    # Se obtiene el estado del viaje a partir del estado del grafo
    travel_state = state.get("travel_state")

    # Lista de mensajes
    messages = [
        SystemMessage(content=FlightPrompts.search_flights(travel_state)),
        HumanMessage(content=state["user_message"])
    ]

    # Se invoca al LLM con herramientas
    response = await llm_with_tools.ainvoke(messages)

    # Se devuelve el estado, los mensajes y las llamadas a herramientas
    return {
        **state,
        "messages": state.get("messages", []) + [response],
        "tool_calls": getattr(response, "tool_calls", None)
    }