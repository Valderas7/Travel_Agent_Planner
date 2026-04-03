# Librerías
from agent.state import GraphState
from langchain_core.messages import SystemMessage, HumanMessage
from core.llm import llm


async def response_node(state: GraphState):

    # Si no se han encontrado vuelos en el estado, se devuelve éste y una
    #respuesta indicando que no se han encontrado vuelos
    if not state.get("flights"):
        return {
            **state,
            "response": "No se han encontrado vuelos con los criterios dados."
        }

    # Lista de mensajes
    messages = [
        SystemMessage(content="Eres un asistente de viajes."),
        HumanMessage(content=f"Vuelos:\n{state['flights']}")
    ]

    result = await llm.ainvoke(messages)

    return {
        **state,
        "response": result.content
    }