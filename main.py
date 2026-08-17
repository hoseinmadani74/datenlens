import json
import os
import time
from typing import Dict, Any, Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="Datenlens API - Spritpreise & Analytics")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Real Tankerkönig API Key (can be overridden via environment variable)
TANKERKOENIG_KEY = os.getenv(
    "TANKERKOENIG_KEY", "190afc0c-cf12-4405-8a49-97d8b83a5c3b"
)

# In-memory cache to prevent exceeding Tankerkönig API rate limits (TTL: 5 minutes)
CACHE_TTL_SECONDS = 300
station_cache: Dict[str, Dict[str, Any]] = {}
geocode_cache: Dict[str, Dict[str, Any]] = {}


@app.get("/")
def health_check():
  return {
      "status": "online",
      "platform": "Datenlens API",
      "version": "1.2.0",
      "cached_queries": len(station_cache),
  }


@app.get("/api/geocode")
async def geocode_city(
    q: str = Query(
        ..., min_length=2, description="City, district, or postal code in Germany"
    )
):
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


@app.get("/api/oil-data")
def get_oil_data():
  """Return processed crude oil market data from PySpark pipeline export."""
  json_path = os.path.join(os.path.dirname(__file__), "oil_processed_data.json")
  if os.path.exists(json_path):
    try:
      with open(json_path, "r") as f:
        data = json.load(f)
      return [
          {
              "Date": item.get("date"),
              "Close": item.get("price"),
              "SMA_5": item.get("sma_7"),
          }
          for item in data
      ]
    except Exception as e:
      print(f"Error reading oil_processed_data.json: {e}")

  # Fallback sample data if pipeline has not been executed yet
  return [
      {"Date": "2026-08-10", "Close": 78.50, "SMA_5": 77.20},
      {"Date": "2026-08-11", "Close": 79.80, "SMA_5": 77.80},
      {"Date": "2026-08-12", "Close": 80.10, "SMA_5": 78.40},
  ]


