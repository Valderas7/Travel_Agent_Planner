# Librerías
from agents.flight_agent import flight_agent
from fastapi import APIRouter
from state import TravelState

# Enrutador de FastAPI
router = APIRouter()


# Se crea un endpoint en 'POST' 
@router.post("/flights")
async def search_flights_endpoint(state: TravelState):
    return await flight_agent(state)