# Librerías
import logging
import json
from core.llm import llm
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient
from prompts.flight_prompts import FlightPrompts
from state import TravelState

# Se obtiene logger del módulo
logger = logging.getLogger(__name__)


async def travel_agent(user_message: str, current_state: dict | None = None) -> dict:
    """
    Agente conversacional principal del Travel Planner.
    Permite al usuario interactuar en lenguaje natural.
    """
    # Se inicializa el estado
    state = _initialize_state(current_state)
    
    try:
        logger.info(f"Usuario: {user_message}")

        tools = await _load_tools()
        llm_with_tools = llm.bind_tools(tools, tool_choice="auto")

        response = await _invoke_llm(llm_with_tools, user_message, state)

        # Procesar tool calls si el LLM decidió usar herramientas
        tool_results = await _process_tool_calls(response, tools, state)

        final_response = getattr(response, "content", str(response))

        logger.info(f"Respuesta generada | Vuelos encontrados: {len(getattr(state, 'flights', []))}")

        return {
            "response": final_response,
            "flights": getattr(state, "flights", []),
            "state": _serialize_state(state),
            "tool_results": tool_results
        }

    except Exception:
        logger.exception("Error en travel_agent")
        return {
            "response": "Lo siento, ha ocurrido un error interno. ¿Puedes intentarlo de nuevo?",
            "flights": [],
            "state": _serialize_state(state) if 'state' in locals() else {},
            "tool_results": []
        }


def _initialize_state(current_state: dict | None) -> TravelState:
    """Inicializa o recupera el estado del viaje."""
    if current_state:
        return TravelState(**current_state)
    return TravelState()


async def _load_tools() -> list:
    """Carga las herramientas desde el servidor MCP."""
    mcp_client = MultiServerMCPClient({
        "flight-search": {
            "transport": "streamable_http",
            "url": "http://localhost:8000/mcp"
        }
    })

    async with mcp_client.session("flight-search") as session:
        await session.initialize()
        tools = await load_mcp_tools(session)
        logger.info(f"Herramientas cargadas: {len(tools)}")
        return tools


async def _invoke_llm(llm_with_tools, user_message: str, state: TravelState):

    # Se crea el prompt de sistema
    system_prompt = FlightPrompts.search_flights(state)
    messages = [
        HumanMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    return await llm_with_tools.ainvoke(messages)


async def _process_tool_calls(response, tools: list, state: TravelState) -> list:
    """Procesa las tool calls y actualiza el estado."""
    tool_results = []

    if not getattr(response, "tool_calls", None):
        return tool_results

    logger.info(f"Se detectaron {len(response.tool_calls)} tool calls")

    for tool_call in response.tool_calls:
        tool_name = tool_call.get("name")
        args = tool_call.get("args", {})

        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            continue

        logger.info(f"Ejecutando herramienta: {tool_name}")

        raw_result = await tool.ainvoke(args)
        _update_state_from_tool(raw_result, state, tool_results, tool_name)

    return tool_results


def _update_state_from_tool(raw_result, state: TravelState, tool_results: list, tool_name: str):
    """Actualiza el estado con los resultados de la herramienta."""
    try:
        if isinstance(raw_result, list) and raw_result and isinstance(raw_result[0], dict):
            text_content = raw_result[0].get("text", "")
            if text_content:
                parsed = json.loads(text_content)
                if "flights" in parsed:
                    state.flights = parsed["flights"]
                    tool_results.append({
                        "tool": tool_name,
                        "flights_found": len(parsed["flights"])
                    })
    except (json.JSONDecodeError, TypeError, KeyError):
        logger.warning(f"No se pudo procesar resultado de herramienta: {tool_name}")


def _serialize_state(state: TravelState) -> dict:
    """Serializa el estado para devolverlo en la respuesta."""
    if hasattr(state, "model_dump"):
        return state.model_dump()
    return dict(state)