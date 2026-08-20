import time
from typing import Dict, Any
import httpx
from app.config import TANKERKOENIG_KEY, CACHE_TTL_SECONDS

station_cache: Dict[str, Dict[str, Any]] = {}


async def get_gas_stations_data(lat: float, lng: float, rad: float) -> Dict[str, Any]:
  """Fetch gas stations and real-time fuel prices from Tankerkönig MTS-K API.

  Includes spatial key caching and summary statistics calculations.
  """
  # Enforce radius limits
  rad = min(max(rad, 1.0), 25.0)

  # Spatial key normalized to ~1km to maximize cache hits
  cache_key = f"{round(lat, 2)}_{round(lng, 2)}_{round(rad, 1)}"
  now = time.time()

  if cache_key in station_cache:
    cached_entry = station_cache[cache_key]
    if now - cached_entry["timestamp"] < CACHE_TTL_SECONDS:
      return {
          **cached_entry["data"],
          "cached": True,
          "cache_age_seconds": int(now - cached_entry["timestamp"]),
      }

  url = "https://creativecommons.tankerkoenig.de/json/list.php"
  params = {
      "lat": lat,
      "lng": lng,
      "rad": rad,
      "sort": "dist",
      "type": "all",
      "apikey": TANKERKOENIG_KEY,
  }

  try:
    async with httpx.AsyncClient(timeout=10.0) as client:
      response = await client.get(url, params=params)
      data = response.json()

    if not data.get("ok"):
      return {
          "success": False,
          "message": data.get("message", "Failed to fetch data from Tankerkönig"),
          "stations": [],
      }

    raw_stations = data.get("stations", [])
    open_stations = [s for s in raw_stations if s.get("isOpen")]
    e5_prices = [
        s["e5"]
        for s in open_stations
        if isinstance(s.get("e5"), (int, float)) and s["e5"] > 0
    ]
    diesel_prices = [
        s["diesel"]
        for s in open_stations
        if isinstance(s.get("diesel"), (int, float)) and s["diesel"] > 0
    ]
    e10_prices = [
        s["e10"]
        for s in open_stations
        if isinstance(s.get("e10"), (int, float)) and s["e10"] > 0
    ]

    analytics = {
        "total_stations": len(raw_stations),
        "open_stations": len(open_stations),
        "min_e5": min(e5_prices) if e5_prices else None,
        "avg_e5": (
            round(sum(e5_prices) / len(e5_prices), 3) if e5_prices else None
        ),
        "min_diesel": min(diesel_prices) if diesel_prices else None,
        "avg_diesel": (
            round(sum(diesel_prices) / len(diesel_prices), 3)
            if diesel_prices
            else None
        ),
        "min_e10": min(e10_prices) if e10_prices else None,
        "avg_e10": (
            round(sum(e10_prices) / len(e10_prices), 3) if e10_prices else None
        ),
    }

    result = {
        "success": True,
        "cached": False,
        "analytics": analytics,
        "stations": raw_stations,
    }

    station_cache[cache_key] = {"timestamp": now, "data": result}
    return result

  except httpx.RequestError as e:
    return {
        "success": False,
        "message": f"Network error connecting to Tankerkönig: {str(e)}",
        "stations": [],
    }
  except Exception as e:
    return {
        "success": False,
        "message": f"Unexpected server error: {str(e)}",
        "stations": [],
    }
