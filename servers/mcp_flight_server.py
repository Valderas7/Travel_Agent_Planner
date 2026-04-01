# Librerías
import logging
import os
import httpx
from contextlib import asynccontextmanager
from fastmcp import Context, FastMCP
from models.flight_models import FlightOption, FlightSearchResult
from typing import AsyncIterator, Dict, Optional

# Se obtiene el logger para este módulo
logger = logging.getLogger(__name__)


# Se crea una función de contexto para manejar el ciclo de vida del servidor
# MCP, incluyendo la creación y cierre del cliente HTTP asíncrono
@asynccontextmanager
async def lifespan(mcp: FastMCP) -> AsyncIterator[None]:
    """
    Contexto de vida del servidor MCP, que se encarga de crear y cerrar el
    cliente HTTP asíncrono utilizado para realizar las solicitudes a SerpAPI.
    
    Args:
        mcp (FastMCP): La instancia del servidor MCP que se está ejecutando
    """
    # Se crea un cliente HTTP asíncrono con límites de conexión para
    # reaizar las solicitudes de manera eficiente
    client = httpx.AsyncClient(
        timeout=15.0,
        limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
        follow_redirects=True,
    )

    # Se asigna el cliente HTTP al estado del servidor MCP para que esté
    # disponible en las herramientas
    yield {"http_client": client}
    
    # Al finalizar el contexto, se cierra el cliente HTTP para liberar
    # recursos
    await client.aclose()

# Se instancia el servidor MCP con el lifespan definido
mcp = FastMCP("flight-search", lifespan=lifespan)


# Se define una herramienta MCP para buscar vuelos usando Google Flights
# a través de SerpAPI 
@mcp.tool(
    name="search_flights",
    title="Buscar vuelos",
    description=(
        "Busca vuelos reales con precios usando Google Flights. Filtra por "
        "presupuesto."
    ),
    annotations={
        "origin": "Código IATA del aeropuerto de origen (ej: MAD)",
        "destination": "Código IATA del aeropuerto de destino (ej: NYC)",
        "outbound_date": "Fecha de salida YYYY-MM-DD",
        "return_date": "Fecha de regreso YYYY-MM-DD (opcional)",
        "budget": "Presupuesto máximo por persona"
    }
)
async def mcp_search_flights(
    ctx: Context,
    origin: str,
    destination: str,
    outbound_date: str,
    return_date: Optional[str] = None,
    budget: float = 1000,
) -> FlightSearchResult:
    """
    Busca vuelos reales con precios usando Google Flights a través de SerpAPI.
    Filtra por presupuesto.
    
    Args:
        origin (str): Código IATA del aeropuerto de origen (ej: MAD)
        destination (str): Código IATA del aeropuerto de destino (ej: NYC)
        outbound_date (str): Fecha de salida en formato YYYY-MM-DD
        return_date (Optional[str]): Fecha de regreso en formato YYYY-MM-DD (opcional)
        budget (float): Presupuesto máximo por persona para el vuelo

    Returns:
        FlightSearchResult: Resultado de la búsqueda de vuelos, con una lista de
        opciones de vuelo que cumplen con los criterios especificados.
    """
    # Se almacena el cliente HTTP asíncrono
    client: httpx.AsyncClient = ctx.lifespan_context["http_client"]

    # Parámetros para la consulta a SerpAPI
    search_params = {
        "engine": "google_flights",
        "hl": "es",
        "gl": "es",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "currency": "EUR",
        "api_key": os.getenv("SERPAPI_KEY"),
    }

    # Se intenta...
    try:

        # Se realiza la solicitud 'GET' a SerpAPI para obtener los datos de vuelos
        response = await client.get(
            "https://serpapi.com/search",
            params=search_params
        )
        response.raise_for_status()

        # Se transforma la respuesta en un diccionario
        data = response.json()

    # En caso de excepción se devuelve lista vacía
    except Exception:
        logger.exception("Error al realizar la solicitud a SerpAPI.")
        return FlightSearchResult(flights=[])

    # Lista vacía para almacenar las opciones de vuelo
    flights = []

    # Dentro de la lista de mejores vuelos de los resultados de SerpAPI...
    for group, flight_group in enumerate(data.get("best_flights", [])):

        # Se obtienen los vuelos de ida y vuelta dentro de cada grupo de
        # mejores vuelos
        legs = flight_group.get("flights", [])

        # Si no hay vuelos se continua
        if not legs:
            continue
        
        # Se obtiene el precio de esos vuelos
        price = flight_group.get("price") or 0

        # Si el precio es superior a nuestro presupuesto, se continúa
        if price > budget:
            logger.info(f"Grupo {group+1} descartado por precio.")
            continue

        # Se toma el primer 'leg' como la ida y el segundo como la vuelta
        outbound_leg = legs[0]
        return_leg = legs[-1] if return_date and len(legs) > 1 else None

        # Se recopila la información del vuelo de ida
        outbound_airport = outbound_leg.get("departure_airport", {}).get("name", "N/A")
        outbound_airline = outbound_leg.get("airline", "Desconocida")
        outbound_departure = outbound_leg.get("departure_airport", {}).get("time", "N/A")
        outbound_arrival = outbound_leg.get("arrival_airport", {}).get("time", "N/A")
        outbound_flight_number = outbound_leg.get("flight_number", "")

        # Se recopila la información del vuelo de vuelta
        return_airport = return_leg.get("departure_airport", {}).get("name", "N/A")
        return_airline = return_leg.get("airline", "Desconocida")
        return_departure = return_leg.get("departure_airport", {}).get("time", "N/A")
        return_arrival = return_leg.get("arrival_airport", {}).get("time", "N/A")
        return_flight_number = return_leg.get("flight_number", "")

        # Se añade a la lista el vuelo con los datos correspondientes
        flights.append(
            FlightOption(
                price=f"{float(price)}€",
                outbound_airport=outbound_airport,
                outbound_airline=outbound_airline,
                outbound_departure_time=outbound_departure,
                outbound_arrival_time=outbound_arrival,
                outbound_flight_number=outbound_flight_number,
                return_airport=return_airport,
                return_airline=return_airline,
                return_departure_time=return_departure,
                return_arrival_time=return_arrival,
                return_flight_number=return_flight_number
            )
        )

    # Se devuelve un máximo de 5 opciones de vuelo
    return FlightSearchResult(flights=flights[:5])


# Se configura el MCP para operar en modo HTTP sin estado en la raíz
mcp_app = mcp.http_app(path='/', stateless_http=True)