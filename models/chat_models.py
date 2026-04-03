# Librerías
from pydantic import BaseModel


class ChatRequest(BaseModel):
    """
    Clase que representa una consulta al modelo de lenguaje en modo chat,
    con la representación del mensaje de la consulta
    """
    message: str