from typing import Dict, Any, List

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


def process_db_punctuality() -> Dict[str, Any]:
  """Process DB stations, computing unpunctuality and 2h cancellation weighted delay."""
  processed = []
  for s in RAW_DB_STATIONS:
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

  sorted_by_punct = sorted(
      processed, key=lambda x: x["punctuality_pct"], reverse=True
  )
  top_10_best = sorted_by_punct[:10]
  top_10_worst = sorted_by_punct[-10:][::-1]

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


# ------------------------------------------------------------------------------
# DB ROUTE DELAY PROBABILITY FORECASTER (CONGESTION + WEATHER MODEL)
# ------------------------------------------------------------------------------
STATION_CONGESTION_SCORES: Dict[str, float] = {
    "Cologne": 0.88,
    "Frankfurt am Main": 0.85,
    "Duisburg": 0.82,
    "Düsseldorf": 0.80,
    "Stuttgart": 0.78,
    "Essen": 0.76,
    "Dortmund": 0.75,
    "Mannheim": 0.72,
    "Hamburg": 0.70,
    "Hanover": 0.65,
    "Munich": 0.62,
    "Berlin": 0.58,
    "Nuremberg": 0.52,
    "Bremen": 0.48,
    "Leipzig": 0.42,
    "Dresden": 0.38,
    "Erfurt": 0.36,
    "Freiburg im Breisgau": 0.28,
    "Kiel": 0.25,
    "Rostock": 0.22,
    "Chemnitz": 0.24,
    "Lübeck": 0.27,
    "Augsburg": 0.35,
    "Braunschweig": 0.38,
    "Magdeburg": 0.39,
    "Münster": 0.44,
    "Aachen": 0.45,
    "Halle (Saale)": 0.40,
    "Karlsruhe": 0.48,
    "Kassel": 0.46,
    "Bielefeld": 0.49,
    "Wiesbaden": 0.51,
    "Mainz": 0.53,
    "Bonn": 0.55,
    "Krefeld": 0.56,
    "Wuppertal": 0.57,
    "Mönchengladbach": 0.58,
    "Gelsenkirchen": 0.60,
    "Bochum": 0.62,
    "Oberhausen": 0.63,
}

WEATHER_IMPACT_WEIGHTS = {
    "clear": {"coeff": 1.0, "en": "Clear / Dry (Optimal)", "de": "Klar / Trocken (Optimal)"},
    "rain": {"coeff": 1.20, "en": "Moderate Rain & Wet Rails", "de": "Mäßiger Regen & nasse Schienen"},
    "heavy_rain": {"coeff": 1.45, "en": "Heavy Rainstorm & Flooding Risk", "de": "Starkregen & Gewitter"},
    "snow_ice": {"coeff": 1.68, "en": "Snow, Frost & Catenary Ice", "de": "Schnee, Frost & Oberleitungseis"},
    "high_wind": {"coeff": 1.78, "en": "High Wind & Storm Warning (>60 km/h)", "de": "Sturmböen & Windwarnung (>60 km/h)"},
    "extreme_heat": {"coeff": 1.25, "en": "Extreme Heat (>32°C / Rail Expansion)", "de": "Hitze (>32°C / Schienendehnung)"},
}


