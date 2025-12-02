"""
Script to fetch the best performing model from MLflow Model Registry.
This script is used in the CD pipeline to get the latest/best model.
"""
import os
import mlflow
import sys
from pathlib import Path

def get_best_model_run_id(experiment_name="exchange_rate_forecasting", metric="rmse", ascending=True):
    """
    Fetch the best model run ID from MLflow based on a metric.
    
    Args:
        experiment_name: Name of the MLflow experiment
        metric: Metric to use for comparison (default: rmse, lower is better)
        ascending: True if lower metric is better (default: True for RMSE)
    
    Returns:
        Best run ID and metric value
    """
    # Set MLflow tracking URI
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "https://dagshub.com/hamnariaz57/Mlops_Project.mlflow")
    mlflow.set_tracking_uri(tracking_uri)
    
    # Set MLflow credentials for Dagshub
    os.environ['MLFLOW_TRACKING_USERNAME'] = os.getenv('DAGSHUB_USERNAME', os.getenv('MLFLOW_TRACKING_USERNAME', ''))
    os.environ['MLFLOW_TRACKING_PASSWORD'] = os.getenv('DAGSHUB_TOKEN', os.getenv('MLFLOW_TRACKING_PASSWORD', ''))
    
    try:
        # Get experiment
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            print(f"Experiment '{experiment_name}' not found!")
            sys.exit(1)
        
        # Search for runs
        runs = mlflow.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=[f"metrics.{metric} {'ASC' if ascending else 'DESC'}"],
            max_results=1
        )
        
        if runs.empty:
            print("No runs found in experiment!")
            sys.exit(1)
        
        best_run = runs.iloc[0]
        run_id = best_run['run_id']
        metric_value = best_run[f'metrics.{metric}']
        
        print(f"Best model found:")
        print(f"  Run ID: {run_id}")
        print(f"  {metric}: {metric_value}")
        
        return run_id, metric_value
        
    except Exception as e:
        print(f"Error fetching model: {str(e)}")
        sys.exit(1)

def download_model(run_id, model_name="rf_model.pkl", output_dir="/app/models"):
    """
    Download model artifact from MLflow run.
    
    Args:
        run_id: MLflow run ID
        model_name: Name of the model file
        output_dir: Directory to save the model
    """
    try:
        model_uri = f"runs:/{run_id}/{model_name}"
        print(f"Downloading model from: {model_uri}")
        
        # Download artifact
        local_path = mlflow.artifacts.download_artifacts(artifact_uri=model_uri)
        
        # Copy to output directory
        output_path = Path(output_dir) / model_name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        import shutil
        shutil.copy2(local_path, str(output_path))
        
        # Return normalized path (use forward slashes for cross-platform compatibility)
        normalized_path = str(output_path).replace('\\', '/')
        print(f"Model saved to: {normalized_path}")
        return normalized_path
        
    except Exception as e:
        print(f"Error downloading model: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Get best model
    run_id, metric_value = get_best_model_run_id()
    
    # Download model
    model_path = download_model(run_id)
    
    # Output run ID for use in service
    print(f"\nMLFLOW_RUN_ID={run_id}")
    print(f"MODEL_PATH={model_path}")

