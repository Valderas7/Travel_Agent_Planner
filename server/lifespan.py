# Librerías
import logging
import httpx
from contextlib import asynccontextmanager
from fastmcp import FastMCP
from typing import AsyncIterator

# Se obtiene el logger del módulo
logger = logging.getLogger(__name__)


# Se crea una función de contexto para manejar el ciclo de vida del servidor
# MCP, incluyendo la creación y cierre del cliente HTTP asíncrono
@asynccontextmanager
async def lifespan(mcp: FastMCP) -> AsyncIterator[None]:
    """
    Contexto de vida del servidor MCP, que se encarga de crear y cerrar el
    cliente HTTP asíncrono utilizado para realizar las solicitudes a SerpAPI.
    
    Args:
        mcp (FastMCP): La instancia del servidor MCP que se está ejecutando
    """
    # Se crea un cliente HTTP asíncrono con límites de conexión para
    # reaizar las solicitudes de manera eficiente
    client = httpx.AsyncClient(
        timeout=15.0,
        limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
        follow_redirects=True,
    )
    logger.info("Cliente HTTP para SerpAPI inicializado.")

    # Se asigna el cliente HTTP al estado del servidor MCP para que esté
    # disponible en las herramientas
    yield {"http_client": client}
    
    # Al finalizar el contexto, se cierra el cliente HTTP para liberar
    # recursos
    await client.aclose()
    logger.info("Cliente HTTP cerrado.")
