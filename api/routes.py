# Librerías
from agents import travel_agent
from agents.travel_agent import travel_agent
from fastapi import APIRouter
from models.flight_models import ChatRequest

# Enrutador de FastAPI
router = APIRouter()


@router.post("/chat", tags=['Vuelos'])
async def chat_endpoint(request: ChatRequest):
    """
    Endpoint conversacional principal.
    Permite al usuario hablar en lenguaje natural.
    """
    result = await travel_agent(
        user_message=request.message,
        current_state=request.state
    )
    return result