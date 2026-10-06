# ============================================================
# FINHUB DASHBOARD — SNOWFLAKE GOLD QUERIES
# ============================================================


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

OVERVIEW_KPIS = """
SELECT
    (SELECT COUNT(*) FROM FINHUB_DB.GOLD.DIM_STOCK) AS STOCKS_COVERED,
    (SELECT COUNT(*) FROM FINHUB_DB.GOLD.FACT_STOCK_MARKET) AS MARKET_DATA_POINTS,
    (SELECT COUNT(*) FROM FINHUB_DB.GOLD.FACT_NEWS) AS NEWS_ARTICLES,
    (SELECT COUNT(*) FROM FINHUB_DB.GOLD.DIM_CRYPTO) AS CRYPTO_ASSETS,
    (SELECT COUNT(*) FROM FINHUB_DB.GOLD.DIM_FOREX) AS FOREX_PAIRS
"""


# ============================================================
# MARKET OVERVIEW
# ============================================================
MARKET_MOVERS = """
WITH latest_quotes AS (
    SELECT
        SYMBOL,
        CURRENT_PRICE,
        PRICE_CHANGE,
        PRICE_CHANGE_PCT,
        HIGH_PRICE,
        LOW_PRICE,
        OPEN_PRICE,
        PREVIOUS_CLOSE,
        INTRADAY_RANGE,
        QUOTE_TIMESTAMP,
        ROW_NUMBER() OVER (
            PARTITION BY SYMBOL
            ORDER BY QUOTE_TIMESTAMP DESC
        ) AS RN
    FROM FINHUB_DB.GOLD.FACT_STOCK_MARKET
    WHERE CURRENT_PRICE IS NOT NULL
)
SELECT
    SYMBOL,
    CURRENT_PRICE,
    PRICE_CHANGE,
    PRICE_CHANGE_PCT,
    HIGH_PRICE,
    LOW_PRICE,
    OPEN_PRICE,
    PREVIOUS_CLOSE,
    INTRADAY_RANGE,
    QUOTE_TIMESTAMP
FROM latest_quotes
WHERE RN = 1
ORDER BY QUOTE_TIMESTAMP DESC
"""

# ============================================================
# STOCKS
# ============================================================

STOCK_LIST = """
SELECT
    SYMBOL,
    COMPANY_NAME,
    EXCHANGE,
    CURRENCY,
    COUNTRY
FROM FINHUB_DB.GOLD.DIM_STOCK
ORDER BY SYMBOL
"""


STOCK_DETAIL = """
SELECT
    s.SYMBOL,
    s.COMPANY_NAME,
    s.EXCHANGE,
    s.CURRENCY,
    s.COUNTRY,
    m.CURRENT_PRICE,
    m.PRICE_CHANGE,
    m.PRICE_CHANGE_PCT,
    m.OPEN_PRICE,
    m.PREVIOUS_CLOSE,
    m.HIGH_PRICE,
    m.LOW_PRICE,
    m.INTRADAY_RANGE,
    m.QUOTE_TIMESTAMP
FROM FINHUB_DB.GOLD.DIM_STOCK s
LEFT JOIN FINHUB_DB.GOLD.FACT_STOCK_MARKET m
    ON s.SYMBOL = m.SYMBOL
WHERE s.SYMBOL = %s
ORDER BY m.QUOTE_TIMESTAMP DESC
LIMIT 1
"""


STOCK_PRICE_HISTORY = """
SELECT
    SYMBOL,
    QUOTE_DATE,
    QUOTE_TIMESTAMP,
    CURRENT_PRICE,
    OPEN_PRICE,
    HIGH_PRICE,
    LOW_PRICE,
    PREVIOUS_CLOSE,
    PRICE_CHANGE,
    PRICE_CHANGE_PCT,
    INTRADAY_RANGE
FROM FINHUB_DB.GOLD.FACT_STOCK_MARKET
WHERE SYMBOL = %s
ORDER BY QUOTE_TIMESTAMP
"""


# ============================================================
# STOCK NEWS
# ============================================================

STOCK_NEWS = """
SELECT
    SYMBOL,
    HEADLINE,
    SOURCE,
    NEWS_TIMESTAMP,
    NEWS_URL
FROM FINHUB_DB.GOLD.FACT_NEWS
WHERE SYMBOL = %s
ORDER BY NEWS_TIMESTAMP DESC
LIMIT 10
"""


# ============================================================
# STOCK EARNINGS
# ============================================================

STOCK_EARNINGS = """
SELECT
    SYMBOL,
    PERIOD,
    YEAR,
    QUARTER,
    ACTUAL_EPS,
    ESTIMATED_EPS,
    EPS_SURPRISE,
    EPS_SURPRISE_PCT
FROM FINHUB_DB.GOLD.FACT_STOCK_EARNINGS
WHERE SYMBOL = %s
ORDER BY PERIOD DESC
LIMIT 8
"""


