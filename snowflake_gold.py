from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook


def load_gold_dim_stock():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    hook.run("""
        CREATE OR REPLACE TABLE FINHUB_DB.GOLD.DIM_STOCK AS

        SELECT
            ROW_NUMBER() OVER (
                ORDER BY s.SYMBOL
            ) AS STOCK_KEY,

            s.SYMBOL,
            p.COMPANY_NAME,
            p.COUNTRY,
            p.CURRENCY,
            p.EXCHANGE,
            p.IPO AS IPO_DATE,
            p.MARKET_CAPITALIZATION,
            p.SHARE_OUTSTANDING,
            p.WEBSITE_URL,
            p.FINNHUB_INDUSTRY

        FROM FINHUB_DB.SILVER.STOCK_SYMBOLS s

        LEFT JOIN FINHUB_DB.SILVER.STOCK_PROFILE p
            ON s.SYMBOL = p.TICKER;
    """)

    print("Gold DIM_STOCK loaded successfully.")

def load_gold_fact_stock_market():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    hook.run("""
        CREATE OR REPLACE TABLE FINHUB_DB.GOLD.FACT_STOCK_MARKET AS

        SELECT
            ROW_NUMBER() OVER (
                ORDER BY q.SYMBOL, q.QUOTE_TIMESTAMP
            ) AS MARKET_KEY,

            d.STOCK_KEY,

            q.SYMBOL,
            TO_DATE(q.QUOTE_TIMESTAMP) AS QUOTE_DATE,
            q.QUOTE_TIMESTAMP,

            q.CURRENT_PRICE,
            q.HIGH_PRICE,
            q.LOW_PRICE,
            q.OPEN_PRICE,
            q.PREVIOUS_CLOSE,

            q.CURRENT_PRICE - q.PREVIOUS_CLOSE
                AS PRICE_CHANGE,

            CASE
                WHEN q.PREVIOUS_CLOSE IS NOT NULL
                     AND q.PREVIOUS_CLOSE <> 0
                THEN
                    (
                        (q.CURRENT_PRICE - q.PREVIOUS_CLOSE)
                        / q.PREVIOUS_CLOSE
                    ) * 100
            END AS PRICE_CHANGE_PCT,

            q.HIGH_PRICE - q.LOW_PRICE
                AS INTRADAY_RANGE

        FROM (
            SELECT *
            FROM FINHUB_DB.SILVER.STOCK_QUOTE

            WHERE QUOTE_TIMESTAMP IS NOT NULL
              AND CURRENT_PRICE > 0

            QUALIFY ROW_NUMBER() OVER (
                PARTITION BY SYMBOL, QUOTE_TIMESTAMP
                ORDER BY EXTRACTED_AT DESC
            ) = 1

        ) q

        INNER JOIN FINHUB_DB.GOLD.DIM_STOCK d
            ON q.SYMBOL = d.SYMBOL;
    """)

    print("Gold FACT_STOCK_MARKET loaded successfully.")

def load_gold_fact_stock_earnings():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    hook.run("""
        CREATE OR REPLACE TABLE FINHUB_DB.GOLD.FACT_STOCK_EARNINGS AS

        SELECT
            ROW_NUMBER() OVER (
                ORDER BY e.SYMBOL, e.PERIOD
            ) AS EARNINGS_KEY,

            d.STOCK_KEY,

            e.SYMBOL,
            e.PERIOD,
            e.YEAR,
            e.QUARTER,

            e.ACTUAL_EPS,
            e.ESTIMATED_EPS,

            e.SURPRISE AS EPS_SURPRISE,
            e.SURPRISE_PERCENT AS EPS_SURPRISE_PCT

        FROM FINHUB_DB.SILVER.STOCK_EARNINGS e

        INNER JOIN FINHUB_DB.GOLD.DIM_STOCK d
            ON e.SYMBOL = d.SYMBOL

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY e.SYMBOL, e.PERIOD
            ORDER BY e.EXTRACTED_AT DESC
        ) = 1;
    """)

    print("Gold FACT_STOCK_EARNINGS loaded successfully.")

