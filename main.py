from fastapi import FastAPI
# Option: Import your pipeline functions here if you want to trigger them via HTTP
# from pipeline import run_pipeline

app = FastAPI(title="Datenlens API")


@app.get("/")
def read_root():
  return {"message": "Datenlens API is live!", "status": "running"}


@app.get("/health")
def health_check():
  return {"status": "ok"}
