# main.py
from fastapi import BackgroundTasks, FastAPI
from pipeline import run_pipeline

app = FastAPI(
    title="Datenlens API",
    description="Production API and Data Pipeline Service",
)


@app.get("/")
def read_root():
  return {"message": "Datenlens API is live!", "status": "running"}


# Sync route: Runs pipeline synchronously and returns output (best for quick runs)
@app.post("/run-pipeline")
def execute_pipeline_sync():
  output = run_pipeline()
  return {"message": "Pipeline completed", "details": output}


# Async route: Runs pipeline in background (best if execution takes long)
@app.post("/run-pipeline-async")
def execute_pipeline_async(background_tasks: BackgroundTasks):
  background_tasks.add_task(run_pipeline)
  return {
      "message": (
          "Pipeline execution started in the background. Check logs for"
          " progress."
      )
  }