def load_gold_fact_earnings_calendar():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    hook.run("""
        CREATE OR REPLACE TABLE FINHUB_DB.GOLD.FACT_EARNINGS_CALENDAR AS

        SELECT
            ROW_NUMBER() OVER (
                ORDER BY e.SYMBOL, e.EARNINGS_DATE, e.YEAR, e.QUARTER
            ) AS EARNINGS_CALENDAR_KEY,

            d.STOCK_KEY,

            e.SYMBOL,
            e.EARNINGS_DATE,
            e.EARNINGS_HOUR,
            e.YEAR,
            e.QUARTER,

            e.EPS_ACTUAL,
            e.EPS_ESTIMATE,

            e.EPS_ACTUAL - e.EPS_ESTIMATE
                AS EPS_SURPRISE,

            CASE
                WHEN e.EPS_ESTIMATE IS NOT NULL
                     AND e.EPS_ESTIMATE <> 0
                     AND e.EPS_ACTUAL IS NOT NULL
                THEN
                    (
                        (e.EPS_ACTUAL - e.EPS_ESTIMATE)
                        / ABS(e.EPS_ESTIMATE)
                    ) * 100
            END AS EPS_SURPRISE_PCT,

            e.REVENUE_ACTUAL,
            e.REVENUE_ESTIMATE,

            e.REVENUE_ACTUAL - e.REVENUE_ESTIMATE
                AS REVENUE_SURPRISE,

            CASE
                WHEN e.REVENUE_ESTIMATE IS NOT NULL
                     AND e.REVENUE_ESTIMATE <> 0
                     AND e.REVENUE_ACTUAL IS NOT NULL
                THEN
                    (
                        (e.REVENUE_ACTUAL - e.REVENUE_ESTIMATE)
                        / ABS(e.REVENUE_ESTIMATE)
                    ) * 100
            END AS REVENUE_SURPRISE_PCT

        FROM FINHUB_DB.SILVER.EARNINGS_CALENDAR e

        INNER JOIN FINHUB_DB.GOLD.DIM_STOCK d
            ON e.SYMBOL = d.SYMBOL;
    """)

    print("Gold FACT_EARNINGS_CALENDAR loaded successfully.")

def load_gold_fact_news():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    hook.run("""
        CREATE OR REPLACE TABLE FINHUB_DB.GOLD.FACT_NEWS AS

        SELECT
            ROW_NUMBER() OVER (
                ORDER BY n.SYMBOL, n.NEWS_TIMESTAMP, n.NEWS_ID
            ) AS NEWS_KEY,

            d.STOCK_KEY,

            n.SYMBOL,
            n.NEWS_ID,
            n.NEWS_TIMESTAMP,
            TO_DATE(n.NEWS_TIMESTAMP) AS NEWS_DATE,

            n.CATEGORY,
            n.SOURCE,
            n.HEADLINE,
            n.SUMMARY,
            n.NEWS_URL,
            n.IMAGE_URL,
            n.RELATED

        FROM FINHUB_DB.SILVER.COMPANY_NEWS n

        INNER JOIN FINHUB_DB.GOLD.DIM_STOCK d
            ON n.SYMBOL = d.SYMBOL

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY n.NEWS_ID
            ORDER BY n.EXTRACTED_AT DESC
        ) = 1;
    """)

    print("Gold FACT_NEWS loaded successfully.")

def load_gold_fact_stock_peer():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    hook.run("""
        CREATE OR REPLACE TABLE FINHUB_DB.GOLD.FACT_STOCK_PEER AS

        SELECT
            ROW_NUMBER() OVER (
                ORDER BY p.SYMBOL, EXTRACTED_PEER
            ) AS PEER_KEY,

            d1.STOCK_KEY,

            d2.STOCK_KEY AS PEER_STOCK_KEY,

            p.SYMBOL,

            EXTRACTED_PEER AS PEER_SYMBOL

        FROM (
            SELECT
                SYMBOL,
                TRY_PARSE_JSON(PEER_SYMBOL):peer::VARCHAR AS EXTRACTED_PEER,
                EXTRACTED_AT
            FROM FINHUB_DB.SILVER.STOCK_PEERS
        ) p

        INNER JOIN FINHUB_DB.GOLD.DIM_STOCK d1
            ON p.SYMBOL = d1.SYMBOL

        LEFT JOIN FINHUB_DB.GOLD.DIM_STOCK d2
            ON p.EXTRACTED_PEER = d2.SYMBOL

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY p.SYMBOL, p.EXTRACTED_PEER
            ORDER BY p.EXTRACTED_AT DESC
        ) = 1;
    """)

    print("Gold FACT_STOCK_PEER loaded successfully.")

