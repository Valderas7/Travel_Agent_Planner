#Librerías
from pydantic import BaseModel
from typing import List


class FlightOption(BaseModel):
    """
    Clase que representa una opción de vuelo, incluyendo detalles como
    aerolínea, precio, horarios de salida y regreso, y si es directo o
    con escalas."""
    airline: str
    price: float
    departure_time: str
    return_time: str
    direct: bool


class FlightSearchResult(BaseModel):
    """
    Clase que representa el resultado de la búsqueda de vuelos, conteniendo una
    lista de opciones de vuelo que cumplen con los criterios especificados en el
    estado del viaje.
    """
    flights: List[FlightOption]