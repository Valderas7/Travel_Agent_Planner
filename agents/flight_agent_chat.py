# Librerías
import logging
import json
from core.llm import llm
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    SystemMessage,
    HumanMessage
)
from langchain_core.runnables import Runnable
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.client import MultiServerMCPClient
from prompts.flight_prompts import FlightPrompts
from state import TravelState
from typing import Sequence

# Se obtiene el logger del módulo
logger = logging.getLogger(__name__)


async def travel_agent(
    user_message: str,
    current_state: dict | None = None
) -> dict:
    """Agente conversacional principal del planeador de viajes"""

    # Se inicializa el estado actual
    state = _initialize_state(current_state)

    # Se intenta...
    try:

        # Se inicia cliente MCP 
        async with MultiServerMCPClient({
            "travel-tools": {
                "transport": "streamable_http",
                "url": "http://localhost:8000/mcp"
            }
        }).session("travel-tools") as session:

            # Se inicia una sesion
            await session.initialize()

            # Se cargan las herramientas del servidor MCP
            tools = await load_mcp_tools(session)
            logger.info(f"Herramientas cargadas correctamente: {len(tools)}")

            # Se enlazan las herramientas con el modelo de lenguaje, dejando
            # elección automática para la herramienta
            llm_with_tools = llm.bind_tools(tools, tool_choice="auto")

            # Consulta al modelo de lenguaje
            response = await _invoke_llm(llm_with_tools, user_message, state)

            # 2️⃣ Ejecutar tools
            tool_results = await _process_tool_calls(response, tools, state)

            # 3️⃣ Segunda llamada al LLM (si hubo tools)
            if tool_results:
                logger.info("Generando respuesta final con resultados de tools")

                followup = await llm.ainvoke([
                    SystemMessage(content="Resume los resultados de vuelos de forma clara para el usuario."),
                    HumanMessage(content=f"Resultados: {state.flights}")
                ])

                final_response = followup.content

            else:
                final_response = getattr(response, "content", str(response))

            return {
                "response": final_response,
                "flights": getattr(state, "flights", []),
                "state": _serialize_state(state),
                "tool_results": tool_results
            }

    except Exception:
        logger.exception("Error en travel_agent")
        return {
            "response": "Lo siento, ha ocurrido un error al procesar tu solicitud.",
            "flights": [],
            "state": _serialize_state(state) if 'state' in locals() else {},
            "tool_results": []
        }


def _initialize_state(current_state: dict | None) -> TravelState:
    """
    Inicializa el estado del viaje a partir de un diccionario existente
    o crea uno nuevo si no se proporciona.

    Args:
        current_state (dict | None): Estado previo del viaje en formato
            diccionario. Puede contener información como origen, destino,
            fechas o resultados anteriores.

    Returns:
        TravelState: Instancia de TravelState inicializada con los datos
        proporcionados o vacía si no se pasó ningún estado.
    """
    if current_state:
        return TravelState(**current_state)
    return TravelState()


async def _invoke_llm(
    llm_with_tools: Runnable[Sequence[BaseMessage], AIMessage],
    user_message: str,
    state: TravelState
) -> AIMessage:
    """
    Construye el prompt del sistema junto con el mensaje del usuario y realiza
    una llamada al modelo de lenguaje con soporte para herramientas (tools).

    Esta función:
    - Genera el prompt del sistema utilizando el estado actual del viaje.
    - Combina dicho prompt con el mensaje del usuario.
    - Invoca el LLM configurado con herramientas, permitiendo que el modelo
      decida si debe realizar llamadas a tools (tool_calls).

    Args:
        llm_with_tools (Runnable[Sequence[BaseMessage], AIMessage]):
            Modelo de lenguaje con herramientas enlazadas mediante `bind_tools`.
        user_message (str): Mensaje en lenguaje natural proporcionado por el usuario.
        state (TravelState): Estado actual del flujo de viaje, utilizado para
            construir el contexto del prompt.

    Returns:
        AIMessage: Respuesta del modelo de lenguaje. Puede contener:
            - `content`: texto generado por el modelo.
            - `tool_calls`: lista de llamadas a herramientas si el modelo decide usarlas.
    """
    # Se construye el prompt de sistema
    system_prompt = FlightPrompts.search_flights(state)

    # Lista de mensajes de sistema y usuario (consulta)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    # Devuelve respuesta del modelo de lenguaje con herramientas enlazadas
    return await llm_with_tools.ainvoke(messages)


async def _process_tool_calls(response, tools, state: TravelState) -> list:
    """Procesa las llamadas a herramientas."""

    tool_results = []

    if not getattr(response, "tool_calls", None):
        logger.info("No hay tool calls en la respuesta")
        return tool_results

    logger.info(f"Se detectaron {len(response.tool_calls)} tool calls")

    for tool_call in response.tool_calls:
        tool_name = tool_call.get("name")
        args = tool_call.get("args", {})

        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            logger.warning(f"Tool no encontrada: {tool_name}")
            continue
        logger.info(f"Ejecutando herramienta: {tool_name} con args: {args}")

        try:
            raw_result = await tool.ainvoke(args)
            _update_state_from_tool(raw_result, state, tool_results, tool_name)
        except Exception as e:
            logger.error(f"Error al ejecutar herramienta {tool_name}: {e}")

    return tool_results


def _update_state_from_tool(raw_result, state, tool_results, tool_name):
    """Actualiza el estado con los resultados de la herramienta."""

    try:
        new_flights = []

        if isinstance(raw_result, list) and raw_result:
            item = raw_result[0]

            if isinstance(item, dict) and "text" in item:
                text_content = item.get("text", "{}")
                parsed = json.loads(text_content)
                new_flights = parsed.get("flights", [])

        if new_flights:
            state.flights = new_flights
            tool_results.append({
                "tool": tool_name,
                "flights_found": len(new_flights)
            })
            logger.info(f"Se añadieron {len(new_flights)} vuelos")

    except Exception as e:
        logger.warning(f"No se pudo parsear resultado de {tool_name}: {e}")


def _serialize_state(state: TravelState) -> dict:
    """Serializa el estado para la respuesta."""
    if hasattr(state, "model_dump"):
        return state.model_dump()
    return dict(state)