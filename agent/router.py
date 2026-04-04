# Librerías
from typing import Any, Dict


def should_call_tools(state: Dict[str, Any]) -> bool:
    """
    Determina si el agente debe ejecutar herramientas (tools).

    Se basa en si el LLM ha generado llamadas a herramientas (`tool_calls`)
    en el último paso del planner.

    Args:
        state (Dict[str, Any]): Estado actual del grafo.

    Returns:
        bool: True si hay tool calls pendientes de ejecutar,
        False en caso contrario.
    """
    # Si el estado tiene llamadas a herramientas pendientes, se devuelve True
    if state.get("tool_calls"):
        return True

    # Se obtiene el estado de los viajes
    travel_state = state.get("travel_state")

    # Si ya hay vuelos, se devuelve False
    if travel_state and travel_state.flights:
        return False

    # En cualquier otro caso se devuelve False
    return False


def should_finish(state: Dict[str, Any]) -> bool:
    """
    Determina si el flujo del agente puede finalizar.

    Se considera que el agente puede terminar cuando ya hay resultados
    suficientes en el estado (por ejemplo, vuelos encontrados).

    Args:
        state (Dict[str, Any]): Estado actual del grafo.

    Returns:
        bool: True si el agente debe finalizar, False en caso contrario.
    """
    return state.get("flights") is not None