def calculate_train_delay_forecast(
    origin: str = "Frankfurt am Main",
    destination: str = "Cologne",
    weather: str = "clear",
    hour: int = 17,
    day_type: str = "weekday",
) -> Dict[str, Any]:
  """Forecast delay probability and expected passenger delay using route congestion and weather factors."""
  c_orig = STATION_CONGESTION_SCORES.get(origin, 0.50)
  c_dest = STATION_CONGESTION_SCORES.get(destination, 0.50)
  avg_congestion = (c_orig + c_dest) / 2.0

  w_data = WEATHER_IMPACT_WEIGHTS.get(weather, WEATHER_IMPACT_WEIGHTS["clear"])
  w_coeff = w_data["coeff"]

  # Time of day coefficient
  if 6 <= hour <= 9:
    time_factor = 1.15
    rush_lbl = "Morning Commute Peak (06:00-09:00)"
  elif 15 <= hour <= 19:
    time_factor = 1.20
    rush_lbl = "Evening Commute Peak (15:00-19:00)"
  elif 22 <= hour or hour <= 5:
    time_factor = 0.88
    rush_lbl = "Night Off-Peak"
  else:
    time_factor = 1.0
    rush_lbl = "Midday Standard Window"

  day_factor = 1.12 if day_type == "weekend" else 1.0

  raw_score = (avg_congestion * 0.45 + 0.20) * w_coeff * time_factor * day_factor
  delay_prob = round(min(max(raw_score * 100.0, 15.0), 96.0), 1)
  on_time_prob = round(100.0 - delay_prob, 1)

  expected_delay = round(max((delay_prob / 100.0) * 28.0 * (w_coeff ** 0.75), 2.0), 1)

  if delay_prob >= 75:
    risk_level = "Severe"
    rating = "D-"
    adv_en = f"High probability of major delays or cancellations on {origin} ➔ {destination} due to {w_data['en'].lower()} and heavy corridor load. Allow at least 45 minutes transfer buffer."
    adv_de = f"Sehr hohes Risiko für erhebliche Verspätungen auf der Strecke {origin} ➔ {destination} aufgrund von {w_data['de'].lower()}. Planen Sie mindestens 45 Minuten Umstiegszeit ein."
  elif delay_prob >= 55:
    risk_level = "High"
    rating = "C"
    adv_en = f"Elevated delay risk on {origin} ➔ {destination}. Junction congestion is high. Direct ICE connections recommended."
    adv_de = f"Erhöhtes Verspätungsrisiko auf {origin} ➔ {destination}. Knotenpunkte stark ausgelastet. ICE-Direktverbindungen empfohlen."
  elif delay_prob >= 35:
    risk_level = "Moderate"
    rating = "B"
    adv_en = f"Moderate operating conditions. Minor delays (5-15 min) possible around peak junctions."
    adv_de = f"Mäßige Betriebsbedingungen. Leichte Verspätungen (5-15 Min) an Hauptknotenpunkten möglich."
  else:
    risk_level = "Low"
    rating = "A"
    adv_en = f"Optimal conditions on {origin} ➔ {destination}. High likelihood of on-time arrival (<5 min delay)."
    adv_de = f"Optimale Reisebedingungen auf {origin} ➔ {destination}. Hohe Pünktlichkeitswahrscheinlichkeit (<5 Min Verspätung)."

  total_impact = (avg_congestion * 40) + ((w_coeff - 1.0) * 50) + ((time_factor - 1.0) * 35) + 20
  pct_junction = round(((avg_congestion * 40) / total_impact) * 100)
  pct_weather = round((((w_coeff - 1.0) * 50 + 5) / total_impact) * 100)
  pct_time = round((((time_factor - 1.0) * 35 + 10) / total_impact) * 100)
  pct_base = max(100 - (pct_junction + pct_weather + pct_time), 5)

  return {
      "success": True,
      "route": {
          "origin": origin,
          "destination": destination,
          "weather": weather,
          "hour": hour,
          "day_type": day_type,
          "time_window": rush_lbl,
      },
      "forecast": {
          "delay_probability_pct": delay_prob,
          "on_time_probability_pct": on_time_prob,
          "expected_delay_minutes": expected_delay,
          "risk_level": risk_level,
          "rating": rating,
          "weather_label": {
              "en": w_data["en"],
              "de": w_data["de"],
          },
          "risk_factors": {
              "junction_congestion_pct": pct_junction,
              "weather_impact_pct": pct_weather,
              "time_of_day_load_pct": pct_time,
              "baseline_network_load_pct": pct_base,
          },
          "advice": {
              "en": adv_en,
              "de": adv_de,
          },
      },
  }
