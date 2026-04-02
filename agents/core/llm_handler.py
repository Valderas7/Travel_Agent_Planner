# Librerías
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_core.runnables import Runnable
from typing import Callable, Sequence
from state import TravelState


async def invoke_llm(
    llm_with_tools: Runnable[Sequence, AIMessage],
    user_message: str,
    state: TravelState,
    system_prompt_function: Callable
) -> AIMessage:
    """
    Construye el prompt del sistema junto con el mensaje del usuario y realiza
    una llamada al modelo de lenguaje con soporte para herramientas (tools).

Args:
    llm_with_tools (Runnable[Sequence[BaseMessage], AIMessage]): Modelo de
    lenguaje con herramientas enlazadas mediante `bind_tools`.
    user_message (str): Mensaje en lenguaje natural proporcionado por el
    usuario.
    state (TravelState): Estado actual del flujo de viaje, utilizado para
    construir el contexto del prompt.

Returns:
    AIMessage: Respuesta del modelo de lenguaje. Puede contener:
    - `content`: texto generado por el modelo.
    - `tool_calls`: lista de llamadas a herramientas.
    """
    # Se crea el prompt de sistema para la herramienta adecuada
    system_prompt = system_prompt_function(state)

    # Se crea la lista de mensajes con el prompt de sistema y el de
    # usuario (la consulta al LLM)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    # Se invoca al modelo de lenguaje con las herramienta enlazadas
    return await llm_with_tools.ainvoke(messages)