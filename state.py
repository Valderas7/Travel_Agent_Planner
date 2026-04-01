# Librerías
from typing_extensions import TypedDict


class TravelState(TypedDict):
    """
    Clase que representa el estado del viaje, incluyendo detalles como origen,
    destino, fechas, presupuesto, opciones de vuelos, hoteles, actividades y
    el itinerario generado.

    Atributos:
        origin (str): Código IATA del aeropuerto de origen (ej: MAD)
        destination (str): Código IATA del aeropuerto de destino (ej: NYC)
        outbound_date (str): Fecha de salida en formato YYYY-MM-DD
        return_date (Optional[str]): Fecha de regreso en formato YYYY-MM-DD
        (opcional)
        budget (float): Presupuesto máximo por persona para el viaje
        adults (int): Número de adultos que viajan
        flights (Optional[List[Dict[str, Any]]]): Lista de opciones de vuelos
        encontradas, cada una representada como un diccionario con detalles
        del vuelo
    """
    origin: str                    
    destination: str               
    outbound_date: str             
    return_date: str     
    budget: float