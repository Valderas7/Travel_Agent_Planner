# Librerías
import logging
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableBinding
from prompts.flight_prompts import FlightPrompts
from typing import Dict, Any

# Logger del módulo
logger = logging.getLogger(__name__)


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

    # Se obtienen los mensajes intercambiados con el modelo de lenguaje
    messages = state.get("messages") or []

    # Si no hay mensajes aún, se forma el prompt de sistema y se almacena
    # la consulta del usuario
    if len(messages) == 0:
        messages = [
            SystemMessage(content=FlightPrompts.search_flights(travel_state)),
            HumanMessage(content=state["user_message"])
        ]
    
    # Si no...
    else:
        
        #  Se obtiene el último mensaje de la lista de mensajes
        last = messages[-1]

        # Si el último mensaje no es humano, se añade a la laista de mensajes
        # la consulta del usuario
        if not isinstance(messages[-1], HumanMessage) and last.content == state["user_message"]:
            messages = messages + [HumanMessage(content=state["user_message"])]

    # Se invoca al LLM con herramientas
    response = await llm_with_tools.ainvoke(messages)

    # Se comprueba si el LLM incluye en su respuesta un atributo para llamadas
    # a herramientas
    tool_calls = getattr(response, "tool_calls", None)

    # Si su valor no es algo vacío, se loggea
    if tool_calls:
        logger.info(f"El modelo solicita {len(tool_calls)} herramienta/s.")

    # Se actualizan los mensajes con la respuesta dada por el modelo de
    # lenguaje
    messages = messages + [response]

    # Se devuelve el estado actualizado con los mensajes intercambiados con el
    # modelo y las llamadas a herramientas MCP solicitadas por el modelo
    return {
        **state,
        "messages": messages,
    }