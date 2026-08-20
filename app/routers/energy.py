from fastapi import APIRouter
from app.services.energy_service import get_oil_market_data

router = APIRouter(prefix="/api", tags=["Energy & Commodities"])


@router.get("/oil-data")
def get_oil_data():
  """Return processed crude oil market data from PySpark pipeline export."""
  return get_oil_market_data()
