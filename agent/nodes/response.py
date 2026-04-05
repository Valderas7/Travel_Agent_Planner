# Librerías
import logging
from core.llm import llm
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Any, Dict, List

# Se obtiene el logger del módulo
logger = logging.getLogger(__name__)


async def response_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Nodo final del grafo encargado de generar la respuesta al usuario
    a partir de los resultados acumulados en el estado del viaje.

    Args:
        state (Dict[str, Any]): Estado actual del grafo. Debe contener:
            - travel_state: objeto con información del viaje (incluye `flights`)
            - messages (opcional): historial conversacional

    Returns:
        Dict[str, Any]: Estado actualizado con:
            - response (str): respuesta final generada para el usuario
    """

    # Se selecciona los vuelos almacenados en el grafo y los mensajes
    # intercambiados con el modelo de lenguaje
    travel_state = state.get("travel_state")
    flights = getattr(travel_state, "flights", [])
    messages: List[Any] = state.get("messages", [])

    # En el caso que no haya vuelos, se actualiza el grafo con una respuesta
    if not flights:
        return {
            **state,
            "response": (
                "No he encontrado vuelos que encajen con tu búsqueda. "
                "¿Quieres que ajuste fechas o presupuesto?"
            )
        }

    # Se crea el prompt de sistema
    system_prompt = SystemMessage(
        content=(
            "Eres un asistente experto en viajes.\n"
            "Tu objetivo es ayudar al usuario a elegir vuelos.\n\n"
            "Reglas:\n"
            "- Usa el contexto de la conversación\n"
            "- NO repitas información innecesaria\n"
            "- Resume opciones de forma clara\n"
            "- Destaca mejores vuelos (precio, duración, horarios)\n"
            "- Si ya se mostraron vuelos antes, enfócate en cambios o mejoras\n"
            "- Sé directo y útil\n"
        )
    )

    # Se construye el contexto final añadiendo los mensajes intercambiados
    # anteriormente con el modelo
    final_messages = [system_prompt] + messages

    # Se invoca al modelo con el mensaje de sistema y de usuario
    result = await llm.ainvoke(final_messages)
    logger.info("Respuesta del modelo obtenida satisfactoriamente.")

    # Se actualizan los mensajes intercambiados con el modelo añadiendo
    # el resultado de la última ejecución
    updated_messages = messages + [result]

    # Se devuelve el grafo actualizado con la respuesta del modelo y los
    # mensajes actualizados
    return {
        **state,
        "messages": updated_messages,
        "response": result.content
    }