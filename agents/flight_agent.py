# Librerías
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from state import TravelState

# Se instancia el modelo de lenguaje local de LM Studio
llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    model="nvidia/nemotron-3-nano-4b",
    temperature=0,
)

# URL del servidor MCP local
MCP_URL = "http://localhost:8000"


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
    # Se cargan las herramientas disponibles en el servidor MCP
    tools = await load_mcp_tools(MCP_URL)

    # Se obtiene la herramienta de búsqueda de vuelos por su nombre
    tool = next(t for t in tools if t.name == "search_flights")

    # Se invoca la herramienta MCP de búsqueda de vuelos con los
    # parámetros del estado del viaje
    result = await tool.ainvoke({
        "origin": state["origin"],
        "destination": state["destination"],
        "outbound_date": state["outbound_date"],
        "return_date": state.get("return_date"),
        "budget": state["budget"],
    })

    # Se devuelve el estado del viaje actualizado con las opciones de
    # vuelos, convirtiendo cada opción a un diccionario
    return {
        **state,
        "flights": [
            flight.model_dump()
            for flight in result.flights
        ]
    }
