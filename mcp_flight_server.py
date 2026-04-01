# Librerías
import os
import httpx
from contextlib import asynccontextmanager
from fastmcp import Context, FastMCP
from models.flight_models import FlightOption, FlightSearchResult
from typing import AsyncIterator, Optional


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
async def search_flights(
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
    except Exception as e:
        return FlightSearchResult(flights=[])

    # Lista vacía para almacenar las opciones de vuelo
    flights = []

    # Dentro de la lista de mejores vuelos de los resultados de SerpAPI...
    for flight_group in data.get("best_flights", []) + data.get("flights", []):
        
        # Para cada vuelo dentro del grupo de mejores vuelos...
        for leg in flight_group.get("flights", []):

            # Se obtiene precio del vuelo
            price = flight_group.get("price", 0) or leg.get("price", 9999)

            # Si el precio es menor o igual al presupuesto, se añade a la lista
            if price <= budget:
                flights.append(FlightOption(
                    airline=leg.get("airline", "Desconocida"),
                    price=float(price),
                    departure_time=leg.get("departure", {}).get("time", "N/A"),
                    return_time=leg.get("arrival", {}).get("time", "N/A") if return_date else "N/A",
                    direct=leg.get("flight_number", "").startswith("Direct") or not leg.get("stops", 0),
                ))

    # Se devuelve un máximo de 10 opciones de vuelo
    return FlightSearchResult(flights=flights[:10])

# Se configura el MCP para operar en modo HTTP sin estado
app = mcp.http_app(stateless_http=True)