def load_gold_fact_ipo_calendar():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    hook.run("""
        CREATE OR REPLACE TABLE FINHUB_DB.GOLD.FACT_IPO_CALENDAR AS

        SELECT
            ROW_NUMBER() OVER (
                ORDER BY i.SYMBOL, i.IPO_DATE
            ) AS IPO_KEY,

            d.STOCK_KEY,

            i.SYMBOL,
            i.COMPANY_NAME,
            i.IPO_DATE,
            i.EXCHANGE,
            i.NUMBER_OF_SHARES,
            i.IPO_PRICE,
            i.STATUS,
            i.TOTAL_SHARES_VALUE

        FROM FINHUB_DB.SILVER.IPO_CALENDAR i

        LEFT JOIN FINHUB_DB.GOLD.DIM_STOCK d
            ON i.SYMBOL = d.SYMBOL;
    """)

    print("Gold FACT_IPO_CALENDAR loaded successfully.")

def load_gold_fact_market_status():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    hook.run("""
        CREATE OR REPLACE TABLE FINHUB_DB.GOLD.FACT_MARKET_STATUS AS

        SELECT
            ROW_NUMBER() OVER (
                ORDER BY m.STATUS_TIMESTAMP
            ) AS MARKET_STATUS_KEY,

            m.EXCHANGE,
            m.IS_OPEN,
            m.SESSION,
            m.STATUS_TIMESTAMP,
            m.TIMEZONE,
            m.HOLIDAY

        FROM FINHUB_DB.SILVER.MARKET_STATUS m;
    """)

    print("Gold FACT_MARKET_STATUS loaded successfully.")

def load_gold_fact_market_holiday():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    hook.run("""
        CREATE OR REPLACE TABLE FINHUB_DB.GOLD.FACT_MARKET_HOLIDAY AS

        SELECT
            ROW_NUMBER() OVER (
                ORDER BY m.HOLIDAY_DATE, m.EVENT_NAME
            ) AS HOLIDAY_KEY,

            m.EVENT_NAME,
            m.HOLIDAY_DATE,
            m.TRADING_HOUR

        FROM FINHUB_DB.SILVER.MARKET_HOLIDAY m;
    """)

    print("Gold FACT_MARKET_HOLIDAY loaded successfully.")

def load_gold_dim_crypto():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    hook.run("""
        CREATE OR REPLACE TABLE FINHUB_DB.GOLD.DIM_CRYPTO AS

        SELECT
            ROW_NUMBER() OVER (
                ORDER BY c.EXCHANGE_NAME, c.SYMBOL
            ) AS CRYPTO_KEY,

            c.SYMBOL,
            c.DISPLAY_SYMBOL,
            c.DESCRIPTION,
            c.EXCHANGE_NAME

        FROM FINHUB_DB.SILVER.CRYPTO_SYMBOLS c;
    """)

    print("Gold DIM_CRYPTO loaded successfully.")

def load_gold_dim_forex():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    hook.run("""
        CREATE OR REPLACE TABLE FINHUB_DB.GOLD.DIM_FOREX AS

        SELECT
            ROW_NUMBER() OVER (
                ORDER BY f.SYMBOL
            ) AS FOREX_KEY,

            f.SYMBOL,
            f.DISPLAY_SYMBOL,
            f.DESCRIPTION

        FROM FINHUB_DB.SILVER.FOREX_SYMBOLS f;
    """)

    print("Gold DIM_FOREX loaded successfully.")

def load_gold_dim_crypto_exchange():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    hook.run("""
        CREATE OR REPLACE TABLE FINHUB_DB.GOLD.DIM_CRYPTO_EXCHANGE AS

        SELECT
            ROW_NUMBER() OVER (
                ORDER BY c.EXCHANGE_NAME
            ) AS EXCHANGE_KEY,

            c.EXCHANGE_NAME

        FROM FINHUB_DB.SILVER.CRYPTO_EXCHANGES c;
    """)

    print("Gold DIM_CRYPTO_EXCHANGE loaded successfully.")

