from langgraph.graph import StateGraph, START, END
from state import TravelState

from flight_agent import flight_agent
from hotel_agent import hotel_agent   # ← nuevo import


async def flight_node(state: TravelState) -> TravelState:
    return await flight_agent(state)


async def hotel_node(state: TravelState) -> TravelState:
    return await hotel_agent(state)


def should_continue(state: TravelState):
    if not state.get("flights"):
        return "end"
    return "hotels"          # siempre pasamos a hoteles si hay vuelos


def build_travel_graph():
    builder = StateGraph(TravelState)

    builder.add_node("flights", flight_node)
    builder.add_node("hotels", hotel_node)

    builder.add_edge(START, "flights")
    builder.add_conditional_edges("flights", should_continue, {"hotels": "hotels", "end": END})
    builder.add_edge("hotels", END)

    return builder.compile()