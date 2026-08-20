from typing import Dict, Any
import httpx

geocode_cache: Dict[str, Dict[str, Any]] = {}


async def geocode_city_query(q: str) -> Dict[str, Any]:
  """Geocode search query in Germany using OpenStreetMap Nominatim with caching."""
  q_norm = q.strip().lower()
  if q_norm in geocode_cache:
    return geocode_cache[q_norm]

  url = "https://nominatim.openstreetmap.org/search"
  params = {
      "q": q.strip(),
      "countrycodes": "de",
      "format": "json",
      "limit": 5,
      "addressdetails": 1,
  }
  headers = {"User-Agent": "Datenlens-App/1.0 (info@datenlens.de)"}

  try:
    async with httpx.AsyncClient(timeout=8.0) as client:
      response = await client.get(url, params=params, headers=headers)
      data = response.json()

    results = []
    for item in data:
      results.append({
          "display_name": item.get("display_name"),
          "name": item.get("name")
          or item.get("display_name", "").split(",")[0],
          "lat": float(item["lat"]),
          "lng": float(item["lon"]),
          "type": item.get("type"),
      })

    res = {"success": True, "results": results}
    geocode_cache[q_norm] = res
    return res
  except Exception as e:
    return {"success": False, "message": str(e), "results": []}
