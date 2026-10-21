"""Optional Airflow DAG. Requires a configured Astro/Airflow runtime."""
from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="people_counting_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 2 * * *",
    catchup=False,
) as dag:
    run_pipeline = BashOperator(
        task_id="run_dvc_pipeline",
        bash_command="cd /usr/local/airflow/ml_project && dvc repro",
    )
