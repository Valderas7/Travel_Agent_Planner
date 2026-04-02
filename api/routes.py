# Librerías
from agents.flight_agent import flight_agent
from agents.flight_agent_chat import travel_agent
from fastapi import APIRouter
from models.flight_models import ChatRequest
from state import TravelState

# Enrutador de FastAPI
router = APIRouter()


# Se crea un endpoint en 'POST' 
@router.post("/flights", tags=['Vuelos'])
async def search_flights_endpoint(state: TravelState):
    return await flight_agent(state)


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