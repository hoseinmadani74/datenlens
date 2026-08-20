from fastapi import APIRouter
from app.services.housing_service import get_german_housing_data

router = APIRouter(prefix="/api", tags=["Housing & Rent Index"])


@router.get("/housing-data")
def get_housing_data():
  """Return aggregated German rental index and housing benchmarks."""
  return get_german_housing_data()
