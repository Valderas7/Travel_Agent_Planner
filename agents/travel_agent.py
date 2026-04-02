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
from typing import Dict, Any, Optional

# Logger del módulo
logger = logging.getLogger(__name__)


async def travel_agent(
    user_message: str,
    current_state: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Agente conversacional principal del Travel Planner.

    Args:
        user_message (str): Mensaje en lenguaje natural del usuario.
        current_state (Optional[Dict[str, Any]]): Estado previo del viaje.
        Si es None, se crea un estado nuevo.

    Returns:
        Dict[str, Any]: Respuesta que contiene:
            - response: Texto generado para el usuario
            - flights: Lista de vuelos encontrados (si aplica)
            - state: Estado actualizado del viaje
            - tool_results: Información sobre las herramientas ejecutadas
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

            # Se realiza la consulta al modelo de lenguaje, el cual responde
            # con la lista de herramientas que decide usar
            response = await invoke_llm(
                llm_with_tools,
                user_message,
                state,
                FlightPrompts.search_flights
            )

            # Se procesan las llamadas a las herramientas del MCP que el
            # modelo de lenguaje ha decidido usar
            tool_results = await process_tool_calls(response, tools, state)

            # Se genera la respuesta final
            final_response = await _generate_final_response(
                response,
                tool_results,
                state
            )

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
            "response": (
                "Lo siento, ha ocurrido un error al procesar tu solicitud."
            ),
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
    Genera la respuesta final para el usuario.

    Si se ejecutaron herramientas (tool_results), realiza una segunda llamada
    al LLM para resumir los resultados de forma natural, clara y atractiva.

    Si no se ejecutaron herramientas, devuelve directamente la respuesta
    original del modelo.

    Args:
        response (AIMessage): Respuesta original del LLM después de la
        primera llamada.
        tool_results (List[Dict[str, Any]]): Lista de resultados de las
        herramientas ejecutadas.
        state (TravelState): Estado actual del viaje (contiene los vuelos
        encontrados, etc.).

    Returns:
        str: Respuesta final lista para mostrar al usuario.
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