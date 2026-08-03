from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pipeline import run_oil_pipeline

app = FastAPI(title="Datenlens API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from localhost:8080, EC2, datenlens.de, etc.
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
