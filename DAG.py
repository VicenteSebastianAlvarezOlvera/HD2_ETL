
import sys
import os

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Add the directory containing quotaTracker.py to PYTHONPATH
sys.path.append('/home/vicente/Syno projects/HD2/HD2_ETL')

from adding_data import get_HD2_data  # Import your function after modifying PYTHONPATH

default_args = {
    'owner': 'val@synoint.com',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=20),
}

dag = DAG(
    'Helldivers_2_DAG',
    default_args=default_args,
    description='Will make a get request to the helldivers 2 API every 10 minutes',
    schedule_interval=timedelta(minutes=10),
    start_date=datetime(2024, 10, 7, 9, 28, 48),
    catchup=False,
)

run_notebook = PythonOperator(
    task_id='run_python_script_to_get_and_store_HD2_data',
    python_callable=get_HD2_data,
    dag=dag
)

run_notebook
