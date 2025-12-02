"""
MLOps Phase 1: Real-Time Exchange Rate Predictive System
Complete ETL Pipeline with Data Quality Checks, Feature Engineering, and DVC Versioning
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowException
from datetime import datetime, timedelta
import requests
import pandas as pd
import numpy as np
import json
import os
import subprocess
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import for data profiling and MLflow
try:
    from ydata_profiling import ProfileReport
except ImportError:
    from pandas_profiling import ProfileReport
import mlflow

# ============================================================================
# CONFIGURATION
# ============================================================================
BASE_DIR = Path("/opt/airflow")
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
REPORTS_DIR = BASE_DIR / "reports"

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Configuration
API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
BASE_CURRENCY = "USD"

# Data Quality Thresholds
NULL_THRESHOLD = 0.01  # 1% null values
MIN_REQUIRED_CURRENCIES = 10  # Minimum number of currencies in response

# MLflow Configuration (DagHub)
MLFLOW_TRACKING_URI = "https://dagshub.com/hamnariaz57/Mlops_Project.mlflow"
os.environ['MLFLOW_TRACKING_USERNAME'] = os.getenv('DAGSHUB_USERNAME', 'hamnariaz57')
os.environ['MLFLOW_TRACKING_PASSWORD'] = os.getenv('DAGSHUB_TOKEN', '')

# ============================================================================
# TASK 1: DATA EXTRACTION
# ============================================================================
def extract_exchange_rate_data(**context):
    """
    Extract live exchange rate data from API and save with timestamp.
    
    Mandatory: Save raw data immediately with collection timestamp.
    """
    print("=" * 80)
    print("PHASE 1.1: DATA EXTRACTION")
    print("=" * 80)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # Fetch data from API
        print(f"Fetching data from: {API_URL}")
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extract relevant information
        rates = data.get('rates', {})
        base = data.get('base', BASE_CURRENCY)
        date = data.get('date', datetime.now().strftime("%Y-%m-%d"))
        time_last_updated = data.get('time_last_updated', timestamp)
        
        # Create DataFrame with timestamp
        df = pd.DataFrame([{
            'timestamp': timestamp,
            'collection_datetime': datetime.now().isoformat(),
            'base_currency': base,
            'api_date': date,
            'time_last_updated': time_last_updated,
            **rates
        }])
        
        # Save raw data with timestamp
        raw_file_path = RAW_DATA_DIR / f"exchange_rates_raw_{timestamp}.csv"
        df.to_csv(raw_file_path, index=False)
        
        print(f"✓ Data extracted successfully")
        print(f"✓ Saved to: {raw_file_path}")
        print(f"✓ Number of currencies: {len(rates)}")
        print(f"✓ Timestamp: {timestamp}")
        
        # Push data path to XCom for next tasks
        context['task_instance'].xcom_push(key='raw_data_path', value=str(raw_file_path))
        context['task_instance'].xcom_push(key='timestamp', value=timestamp)
        context['task_instance'].xcom_push(key='num_currencies', value=len(rates))
        
        return str(raw_file_path)
        
    except requests.exceptions.RequestException as e:
        raise AirflowException(f"Failed to fetch data from API: {str(e)}")
    except Exception as e:
        raise AirflowException(f"Unexpected error during extraction: {str(e)}")


# ============================================================================
# TASK 2: DATA QUALITY CHECK (MANDATORY GATE)
# ============================================================================
def data_quality_check(**context):
    """
    Mandatory Quality Gate: Validate data quality before proceeding.
    
    Checks:
    1. No more than 1% null values in key columns
    2. Schema validation
    3. Minimum number of currencies present
    
    If any check fails, the DAG must stop.
    """
    print("=" * 80)
    print("PHASE 1.2: DATA QUALITY CHECK (MANDATORY GATE)")
    print("=" * 80)
    
    # Get raw data path from previous task
    raw_data_path = context['task_instance'].xcom_pull(
        task_ids='extract_data',
        key='raw_data_path'
    )
    
    if not raw_data_path or not Path(raw_data_path).exists():
        raise AirflowException("Raw data file not found!")
    
    # Load raw data
    df = pd.read_csv(raw_data_path)
    
    print(f"✓ Loaded data from: {raw_data_path}")
    print(f"✓ Shape: {df.shape}")
    
    # ========== QUALITY CHECK 1: Null Values ==========
    print("\n--- Quality Check 1: Null Values ---")
    null_percentage = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
    print(f"Total null percentage: {null_percentage:.2f}%")
    print(f"Threshold: {NULL_THRESHOLD * 100}%")
    
    if null_percentage > (NULL_THRESHOLD * 100):
        raise AirflowException(
            f"QUALITY CHECK FAILED: Null values ({null_percentage:.2f}%) exceed threshold ({NULL_THRESHOLD * 100}%)"
        )
    print("✓ PASSED: Null values within acceptable range")
    
    # ========== QUALITY CHECK 2: Schema Validation ==========
    print("\n--- Quality Check 2: Schema Validation ---")
    required_columns = ['timestamp', 'collection_datetime', 'base_currency', 'api_date']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise AirflowException(
            f"QUALITY CHECK FAILED: Missing required columns: {missing_columns}"
        )
    print(f"✓ PASSED: All required columns present")
    
    # ========== QUALITY CHECK 3: Minimum Currency Count ==========
    print("\n--- Quality Check 3: Minimum Currency Count ---")
    currency_columns = [col for col in df.columns if col not in required_columns]
    num_currencies = len(currency_columns)
    print(f"Number of currencies: {num_currencies}")
    print(f"Minimum required: {MIN_REQUIRED_CURRENCIES}")
    
    if num_currencies < MIN_REQUIRED_CURRENCIES:
        raise AirflowException(
            f"QUALITY CHECK FAILED: Only {num_currencies} currencies found, minimum {MIN_REQUIRED_CURRENCIES} required"
        )
    print("✓ PASSED: Sufficient currencies present")
    
    # ========== QUALITY CHECK 4: Data Type Validation ==========
    print("\n--- Quality Check 4: Data Type Validation ---")
    # Check if currency rates are numeric
    for col in currency_columns[:5]:  # Sample check
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise AirflowException(
                f"QUALITY CHECK FAILED: Column '{col}' is not numeric"
            )
    print("✓ PASSED: Currency columns are numeric")
    
    print("\n" + "=" * 80)
    print("✓✓✓ ALL QUALITY CHECKS PASSED ✓✓✓")
    print("=" * 80 + "\n")
    
    # Store quality metrics in XCom
    quality_metrics = {
        'null_percentage': null_percentage,
        'num_currencies': num_currencies,
        'num_rows': len(df),
        'num_columns': len(df.columns)
    }
    context['task_instance'].xcom_push(key='quality_metrics', value=quality_metrics)
    
    return True


# ============================================================================
# TASK 3: DATA TRANSFORMATION & FEATURE ENGINEERING
# ============================================================================
def transform_and_engineer_features(**context):
    """
    Clean data and perform time-series feature engineering.
    
    Features:
    - Lag features (previous day's rates)
    - Rolling means (7-day, 30-day averages)
    - Rate of change (daily, weekly)
    - Time-based features (day of week, month, quarter)
    - Volatility measures
    """
    print("=" * 80)
    print("PHASE 1.3: TRANSFORMATION & FEATURE ENGINEERING")
    print("=" * 80)
    
    # Get raw data path
    raw_data_path = context['task_instance'].xcom_pull(
        task_ids='extract_data',
        key='raw_data_path'
    )
    timestamp = context['task_instance'].xcom_pull(
        task_ids='extract_data',
        key='timestamp'
    )
    
    # Load raw data
    df = pd.read_csv(raw_data_path)
    print(f"✓ Loaded raw data: {df.shape}")
    
    # Convert collection_datetime to datetime
    df['collection_datetime'] = pd.to_datetime(df['collection_datetime'])
    
    # ========== Feature Engineering ==========
    print("\n--- Feature Engineering ---")
    
    # 1. Time-based features
    df['day_of_week'] = df['collection_datetime'].dt.dayofweek
    df['day_of_month'] = df['collection_datetime'].dt.day
    df['month'] = df['collection_datetime'].dt.month
    df['quarter'] = df['collection_datetime'].dt.quarter
    df['year'] = df['collection_datetime'].dt.year
    df['hour'] = df['collection_datetime'].dt.hour
    
    print("✓ Added time-based features")
    
    # 2. Load historical data if exists to create lag and rolling features
    historical_file = PROCESSED_DATA_DIR / "exchange_rates.csv"
    
    if historical_file.exists():
        try:
            # Try to read CSV with error handling for malformed rows
            try:
                # Try with newer pandas API first
                historical_df = pd.read_csv(
                    historical_file,
                    on_bad_lines='skip',  # Skip malformed lines
                    engine='python',  # Use Python engine for better error handling
                    warn_bad_lines=False
                )
            except TypeError:
                # Fallback for older pandas versions
                historical_df = pd.read_csv(
                    historical_file,
                    error_bad_lines=False,
                    warn_bad_lines=False,
                    engine='python'
                )
            
            # If file is empty or has no valid data, skip historical
            if historical_df.empty or len(historical_df) == 0:
                print("⚠ Historical file exists but is empty - skipping historical data")
                historical_df = None
            else:
                # Ensure collection_datetime column exists and convert
                if 'collection_datetime' in historical_df.columns:
                    historical_df['collection_datetime'] = pd.to_datetime(historical_df['collection_datetime'], errors='coerce')
                    # Remove rows with invalid dates
                    historical_df = historical_df.dropna(subset=['collection_datetime'])
                else:
                    print("⚠ Historical file missing collection_datetime - skipping historical data")
                    historical_df = None
                    
        except Exception as e:
            print(f"⚠ Error reading historical file: {str(e)}")
            print("⚠ Skipping historical data and creating new file")
            historical_df = None
        
        if historical_df is not None and not historical_df.empty:
            # Ensure column alignment - only keep columns that exist in both
            common_cols = [col for col in df.columns if col in historical_df.columns]
            if len(common_cols) < 5:  # Too few common columns, likely incompatible
                print("⚠ Historical data has incompatible structure - skipping historical data")
                historical_df = None
            else:
                # Align columns
                historical_df = historical_df[common_cols]
                df_aligned = df[common_cols]
                
                # Combine with historical data
                combined_df = pd.concat([historical_df, df_aligned], ignore_index=True)
                combined_df = combined_df.sort_values('collection_datetime').reset_index(drop=True)
        else:
            combined_df = None
    else:
        combined_df = None
    
    if combined_df is not None and not combined_df.empty:
        
        print(f"✓ Combined with historical data: {combined_df.shape}")
        
        # Get currency columns (exclude metadata and time features)
        exclude_cols = ['timestamp', 'collection_datetime', 'base_currency', 
                       'api_date', 'time_last_updated', 'day_of_week', 
                       'day_of_month', 'month', 'quarter', 'year', 'hour']
        # Also exclude any existing feature columns (lag, rolling, etc.)
        exclude_cols.extend([col for col in combined_df.columns 
                            if any(x in col for x in ['_lag', '_rolling', '_pct_change'])])
        
        currency_columns = [col for col in combined_df.columns if col not in exclude_cols]
        
        # 3. Create lag features for major currencies (last 1, 7, 30 observations)
        major_currencies = ['EUR', 'GBP', 'JPY', 'CAD', 'AUD']
        available_major = [c for c in major_currencies if c in currency_columns]
        
        for currency in available_major:
            # Lag features
            combined_df[f'{currency}_lag1'] = combined_df[currency].shift(1)
            combined_df[f'{currency}_lag7'] = combined_df[currency].shift(7)
            
            # Rolling mean features
            combined_df[f'{currency}_rolling_mean_7'] = combined_df[currency].rolling(window=7, min_periods=1).mean()
            combined_df[f'{currency}_rolling_mean_30'] = combined_df[currency].rolling(window=30, min_periods=1).mean()
            
            # Rolling standard deviation (volatility)
            combined_df[f'{currency}_rolling_std_7'] = combined_df[currency].rolling(window=7, min_periods=1).std()
            combined_df[f'{currency}_rolling_std_30'] = combined_df[currency].rolling(window=30, min_periods=1).std()
            
            # Rate of change
            combined_df[f'{currency}_pct_change_1d'] = combined_df[currency].pct_change(1)
            combined_df[f'{currency}_pct_change_7d'] = combined_df[currency].pct_change(7)
        
        print(f"✓ Created lag and rolling features for {len(available_major)} major currencies")
        
        # Use only the latest row (current data) for final dataset
        df_final = combined_df.tail(1).copy()
        
    else:
        print("⚠ No historical data found - skipping lag/rolling features")
        df_final = df.copy()
        # Fill NaN values for first run
        df_final = df_final.fillna(0)
    
    # ========== Save Processed Data ==========
    processed_file_path = PROCESSED_DATA_DIR / "exchange_rates.csv"
    
    # Always read existing file first to check structure, then append or recreate
    if historical_file.exists():
        try:
            # Check if we can read the file properly
            test_read = pd.read_csv(processed_file_path, nrows=1)
            # Check if columns match
            if set(test_read.columns) == set(df_final.columns):
                # Structure matches, safe to append
                df_final.to_csv(processed_file_path, mode='a', header=False, index=False)
                print(f"✓ Appended to: {processed_file_path}")
            else:
                # Structure doesn't match - backup old file and create new
                backup_path = PROCESSED_DATA_DIR / f"exchange_rates_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                shutil.copy2(processed_file_path, backup_path)
                print(f"⚠ Column structure mismatch - backed up old file to {backup_path}")
                # Load all valid historical data and combine
                try:
                    try:
                        historical_all = pd.read_csv(processed_file_path, on_bad_lines='skip', engine='python', warn_bad_lines=False)
                    except TypeError:
                        historical_all = pd.read_csv(processed_file_path, error_bad_lines=False, warn_bad_lines=False, engine='python')
                    if not historical_all.empty and 'collection_datetime' in historical_all.columns:
                        historical_all['collection_datetime'] = pd.to_datetime(historical_all['collection_datetime'], errors='coerce')
                        historical_all = historical_all.dropna(subset=['collection_datetime'])
                        # Keep only common columns
                        common_cols = [col for col in df_final.columns if col in historical_all.columns]
                        if len(common_cols) > 5:
                            historical_all = historical_all[common_cols]
                            df_final_aligned = df_final[common_cols]
                            combined_all = pd.concat([historical_all, df_final_aligned], ignore_index=True)
                            combined_all = combined_all.sort_values('collection_datetime').reset_index(drop=True)
                            combined_all.to_csv(processed_file_path, index=False)
                            print(f"✓ Recreated file with aligned structure: {processed_file_path}")
                        else:
                            # Too incompatible, start fresh
                            df_final.to_csv(processed_file_path, index=False)
                            print(f"✓ Created new file (structure too incompatible): {processed_file_path}")
                    else:
                        df_final.to_csv(processed_file_path, index=False)
                        print(f"✓ Created new file: {processed_file_path}")
                except Exception as e:
                    print(f"⚠ Could not recover historical data: {str(e)}")
                    df_final.to_csv(processed_file_path, index=False)
                    print(f"✓ Created new file: {processed_file_path}")
        except Exception as e:
            print(f"⚠ Error checking file structure: {str(e)}")
            # Backup and create new
            try:
                backup_path = PROCESSED_DATA_DIR / f"exchange_rates_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                shutil.copy2(processed_file_path, backup_path)
                print(f"⚠ Backed up corrupted file to {backup_path}")
            except:
                pass
            df_final.to_csv(processed_file_path, index=False)
            print(f"✓ Created new file: {processed_file_path}")
    else:
        df_final.to_csv(processed_file_path, index=False)
        print(f"✓ Created new file: {processed_file_path}")
    
    print(f"✓ Final processed shape: {df_final.shape}")
    print(f"✓ Total features: {len(df_final.columns)}")
    
    # Push to XCom
    context['task_instance'].xcom_push(key='processed_data_path', value=str(processed_file_path))
    context['task_instance'].xcom_push(key='num_features', value=len(df_final.columns))
    
    return str(processed_file_path)


# ============================================================================
# TASK 4: GENERATE PANDAS PROFILING REPORT
# ============================================================================
def generate_profiling_report(**context):
    """
    Generate detailed data quality and feature summary report using Pandas Profiling.
    Log as artifact to MLflow (DagHub).
    """
    print("=" * 80)
    print("PHASE 1.4: PANDAS PROFILING REPORT GENERATION")
    print("=" * 80)
    
    # Get processed data path
    processed_data_path = context['task_instance'].xcom_pull(
        task_ids='transform_data',
        key='processed_data_path'
    )
    timestamp = context['task_instance'].xcom_pull(
        task_ids='extract_data',
        key='timestamp'
    )
    
    # Load processed data
    df = pd.read_csv(processed_data_path)
    print(f"✓ Loaded processed data: {df.shape}")
    
    # Generate profiling report
    print("\n--- Generating Profiling Report ---")
    print("This may take a few minutes...")
    
    profile = ProfileReport(
        df,
        title=f"Exchange Rate Data Quality Report - {timestamp}",
        minimal=True,  # Faster generation
        explorative=True
    )
    
    # Save report
    report_path = REPORTS_DIR / f"data_profile_{timestamp}.html"
    profile.to_file(report_path)
    print(f"✓ Report saved to: {report_path}")
    
    # ========== Log to MLflow (DagHub) ==========
    print("\n--- Logging to MLflow (DagHub) ---")
    
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        
        with mlflow.start_run(run_name=f"data_pipeline_{timestamp}"):
            # Log parameters
            mlflow.log_param("timestamp", timestamp)
            mlflow.log_param("num_rows", len(df))
            mlflow.log_param("num_features", len(df.columns))
            mlflow.log_param("base_currency", BASE_CURRENCY)
            
            # Log metrics
            quality_metrics = context['task_instance'].xcom_pull(
                task_ids='quality_check',
                key='quality_metrics'
            )
            if quality_metrics:
                mlflow.log_metrics(quality_metrics)
            
            # Log profiling report as artifact
            mlflow.log_artifact(str(report_path))
            
            print("✓ Logged to MLflow/DagHub successfully")
            
    except Exception as e:
        print(f"⚠ Warning: Could not log to MLflow: {str(e)}")
        print("Continuing without MLflow logging...")
    
    context['task_instance'].xcom_push(key='report_path', value=str(report_path))
    
    return str(report_path)


# ============================================================================
# TASK 5: DATA VERSIONING WITH DVC
# ============================================================================
def version_data_with_dvc(**context):
    """
    Version the processed dataset using DVC and push to remote storage (DagHub S3).
    """
    print("=" * 80)
    print("PHASE 1.5: DATA VERSIONING WITH DVC")
    print("=" * 80)
    
    processed_file = PROCESSED_DATA_DIR / "exchange_rates.csv"
    timestamp = context['task_instance'].xcom_pull(
        task_ids='extract_data',
        key='timestamp'
    )
    
    if not processed_file.exists():
        raise AirflowException(f"Processed file not found: {processed_file}")
    
    try:
        # Change to project directory
        os.chdir(BASE_DIR)
        
        # ========== DVC Add ==========
        print("\n--- Adding file to DVC ---")
        result = subprocess.run(
            ['dvc', 'add', str(processed_file)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✓ File added to DVC: {processed_file}")
            print(result.stdout)
        else:
            print(f"⚠ DVC add warning: {result.stderr}")
        
        # ========== DVC Push to Remote Storage ==========
        print("\n--- Pushing to remote storage (DagHub S3) ---")
        result = subprocess.run(
            ['dvc', 'push'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✓ Data pushed to remote storage successfully")
            print(result.stdout)
        else:
            print(f"⚠ DVC push warning: {result.stderr}")
        
        # ========== Git Add DVC Files ==========
        print("\n--- Committing DVC metadata to Git ---")
        dvc_file = f"{processed_file}.dvc"
        
        subprocess.run(['git', 'add', dvc_file], capture_output=True)
        subprocess.run(['git', 'add', '.gitignore'], capture_output=True)
        
        commit_message = f"Data version update - {timestamp}"
        result = subprocess.run(
            ['git', 'commit', '-m', commit_message],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✓ DVC metadata committed to Git")
            print(f"  Commit message: {commit_message}")
        else:
            print(f"⚠ Git commit info: {result.stderr}")
        
        print("\n✓✓✓ DATA VERSIONING COMPLETE ✓✓✓")
        
    except Exception as e:
        print(f"⚠ Warning: DVC operations encountered issues: {str(e)}")
        print("Data is saved but versioning may need manual intervention")
    
    return True


# ============================================================================
# DAG DEFINITION
# ============================================================================
default_args = {
    'owner': 'mlops_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id="exchange_rate_mlops_pipeline_phase1",
    default_args=default_args,
    description="Complete MLOps Phase 1: ETL Pipeline with Quality Checks, Feature Engineering, and DVC",
    schedule_interval="@daily",  # Run daily
    start_date=datetime(2025, 11, 1),
    catchup=False,
    tags=['mlops', 'phase1', 'etl', 'exchange-rate', 'dvc'],
) as dag:
    
    # Task 1: Extract Data
    task_extract = PythonOperator(
        task_id='extract_data',
        python_callable=extract_exchange_rate_data,
        provide_context=True,
    )
    
    # Task 2: Quality Check (Mandatory Gate)
    task_quality_check = PythonOperator(
        task_id='quality_check',
        python_callable=data_quality_check,
        provide_context=True,
    )
    
    # Task 3: Transform & Feature Engineering
    task_transform = PythonOperator(
        task_id='transform_data',
        python_callable=transform_and_engineer_features,
        provide_context=True,
    )
    
    # Task 4: Generate Profiling Report
    task_profiling = PythonOperator(
        task_id='generate_profiling_report',
        python_callable=generate_profiling_report,
        provide_context=True,
    )
    
    # Task 5: DVC Versioning
    task_dvc = PythonOperator(
        task_id='version_with_dvc',
        python_callable=version_data_with_dvc,
        provide_context=True,
    )
    
    # Define task dependencies (DAG flow)
    task_extract >> task_quality_check >> task_transform >> task_profiling >> task_dvc
