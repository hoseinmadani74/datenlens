from fastapi import APIRouter, Query
from app.services.jobs_service import get_jobs_cached

router = APIRouter(prefix="/api", tags=["Tech Jobs Radar"])


@router.get("/jobs")
async def get_jobs(
    query: str = Query("Data Analyst", description="Search keyword or job title"),
    hours: int = Query(24, description="Hours lookback window (12, 24, 72)"),
):
  """Expose aggregated and filtered English-friendly tech jobs in Germany."""
  return await get_jobs_cached(query=query, hours=hours)
