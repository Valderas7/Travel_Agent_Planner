# Librerías
from agent.state import GraphState


def should_call_tools(state: GraphState):
    return state.get("tool_calls") is not None


def should_finish(state: GraphState):
    return state.get("flights") is not None