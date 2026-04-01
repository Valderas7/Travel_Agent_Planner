import os
import requests
from mcp import FastMCP, Tool
from pydantic import BaseModel, Field
from typing import List, Optional


mcp = FastMCP("hotel-search")

@mcp.tool(
    name="search_hotels",
    description="Busca hoteles reales en Google Hotels con precios, rating y ubicación. Filtra por presupuesto total.",
    parameters={
        "destination": {"type": "string", "description": "Ciudad o destino (ej: Barcelona, New York)"},
        "check_in_date": {"type": "string", "description": "Fecha de entrada YYYY-MM-DD"},
        "check_out_date": {"type": "string", "description": "Fecha de salida YYYY-MM-DD"},
        "budget": {"type": "number", "description": "Presupuesto máximo TOTAL para el alojamiento"},
        "adults": {"type": "integer", "description": "Número de adultos", "default": 1},
    }
)
async def search_hotels(
    destination: str,
    check_in_date: str,
    check_out_date: str,
    budget: float = 1000,
    adults: int = 1,
) -> HotelSearchResult:
    params = {
        "engine": "google_hotels",
        "q": destination,                    # ciudad o "Hotels in Barcelona"
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "adults": adults,
        "currency": "EUR",
        "hl": "es",
        "gl": "es",
        "api_key": os.getenv("SERPAPI_KEY"),
    }

    response = requests.get("https://serpapi.com/search", params=params)
    response.raise_for_status()
    data = response.json()

    hotels = []
    nights = 0
    try:
        nights = (requests.utils.parse_date(check_out_date) - requests.utils.parse_date(check_in_date)).days
    except:
        nights = 1  # fallback

    for prop in data.get("properties", [])[:15]:   # limitamos a 15 resultados
        price_per_night = prop.get("rate_per_night", {}).get("lowest", 0) or 0
        total_price = price_per_night * max(nights, 1)

        if total_price <= budget and price_per_night > 0:
            hotels.append(HotelOption(
                name=prop.get("name", "Hotel sin nombre"),
                price_per_night=float(price_per_night),
                total_price=float(total_price),
                rating=prop.get("overall_rating"),
                address=prop.get("address"),
                stars=prop.get("stars"),
                amenities=prop.get("amenities", [])[:8]  # máximo 8 amenities
            ))

    return HotelSearchResult(hotels=hotels)


if __name__ == "__main__":
    mcp.run()