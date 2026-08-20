import os

TANKERKOENIG_KEY: str = os.getenv(
    "TANKERKOENIG_KEY", "190afc0c-cf12-4405-8a49-97d8b83a5c3b"
)

CACHE_TTL_SECONDS: int = 300
JOBS_CACHE_TTL_SECONDS: int = 180

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OIL_DATA_FILE: str = os.path.join(BASE_DIR, "oil_processed_data.json")
