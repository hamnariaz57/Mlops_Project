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
    df = pd.read_csv(DATA_PATH)
    df[TIMESTAMP_COL] = pd.to_datetime(df[TIMESTAMP_COL])
    df = df.sort_values(TIMESTAMP_COL)
    return df

def create_lags(df, n_lags=3):
    for lag in range(1, n_lags + 1):
        df[f"lag_{lag}"] = df[TARGET_COL].shift(lag)
    df = df.dropna()
    X = df[[f"lag_{i}" for i in range(1, n_lags + 1)]]
    y = df[TARGET_COL]
    return X, y

def train():
    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "exchange_rate_forecasting"))

    df = load_data()
    X, y = create_lags(df)

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
