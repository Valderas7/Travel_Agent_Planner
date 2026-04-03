# Librerías
from pydantic import BaseModel
from typing import List, Optional


class FlightLeg(BaseModel):
    """
    Modelo que representa un vuelo individual (ida o vuelta), incluyendo
    detalles como códigos de aeropuertos y nombres, tiempos de salida y
    llegada, aerolíneas, números de vuelos, duración del vuelo y avión
    """
    departure_airport_code: str      
    departure_airport_name: str
    departure_time: str              
    arrival_airport_code: str
    arrival_airport_name: str
    arrival_time: str
    airline: str
    flight_number: str
    duration_minutes: Optional[int] = None
    airplane: Optional[str] = None


class FlightOption(BaseModel):
    """
    Modelo que representa una opción completa de vuelo (ida + vuelta).
    """
    outbound_flight: FlightLeg
    return_flight: Optional[FlightLeg] = None
    price: float


class FlightSearchResult(BaseModel):
    """
    Modelo que representa una lista de opciones completas de vuelos (ida +
    vuelta).
    """
    flights: List[FlightOption]
