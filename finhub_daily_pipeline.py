import sys
from datetime import datetime, timedelta

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook

PROJECT_PATH = "/mnt/c/finhub-pipeline"

if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)


from snowflake_silver import (
    load_stock_symbols,
    load_stock_quote,
    load_stock_profile,
    load_stock_peers,
    load_stock_earnings,
    load_company_news,
    load_earnings_calendar,
    load_ipo_calendar,
    load_market_status,
    load_market_holiday,
    load_forex_symbols,
    load_crypto_symbols,
    load_crypto_exchanges,
    load_general_news,
)

from snowflake_gold import (
    load_gold_dim_stock,
    load_gold_fact_stock_market,
    load_gold_fact_stock_earnings,
    load_gold_fact_earnings_calendar,
    load_gold_fact_news,
    load_gold_fact_stock_peer,
    load_gold_fact_ipo_calendar,
    load_gold_fact_market_status,
    load_gold_fact_market_holiday,
    load_gold_dim_crypto,
    load_gold_dim_forex,
    load_gold_dim_crypto_exchange,
)



# ============================================================
# EXTRACTION
# ============================================================

def run_finnhub_extraction():

    from run_extraction import main

    main()


# ============================================================
# BRONZE LOAD
# ============================================================

def run_bronze_load():

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

    print(
        "S3 → Bronze load completed successfully."
    )


# ============================================================
# DAG
# ============================================================

