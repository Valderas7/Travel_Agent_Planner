# Librerías
from typing import Any, Dict


def update_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aplica resultados de búsqueda de vuelos al estado del grafo.

    Args:
        state (Dict[str, Any]): Estado del grafo (mutable).
        data (Dict[str, Any]): Datos normalizados de la herramienta.
        tool_results (List[Dict[str, Any]]): Lista de trazas de herramientas.

    Returns:
        Dict[str, Any]: Estado del grafo actualizado.
    """
    # Se obtienen los resultados de las llamadas a herramientas
    tool_results = state.get("tool_results", [])

    # Para cada resultado...
    for result in tool_results:
        
        # Si es la herramienta de vuelos...
        if result["tool"] == "search_flights":
            
            # Se obtienen los vuelos
            data = result.get("data", {})
            flights = data.get("flights", [])

            # Si no hay vuelos se continúa
            if not flights:
                continue

            # Se actualizan los vuelos del estado del viaje
            state["travel_state"].flights.extend(flights)

            # Extraer info del primer vuelo
            first = flights[0]

            # Se obtienen los datos de un vuelo de ida y se actualiza el
            # estado del viaje
            outbound = first.get("outbound_flight")
            if outbound:
                if outbound.get("departure_airport_code"):
                    state["travel_state"].origin = outbound["departure_airport_code"]

                if outbound.get("arrival_airport_code"):
                    state["travel_state"].destination = outbound["arrival_airport_code"]

                if outbound.get("departure_time"):
                    state["travel_state"].outbound_date = outbound["departure_time"].split(" ")[0]
            
            # Se obtienen los datos de un vuelo de vuelta y se actualiza el
            # estado del viaje
            return_flight = first.get("return_flight")
            if return_flight and return_flight.get("departure_time"):
                state["travel_state"].return_date = return_flight["departure_time"].split(" ")[0]

    # Se devuelve el estado actualizado
    return state
    