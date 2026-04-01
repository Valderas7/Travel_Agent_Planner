# Librerías
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (solo en desarrollo)
load_dotenv()


# Clase para obtener variables de entorno
class Settings:
    MCP_URL = os.getenv("MCP_URL")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL")
    LLM_MODEL = os.getenv("LLM_MODEL")
    SERPAPI_KEY=os.getenv("SERPAPI_KEY")
    SERPAPI_URL=os.getenv("SERPAPI_URL")

# Instancia de la clase
settings = Settings()