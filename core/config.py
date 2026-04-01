# Librerías
import os


# Clase para obtener variables de entorno
class Settings:
    SERPAPI_KEY=os.getenv("SERPAPI_KEY", "98c854b25d527649497530e342814dc9efca3e6ed56a89aff9b5f26adf6445e6")
    MCP_URL = os.getenv("MCP_URL", "http://localhost:8000")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
    LLM_MODEL = os.getenv("LLM_MODEL", "mistralai/ministral-3-3b")

# Instancia de la clase
settings = Settings()