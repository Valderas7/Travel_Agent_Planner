# Librerías
from typing import Any, Dict


def should_call_tools(state: Dict[str, Any]) -> bool:
    """
    Determina si el agente debe ejecutar herramientas (tools) basándose en
    el último mensaje intercambiado con el modelo de lenguaje.

    Args:
        state (Dict[str, Any]): Estado actual del grafo.

    Returns:
        bool: True si hay tool calls pendientes de ejecutar,
        False en caso contrario.
    """
    # Se obtienen los mensajes intercambiados con el modelo del grafo
    messages = state.get("messages", [])

    # Si no hay, se retorna False
    if not messages:
        return False

    # Se obtiene el último mensaje
    last_msg = messages[-1]

    # Se devuelve un booleano indicando si el último mensaje tiene el
    # atributo de llamadas a herramientas
    return bool(getattr(last_msg, "tool_calls", None))
