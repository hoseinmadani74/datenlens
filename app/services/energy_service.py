import json
import os
from typing import List, Dict, Any
from app.config import OIL_DATA_FILE


def get_oil_market_data() -> List[Dict[str, Any]]:
  """Return processed crude oil market data from PySpark pipeline export."""
  if os.path.exists(OIL_DATA_FILE):
    try:
      with open(OIL_DATA_FILE, "r") as f:
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
