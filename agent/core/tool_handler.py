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
    # Diccionario para procesar cada herramienta
    TOOL_HANDLERS = {
        "search_flights": _apply_flight_results,
    }

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

        # Mensaje de información
        logger.info(f"Ejecutando herramienta: '{tool_name}'.")

        # Se intenta...
        try:

            # Invocar a la herramienta con los argumentos y actualizar el
            # estado
            raw_result = await tool.ainvoke(args)

            # Se intenta normalizar la salida de cualquier herramienta MCP, ya
            # sea diccionario, lista o lo que sea
            data = _parse_tool_output(raw_result)

            # Se busca la función que procesa la herramienta MCP en proceso
            handler = TOOL_HANDLERS.get(tool_name)

            # Si se ha encontrado la función, se ejecuta. Si no, se loggea
            # advertencia
            if handler:
                handler(state, data, tool_results)
            else:
                logger.warning(
                    f"No hay handler registrado para: {tool_name}."
                )

        # Si hay excepción, se loggea
        except Exception:
            logger.exception(f"Error al ejecutar herramienta {tool_name}.")

    # Se devuelve los resultados tras ejecutar las herramientas
    return tool_results


def _parse_tool_output(raw_result: Any) -> Dict:
    """
    Normaliza la salida de cualquier herramienta MCP a un
    diccionario estándar.
    """
    # Se intenta...
    try:

        # Si el resultado tiene atributo para convertir a diccionario, se usa
        if hasattr(raw_result, "model_dump"):
            return raw_result.model_dump()

        # Si el resultado es directamente un diccionario, se devuelve
        if isinstance(raw_result, dict):
            return raw_result

        # Si es una lista, se obtiene el primer miembro
        if isinstance(raw_result, list) and raw_result:
            item = raw_result[0]

            # Si dicho miembro es un diccionario y la tiene la clave 'text',
            # se devuelve dicha clave parseada como diccionario
            if isinstance(item, dict) and "text" in item:
                return json.loads(item["text"])

        # Si por el contrario es un string, se convierte a diccionario y se
        # devuelve
        if isinstance(raw_result, str):
            return json.loads(raw_result)

    # Si hay excepción, se devuelve un diccionario
    except Exception:
        logger.exception(
            "Error al normalizar la respuesta de la herramienta MCP."
        )
        return {}

    # Se devuelve diccionario
    return {}


def _apply_flight_results(
    state: TravelState,
    data: Dict,
    tool_results: List[Dict],
) -> None:
    """
    Aplica resultados de vuelos al estado.
    """
    # Se obtienen los vuelos
    flights = data.get("flights", [])

    # Si no hy, no se devuelve nada
    if not flights:
        return
    
    # Inicializar los vuelos del estado si es necesario
    if state.flights is None:
        state.flights = []

    # Se extiende los vuelos del estado con los vuelos descubiertos por la
    # herramienta
    state.flights.extend(flights)

    # Se añade un diccionario a la lista de resultados de herramientas
    # indicando los vuelos que se han encontrado para dicha herramienta
    tool_results.append({
        "tool": "search_flights",
        "flights_found": len(flights)
    })

    # Se modifica el estado desde datos reales (NO args) eligiendo el primer
    # vuelo completo
    first_flight = flights[0]

    # Dentro de ese vuelo, se elige el de ida
    outbound = first_flight.get("outbound_flight")

    # Si existe, se actualiza el estado
    if outbound:
        if outbound.get("departure_airport_code"):
            state.origin = outbound["departure_airport_code"]

        if outbound.get("arrival_airport_code"):
            state.destination = outbound["arrival_airport_code"]

        if outbound.get("departure_time"):
            state.outbound_date = outbound["departure_time"].split(" ")[0]
    
    # Dentro del primer vuelo, se elige el vuelo de vuelta
    return_flight = first_flight.get("return_flight")

    # Si existe, se actualiza el estado
    if return_flight and return_flight.get("departure_time"):
        state.return_date = return_flight["departure_time"].split(" ")[0]

