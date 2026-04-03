# Librerías
import logging
import json
from agent.graph import build_graph
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from core.llm import llm
from langchain_core.messages import AIMessage
from langchain_core.tools import StructuredTool
from state import create_travel_state
from typing import Any, Dict, List

# Se obtiene logger del módulo
logger = logging.getLogger(__name__)


async def travel_agent(user_message: str) -> Dict[str, Any]:
    """
    Agente principal de planificación de viajes basado en LangGraph + MCP.

    Este agente:
    - Inicializa el estado del viaje
    - Conecta con un servidor MCP de herramientas
    - Construye y ejecuta un grafo de ejecución
    - Devuelve vuelos, estado y resultados de herramientas

    Args:
        user_message (str): Mensaje del usuario en lenguaje natural.

    Returns:
        Dict[str, Any]: Resultado final del agente con:
            - response: Respuesta final generada
            - flights: Lista de vuelos encontrados
            - state: Estado completo del grafo
            - tool_results: Resultados de herramientas ejecutadas
    """
    # Se crea un diccionario con la consulta del usuario
    state = {
        "user_message": user_message,
        "messages": [],
        "travel_state": create_travel_state(None),
        "tool_calls": None,
        "tool_results": [],
        "response": ""
    }

    # Se crea un cliente MCP con una sesión para conectar al servidor MCP
    async with MultiServerMCPClient({
        "travel-tools": {
            "transport": "streamable_http",
            "url": "http://localhost:8000/mcp"
        }
    }).session("travel-tools") as session:

        # Se inicializa la sesión
        await session.initialize()

        # Se cargan las herramientas MCP del servidor
        tools = await load_mcp_tools(session)

        # Se enlaza el modelo de lenguaje con las herramientas MCP
        llm_with_tools = llm.bind_tools(tools, tool_choice="auto")
        
        # Se construye el grafo de ejecución
        graph = build_graph(
            llm_with_tools=llm_with_tools,
            tools=tools,
            process_tool_calls_fn=_process_tool_calls
        )

        # Se ejecuta el grafo
        final_state = await graph.ainvoke(state)

        # Se devuelve un diccionario
        return {
            "response": final_state["response"],
            "flights": final_state["flights"],
            "state": final_state,
            "tool_results": final_state["tool_results"]
        }
    

async def _process_tool_calls(
    response: AIMessage,
    tools: List[StructuredTool],
    state: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Procesa todas las llamadas a herramientas realizadas por el LLM y
    actualiza el estado

    Args:
        response (AIMessage): Respuesta del modelo que puede contener
        tool_calls.
        tools (List[StructuredTool]): Lista de herramientas disponibles del
        MCP.
        state (Dict[str, Any]): Estado del grafo que será actualizado.

    Returns:
        List[Dict[str, Any]]: Lista de resultados estructurados de
        herramientas ejecutadas.
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
    
    # Mensaje de información
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
                    f"No hay handler registrado para herramienta: {tool_name}."
                )

        # Si hay excepción, se loggea
        except Exception:
            logger.exception(f"Error al ejecutar herramienta {tool_name}.")

    # Se devuelve los resultados tras ejecutar las herramientas
    return tool_results


def _parse_tool_output(raw_result: Any) -> Dict[str, Any]:
    """
    Normaliza la salida de cualquier herramienta MCP a un diccionario
    estándar.

    Args:
        raw_result (Any): Resultado bruto de la herramienta.

    Returns:
        Dict[str, Any]: Resultado normalizado en formato diccionario.
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
    state: Dict[str, Any],
    data: Dict[str, Any],
    tool_results: List[Dict[str, Any]],
) -> None:
    """
    Aplica resultados de búsqueda de vuelos al estado del grafo.

    Este handler:
    - Añade vuelos al estado
    - Actualiza campos semánticos del viaje (origen, destino, fechas)
    - Registra métricas de tool execution

    Args:
        state (Dict[str, Any]): Estado del grafo (mutable).
        data (Dict[str, Any]): Datos normalizados de la herramienta.
        tool_results (List[Dict[str, Any]]): Lista de trazas de herramientas.
    """
    # Se obtienen los vuelos
    flights = data.get("flights", [])

    # Si no hy, no se devuelve nada
    if not flights:
        return

    # Se extiende los vuelos del estado con los vuelos descubiertos por la
    # herramienta
    state["travel_state"].flights.extend(flights)

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
            state["travel_state"].origin = outbound["departure_airport_code"]

        if outbound.get("arrival_airport_code"):
            state["travel_state"].destination = outbound["arrival_airport_code"]

        if outbound.get("departure_time"):
            state["travel_state"].outbound_date = outbound["departure_time"].split(" ")[0]
    
    # Dentro del primer vuelo, se elige el vuelo de vuelta
    return_flight = first_flight.get("return_flight")

    # Si existe, se actualiza el estado
    if return_flight and return_flight.get("departure_time"):
        state["travel_state"].return_date = return_flight["departure_time"].split(" ")[0]
