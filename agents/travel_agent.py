import logging
from agents.core.llm_handler import invoke_llm
from agents.core.tool_handler import process_tool_calls
from agents.core.state_handler import initialize_state, serialize_state
from core.llm import llm
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from prompts.flight_prompts import FlightPrompts
from state import TravelState

# Logger del módulo
logger = logging.getLogger(__name__)


async def travel_agent(
    user_message: str,
    current_state: dict | None = None
) -> dict:
    """
    Agente conversacional principal del Travel Planner.
    """
    # Se inicializa el estado
    state = initialize_state(current_state)

    # Se intenta...
    try:

        # Se conecta el servidor MCP, iniciando una sesión...
        async with MultiServerMCPClient({
            "travel-tools": {
                "transport": "streamable_http",
                "url": "http://localhost:8000/mcp"
            }
        }).session("travel-tools") as session:

            # Se inicializa la sesión
            await session.initialize()
            
            # Se cargan las herramientas del servidor MCP
            tools = await load_mcp_tools(session)
            logger.info(f"Herramientas cargadas del MCP: {len(tools)}.")

            # Se enlaza el modelo de lenguaje con las herramientas del MCP
            llm_with_tools = llm.bind_tools(tools, tool_choice="auto")

            # Se realiza la consulta al modelo de lenguaje
            response = await invoke_llm(
                llm_with_tools,
                user_message,
                state,
                FlightPrompts.search_flights
            )

            # Se procesan las llamadas a las herramientas del MCP
            tool_results = await process_tool_calls(response, tools, state)

            # Se genera la respuesta final
            final_response = await _generate_final_response(response, tool_results, state)

            return {
                "response": final_response,
                "flights": getattr(state, "flights", []),
                "state": serialize_state(state),
                "tool_results": tool_results
            }

    # Si hay alguna excepción se loggea y se devuelve un diccionario
    except Exception:
        logger.exception("Error en el MCP 'travel_agent'.")
        return {
            "response": "Lo siento, ha ocurrido un error al procesar tu solicitud.",
            "flights": [],
            "state": serialize_state(state) if 'state' in locals() else {},
            "tool_results": []
        }


async def _generate_final_response(
    response: AIMessage,
    tool_results: list,
    state: TravelState
) -> str:
    """
    Genera la respuesta final (con resultados reales de tools).
    """
    # Si hay resultados de llamadas a herramientas...
    if tool_results:

        # Lista de mensajes de sistema y usuario
        messages = [
            SystemMessage(
                content=(
                    "Eres un asistente de viajes. Usa los resultados de "
                    "vuelos para responder al usuario de forma clara."
                )
            ),
            HumanMessage(
                content=f"Resultados de vuelos: {getattr(state, 'flights', [])}"
            )
        ]

        # Se invoca al modelo de lenguaje con los mensajes
        final = await llm.ainvoke(messages)

        # Se devuelve la respuesta
        return final.content

    # Se devuelve la respuesta
    return getattr(response, "content", str(response))