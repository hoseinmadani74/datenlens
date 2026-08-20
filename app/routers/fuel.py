from fastapi import APIRouter, Query
from app.services.fuel_service import get_gas_stations_data
from app.services.geocode_service import geocode_city_query

router = APIRouter(prefix="/api", tags=["Fuel & GIS"])


@router.get("/gas-stations")
async def get_gas_stations(
    lat: float = Query(52.5200, description="Latitude (default: Berlin)"),
    lng: float = Query(13.4050, description="Longitude (default: Berlin)"),
    rad: float = Query(5.0, description="Search radius in km (max 25)"),
):
  """Fetch gas stations and real-time fuel prices from Tankerkönig MTS-K API."""
  return await get_gas_stations_data(lat=lat, lng=lng, rad=rad)


@router.get("/geocode")
async def geocode_city(
    q: str = Query(
        ..., min_length=2, description="City, district, or postal code in Germany"
    )
):
  """Geocode search query in Germany using OpenStreetMap Nominatim with caching."""
  return await geocode_city_query(q=q)
