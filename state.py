# Librerías
from typing import TypedDict, List, Optional, Dict, Any


class TravelState(TypedDict):
    """
    Clase que representa el estado del viaje, incluyendo detalles como origen,
    destino, fechas, presupuesto, opciones de vuelos, hoteles, actividades y
    el itinerario generado.
    """
    origin: str
    destination: str
    start_date: str
    end_date: str
    budget: float

    flights: Optional[List[Dict[str, Any]]]
    hotels: Optional[List[Dict[str, Any]]]
    activities: Optional[List[Dict[str, Any]]]

    itinerary: Optional[str]