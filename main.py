# Librerías
from api.routes import router
from core.logging import setup_logging
from fastapi import FastAPI
from server.mcp_server import mcp_app

# Inicia el logger
setup_logging()

# Inicia la API usando el lifespan del MCP
app = FastAPI(
    title='Agente Planeador de Viajes',
    lifespan=mcp_app.lifespan
)

# Incluye en la API el enrutador y monta el servidor MCP en '/mcp'
app.include_router(router)
app.mount("/mcp", mcp_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000)