from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import fuel, trains, housing, energy, jobs
from app.services.fuel_service import station_cache

app = FastAPI(
    title="Datenlens API - German Data Intelligence Platform",
    description="Full-stack real-time analytics for fuel, rail transit, housing, energy, and tech jobs across Germany.",
    version="1.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register modular routers
app.include_router(fuel.router)
app.include_router(trains.router)
app.include_router(housing.router)
app.include_router(energy.router)
app.include_router(jobs.router)


@app.get("/")
def health_check():
  return {
      "status": "online",
      "platform": "Datenlens API",
      "version": "1.3.0",
      "cached_queries": len(station_cache),
  }
