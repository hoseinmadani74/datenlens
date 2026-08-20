from typing import Dict, Any

GERMANY_HOUSING_DATA: Dict[str, Any] = {
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


def get_german_housing_data() -> Dict[str, Any]:
  """Return aggregated German rental index and housing benchmarks."""
  return GERMANY_HOUSING_DATA
