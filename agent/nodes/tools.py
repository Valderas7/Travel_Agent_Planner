# Librerías
import logging
from core.utils import parse_tool_output
from typing import Any, Dict, List

# Se obtiene el logger del módulo
logger = logging.getLogger(__name__)


async def tool_node(
    state: Dict[str, Any],
    tools: List[Any],
) -> Dict[str, Any]:
    """
    Ejecuta las tool calls generadas por el LLM

    Args:
        state (GraphState): Estado actual del grafo, incluyendo mensajes,
            tool_calls y travel_state.
        tools (List[Any]): Lista de herramientas disponibles (MCP tools o
            similares).

    Returns:
        Dict[str, Any]: Grafo actualizado
    """
    # Se obtiene el último 'AIMessage' (respuesta del modelo) del estado
    response = state["messages"][-1]

    # Lista para recopilar resultados de herramientas
    tool_results = []

    # Para cada llamada a herramienta dentro de la respuesta...
    for tool_call in response.tool_calls:

        # Se obtiene el nombre de la herramienta
        tool = next((t for t in tools if t.name == tool_call["name"]), None)

        # Si no existe, se continúa
        if not tool:
            continue
        
        # Se llama a la herramienta con los argumentos requeridos
        raw = await tool.ainvoke(tool_call["args"])

        # Se intenta normalizar la salida de cualquier herramienta MCP, ya
        # sea diccionario, lista o lo que sea
        data = parse_tool_output(raw)

        # Se añade a la lista de herramientas el nombre de la misma y el
        # resultado tras llamarla
        tool_results.append({
            "tool": tool_call["name"],
            "data": data
        })

    # Se devuelve un diccionario con el estado actualizado con los resultados
    # de las herramientas, además de limpiar las llamadas a herramientas, ya
    # que ya se han realizado en este punto
    return {
        **state,
        "tool_calls": None,
        "tool_results": tool_results
    }
