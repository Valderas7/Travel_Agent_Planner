# Librerías
import logging
from agent.registry import TOOL_MAPPERS
from typing import Any, Dict

# Se obtiene el logger del módulo
logger = logging.getLogger(__name__)


def update_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aplica resultados de búsqueda de vuelos al estado del grafo.

    Args:
        state (Dict[str, Any]): Estado del grafo (mutable).
        data (Dict[str, Any]): Datos normalizados de la herramienta.
        tool_results (List[Dict[str, Any]]): Lista de trazas de herramientas.

    Returns:
        Dict[str, Any]: Estado del grafo actualizado.
    """
    # Para cada resultado en los resultados de las herramientas del MCP...
    for result in state.get("tool_results", []):

        # Se selecciona el handler de la herramienta
        handler = TOOL_MAPPERS.get(result.get("tool"))

        # Si existe, se llama a la funcion que procesa los datos obtenidos
        if handler:
            handler(state, result.get("data", {}))

    # Se devuelve el grafo actualizado
    logger.info(
        "Grafo actualizado con la información obtenida en las herramientas."
    )
    return state

    