import logging
from core.config import settings
from fastmcp import Context
from models.flight_models import FlightLeg, FlightOption, FlightSearchResult
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

    # Lista para recopilar los vuelos
    flights = []

    # Parámetros de búsqueda
    search_params = {
        "engine": "google_flights",
        "hl": "es",
        "gl": "es",
        "type": "1",
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

    # Se obtienen los grupos de vuelos
    flight_groups = (
        data.get("best_flights", [])
        + data.get("other_flights", [])
    )

    # Para cada grupo de ida...
    for flight_group in flight_groups[:10]:

        # Se obtiene el token de salida y el precio
        departure_token = flight_group.get("departure_token")
        price = flight_group.get("price") or 0

        # Si no hay token, el precio es mayor que el presupuesto o es cero,
        # se continúa con otro grupo
        if not departure_token or price > budget or price == 0:
            continue

        # Se almacenan los parámetros para la segunda petición, que es para
        # los vuelos de vuelta para este vuelo de ida concreto
        return_params = {
            "engine": "google_flights",
            "hl": "es",
            "gl": "es",
            "type": "1",
            "departure_id": origin,
            "arrival_id": destination,
            "outbound_date": outbound_date,
            "return_date": return_date,
            "departure_token": departure_token,
            "currency": "EUR",
            "api_key": settings.SERPAPI_KEY
        }

        # Se intenta realizar la solicitud a SerpAPI
        try:
            return_response = await client.get(
                settings.SERPAPI_URL,
                params=return_params
            )
            return_response.raise_for_status()
            return_data = return_response.json()

            # Se obtienen los grupos de vuelo de vuelta
            return_groups = (
                return_data.get("best_flights", [])
                + return_data.get("other_flights", [])
            )

            # Si no ay, se continúa con el siguiente
            if not return_groups:
                continue

            # Se toma el primer grupo de vuelta
            return_group = return_groups[0]

            # Se obtienen los vuelos de ida del grupo
            outbound_legs = flight_group.get("flights", [])

            # Se obtienen los vuelos de vuelta del grupo
            return_legs = return_group.get("flights", [])

            # Si no hay vuelos de ida o vuelta, se continúa con otro
            if not outbound_legs or not return_legs:
                continue

            # Vuelo individual de ida
            outbound = outbound_legs[0]

            # Vuelo individual de vuelta
            return_leg = return_legs[0]

            # Se obtienen los datos del vuelo de ida
            outbound_leg = FlightLeg(
                departure_airport_code=outbound.get("departure_airport", {}).get("id", "N/A"),
                departure_airport_name=outbound.get("departure_airport", {}).get("name", "N/A"),
                departure_time=outbound.get("departure_airport", {}).get("time", "N/A"),
                arrival_airport_code=outbound.get("arrival_airport", {}).get("id", "N/A"),
                arrival_airport_name=outbound.get("arrival_airport", {}).get("name", "N/A"),
                arrival_time=outbound.get("arrival_airport", {}).get("time", "N/A"),
                airline=outbound.get("airline", "Desconocida"),
                flight_number=outbound.get("flight_number", ""),
                duration_minutes=outbound.get("duration"),
                airplane=outbound.get("airplane"),
            )

            # Se obtienen los datos del vuelo de vuelta
            return_leg_model = FlightLeg(
                departure_airport_code=return_leg.get("departure_airport", {}).get("id", "N/A"),
                departure_airport_name=return_leg.get("departure_airport", {}).get("name", "N/A"),
                departure_time=return_leg.get("departure_airport", {}).get("time", "N/A"),
                arrival_airport_code=return_leg.get("arrival_airport", {}).get("id", "N/A"),
                arrival_airport_name=return_leg.get("arrival_airport", {}).get("name", "N/A"),
                arrival_time=return_leg.get("arrival_airport", {}).get("time", "N/A"),
                airline=return_leg.get("airline", "Desconocida"),
                flight_number=return_leg.get("flight_number", ""),
                duration_minutes=return_leg.get("duration"),
                airplane=return_leg.get("airplane"),
            )

            # Si el vuelo de vuelta no llega al aeropuerto de origen, se
            # descarta
            if return_leg_model.arrival_airport_code != origin:
                logger.info(
                    f"Vuelo descartado: la vuelta no vuelve a '{origin}'."
                )
                continue

            # Se añade a la lista los dos posibles vuelos
            flights.append(
                FlightOption(
                    outbound_flight=outbound_leg,
                    return_flight=return_leg_model,
                    price=float(price),
                )
            )

        # Si hay excepción se continúa...
        except Exception as e:
            logger.error(f"Error al obtener vuelo de vuelta con token: {e}")
            continue

    # Se devuelve la lista de vuelos
    logger.info(
        f"Se encontraron {len(flights)} opciones preliminares de vuelos de "
        "ida y vuelta dentro del presupuesto."
    )
    return FlightSearchResult(flights=flights[:5])