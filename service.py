from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow
import joblib
import os
from pathlib import Path

app = FastAPI(title="Exchange Rate Forecast API", version="1.0.0")

# Set MLflow tracking URI and credentials
tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "https://dagshub.com/hamnariaz57/Mlops_Project.mlflow")
mlflow.set_tracking_uri(tracking_uri)

# Set MLflow credentials for Dagshub
os.environ['MLFLOW_TRACKING_USERNAME'] = os.getenv('DAGSHUB_USERNAME', os.getenv('MLFLOW_TRACKING_USERNAME', ''))
os.environ['MLFLOW_TRACKING_PASSWORD'] = os.getenv('DAGSHUB_TOKEN', os.getenv('MLFLOW_TRACKING_PASSWORD', ''))

# Model loading logic
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/rf_model.pkl")
RUN_ID = os.getenv("MLFLOW_RUN_ID", None)

def load_model():
    """Load model from local path or MLflow."""
    global model
    
    # Try to load from local path first (for Docker deployment)
    if Path(MODEL_PATH).exists():
        print(f"Loading model from local path: {MODEL_PATH}")
        try:
            model = joblib.load(MODEL_PATH)
            print("Model loaded successfully from local path!")
            return
        except Exception as e:
            print(f"Error loading from local path: {str(e)}")
    
    # Fallback to MLflow if RUN_ID is provided
    if RUN_ID:
        print(f"Loading model from MLflow run: {RUN_ID}")
        try:
            MODEL_URI = f"runs:/{RUN_ID}/rf_model.pkl"
            local_path = mlflow.artifacts.download_artifacts(artifact_uri=MODEL_URI)
            model = joblib.load(local_path)
            
            # Save to MODEL_PATH for future use
            Path(MODEL_PATH).parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(local_path, MODEL_PATH)
            print(f"Model loaded from MLflow and saved to {MODEL_PATH}")
            return
        except Exception as e:
            print(f"Error loading from MLflow: {str(e)}")
    
    # Last resort: try to fetch best model automatically
    print("Attempting to fetch best model from MLflow...")
    try:
        from fetch_model import get_best_model_run_id, download_model
        best_run_id, metric_value = get_best_model_run_id()
        model_path = download_model(best_run_id, output_dir="/app/models")
        model = joblib.load(model_path)
        print(f"Successfully loaded best model (RMSE: {metric_value})")
        return
    except Exception as e:
        print(f"Error fetching best model: {str(e)}")
    
    raise RuntimeError("Model not found! Please ensure MODEL_PATH or MLFLOW_RUN_ID is set correctly.")

# Load model at startup
try:
    load_model()
except Exception as e:
    print(f"Failed to load model: {str(e)}")
    model = None

class History(BaseModel):
    history: list

@app.get("/")
def home():
    """Health check endpoint."""
    return {
        "message": "Exchange Rate Forecast API Running",
        "status": "healthy",
        "model_loaded": model is not None
    }

@app.get("/health")
def health():
    """Health check endpoint for Docker."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model_loaded": True}

@app.post("/predict")
def predict(data: History):
    """Predict exchange rate based on historical values."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if len(data.history) < 3:
        raise HTTPException(status_code=400, detail="Need at least 3 historical values")
    
    values = data.history[-3:]  # Use recent 3 values as lags
    try:
        pred = model.predict([values])
        return {"prediction": float(pred[0])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