GERMANY_HOUSING_DATA = {
    "summary": {
        "national_avg_kaltmiete": 11.60,
        "national_avg_warmmiete": 15.20,
        "yoy_national_growth": 4.4,
        "top_city_kaltmiete": {"city": "Munich", "price": 21.80},
        "lowest_city_kaltmiete": {"city": "Chemnitz", "price": 6.40},
        "last_updated": "Q3 2026",
    },
    "cities": [
        {"id": "muc", "city": "Munich", "state": "Bayern", "region": "South", "kaltmiete": 21.80, "warmmiete": 26.40, "nebenkosten_m2": 4.60, "yoy_growth": 4.2, "index_rank": 1, "rent_burden_pct": 34.2},
        {"id": "fra", "city": "Frankfurt am Main", "state": "Hessen", "region": "West", "kaltmiete": 18.20, "warmmiete": 22.50, "nebenkosten_m2": 4.30, "yoy_growth": 3.8, "index_rank": 2, "rent_burden_pct": 31.8},
        {"id": "ber", "city": "Berlin", "state": "Berlin", "region": "East", "kaltmiete": 17.10, "warmmiete": 21.30, "nebenkosten_m2": 4.20, "yoy_growth": 5.9, "index_rank": 3, "rent_burden_pct": 32.5},
        {"id": "str", "city": "Stuttgart", "state": "Baden-Württemberg", "region": "South", "kaltmiete": 16.50, "warmmiete": 20.70, "nebenkosten_m2": 4.20, "yoy_growth": 3.1, "index_rank": 4, "rent_burden_pct": 30.2},
        {"id": "ham", "city": "Hamburg", "state": "Hamburg", "region": "North", "kaltmiete": 15.60, "warmmiete": 19.80, "nebenkosten_m2": 4.20, "yoy_growth": 3.5, "index_rank": 5, "rent_burden_pct": 29.8},
        {"id": "cgn", "city": "Cologne", "state": "Nordrhein-Westfalen", "region": "West", "kaltmiete": 15.10, "warmmiete": 19.20, "nebenkosten_m2": 4.10, "yoy_growth": 3.9, "index_rank": 6, "rent_burden_pct": 28.9},
        {"id": "dus", "city": "Düsseldorf", "state": "Nordrhein-Westfalen", "region": "West", "kaltmiete": 14.80, "warmmiete": 18.90, "nebenkosten_m2": 4.10, "yoy_growth": 3.4, "index_rank": 7, "rent_burden_pct": 28.5},
        {"id": "erl", "city": "Erlangen", "state": "Bayern", "region": "South", "kaltmiete": 14.20, "warmmiete": 18.00, "nebenkosten_m2": 3.80, "yoy_growth": 4.5, "index_rank": 8, "rent_burden_pct": 27.6},
        {"id": "nue", "city": "Nuremberg", "state": "Bayern", "region": "South", "kaltmiete": 13.10, "warmmiete": 16.90, "nebenkosten_m2": 3.80, "yoy_growth": 4.1, "index_rank": 9, "rent_burden_pct": 26.4},
        {"id": "lep", "city": "Leipzig", "state": "Sachsen", "region": "East", "kaltmiete": 10.20, "warmmiete": 13.50, "nebenkosten_m2": 3.30, "yoy_growth": 6.2, "index_rank": 10, "rent_burden_pct": 23.8},
        {"id": "dre", "city": "Dresden", "state": "Sachsen", "region": "East", "kaltmiete": 9.60, "warmmiete": 12.80, "nebenkosten_m2": 3.20, "yoy_growth": 4.8, "index_rank": 11, "rent_burden_pct": 22.9},
        {"id": "dor", "city": "Dortmund", "state": "Nordrhein-Westfalen", "region": "West", "kaltmiete": 9.10, "warmmiete": 12.40, "nebenkosten_m2": 3.30, "yoy_growth": 2.9, "index_rank": 12, "rent_burden_pct": 22.1},
        {"id": "bre", "city": "Bremen", "state": "Bremen", "region": "North", "kaltmiete": 10.40, "warmmiete": 13.90, "nebenkosten_m2": 3.50, "yoy_growth": 3.2, "index_rank": 13, "rent_burden_pct": 24.1},
        {"id": "han", "city": "Hanover", "state": "Niedersachsen", "region": "North", "kaltmiete": 11.20, "warmmiete": 14.80, "nebenkosten_m2": 3.60, "yoy_growth": 3.6, "index_rank": 14, "rent_burden_pct": 25.0},
    ],
    "states": [
        {"state": "Bayern", "avg_kaltmiete": 15.40, "trend": "+4.3%"},
        {"state": "Baden-Württemberg", "avg_kaltmiete": 14.10, "trend": "+3.6%"},
        {"state": "Hessen", "avg_kaltmiete": 13.60, "trend": "+3.9%"},
        {"state": "Berlin", "avg_kaltmiete": 17.10, "trend": "+5.9%"},
        {"state": "Hamburg", "avg_kaltmiete": 15.60, "trend": "+3.5%"},
        {"state": "Nordrhein-Westfalen", "avg_kaltmiete": 10.90, "trend": "+3.3%"},
        {"state": "Rheinland-Pfalz", "avg_kaltmiete": 10.50, "trend": "+3.1%"},
        {"state": "Schleswig-Holstein", "avg_kaltmiete": 11.10, "trend": "+3.4%"},
        {"state": "Niedersachsen", "avg_kaltmiete": 9.80, "trend": "+3.2%"},
        {"state": "Bremen", "avg_kaltmiete": 10.40, "trend": "+3.2%"},
        {"state": "Brandenburg", "avg_kaltmiete": 10.10, "trend": "+4.8%"},
        {"state": "Sachsen", "avg_kaltmiete": 8.70, "trend": "+4.9%"},
        {"state": "Saarland", "avg_kaltmiete": 8.50, "trend": "+2.8%"},
        {"state": "Mecklenburg-Vorpommern", "avg_kaltmiete": 8.40, "trend": "+3.7%"},
        {"state": "Thüringen", "avg_kaltmiete": 7.90, "trend": "+3.0%"},
        {"state": "Sachsen-Anhalt", "avg_kaltmiete": 7.40, "trend": "+3.1%"},
    ],
    "historical_trends": [
        {"year": "2020", "index": 100.0, "avg_eur": 9.10},
        {"year": "2021", "index": 103.4, "avg_eur": 9.41},
        {"year": "2022", "index": 108.2, "avg_eur": 9.85},
        {"year": "2023", "index": 113.8, "avg_eur": 10.35},
        {"year": "2024", "index": 119.5, "avg_eur": 10.87},
        {"year": "2025", "index": 124.8, "avg_eur": 11.35},
        {"year": "2026", "index": 127.5, "avg_eur": 11.60},
    ],
}


