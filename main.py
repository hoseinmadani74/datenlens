from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pipeline import run_oil_pipeline

app = FastAPI(title="Datenlens API")

# Explicit list of allowed origins (NO WILDCARD "*" WITH CREDENTIALS)
origins = [
    "http://localhost:8080",  # Your local Nginx/Docker frontend
    "http://localhost:5173",  # Local Vite dev server
    "http://localhost:3000",
    "https://datenlens.de",  # Your production domain
    "https://www.datenlens.de",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
  return {"status": "online"}


@app.get("/api/oil-data")
def get_oil_data():
  return run_oil_pipeline()
