# Librerías
from agent.graph import build_graph
from core.llm import llm
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.graph.state import CompiledStateGraph
from typing import Any, List, Optional


class MCPManager:
    """
    Gestor de ciclo de vida para la integración con
    MCP (Model Context Protocol).

    Esta clase se encarga de:
        - Crear y mantener una sesión persistente con el servidor MCP
        - Cargar herramientas (tools) una única vez
        - Construir y cachear el grafo de LangGraph
        - Evitar recreación innecesaria de recursos en cada request

    Diseñado para ser utilizado como singleton a nivel de aplicación.
    """

    def __init__(self) -> None:
        """
        Inicializa el cliente MCP y prepara atributos internos.

        No abre la sesión todavía (lazy initialization).
        """
        self.client = MultiServerMCPClient({
            "travel-tools": {
                "transport": "streamable_http",
                "url": "http://localhost:8000/mcp"
            }
        })

        self._ctx: Optional[Any] = None
        self.session: Optional[Any] = None
        self.tools: Optional[List[Any]] = None
        self.graph: Optional[CompiledStateGraph] = None

    async def init(self) -> CompiledStateGraph:
        """
        Inicializa la sesión MCP, carga herramientas y construye el grafo.

        Este método es idempotente:
            - Si el grafo ya está inicializado, lo devuelve directamente
            - Si no, inicializa todos los recursos necesarios

        Returns:
            CompiledStateGraph: Grafo compilado listo para ejecución
        """
        # Si ya está inicializado el grafo de estado, se devuelve
        if self.graph:
            return self.graph

        # Se abre el contexto MCP y se crea una sesión dentro del servidor MCP
        self._ctx = self.client.session("travel-tools")
        self.session = await self._ctx.__aenter__()
        await self.session.initialize()

        # Se cargan las herramientas del servidor MCP
        self.tools = await load_mcp_tools(self.session)

        # Se une el modelo con las herramientas MCP
        llm_with_tools = llm.bind_tools(self.tools, tool_choice="auto")

        # Se construye el grafo de ejecución
        self.graph = build_graph(
            llm_with_tools=llm_with_tools,
            tools=self.tools,
        )

        # Se devuelve el grafo de ejecución
        return self.graph

    async def close(self) -> None:
        """
        Cierra la sesión MCP y libera recursos asociados.
        """
        # Se sale del contexto
        if self._ctx:
            await self._ctx.__aexit__(None, None, None)

            # Se reinician todos los atributos
            self._ctx = None
            self.session = None
            self.tools = None
            self.graph = None
