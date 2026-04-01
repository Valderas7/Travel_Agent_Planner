# Librerías
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (solo en desarrollo)
load_dotenv()


# Clase para obtener variables de entorno
class Settings:
    SERPAPI_KEY=os.getenv("SERPAPI_KEY")
    MCP_URL = os.getenv("MCP_URL")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL")
    LLM_MODEL = os.getenv("LLM_MODEL")

# Instancia de la clase
settings = Settings()