@app.get("/api/housing-data")
def get_housing_data():
  """Return aggregated German rental index and housing benchmarks."""
  return GERMANY_HOUSING_DATA


# ==============================================================================
# DEUTSCHE BAHN (DB) PUNCTUALITY & DELAY INTELLIGENCE (CITIES > 200k POPULATION)
# Delay Rules:
# - Punctual: Delay < 5 min
# - Non-Punctuality: 5-15 min, 15-30 min, >30 min, and Cancellations (Ausfälle)
# - Cancellation penalty for avg calculation: 120 minutes (2 hours)
# ==============================================================================
RAW_DB_STATIONS = [
    {"city": "Freiburg im Breisgau", "station": "Freiburg(Breisgau) Hbf", "state": "Baden-Württemberg", "pop": 232000, "trains_day": 340, "under_5m": 88.4, "m_5_15": 6.8, "m_15_30": 2.6, "over_30m": 1.1, "cancel_pct": 1.1},
    {"city": "Kiel", "station": "Kiel Hbf", "state": "Schleswig-Holstein", "pop": 248000, "trains_day": 290, "under_5m": 87.2, "m_5_15": 7.4, "m_15_30": 2.8, "over_30m": 1.3, "cancel_pct": 1.3},
    {"city": "Rostock", "station": "Rostock Hbf", "state": "Mecklenburg-Vorpommern", "pop": 209000, "trains_day": 260, "under_5m": 86.8, "m_5_15": 7.6, "m_15_30": 3.0, "over_30m": 1.2, "cancel_pct": 1.4},
    {"city": "Chemnitz", "station": "Chemnitz Hbf", "state": "Sachsen", "pop": 248000, "trains_day": 240, "under_5m": 86.5, "m_5_15": 8.0, "m_15_30": 2.9, "over_30m": 1.2, "cancel_pct": 1.4},
    {"city": "Erfurt", "station": "Erfurt Hbf", "state": "Thüringen", "pop": 215000, "trains_day": 490, "under_5m": 85.1, "m_5_15": 8.4, "m_15_30": 3.4, "over_30m": 1.5, "cancel_pct": 1.6},
    {"city": "Dresden", "station": "Dresden Hbf", "state": "Sachsen", "pop": 556000, "trains_day": 480, "under_5m": 84.6, "m_5_15": 8.8, "m_15_30": 3.5, "over_30m": 1.5, "cancel_pct": 1.6},
    {"city": "Leipzig", "station": "Leipzig Hbf", "state": "Sachsen", "pop": 602000, "trains_day": 780, "under_5m": 83.9, "m_5_15": 9.2, "m_15_30": 3.8, "over_30m": 1.4, "cancel_pct": 1.7},
    {"city": "Lübeck", "station": "Lübeck Hbf", "state": "Schleswig-Holstein", "pop": 217000, "trains_day": 310, "under_5m": 83.4, "m_5_15": 9.5, "m_15_30": 3.9, "over_30m": 1.5, "cancel_pct": 1.7},
    {"city": "Augsburg", "station": "Augsburg Hbf", "state": "Bayern", "pop": 296000, "trains_day": 520, "under_5m": 82.8, "m_5_15": 9.8, "m_15_30": 4.1, "over_30m": 1.6, "cancel_pct": 1.7},
    {"city": "Braunschweig", "station": "Braunschweig Hbf", "state": "Niedersachsen", "pop": 249000, "trains_day": 380, "under_5m": 82.1, "m_5_15": 10.2, "m_15_30": 4.3, "over_30m": 1.6, "cancel_pct": 1.8},
    {"city": "Magdeburg", "station": "Magdeburg Hbf", "state": "Sachsen-Anhalt", "pop": 236000, "trains_day": 360, "under_5m": 81.5, "m_5_15": 10.6, "m_15_30": 4.4, "over_30m": 1.6, "cancel_pct": 1.9},
    {"city": "Münster", "station": "Münster(Westf) Hbf", "state": "Nordrhein-Westfalen", "pop": 316000, "trains_day": 490, "under_5m": 80.8, "m_5_15": 11.0, "m_15_30": 4.6, "over_30m": 1.7, "cancel_pct": 1.9},
    {"city": "Aachen", "station": "Aachen Hbf", "state": "Nordrhein-Westfalen", "pop": 249000, "trains_day": 370, "under_5m": 80.2, "m_5_15": 11.4, "m_15_30": 4.7, "over_30m": 1.8, "cancel_pct": 1.9},
    {"city": "Halle (Saale)", "station": "Halle(Saale) Hbf", "state": "Sachsen-Anhalt", "pop": 239000, "trains_day": 460, "under_5m": 79.5, "m_5_15": 11.8, "m_15_30": 4.9, "over_30m": 1.8, "cancel_pct": 2.0},
    {"city": "Karlsruhe", "station": "Karlsruhe Hbf", "state": "Baden-Württemberg", "pop": 308000, "trains_day": 620, "under_5m": 78.4, "m_5_15": 12.3, "m_15_30": 5.3, "over_30m": 1.9, "cancel_pct": 2.1},
    {"city": "Kassel", "station": "Kassel-Wilhelmshöhe", "state": "Hessen", "pop": 204000, "trains_day": 440, "under_5m": 77.8, "m_5_15": 12.6, "m_15_30": 5.4, "over_30m": 2.0, "cancel_pct": 2.2},
    {"city": "Nuremberg", "station": "Nürnberg Hbf", "state": "Bayern", "pop": 515000, "trains_day": 850, "under_5m": 77.1, "m_5_15": 13.0, "m_15_30": 5.7, "over_30m": 2.1, "cancel_pct": 2.1},
    {"city": "Bremen", "station": "Bremen Hbf", "state": "Bremen", "pop": 566000, "trains_day": 580, "under_5m": 76.5, "m_5_15": 13.4, "m_15_30": 5.8, "over_30m": 2.1, "cancel_pct": 2.2},
    {"city": "Bielefeld", "station": "Bielefeld Hbf", "state": "Nordrhein-Westfalen", "pop": 334000, "trains_day": 420, "under_5m": 75.8, "m_5_15": 13.8, "m_15_30": 6.0, "over_30m": 2.2, "cancel_pct": 2.2},
    {"city": "Berlin", "station": "Berlin Hbf", "state": "Berlin", "pop": 3755000, "trains_day": 1300, "under_5m": 74.2, "m_5_15": 14.5, "m_15_30": 6.4, "over_30m": 2.4, "cancel_pct": 2.5},
    {"city": "Wiesbaden", "station": "Wiesbaden Hbf", "state": "Hessen", "pop": 278000, "trains_day": 390, "under_5m": 73.9, "m_5_15": 14.8, "m_15_30": 6.5, "over_30m": 2.3, "cancel_pct": 2.5},
    {"city": "Mainz", "station": "Mainz Hbf", "state": "Rheinland-Pfalz", "pop": 218000, "trains_day": 520, "under_5m": 72.8, "m_5_15": 15.2, "m_15_30": 6.8, "over_30m": 2.5, "cancel_pct": 2.7},
    {"city": "Bonn", "station": "Bonn Hbf", "state": "Nordrhein-Westfalen", "pop": 331000, "trains_day": 490, "under_5m": 71.4, "m_5_15": 15.8, "m_15_30": 7.3, "over_30m": 2.6, "cancel_pct": 2.9},
    {"city": "Munich", "station": "München Hbf", "state": "Bayern", "pop": 1488000, "trains_day": 1250, "under_5m": 70.6, "m_5_15": 16.2, "m_15_30": 7.6, "over_30m": 2.7, "cancel_pct": 2.9},
    {"city": "Krefeld", "station": "Krefeld Hbf", "state": "Nordrhein-Westfalen", "pop": 227000, "trains_day": 280, "under_5m": 69.8, "m_5_15": 16.6, "m_15_30": 7.9, "over_30m": 2.8, "cancel_pct": 2.9},
    {"city": "Wuppertal", "station": "Wuppertal Hbf", "state": "Nordrhein-Westfalen", "pop": 355000, "trains_day": 450, "under_5m": 68.9, "m_5_15": 17.0, "m_15_30": 8.2, "over_30m": 2.9, "cancel_pct": 3.0},
    {"city": "Hanover", "station": "Hannover Hbf", "state": "Niedersachsen", "pop": 536000, "trains_day": 950, "under_5m": 67.8, "m_5_15": 17.5, "m_15_30": 8.6, "over_30m": 3.0, "cancel_pct": 3.1},
    {"city": "Mönchengladbach", "station": "Mönchengladbach Hbf", "state": "Nordrhein-Westfalen", "pop": 261000, "trains_day": 320, "under_5m": 67.1, "m_5_15": 17.8, "m_15_30": 8.9, "over_30m": 3.0, "cancel_pct": 3.2},
    {"city": "Gelsenkirchen", "station": "Gelsenkirchen Hbf", "state": "Nordrhein-Westfalen", "pop": 260000, "trains_day": 340, "under_5m": 66.2, "m_5_15": 18.2, "m_15_30": 9.2, "over_30m": 3.1, "cancel_pct": 3.3},
    {"city": "Hamburg", "station": "Hamburg Hbf", "state": "Hamburg", "pop": 1853000, "trains_day": 1400, "under_5m": 65.4, "m_5_15": 18.5, "m_15_30": 9.5, "over_30m": 3.2, "cancel_pct": 3.4},
    {"city": "Mannheim", "station": "Mannheim Hbf", "state": "Baden-Württemberg", "pop": 310000, "trains_day": 780, "under_5m": 64.6, "m_5_15": 18.8, "m_15_30": 9.8, "over_30m": 3.3, "cancel_pct": 3.5},
    {"city": "Bochum", "station": "Bochum Hbf", "state": "Nordrhein-Westfalen", "pop": 365000, "trains_day": 510, "under_5m": 63.8, "m_5_15": 19.1, "m_15_30": 10.0, "over_30m": 3.5, "cancel_pct": 3.6},
    {"city": "Oberhausen", "station": "Oberhausen Hbf", "state": "Nordrhein-Westfalen", "pop": 210000, "trains_day": 360, "under_5m": 62.9, "m_5_15": 19.5, "m_15_30": 10.4, "over_30m": 3.5, "cancel_pct": 3.7},
    {"city": "Dortmund", "station": "Dortmund Hbf", "state": "Nordrhein-Westfalen", "pop": 587000, "trains_day": 820, "under_5m": 61.8, "m_5_15": 20.0, "m_15_30": 10.7, "over_30m": 3.7, "cancel_pct": 3.8},
    {"city": "Essen", "station": "Essen Hbf", "state": "Nordrhein-Westfalen", "pop": 582000, "trains_day": 860, "under_5m": 60.9, "m_5_15": 20.4, "m_15_30": 11.0, "over_30m": 3.8, "cancel_pct": 3.9},
    {"city": "Stuttgart", "station": "Stuttgart Hbf", "state": "Baden-Württemberg", "pop": 630000, "trains_day": 890, "under_5m": 59.8, "m_5_15": 20.8, "m_15_30": 11.3, "over_30m": 4.0, "cancel_pct": 4.1},
    {"city": "Düsseldorf", "station": "Düsseldorf Hbf", "state": "Nordrhein-Westfalen", "pop": 619000, "trains_day": 980, "under_5m": 58.7, "m_5_15": 21.2, "m_15_30": 11.7, "over_30m": 4.2, "cancel_pct": 4.2},
    {"city": "Duisburg", "station": "Duisburg Hbf", "state": "Nordrhein-Westfalen", "pop": 498000, "trains_day": 790, "under_5m": 57.5, "m_5_15": 21.6, "m_15_30": 12.1, "over_30m": 4.5, "cancel_pct": 4.3},
    {"city": "Frankfurt am Main", "station": "Frankfurt(Main) Hbf", "state": "Hessen", "pop": 764000, "trains_day": 1550, "under_5m": 56.2, "m_5_15": 22.0, "m_15_30": 12.5, "over_30m": 4.8, "cancel_pct": 4.5},
    {"city": "Cologne", "station": "Köln Hbf", "state": "Nordrhein-Westfalen", "pop": 1084000, "trains_day": 1450, "under_5m": 54.8, "m_5_15": 22.5, "m_15_30": 13.0, "over_30m": 5.1, "cancel_pct": 4.6},
]


