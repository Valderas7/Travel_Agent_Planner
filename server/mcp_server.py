# Librerías
import logging
from fastmcp import FastMCP
from server.lifespan import lifespan
from server.tools.flights.search_flights import search_flights

# Se obtiene el logger para este módulo
logger = logging.getLogger(__name__)

# Se instancia el servidor MCP con el lifespan definido
mcp = FastMCP("travel-tools", lifespan=lifespan)

# Se añade la herramienta de búsqueda de vuelos
mcp.tool(search_flights)

# Se configura el MCP para operar en modo HTTP sin estado en la raíz
mcp_app = mcp.http_app(path='/', stateless_http=True)
logger.info("Servidor MCP 'travel-tools' iniciado con múltiples herramientas.")