from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import mlflow
import joblib
import os
import json
import time
from pathlib import Path
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Exchange Rate Forecast API", version="1.0.0")

# Prometheus metrics
# Service metrics
http_request_count = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

inference_latency = Histogram(
    'inference_latency_seconds',
    'Inference latency in seconds',
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
)

# Data drift metrics
data_drift_requests = Counter(
    'data_drift_requests_total',
    'Total number of requests with out-of-distribution features'
)

data_drift_ratio = Gauge(
    'data_drift_ratio',
    'Ratio of requests with out-of-distribution features (0-1)'
)

total_prediction_requests = Counter(
    'prediction_requests_total',
    'Total number of prediction requests'
)

# Initialize Prometheus instrumentation
Instrumentator().instrument(app).expose(app)

# Set MLflow tracking URI and credentials
tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "https://dagshub.com/hamnariaz57/Mlops_Project.mlflow")
mlflow.set_tracking_uri(tracking_uri)

# Set MLflow credentials for Dagshub
os.environ['MLFLOW_TRACKING_USERNAME'] = os.getenv('DAGSHUB_USERNAME', os.getenv('MLFLOW_TRACKING_USERNAME', ''))
os.environ['MLFLOW_TRACKING_PASSWORD'] = os.getenv('DAGSHUB_TOKEN', os.getenv('MLFLOW_TRACKING_PASSWORD', ''))

# Model loading logic
MODEL_PATH = os.getenv("MODEL_PATH", "/app/models/rf_model.pkl")
RUN_ID = os.getenv("MLFLOW_RUN_ID", None)
TRAINING_STATS_PATH = os.getenv("TRAINING_STATS_PATH", "/app/models/training_stats.json")

# Training data statistics for drift detection
training_stats = None

def load_training_stats():
    """Load training data statistics for drift detection."""
    global training_stats
    try:
        if Path(TRAINING_STATS_PATH).exists():
            with open(TRAINING_STATS_PATH, 'r') as f:
                training_stats = json.load(f)
            print(f"✓ Training statistics loaded from {TRAINING_STATS_PATH}")
        else:
            print(f"⚠ Warning: Training statistics not found at {TRAINING_STATS_PATH}")
            print("  Data drift detection will be disabled until statistics are available.")
    except Exception as e:
        print(f"⚠ Error loading training statistics: {str(e)}")
        training_stats = None

def check_data_drift(feature_values):
    """
    Check if feature values are out-of-distribution.
    Returns True if any feature is outside 3 standard deviations from training mean.
    """
    if training_stats is None or 'features' not in training_stats:
        return False
    
    for i, value in enumerate(feature_values):
        feature_name = f"lag_{i+1}"
        if feature_name not in training_stats['features']:
            continue
        
        stats = training_stats['features'][feature_name]
        mean = stats['mean']
        std = stats['std']
        min_val = stats['min']
        max_val = stats['max']
        
        # Check if value is outside training range (with some tolerance)
        # Also check if value is more than 3 standard deviations from mean
        z_score = abs((value - mean) / std) if std > 0 else 0
        out_of_range = value < min_val or value > max_val
        
        if out_of_range or z_score > 3:
            return True
    
    return False

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

# Load model and training statistics at startup
try:
    load_model()
    load_training_stats()
except Exception as e:
    print(f"Failed to load model: {str(e)}")
    model = None

class History(BaseModel):
    history: list

@app.get("/")
def home(request: Request):
    """Health check endpoint."""
    http_request_count.labels(method=request.method, endpoint="/", status=200).inc()
    return {
        "message": "Exchange Rate Forecast API Running",
        "status": "healthy",
        "model_loaded": model is not None,
        "monitoring": {
            "prometheus": "/metrics",
            "drift_detection": training_stats is not None
        }
    }

@app.get("/health")
def health(request: Request):
    """Health check endpoint for Docker."""
    if model is None:
        http_request_count.labels(method=request.method, endpoint="/health", status=503).inc()
        raise HTTPException(status_code=503, detail="Model not loaded")
    http_request_count.labels(method=request.method, endpoint="/health", status=200).inc()
    return {"status": "healthy", "model_loaded": True}

@app.post("/predict")
def predict(data: History, request: Request):
    """Predict exchange rate based on historical values."""
    start_time = time.time()
    
    if model is None:
        http_request_count.labels(method=request.method, endpoint="/predict", status=503).inc()
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if len(data.history) < 3:
        http_request_count.labels(method=request.method, endpoint="/predict", status=400).inc()
        raise HTTPException(status_code=400, detail="Need at least 3 historical values")
    
    values = data.history[-3:]  # Use recent 3 values as lags
    
    # Check for data drift
    is_drift = check_data_drift(values)
    if is_drift:
        data_drift_requests.inc()
    
    # Update total prediction requests
    total_prediction_requests.inc()
    
    # Calculate and update drift ratio
    # Note: The actual drift ratio calculation in Grafana should use PromQL:
    # rate(data_drift_requests_total[5m]) / rate(prediction_requests_total[5m])
    # This gauge provides a simple approximation, but PromQL rate() is more accurate
    # We'll update it here for convenience, but Grafana dashboard uses PromQL for accuracy
    
    try:
        pred = model.predict([values])
        prediction_value = float(pred[0])
        
        # Record inference latency
        latency = time.time() - start_time
        inference_latency.observe(latency)
        
        # Record successful request
        http_request_count.labels(method=request.method, endpoint="/predict", status=200).inc()
        
        return {
            "prediction": prediction_value,
            "drift_detected": is_drift,
            "latency_ms": round(latency * 1000, 2)
        }
    except Exception as e:
        http_request_count.labels(method=request.method, endpoint="/predict", status=500).inc()
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
