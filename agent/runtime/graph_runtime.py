# Librerías
from agent.runtime.mcp_manager import MCPManager
from langgraph.graph.state import CompiledStateGraph

# Se inicia una instancia singleton del gestor MCP 
_mcp_manager = MCPManager()


async def get_graph() -> CompiledStateGraph:
    """
    Obtiene el grafo compilado del agente de viajes.

    Este método inicializa el entorno MCP (session, tools y grafo)
    únicamente la primera vez que se invoca. En llamadas posteriores,
    reutiliza la instancia ya creada, evitando overhead innecesario.

    Returns:
        CompiledStateGraph: Grafo de LangGraph listo para ejecución,
        con tools MCP enlazadas y memoria habilitada.
    """
    return await _mcp_manager.init()


async def close_graph() -> None:
    """
    Cierra la sesión MCP activa y libera recursos asociados.

    Debe utilizarse en eventos de apagado de la aplicación (shutdown),
    para cerrar correctamente la conexión con el servidor MCP y evitar
    fugas de recursos o conexiones colgadas.
    """
    await _mcp_manager.close()