from fastapi import FastAPI
from pydantic import BaseModel
import mlflow
import joblib
import os

app = FastAPI()

# Set MLflow tracking URI and credentials
tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "https://dagshub.com/hamnariaz57/Mlops_Project.mlflow")
mlflow.set_tracking_uri(tracking_uri)

# Set MLflow credentials for Dagshub
os.environ['MLFLOW_TRACKING_USERNAME'] = os.getenv('DAGSHUB_USERNAME', os.getenv('MLFLOW_TRACKING_USERNAME', ''))
os.environ['MLFLOW_TRACKING_PASSWORD'] = os.getenv('DAGSHUB_TOKEN', os.getenv('MLFLOW_TRACKING_PASSWORD', ''))

# Use the latest run ID from training
RUN_ID = os.getenv("MLFLOW_RUN_ID", "cf250281569e4b4b8e89b3a2d0ddb5e4")
MODEL_URI = f"runs:/{RUN_ID}/rf_model.pkl"

# Load model from MLflow
print(f"Loading model from MLflow run: {RUN_ID}")
local_path = mlflow.artifacts.download_artifacts(artifact_uri=MODEL_URI)
model = joblib.load(local_path)
print("Model loaded successfully!")

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
