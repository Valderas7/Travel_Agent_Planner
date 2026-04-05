# Librerías
from state import TravelState
from typing import TypedDict, List, Dict, Any


class GraphState(TypedDict):
    """
    Estado compartido del grafo de ejecución del agente de viajes. Se pasa
    entre todos los nodos del grafo y actúa como única fuente de verdad
    durante la ejecución del agente.

    Campos:
        user_message (str): Mensaje original del usuario en lenguaje natural.
        travel_state (TravelState): Estado semántico del viaje. Contiene
            información estructurada como origen, destino, fechas,
            presupuesto, vuelos, etc.
        messages (List): Historial de mensajes intercambiados con el LLM,
            incluyendo:
                - SystemMessage (prompt inicial)
                - HumanMessage (entrada del usuario)
                - AIMessage (respuestas del modelo)
                - ToolMessage (resultados de herramientas)
            Este historial permite al modelo razonar de forma iterativa.
        tool_results (List[Dict[str, Any]]): Resultados estructurados devueltos
            por las herramientas ejecutadas.
        response (str): Respuesta final generada para el usuario.
    """
    user_message: str
    travel_state: TravelState
    messages: List
    tool_results: List[Dict[str, Any]]
    response: str