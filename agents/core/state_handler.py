# Librerías
from state import create_travel_state, TravelState


def initialize_state(current_state: dict | None) -> TravelState:
    """
    Inicializa el estado del viaje a partir de un diccionario existente
    o crea uno nuevo si no se proporciona.
    
    Args:
        current_state (dict | None): Estado previo del viaje en formato
        diccionario. Puede contener información como origen, destino,
        fechas o resultados anteriores.

    Returns:
        TravelState: Instancia de TravelState inicializada con los datos
        proporcionados o vacía si no se pasó ningún estado.
"""
    return create_travel_state(current_state)


def serialize_state(state: TravelState) -> dict:
    """
    Convierte un objeto TravelState en un diccionario serializable.

    Args:
        state (TravelState): Objeto que representa el estado actual del viaje.

    Returns:
        dict: Representación del estado en formato diccionario.
    """
    return state.model_dump()
