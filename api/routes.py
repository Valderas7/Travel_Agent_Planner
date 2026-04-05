# Librerías
from agent.entrypoint import travel_agent
from fastapi import APIRouter
from models.chat_models import ChatRequest
from typing import Any, Dict

# Enrutador de FastAPI
router = APIRouter()


@router.post("/chat", tags=['Asistente Conversacional'])
async def chat_endpoint(request: ChatRequest) -> Dict[str, Any]:
    """
    Endpoint conversacional principal.
    Permite al usuario hablar en lenguaje natural.
    """
    # Se obtiene el ID de sesión
    thread_id = request.session_id

    # Se llama a la función que es el punto de entrada del agente
    result = await travel_agent(
        user_message=request.message,
        thread_id=thread_id
    )

    # Se devuelve el resultado
    return result