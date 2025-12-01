from fastapi import FastAPI
from pydantic import BaseModel
import mlflow
import joblib
import os

app = FastAPI()

RUN_ID = "710aa71d43ae44db9f4e996133724686"
MODEL_URI = f"runs:/{RUN_ID}/rf_model.pkl"

# Load model from MLflow
local_path = mlflow.artifacts.download_artifacts(artifact_uri=MODEL_URI)
model = joblib.load(local_path)

class History(BaseModel):
    history: list

@app.get("/")
def home():
    return {"message": "Exchange Rate Forecast API Running"}

@app.post("/predict")
def predict(data: History):
    values = data.history[-3:]  # Use recent 3 values as lags
    pred = model.predict([values])
    return {"prediction": float(pred[0])}