# ============================================================
# STOCK PEERS
# ============================================================

STOCK_PEERS = """
SELECT
    p.SYMBOL AS STOCK_SYMBOL,
    p.PEER_SYMBOL,
    m.CURRENT_PRICE,
    m.PRICE_CHANGE,
    m.PRICE_CHANGE_PCT,
    m.OPEN_PRICE,
    m.PREVIOUS_CLOSE,
    m.HIGH_PRICE,
    m.LOW_PRICE,
    m.INTRADAY_RANGE,
    m.QUOTE_TIMESTAMP
FROM FINHUB_DB.GOLD.FACT_STOCK_PEER p
LEFT JOIN (
    SELECT *
    FROM FINHUB_DB.GOLD.FACT_STOCK_MARKET
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY SYMBOL
        ORDER BY QUOTE_TIMESTAMP DESC
    ) = 1
) m
    ON p.PEER_SYMBOL = m.SYMBOL
WHERE p.SYMBOL = %s
ORDER BY
    CASE WHEN m.CURRENT_PRICE IS NULL THEN 1 ELSE 0 END,
    ABS(m.PRICE_CHANGE_PCT) DESC NULLS LAST,
    p.PEER_SYMBOL
LIMIT 10
"""


# ============================================================
# EARNINGS & EVENTS
# ============================================================

EARNINGS_CALENDAR = """
SELECT
    SYMBOL,
    EARNINGS_DATE,
    EARNINGS_HOUR,
    YEAR,
    QUARTER,
    EPS_ACTUAL,
    EPS_ESTIMATE,
    EPS_SURPRISE,
    EPS_SURPRISE_PCT,
    REVENUE_ACTUAL,
    REVENUE_ESTIMATE,
    REVENUE_SURPRISE,
    REVENUE_SURPRISE_PCT
FROM FINHUB_DB.GOLD.FACT_EARNINGS_CALENDAR
ORDER BY EARNINGS_DATE DESC
LIMIT 20
"""


IPO_CALENDAR = """
SELECT
    SYMBOL,
    COMPANY_NAME,
    IPO_DATE,
    EXCHANGE,
    NUMBER_OF_SHARES,
    IPO_PRICE,
    STATUS,
    TOTAL_SHARES_VALUE
FROM FINHUB_DB.GOLD.FACT_IPO_CALENDAR
ORDER BY IPO_DATE DESC
LIMIT 20
"""


# ============================================================
# NEWS
# ============================================================

LATEST_NEWS = """
SELECT
    SYMBOL,
    HEADLINE,
    SOURCE,
    NEWS_TIMESTAMP,
    NEWS_URL
FROM FINHUB_DB.GOLD.FACT_NEWS
ORDER BY NEWS_TIMESTAMP DESC
LIMIT 50
"""


NEWS_BY_SYMBOL = """
SELECT
    SYMBOL,
    HEADLINE,
    SOURCE,
    NEWS_TIMESTAMP,
    NEWS_URL
FROM FINHUB_DB.GOLD.FACT_NEWS
WHERE SYMBOL = %s
ORDER BY NEWS_TIMESTAMP DESC
LIMIT 30
"""


# ============================================================
# CRYPTO
# ============================================================

CRYPTO_OVERVIEW = """
SELECT
    COUNT(*) AS TOTAL_CRYPTO_ASSETS
FROM FINHUB_DB.GOLD.DIM_CRYPTO
"""


CRYPTO_ASSETS = """
SELECT *
FROM FINHUB_DB.GOLD.DIM_CRYPTO
ORDER BY SYMBOL
LIMIT 100
"""


CRYPTO_EXCHANGES = """
SELECT *
FROM FINHUB_DB.GOLD.DIM_CRYPTO_EXCHANGE
ORDER BY EXCHANGE_NAME
"""


# ============================================================
# FOREX
# ============================================================

# NOTE:
# Finnhub /forex/rates returned 403 in this pipeline.
# Therefore this dashboard only shows available Forex
# symbol coverage, not fabricated exchange rates.

FOREX_PAIRS = """
SELECT *
FROM FINHUB_DB.GOLD.DIM_FOREX
ORDER BY SYMBOL
"""


# ============================================================
# MARKET STATUS
# ============================================================

MARKET_STATUS = """
SELECT *
FROM FINHUB_DB.GOLD.FACT_MARKET_STATUS
LIMIT 1
"""


# ============================================================
# MARKET HOLIDAYS
# ============================================================

MARKET_HOLIDAYS = """
SELECT
    EVENT_NAME,
    HOLIDAY_DATE,
    TRADING_HOUR
FROM FINHUB_DB.GOLD.FACT_MARKET_HOLIDAY
ORDER BY HOLIDAY_DATE
"""