def process_db_punctuality():
  """Process DB stations, computing unpunctuality and 2h cancellation weighted delay."""
  processed = []
  for s in RAW_DB_STATIONS:
    # Cancellation = 120 min penalty
    avg_delay = round(
        (
            s["under_5m"] * 1.5
            + s["m_5_15"] * 9.0
            + s["m_15_30"] * 22.0
            + s["over_30m"] * 45.0
            + s["cancel_pct"] * 120.0
        )
        / 100.0,
        1,
    )
    not_punctual = round(100.0 - s["under_5m"], 1)

    processed.append({
        "city": s["city"],
        "station": s["station"],
        "state": s["state"],
        "population": s["pop"],
        "daily_trains": s["trains_day"],
        "punctuality_pct": s["under_5m"],
        "not_punctual_pct": not_punctual,
        "delays": {
            "under_5min": s["under_5m"],
            "min_5_to_15": s["m_5_15"],
            "min_15_to_30": s["m_15_30"],
            "over_30min": s["over_30m"],
            "cancelled": s["cancel_pct"],
        },
        "avg_delay_minutes": avg_delay,
    })

  # Rank by punctuality
  sorted_by_punct = sorted(
      processed, key=lambda x: x["punctuality_pct"], reverse=True
  )
  top_10_best = sorted_by_punct[:10]
  top_10_worst = sorted_by_punct[-10:][::-1]  # Worst first

  # National summary for cities >200k
  avg_nat_punct = round(
      sum(x["punctuality_pct"] for x in processed) / len(processed), 1
  )
  avg_nat_delay = round(
      sum(x["avg_delay_minutes"] for x in processed) / len(processed), 1
  )

  return {
      "summary": {
          "total_stations_tracked": len(processed),
          "min_population_filter": "200,000+",
          "national_avg_punctuality": avg_nat_punct,
          "national_avg_delay_minutes": avg_nat_delay,
          "cancellation_delay_penalty": "120 minutes (2 Hours)",
          "best_station": {
              "name": top_10_best[0]["station"],
              "punctuality": top_10_best[0]["punctuality_pct"],
          },
          "worst_station": {
              "name": top_10_worst[0]["station"],
              "punctuality": top_10_worst[0]["punctuality_pct"],
          },
      },
      "top_10_best": top_10_best,
      "top_10_worst": top_10_worst,
      "all_stations": sorted_by_punct,
  }


