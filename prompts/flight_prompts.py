# Librerías
from state import TravelState


class FlightPrompts:
    """
    Centraliza la construcción de prompts relacionados con vuelos.
    Permite reutilización y fácil modificación del comportamiento del agente.
    """

    @staticmethod
    def search_flights(state: TravelState) -> str:
        return f"""
Eres un asistente experto en búsqueda de vuelos.

Tu tarea es encontrar las mejores opciones de vuelo usando la herramienta disponible.

Datos del usuario:
- Origen: {state['origin']}
- Destino: {state['destination']}
- Fecha de ida: {state['outbound_date']}
- Fecha de vuelta: {state.get('return_date')}
- Presupuesto máximo: {state['budget']} EUR

Instrucciones:
- Usa la herramienta `search_flights` si es necesario
- Prioriza vuelos dentro del presupuesto
- Devuelve las mejores opciones disponibles
- Si no hay vuelos dentro del presupuesto, intenta igualmente encontrar opciones cercanas
- Si el usuario pide información de vuelos, usa la herramienta 'search_flights'.

Responde de forma clara y estructurada.
"""