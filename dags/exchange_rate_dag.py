from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import pandas as pd

def fetch_exchange_rate():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    data = requests.get(url).json()
    df = pd.DataFrame([data])
    print(df)

with DAG(
    dag_id="exchange_rate_dag",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:

    task_fetch = PythonOperator(
        task_id="fetch_exchange_rate",
        python_callable=fetch_exchange_rate
    )
