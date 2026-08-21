from typing import Optional
from fastapi import APIRouter, Query
from app.services.jobs_service import get_jobs_cached

router = APIRouter(prefix="/api", tags=["Tech Jobs Radar"])


@router.get("/jobs")
async def get_jobs(
    query: str = Query("Junior Data Analyst", description="Search keyword or job title"),
    hours: int = Query(72, description="Hours lookback window (12, 24, 72, 168)"),
    track: Optional[str] = Query("track1", description="Career Track: track1, track2, track3"),
    workplace: str = Query("all", description="Workplace mode: all | onsite_hybrid | remote_germany"),
    dax40_only: bool = Query(False, description="Filter only DAX 40 / GER 40 enterprise employers"),
):
  """Expose aggregated and strictly filtered English-friendly Junior (<3y) tech jobs in Germany."""
  return await get_jobs_cached(
      query=query,
      hours=hours,
      track=track,
      workplace_preference=workplace,
      dax40_only=dax40_only,
  )
