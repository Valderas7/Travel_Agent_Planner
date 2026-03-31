# Librerías
from state import TravelState


class FlightSearchPrompt:
    """
    Clase que genera el prompt para el agente de búsqueda de vuelos, utilizando
    la información del estado del viaje (origen, destino, fechas, presupuesto)
    para solicitar opciones de vuelos realistas.
    """
    @staticmethod
    def generate(state: TravelState) -> str:
        """
        Genera el prompt para el agente de búsqueda de vuelos.

        Args:
            state (TravelState): El estado actual del viaje

        Returns:
            str: El prompt generado para el agente de búsqueda de vuelos
        """
        f"""
Eres un asistente de búsqueda de vuelos.

Viaje del usuario:
- De: {state["origin"]}
- A: {state["destination"]}
- Fechas: {state["start_date"]} → {state["end_date"]}
- Presupuesto: {state["budget"]} EUR

Task:
Sugiere 2-3 opciones de vuelo realistas.
"""