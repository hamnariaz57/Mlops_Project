import os
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import mlflow
import joblib

DATA_PATH = "data/processed/exchange_rates.csv"
TARGET_COL = "EUR"
TIMESTAMP_COL = "collection_datetime"

def load_data():
    # Read CSV and handle potential parsing errors
    try:
        df = pd.read_csv(DATA_PATH, on_bad_lines='skip')
    except TypeError:
        # Fallback for older pandas versions
        df = pd.read_csv(DATA_PATH, error_bad_lines=False, warn_bad_lines=False)
    
    if df.empty:
        raise ValueError(f"Data file {DATA_PATH} is empty. Please run the Airflow DAG to collect data first.")
    
    # Select only the columns we need
    required_cols = [TIMESTAMP_COL, TARGET_COL]
    available_cols = [col for col in required_cols if col in df.columns]
    
    # Check if required columns exist
    if TARGET_COL not in df.columns:
        raise ValueError(f"Target column '{TARGET_COL}' not found in data. Available columns: {list(df.columns)}")
    
    # Keep only essential columns
    essential_cols = [TIMESTAMP_COL, TARGET_COL]
    df = df[[col for col in essential_cols if col in df.columns]]
    
    df[TIMESTAMP_COL] = pd.to_datetime(df[TIMESTAMP_COL], errors='coerce')
    df = df.dropna(subset=[TIMESTAMP_COL, TARGET_COL])
    df = df.sort_values(TIMESTAMP_COL)
    
    if df.empty:
        raise ValueError(f"After filtering, no valid data remains. Please check your data file.")
    
    return df

def create_lags(df, n_lags=3):
    """
    Create lag features for time series prediction.
    Requires at least n_lags + 1 rows of data.
    """
    min_required_rows = n_lags + 1
    
    if len(df) < min_required_rows:
        raise ValueError(
            f"Insufficient data for training! "
            f"Need at least {min_required_rows} rows, but only have {len(df)} rows. "
            f"Please run the Airflow DAG multiple times to collect more data, or reduce n_lags."
        )
    
    # Create lag features
    for lag in range(1, n_lags + 1):
        df[f"lag_{lag}"] = df[TARGET_COL].shift(lag)
    
    # Drop rows with NaN (first n_lags rows will have NaN in lag columns)
    df = df.dropna()
    
    if len(df) == 0:
        raise ValueError(
            f"After creating lag features, no valid data remains. "
            f"This should not happen if you have at least {min_required_rows} rows."
        )
    
    X = df[[f"lag_{i}" for i in range(1, n_lags + 1)]]
    y = df[TARGET_COL]
    
    return X, y

def train():
    # Set MLflow tracking URI
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "https://dagshub.com/hamnariaz57/Mlops_Project.mlflow")
    mlflow.set_tracking_uri(tracking_uri)
    
    # Set MLflow credentials for Dagshub
    os.environ['MLFLOW_TRACKING_USERNAME'] = os.getenv('DAGSHUB_USERNAME', os.getenv('MLFLOW_TRACKING_USERNAME', ''))
    os.environ['MLFLOW_TRACKING_PASSWORD'] = os.getenv('DAGSHUB_TOKEN', os.getenv('MLFLOW_TRACKING_PASSWORD', ''))
    
    mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "exchange_rate_forecasting"))

    df = load_data()
    print(f"✓ Loaded {len(df)} rows of data")
    
    X, y = create_lags(df)
    print(f"✓ Created lag features: {len(X)} samples available")

    # Check if we have enough data for train/test split
    if len(X) < 2:
        raise ValueError(
            f"Not enough data for train/test split! "
            f"Need at least 2 samples after creating lags, but only have {len(X)}. "
            f"Please collect more data by running the Airflow DAG multiple times."
        )
    
    # Adjust test_size if we have very few samples
    if len(X) < 10:
        print(f"⚠ Warning: Only {len(X)} samples available. Using all data for training (no test split).")
        X_train, X_test, y_train, y_test = X, X, y, y
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

    with mlflow.start_run(run_name="rf_exchange_rate"):
        model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        # Metrics
        mse = mean_squared_error(y_test, y_pred)
        rmse = mse ** 0.5
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2", r2)

        mlflow.log_params({"n_estimators": 200, "max_depth": 10})

        # Save locally + upload as artifact
        model_path = "rf_model.pkl"
        joblib.dump(model, model_path)
        mlflow.log_artifact(model_path)

        run_id = mlflow.active_run().info.run_id

        print("🎯 Model trained and logged to MLflow successfully!")
        print(f"Run ID: {run_id}")
        print(f"RMSE: {rmse:.4f}, MAE: {mae:.4f}, R2: {r2:.4f}")

if __name__ == "__main__":
    train()
