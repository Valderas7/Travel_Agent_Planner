# Librerías
from pydantic import BaseModel, Field
from typing import List, Optional

class HotelOption(BaseModel):
    """Modelo para cada hotel devuelto por Google Hotels."""
    name: str
    price_per_night: float
    total_price: float
    rating: Optional[float] = None
    address: Optional[str] = None
    stars: Optional[int] = None
    amenities: List[str] = Field(default_factory=list)


class HotelSearchResult(BaseModel):
    """Resultado de la búsqueda de hoteles."""
    hotels: List[HotelOption]