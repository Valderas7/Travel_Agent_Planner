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
        )

        # Se ejecuta el grafo
        final_state = await graph.ainvoke(state)

        # Se devuelve un diccionario
        return {
            "response": final_state["response"],
            "flights": final_state["travel_state"].flights,
            "state": final_state,
            "tool_results": final_state["tool_results"]
        }
    