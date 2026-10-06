from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from datetime import datetime


def load_bronze():
    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    hook.run("""
        COPY INTO FINHUB_DB.BRONZE.FINHUB_RAW
        (
            raw_payload,
            file_name
        )
        FROM (
            SELECT
                $1,
                METADATA$FILENAME
            FROM @FINHUB_DB.PUBLIC.S3_FINHUB_STAGE
        )
        PATTERN = '.*[.]json';
    """)

    print("S3 → Bronze load completed successfully.")


with DAG(
    dag_id="finhub_bronze_load",
    start_date=datetime(2026, 9, 24),
    schedule=None,
    catchup=False,
    tags=["finnhub", "snowflake", "bronze"],
) as dag:

    load_bronze_task = PythonOperator(
        task_id="load_bronze",
        python_callable=load_bronze,
    )
