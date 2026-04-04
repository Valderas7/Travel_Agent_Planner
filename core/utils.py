# Librerías
import logging
import json
from typing import Any, Dict

# Logger del módulo
logger = logging.getLogger(__name__)


def parse_tool_output(raw_result: Any) -> Dict[str, Any]:
    """
    Normaliza la salida de cualquier herramienta MCP a un diccionario
    estándar.

    Args:
        raw_result (Any): Resultado bruto de la herramienta.

    Returns:
        Dict[str, Any]: Resultado normalizado en formato diccionario.
    """
    # Se intenta...
    try:

        # Si el resultado tiene atributo para convertir a diccionario, se usa
        if hasattr(raw_result, "model_dump"):
            return raw_result.model_dump()

        # Si el resultado es directamente un diccionario, se devuelve
        if isinstance(raw_result, dict):
            return raw_result

        # Si es una lista, se obtiene el primer miembro
        if isinstance(raw_result, list) and raw_result:
            item = raw_result[0]

            # Si dicho miembro es un diccionario y la tiene la clave 'text',
            # se devuelve dicha clave parseada como diccionario
            if isinstance(item, dict) and "text" in item:
                return json.loads(item["text"])

        # Si por el contrario es un string, se convierte a diccionario y se
        # devuelve
        if isinstance(raw_result, str):
            return json.loads(raw_result)

    # Si hay excepción, se devuelve un diccionario
    except Exception:
        logger.exception(
            "Error al normalizar la respuesta de la herramienta MCP."
        )
        return {}

    # Se devuelve diccionario
    return {}
