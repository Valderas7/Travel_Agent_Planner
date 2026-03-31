# Librerías
from langchain_openai import ChatOpenAI
from state import TravelState
from prompts.flight_prompt import FlightSearchPrompt
from models.flight_models import FlightSearchResult

# Se instancia el modelo de lenguaje local de LM Studio
llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    model="nvidia/nemotron-3-nano-4b",
    temperature=0,
)
structured_llm = llm.with_structured_output(FlightSearchResult)


def flight_agent(state: TravelState) -> TravelState:
    """
    Agente encargado de buscar opciones de vuelos basándose en el destino y
    las fechas proporcionadas en el estado del viaje.

    Args:
        state (TravelState): El estado actual del viaje

    Returns:
        TravelState: El estado actualizado con las opciones de vuelos
        encontradas
    """
    # Se genera el prompt para el agente de búsqueda de vuelos usando
    # la información del estado del viaje
    prompt = FlightSearchPrompt.generate(state)

    # Se invoca el modelo estructurado para obtener las opciones de vuelos
    result = structured_llm.invoke(prompt)

    # Se actualiza el estado con las opciones de vuelos obtenidas
    return {
        **state,
        "flights": result.flights
    }