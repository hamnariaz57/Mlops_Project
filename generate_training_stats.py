"""
Generate training statistics for drift detection without MLflow dependency.
This script loads the data, creates features, and saves statistics.
"""
import os
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

DATA_PATH = "data/processed/exchange_rates.csv"
TARGET_COL = "EUR"
TIMESTAMP_COL = "collection_datetime"

def load_data():
    """Load and prepare data."""
    try:
        df = pd.read_csv(DATA_PATH, on_bad_lines='skip')
    except TypeError:
        df = pd.read_csv(DATA_PATH, error_bad_lines=False, warn_bad_lines=False)
    
    if df.empty:
        raise ValueError(f"Data file {DATA_PATH} is empty.")
    
    essential_cols = [TIMESTAMP_COL, TARGET_COL]
    df = df[[col for col in essential_cols if col in df.columns]]
    
    df[TIMESTAMP_COL] = pd.to_datetime(df[TIMESTAMP_COL], errors='coerce')
    df = df.dropna(subset=[TIMESTAMP_COL, TARGET_COL])
    df = df.sort_values(TIMESTAMP_COL)
    
    if df.empty:
        raise ValueError("No valid data after filtering.")
    
    return df

def create_lags(df, n_lags=3):
    """Create lag features."""
    min_required_rows = n_lags + 1
    
    if len(df) < min_required_rows:
        raise ValueError(f"Insufficient data! Need at least {min_required_rows} rows.")
    
    # Create lag features
    for lag in range(1, n_lags + 1):
        df[f"lag_{lag}"] = df[TARGET_COL].shift(lag)
    
    df = df.dropna()
    
    if len(df) == 0:
        raise ValueError("No valid data after creating lags.")
    
    X = df[[f"lag_{i}" for i in range(1, n_lags + 1)]]
    y = df[TARGET_COL]
    
    return X, y

def generate_stats():
    """Generate and save training statistics."""
    print("Loading data...")
    df = load_data()
    print(f"✓ Loaded {len(df)} rows of data")
    
    print("Creating lag features...")
    X, y = create_lags(df)
    print(f"✓ Created lag features: {len(X)} samples available")
    
    # Generate statistics
    training_stats = {
        "features": {},
        "timestamp": datetime.now().isoformat()
    }
    
    for col in X.columns:
        training_stats["features"][col] = {
            "min": float(X[col].min()),
            "max": float(X[col].max()),
            "mean": float(X[col].mean()),
            "std": float(X[col].std())
        }
    
    # Save to models directory
    Path("models").mkdir(exist_ok=True)
    stats_path = "models/training_stats.json"
    
    with open(stats_path, 'w') as f:
        json.dump(training_stats, f, indent=2)
    
    print(f"✓ Training statistics saved to {stats_path}")
    print("\nStatistics generated:")
    for feature, stats in training_stats["features"].items():
        print(f"  {feature}: min={stats['min']:.4f}, max={stats['max']:.4f}, mean={stats['mean']:.4f}, std={stats['std']:.4f}")

if __name__ == "__main__":
    try:
        generate_stats()
        print("\n✅ Training statistics generation complete!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        exit(1)

