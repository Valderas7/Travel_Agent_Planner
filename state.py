# Librerías
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class TravelState(BaseModel):
    """
    Clase que representa el estado del viaje. Se usa BaseModel para permitir
    campos dinámicos como 'flights', 'hotels', etc.

    Atributos:
        origin (str): Código IATA del aeropuerto de origen (ej: MAD)
        destination (str): Código IATA del aeropuerto de destino (ej: NYC)
        outbound_date (str): Fecha de salida en formato YYYY-MM-DD
        return_date (Optional[str]): Fecha de regreso en formato YYYY-MM-DD
        (opcional)
        budget (float): Presupuesto máximo por persona para el viaje
    """
    origin: Optional[str] = None                   
    destination: Optional[str] = None
    outbound_date: Optional[str] = None
    return_date: Optional[str] = None
    budget: Optional[float] = None
    flights: List[Dict[str, Any]] = Field(default_factory=list)
    hotels: List[Dict[str, Any]] = Field(default_factory=list)


# Función helper para crear estado desde dict
def create_travel_state(current_state: dict | None = None) -> TravelState:
    """
    Función que transforma un diccionario del estado del viaje a uno de tipo
    'TravelState'. Y si no hay estado, crea uno vacío
    """
    if current_state:
        return TravelState(**current_state)
    return TravelState()