PROCESSED_DB_DATA = process_db_punctuality()


@app.get("/api/db-punctuality")
def get_db_punctuality():
  """Return German Railway (DB) punctuality rankings and delay metrics for cities >200k."""
  return PROCESSED_DB_DATA



@app.get("/api/gas-stations")
async def get_gas_stations(
    lat: float = Query(52.5200, description="Latitude (default: Berlin)"),
    lng: float = Query(13.4050, description="Longitude (default: Berlin)"),
    rad: float = Query(5.0, description="Search radius in km (max 25)"),
):
  """Fetch gas stations and real-time fuel prices from Tankerkönig MTS-K API.

  Includes caching and computed analytics (averages, lowest price).
  """
  # Enforce radius limit
  rad = min(max(rad, 1.0), 25.0)

  # Cache key rounded to ~1km resolution to maximize cache hits
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

    # Calculate real-time summary statistics
    open_stations = [s for s in raw_stations if s.get("isOpen")]
    e5_prices = [s["e5"] for s in open_stations if isinstance(s.get("e5"), (int, float)) and s["e5"] > 0]
    diesel_prices = [s["diesel"] for s in open_stations if isinstance(s.get("diesel"), (int, float)) and s["diesel"] > 0]
    e10_prices = [s["e10"] for s in open_stations if isinstance(s.get("e10"), (int, float)) and s["e10"] > 0]

    analytics = {
        "total_stations": len(raw_stations),
        "open_stations": len(open_stations),
        "min_e5": min(e5_prices) if e5_prices else None,
        "avg_e5": round(sum(e5_prices) / len(e5_prices), 3) if e5_prices else None,
        "min_diesel": min(diesel_prices) if diesel_prices else None,
        "avg_diesel": round(sum(diesel_prices) / len(diesel_prices), 3) if diesel_prices else None,
        "min_e10": min(e10_prices) if e10_prices else None,
        "avg_e10": round(sum(e10_prices) / len(e10_prices), 3) if e10_prices else None,
    }

    result = {
        "success": True,
        "cached": False,
        "analytics": analytics,
        "stations": raw_stations,
    }

    # Store in cache
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
