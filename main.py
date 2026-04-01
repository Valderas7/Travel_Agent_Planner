# Librerías
from api.routes import router
from core.logging import setup_logging
from fastapi import FastAPI

# Inicia el logger
logger = setup_logging()

# Inicia la API
app = FastAPI()

# Incluye en la API el enrutador
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)