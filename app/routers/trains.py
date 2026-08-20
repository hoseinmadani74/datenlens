from fastapi import APIRouter, Query
from app.services.train_service import PROCESSED_DB_DATA, calculate_train_delay_forecast

router = APIRouter(prefix="/api", tags=["Deutsche Bahn Rail Transit"])


@router.get("/db-punctuality")
def get_db_punctuality():
  """Return German Railway (DB) punctuality rankings and delay metrics for cities >200k."""
  return PROCESSED_DB_DATA


@router.get("/train-delay-forecast")
def get_train_delay_forecast(
    origin: str = Query("Frankfurt am Main", description="Origin city / station"),
    destination: str = Query("Cologne", description="Destination city / station"),
    weather: str = Query("clear", description="Weather condition (clear, rain, heavy_rain, snow_ice, high_wind, extreme_heat)"),
    hour: int = Query(17, ge=0, le=23, description="Departure hour (0-23)"),
    day_type: str = Query("weekday", description="Day type: weekday | weekend"),
):
  """Forecast delay probability and expected passenger delay using route congestion and weather factors."""
  return calculate_train_delay_forecast(
      origin=origin,
      destination=destination,
      weather=weather,
      hour=hour,
      day_type=day_type,
  )
