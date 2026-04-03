# Librerías
from typing import TypedDict, List, Dict, Any


class GraphState(TypedDict):
    """
    Estado del grafo.
    """
    user_message: str
    travel_state: dict
    messages: List
    tool_calls: Any
    tool_results: List[Dict[str, Any]]
    response: str