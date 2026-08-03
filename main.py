# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pipeline import run_oil_pipeline

app = FastAPI(
    title="Datenlens API",
    description="Backend processing engine powering datenlens.de",
)

# Enable CORS so your React frontend can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",  # <--- Add your local Docker port here!
        "http://localhost:3000",  # Default local React development server
        "http://localhost:5173",  # Default local Vite + React server
        "https://datenlens.de",  # Your production domain
        "https://www.datenlens.de",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)


@app.get("/")
def health_check():
  return {"status": "online", "service": "Datenlens Backend API"}


@app.get("/api/oil-data")
def get_oil_data():
  """Endpoint called by React to get the latest PySpark oil calculations."""
  result = run_oil_pipeline()
  return result
