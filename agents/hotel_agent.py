import os
from langchain_openai import ChatOpenAI
from state import TravelState
from mcp.client.stdio import stdio_client, StdioServerParameters
from langchain_mcp_adapters.tools import load_mcp_tools


async def hotel_agent(state: TravelState) -> TravelState:
    """
    Nodo que busca hoteles reales usando tu segundo MCP server + SerpAPI.
    """
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_hotel_server.py"],
        env={"SERPAPI_KEY": os.getenv("SERPAPI_KEY")},
    )

    async with stdio_client(server_params) as (read, write):
        tools = await load_mcp_tools(read, write)

        result = await tools[0].ainvoke({
            "destination": state["destination"],
            "check_in_date": state["outbound_date"],      # usamos las mismas fechas del vuelo
            "check_out_date": state.get("return_date") or state["outbound_date"],
            "budget": state["budget"] * 0.6,              # ejemplo: 60% del presupuesto total para hoteles
            "adults": state.get("adults", 1),
        })

        return {
            **state,
            "hotels": [hotel.model_dump() for hotel in result.hotels]
        }