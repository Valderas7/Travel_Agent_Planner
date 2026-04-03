# Librerías
from agent.state import GraphState


async def tool_node(state: GraphState, tools, process_tool_calls_fn):
    response = state["messages"][-1]

    tool_results = await process_tool_calls_fn(
        response,
        tools,
        state
    )

    return {
        **state,
        "tool_results": tool_results
    }