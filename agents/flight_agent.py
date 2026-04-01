# Librerías
import logging
import json
from core.llm import llm
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient
from prompts.flight_prompts import FlightPrompts
from state import TravelState

# Se obtiene el logger para este módulo
logger = logging.getLogger(__name__)


async def flight_agent(state: TravelState) -> TravelState:
    """
    Agente encargado de buscar opciones de vuelos basándose en el destino y
    las fechas proporcionadas en el estado del viaje.

    Args:
        state (TravelState): El estado actual del viaje

    Returns:
        TravelState: El estado actualizado con las opciones de vuelos
        encontradas
    """
    # Lista vacía para almacenar vuelos
    flights = []

    # Se intenta...
    try:

        # Se crea un cliente con conexión al servidor MCP
        mcp_client = MultiServerMCPClient({
            "flight-search": {
                "transport": "streamable_http",
                "url": "http://localhost:8000/mcp"
            }
        })

        # El cliente se conecta al servidor MCP e inicializa una sesión
        async with mcp_client.session("flight-search") as session:
            await session.initialize()

            # Se cargan las herramientas disponibles en el servidor MCP
            tools = await load_mcp_tools(session)
            logger.info(
                f"Herramientas cargadas correctamente. Total: {len(tools)}"
            )

            # Se enlaza las herramientas con el modelo de lenguaje, forzándolo
            # a usar una
            llm_with_tools = llm.bind_tools(tools, tool_choice="required")

            # Se construye el prompt de vuelos
            user_prompt = FlightPrompts.search_flights(state)
            logger.info(
                f"Buscando vuelos: {state.get('origin')} → "
                f"{state.get('destination')} | {state.get('outbound_date')}"
            )

            # Se invoca al modelo de lenguaje
            response = await llm_with_tools.ainvoke([
                HumanMessage(content=user_prompt)
            ])

            # Si la respuesta tiene el atributo tool_calls...
            if getattr(response, "tool_calls", None):

                # Para cada herramienta de la respuesta del modelo...
                for tool_call in response.tool_calls:
                    
                    # Se almacena el nombre de la herramienta
                    tool = next(t for t in tools if t.name == tool_call["name"])

                    # Se invoca a la herramienta para obtener los resultados
                    raw_result = await tool.ainvoke(tool_call["args"])

                    # Si los resultados son una lista con longitud
                    # mayor de cero, se selecciona el primer diccionario de
                    # la lista
                    if isinstance(raw_result, list) and len(raw_result) > 0:
                        item = raw_result[0]

                        # Si el diccionario tiene la clave 'text, se parsea
                        # el string JSON que ha dado como respuesta
                        if isinstance(item, dict) and "text" in item:
                            text_content = item.get("text")
                            parsed_data = json.loads(text_content)
                            new_flights = parsed_data.get("flights", [])

                    # Se extiende la lista de vuelos
                    flights.extend(new_flights)
                    logger.info(f"Se añadieron {len(new_flights)} vuelos.")

            # Se devuelve el estado con las opciones de vuelo
            return {
                **state,
                "flights": flights
            }
        
    # Excepción
    except Exception:
        logger.exception(
            "Error durante la ejecución del agente de búsqueda de vuelos."
        )

    # Finalmente...
    finally:
        logger.info(
            "Búsqueda de vuelos finalizada. Total de vuelos "
            f"encontrados: {len(flights)}."
        )