import logging
from core.config import settings
from fastmcp import Context
from models.flight_models import FlightOption, FlightSearchResult
from typing import Optional

# Se obtiene el logger del módulo
logger = logging.getLogger(__name__)


async def search_flights(
    ctx: Context,
    origin: str,
    destination: str,
    outbound_date: str,
    return_date: Optional[str] = None,
    budget: float = 1000,
) -> FlightSearchResult:
    """
    Busca vuelos reales usando Google Flights a través de SerpAPI.
    """
    # Se obtiene el cliente HTTP asíncrono del lifespan
    client = ctx.lifespan_context["http_client"]

    # Parámetros de búsqueda
    search_params = {
        "engine": "google_flights",
        "hl": "es",
        "gl": "es",
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": outbound_date,
        "return_date": return_date,
        "currency": "EUR",
        "api_key": settings.SERPAPI_KEY
    }

    # Se intenta realizar la solicitud a SerpAPI
    try:
        response = await client.get(settings.SERPAPI_URL, params=search_params)
        response.raise_for_status()
        data = response.json()
    
    # Si hay excepción se devuelve una lista vacía
    except Exception:
        logger.exception("Error al llamar a SerpAPI.")
        return FlightSearchResult(flights=[])

    # Lista para recopiar los vuelos
    flights = []

    # Para cada grupo de mejores u otros vuelos...
    for flight_group in data.get("best_flights", []) + data.get("other_flights", []):

        # Se buscan los vuelos
        legs = flight_group.get("flights", [])

        # Si no hay, se continúa
        if not legs:
            continue
        
        # Se obtiene el precio de los vuelos
        price = flight_group.get("price") or 0

        # Si éste es mayor que el presupuesto o cero, se continúa
        if price > budget or price == 0:
            continue
        
        # Se almacena el vuelo de ida y el de vuelta
        outbound = legs[0]
        return_leg = legs[-1] if return_date and len(legs) > 1 else None

        # Se añade a la lista de vuelos todad la información de cada uno
        flights.append(
            FlightOption(
                price=float(price),
                outbound_airport=outbound.get("departure_airport", {}).get("name", "N/A"),
                outbound_airline=outbound.get("airline", "Desconocida"),
                outbound_departure_time=outbound.get("departure_airport", {}).get("time", "N/A"),
                outbound_arrival_time=outbound.get("arrival_airport", {}).get("time", "N/A"),
                outbound_flight_number=outbound.get("flight_number", ""),
                return_airport=return_leg.get("departure_airport", {}).get("name", "N/A") if return_leg else "N/A",
                return_airline=return_leg.get("airline", "Desconocida") if return_leg else "N/A",
                return_departure_time=return_leg.get("departure_airport", {}).get("time", "N/A") if return_leg else "N/A",
                return_arrival_time=return_leg.get("arrival_airport", {}).get("time", "N/A") if return_leg else "N/A",
                return_flight_number=return_leg.get("flight_number", "") if return_leg else "N/A",
            )
        )

    # Se devuelve la lista de vuelos
    return FlightSearchResult(flights=flights[:8])