with DAG(
    dag_id="finhub_daily_pipeline",

    start_date=datetime(2026, 9, 30),

    schedule="0 2 * * *",

    catchup=False,

    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=10),
    },

    tags=[
        "finnhub",
        "extraction",
        "daily",
    ],

) as dag:

    # ========================================================
    # EXTRACTION TASK
    # ========================================================

    extraction_task = PythonOperator(
        task_id="finnhub_extraction",

        python_callable=run_finnhub_extraction,

        execution_timeout=timedelta(
            hours=6
        ),
    )


    # ========================================================
    # BRONZE TASK
    # ========================================================

    bronze_task = PythonOperator(
        task_id="load_bronze",

        python_callable=run_bronze_load,
    )


    # ========================================================
    # SILVER TASKS
    # ========================================================

    stock_symbols_task = PythonOperator(
        task_id="load_stock_symbols",
        python_callable=load_stock_symbols,
    )

    stock_quote_task = PythonOperator(
        task_id="load_stock_quote",
        python_callable=load_stock_quote,
    )

    stock_profile_task = PythonOperator(
        task_id="load_stock_profile",
        python_callable=load_stock_profile,
    )

    stock_peers_task = PythonOperator(
        task_id="load_stock_peers",
        python_callable=load_stock_peers,
    )

    stock_earnings_task = PythonOperator(
        task_id="load_stock_earnings",
        python_callable=load_stock_earnings,
    )

    company_news_task = PythonOperator(
        task_id="load_company_news",
        python_callable=load_company_news,
    )

    earnings_calendar_task = PythonOperator(
        task_id="load_earnings_calendar",
        python_callable=load_earnings_calendar,
    )

    ipo_calendar_task = PythonOperator(
        task_id="load_ipo_calendar",
        python_callable=load_ipo_calendar,
    )

    market_status_task = PythonOperator(
        task_id="load_market_status",
        python_callable=load_market_status,
    )

    market_holiday_task = PythonOperator(
        task_id="load_market_holiday",
        python_callable=load_market_holiday,
    )

    forex_symbols_task = PythonOperator(
        task_id="load_forex_symbols",
        python_callable=load_forex_symbols,
    )

    crypto_symbols_task = PythonOperator(
        task_id="load_crypto_symbols",
        python_callable=load_crypto_symbols,
    )

    crypto_exchanges_task = PythonOperator(
        task_id="load_crypto_exchanges",
        python_callable=load_crypto_exchanges,
    )

    general_news_task = PythonOperator(
        task_id="load_general_news",
        python_callable=load_general_news,
    )


    # ============================================================
    # GOLD
    # ============================================================

    gold_dim_stock_task = PythonOperator(
        task_id="gold_dim_stock",
        python_callable=load_gold_dim_stock,
    )

    gold_fact_stock_market_task = PythonOperator(
        task_id="gold_fact_stock_market",
        python_callable=load_gold_fact_stock_market,
    )

    gold_fact_stock_earnings_task = PythonOperator(
        task_id="gold_fact_stock_earnings",
        python_callable=load_gold_fact_stock_earnings,
    )

    gold_fact_earnings_calendar_task = PythonOperator(
        task_id="gold_fact_earnings_calendar",
        python_callable=load_gold_fact_earnings_calendar,
    )

    gold_fact_news_task = PythonOperator(
        task_id="gold_fact_news",
        python_callable=load_gold_fact_news,
    )

    gold_fact_stock_peer_task = PythonOperator(
        task_id="gold_fact_stock_peer",
        python_callable=load_gold_fact_stock_peer,
    )

    gold_fact_ipo_calendar_task = PythonOperator(
        task_id="gold_fact_ipo_calendar",
        python_callable=load_gold_fact_ipo_calendar,
    )

    gold_fact_market_status_task = PythonOperator(
        task_id="gold_fact_market_status",
        python_callable=load_gold_fact_market_status,
    )

    gold_fact_market_holiday_task = PythonOperator(
        task_id="gold_fact_market_holiday",
        python_callable=load_gold_fact_market_holiday,
    )

    gold_dim_crypto_task = PythonOperator(
        task_id="gold_dim_crypto",
        python_callable=load_gold_dim_crypto,
    )

    gold_dim_forex_task = PythonOperator(
        task_id="gold_dim_forex",
        python_callable=load_gold_dim_forex,
    )

    gold_dim_crypto_exchange_task = PythonOperator(
        task_id="gold_dim_crypto_exchange",
        python_callable=load_gold_dim_crypto_exchange,
    )



    # ========================================================
    # DEPENDENCIES
    # ========================================================

    # Extraction → Bronze
    extraction_task >> bronze_task


    # Bronze → Stock Symbols
    bronze_task >> stock_symbols_task


    # Stock Symbols → Stock-specific Silver tables
    stock_symbols_task >> [
        stock_quote_task,
        stock_profile_task,
        stock_peers_task,
        stock_earnings_task,
        company_news_task,
    ]


    # Bronze → Independent Silver tables
    bronze_task >> [
        earnings_calendar_task,
        ipo_calendar_task,
        market_status_task,
        market_holiday_task,
        forex_symbols_task,
        crypto_symbols_task,
        crypto_exchanges_task,
        general_news_task,
    ]

    # ============================================================
    # GOLD DEPENDENCIES
    # ============================================================

    # DIM_STOCK requires stock symbols + stock profile
    stock_symbols_task >> gold_dim_stock_task
    stock_profile_task >> gold_dim_stock_task

    # Stock-related facts require DIM_STOCK + their Silver source
    stock_quote_task >> gold_fact_stock_market_task
    gold_dim_stock_task >> gold_fact_stock_market_task

    stock_earnings_task >> gold_fact_stock_earnings_task
    gold_dim_stock_task >> gold_fact_stock_earnings_task

    earnings_calendar_task >> gold_fact_earnings_calendar_task
    gold_dim_stock_task >> gold_fact_earnings_calendar_task

    company_news_task >> gold_fact_news_task
    gold_dim_stock_task >> gold_fact_news_task

    stock_peers_task >> gold_fact_stock_peer_task
    gold_dim_stock_task >> gold_fact_stock_peer_task

    ipo_calendar_task >> gold_fact_ipo_calendar_task
    gold_dim_stock_task >> gold_fact_ipo_calendar_task

    # Independent Gold tables
    market_status_task >> gold_fact_market_status_task
    market_holiday_task >> gold_fact_market_holiday_task

    forex_symbols_task >> gold_dim_forex_task

    crypto_symbols_task >> gold_dim_crypto_task
    crypto_exchanges_task >> gold_dim_crypto_exchange_task