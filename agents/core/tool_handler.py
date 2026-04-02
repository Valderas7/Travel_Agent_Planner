# Librerías
import logging
import json
from langchain_core.messages import AIMessage
from langchain_core.tools import StructuredTool
from state import TravelState
from typing import Any, Dict, List

# Logger del módulo
logger = logging.getLogger(__name__)


async def process_tool_calls(
    response: AIMessage,
    tools: List[StructuredTool],
    state: TravelState
) -> List[Dict[str, Any]]:
    """
    Procesa todas las llamadas a herramientas realizadas por el LLM.

    Args:
        response: Respuesta del modelo de lenguaje (puede contener tool_calls).
        tools: Lista de herramientas disponibles.
        state: Estado actual del viaje (se actualizará con los resultados).

    Returns:
        Lista de resultados de las herramientas ejecutadas.
    """
    # Lista para recopilar resultados de herramientas
    tool_results = []

    # Si la respuesta no tiene atributo de 'tool_calls', se devuelve una lista
    # vacía
    if not getattr(response, "tool_calls", None):
        return tool_results
    logger.info(
        f"Se detectaron {len(response.tool_calls)} llamada/s a herramientas "
        "del MCP."
    )

    # Para cada llamada a herramientas de la respuesta del modelo de lenguaje...
    for tool_call in response.tool_calls:
        
        # Se obtiene el nombre de la herramienta del MCP y los argumentos
        tool_name = tool_call.get("name")
        args = tool_call.get("args", {})

        # Se encuentra la herramienta con el nombre de la herramienta
        tool = next((t for t in tools if t.name == tool_name), None)
        
        # Si no se encuentra, se continúa
        if not tool:
            logger.warning(f"Herramienta no encontrada: {tool_name}")
            continue
        logger.info(f"Ejecutando herramienta: '{tool_name}'.")

        # Se intenta...
        try:

            # Invocar a la herramienta con los argumentos y actualizar el
            # estado
            raw_result = await tool.ainvoke(args)
            _update_state_from_tool(raw_result, state, tool_results, tool_name)

        # Si hay excepción, se loggea
        except Exception:
            logger.exception(f"Error al ejecutar herramienta {tool_name}.")

    # Se devuelve los resultados tras ejecutar las herramientas
    return tool_results


def _update_state_from_tool(
    raw_result: Any,
    state: TravelState,
    tool_results: List[Dict[str, Any]],
    tool_name: str
) -> None:
    """
    Actualiza el estado del viaje con los resultados de una herramienta.

    Args:
        raw_result: Resultado crudo devuelto por la herramienta.
        state: Estado del viaje a actualizar.
        tool_results: Lista donde se registran los resultados de las tools.
        tool_name: Nombre de la herramienta ejecutada.
    """
    # Se intenta...
    try:

        # Lista vacía para almacenar vuelos
        new_flights = []

        # Si el resultado crudo es un diccionario, se obtiene la clave
        # 'flights' del mismo
        if isinstance(raw_result, dict):
            new_flights = raw_result.get("flights", [])

        # Si por el contrario es una lista, se obtiene el primer miembro
        # de la misma
        elif isinstance(raw_result, list) and raw_result:
            item = raw_result[0]

            # Si este miembro es un diccionario y tiene la clave 'text',
            # se obtiene su valor y se parsea a diccionario
            if isinstance(item, dict) and "text" in item:
                text_content = item.get("text", "{}")
                parsed = json.loads(text_content)
                new_flights = parsed.get("flights", [])

        # Si hay nuevos vuelos...
        if new_flights:

            # Se actualizado el estado del viaje con los vuelos
            state.flights = (state.flights or []) + new_flights

            # Se añaden a la lista un diccionario con el nombre de la
            # herramienta y la cantidad de vuelos encontrados
            tool_results.append({
                "tool": tool_name,
                "flights_found": len(new_flights)
            })
            logger.info(
                f"Se añadieron {len(new_flights)} vuelos desde '{tool_name}'."
            )

    # Si hay excepción, se loggea
    except Exception as e:
        logger.warning(f"No se pudo parsear resultado de {tool_name}: {e}.")