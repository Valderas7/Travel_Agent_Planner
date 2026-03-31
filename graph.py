# Librerías
from agents.flight_agent import flight_agent
from agents.stay_agent import stay_agent
from agents.activities_agent import activities_agent
from agents.host_agent import host_agent
from langgraph.graph import StateGraph, END
from state import TravelState


def build_graph():
    """
    Construye el grafo de estados para el planificador de viajes, definiendo
    los nodos para cada agente (host, vuelos, hoteles, actividades) y las
    conexiones entre ellos
    """
    graph = StateGraph(TravelState)

    # nodos
    graph.add_node("host", host_agent)
    graph.add_node("flights", flight_agent)
    graph.add_node("hotels", stay_agent)
    graph.add_node("activities", activities_agent)

    # flujo principal
    graph.set_entry_point("host")

    graph.add_edge("host", "flights")
    graph.add_edge("host", "hotels")
    graph.add_edge("host", "activities")

    # convergencia final
    graph.add_edge("flights", END)
    graph.add_edge("hotels", END)
    graph.add_edge("activities", END)

    return graph.compile()