# Librerías
from typing import Any, Dict


def handle_search_flights(
    state: Dict[str, Any],
    data: Dict[str, Any]
) -> None:
    """
    Aplica los resultados de la herramienta `search_flights` al estado del
    agente.

    - Añade los vuelos al estado (`travel_state.flights`)
    - Extrae metadatos del primer vuelo (origen, destino, fechas)

    Args:
        state: Estado global del grafo que contiene `travel_state`.
        data: Resultado normalizado de la herramienta de vuelos. Se espera
            un diccionario con clave `flights`.
    """
    # Se obtienen los vuelos de la respuesta de la herramienta de vuelos
    flights = data.get("flights", [])

    # Si no hay vuelos no se devuelve nada
    if not flights:
        return

    # Se selecciona el estado del viaje que hay dentro del grafo y se
    # extienden los vuelos con los obtenidos de la herramienta de vuelos
    travel = state["travel_state"]
    travel.flights.extend(flights)

    # Se aplican los metadatos
    _apply_flight_metadata(travel, flights[0])


def _apply_flight_metadata(travel: Any, first: Dict[str, Any]) -> None:
    """
    Extrae y aplica metadatos relevantes del primer vuelo al estado del viaje.

    Actualiza:
    - origin
    - destination
    - outbound_date
    - return_date

    Args:
        travel: Objeto `TravelState` que se actualiza.
        first_flight: Primer elemento de la lista de vuelos devuelta por la
            herramienta.
    """
    # Se obtiene el vuelo de ida del primer grupos de vuelos
    outbound = first.get("outbound_flight")

    # Si hay vuelo de ida se actualiza el origen y el destino del viaje
    if outbound:
        travel.origin = outbound.get("departure_airport_code")
        travel.destination = outbound.get("arrival_airport_code")

        # Se obtiene la fecha y hora de salida del vuelo de ida
        departure = outbound.get("departure_time")

        # Si existe, se actualiza la fecha de comienzo del viaje
        if departure:
            travel.outbound_date = departure.split(" ")[0]

    # Se obtiene el vuelo de vuelta
    return_flight = first.get("return_flight")

    # Si hay vuelo de vuelta, se comprueba la fecha y hora de salida
    if return_flight:
        departure = return_flight.get("departure_time")

        # Si existe, se actualiza la fecha de fin del viaje
        if departure:
            travel.return_date = departure.split(" ")[0]