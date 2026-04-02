# Librerías
from pydantic import BaseModel
from typing import List


class FlightOption(BaseModel):
    """
    Clase que representa una opción de vuelo, incluyendo detalles como
    precio, aerolíneas, horas de despegue y llegada en la ida y la vuelta
    y números de vuelo."""
    price: str
    outbound_airport: str
    outbound_airline: str
    outbound_departure_time: str
    outbound_arrival_time: str
    outbound_flight_number: str
    return_airport: str
    return_airline: str
    return_departure_time: str
    return_arrival_time: str
    return_flight_number: str


class FlightSearchResult(BaseModel):
    """
    Clase que representa el resultado de la búsqueda de vuelos, conteniendo una
    lista de opciones de vuelo que cumplen con los criterios especificados en el
    estado del viaje.
    """
    flights: List[FlightOption]


class ChatRequest(BaseModel):
    """
    Clase que representa una consulta al modelo de lenguaje en modo chat,
    con la representación del mensaje de la consulta y el estado
    """
    message: str
    state: dict | None = None