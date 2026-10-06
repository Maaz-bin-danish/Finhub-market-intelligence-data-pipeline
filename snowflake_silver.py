from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from datetime import datetime


def load_stock_quote():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    sql = """
    INSERT INTO FINHUB_DB.SILVER.STOCK_QUOTE (
        symbol,
        current_price,
        high_price,
        low_price,
        open_price,
        previous_close,
        quote_timestamp,
        extracted_at,
        source_file
    )
    SELECT
        b.raw_payload:request_parameters:symbol::STRING,
        b.raw_payload:data:c::NUMBER(18,6),
        b.raw_payload:data:h::NUMBER(18,6),
        b.raw_payload:data:l::NUMBER(18,6),
        b.raw_payload:data:o::NUMBER(18,6),
        b.raw_payload:data:pc::NUMBER(18,6),

        CASE
            WHEN TRY_TO_NUMBER(b.raw_payload:data:t::STRING) = 0
            THEN NULL
            ELSE TO_TIMESTAMP_TZ(
                TRY_TO_NUMBER(b.raw_payload:data:t::STRING)
            )
        END,

        b.raw_payload:extracted_at::TIMESTAMP_TZ,
        b.file_name

    FROM FINHUB_DB.BRONZE.FINHUB_RAW b

    INNER JOIN FINHUB_DB.SILVER.STOCK_SYMBOLS ss
        ON ss.SYMBOL = b.raw_payload:request_parameters:symbol::STRING

    WHERE b.raw_payload:endpoint::STRING = 'stock_quote'

      AND NOT EXISTS (
          SELECT 1
          FROM FINHUB_DB.SILVER.STOCK_QUOTE s
          WHERE s.source_file = b.file_name
      );
    """

    result = hook.run(sql)

    print("STOCK_QUOTE Silver load completed successfully.")
    print(f"Result: {result}")

def load_crypto_symbols():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    sql = """
    MERGE INTO FINHUB_DB.SILVER.CRYPTO_SYMBOLS AS target

    USING (
        SELECT
            b.raw_payload:request_parameters:exchange::STRING AS exchange_name,
            item.value:symbol::STRING AS symbol,
            item.value:displaySymbol::STRING AS display_symbol,
            item.value:description::STRING AS description,
            b.raw_payload:extracted_at::TIMESTAMP_TZ AS extracted_at,
            b.file_name AS source_file

        FROM FINHUB_DB.BRONZE.FINHUB_RAW b,

        LATERAL FLATTEN(
            INPUT => b.raw_payload:data
        ) item

        WHERE b.raw_payload:endpoint::STRING = 'crypto_symbols'

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY
                b.raw_payload:request_parameters:exchange::STRING,
                item.value:symbol::STRING
            ORDER BY
                b.raw_payload:extracted_at::TIMESTAMP_TZ DESC,
                b.file_name DESC
        ) = 1
    ) AS source

    ON target.exchange_name = source.exchange_name
    AND target.symbol = source.symbol

    WHEN MATCHED THEN
        UPDATE SET
            target.display_symbol = source.display_symbol,
            target.description = source.description,
            target.extracted_at = source.extracted_at,
            target.source_file = source.source_file

    WHEN NOT MATCHED THEN
        INSERT (
            exchange_name,
            symbol,
            display_symbol,
            description,
            extracted_at,
            source_file
        )
        VALUES (
            source.exchange_name,
            source.symbol,
            source.display_symbol,
            source.description,
            source.extracted_at,
            source.source_file
        );
    """

    result = hook.run(sql)

    print("CRYPTO_SYMBOLS Silver load completed successfully.")
    print(f"Result: {result}")

def load_crypto_exchanges():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    sql = """
    MERGE INTO FINHUB_DB.SILVER.CRYPTO_EXCHANGES AS target

    USING (
        SELECT
            item.value:name::STRING AS exchange_name,
            b.raw_payload:extracted_at::TIMESTAMP_TZ AS extracted_at,
            b.file_name AS source_file

        FROM FINHUB_DB.BRONZE.FINHUB_RAW b,

        LATERAL FLATTEN(
            INPUT => b.raw_payload:data
        ) item

        WHERE b.raw_payload:endpoint::STRING = 'crypto_exchanges'

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY item.value:name::STRING
            ORDER BY
                b.raw_payload:extracted_at::TIMESTAMP_TZ DESC,
                b.file_name DESC
        ) = 1
    ) AS source

    ON target.exchange_name = source.exchange_name

    WHEN MATCHED THEN
        UPDATE SET
            target.extracted_at = source.extracted_at,
            target.source_file = source.source_file

    WHEN NOT MATCHED THEN
        INSERT (
            exchange_name,
            extracted_at,
            source_file
        )
        VALUES (
            source.exchange_name,
            source.extracted_at,
            source.source_file
        );
    """

    result = hook.run(sql)

    print("CRYPTO_EXCHANGES Silver load completed successfully.")
    print(f"Result: {result}")

def load_general_news():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    sql = """
    MERGE INTO FINHUB_DB.SILVER.GENERAL_NEWS AS target

    USING (
        SELECT
            b.raw_payload:data:id::NUMBER AS news_id,
            b.raw_payload:data:category::STRING AS category,
            TO_TIMESTAMP_NTZ(
                b.raw_payload:data:datetime::NUMBER
            ) AS news_datetime,
            b.raw_payload:data:headline::STRING AS headline,
            b.raw_payload:data:image::STRING AS image,
            b.raw_payload:data:related::STRING AS related,
            b.raw_payload:data:source::STRING AS source,
            b.raw_payload:data:summary::STRING AS summary,
            b.raw_payload:data:url::STRING AS url,
            b.raw_payload:extracted_at::TIMESTAMP_TZ AS extracted_at,
            b.file_name AS source_file

        FROM FINHUB_DB.BRONZE.FINHUB_RAW b

        WHERE b.raw_payload:endpoint::STRING = 'general_news'

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY b.raw_payload:data:id::NUMBER
            ORDER BY
                b.raw_payload:extracted_at::TIMESTAMP_TZ DESC,
                b.file_name DESC
        ) = 1
    ) AS source

    ON target.news_id = source.news_id

    WHEN MATCHED THEN
        UPDATE SET
            target.category = source.category,
            target.news_datetime = source.news_datetime,
            target.headline = source.headline,
            target.image = source.image,
            target.related = source.related,
            target.source = source.source,
            target.summary = source.summary,
            target.url = source.url,
            target.extracted_at = source.extracted_at,
            target.source_file = source.source_file

    WHEN NOT MATCHED THEN
        INSERT (
            news_id,
            category,
            news_datetime,
            headline,
            image,
            related,
            source,
            summary,
            url,
            extracted_at,
            source_file
        )
        VALUES (
            source.news_id,
            source.category,
            source.news_datetime,
            source.headline,
            source.image,
            source.related,
            source.source,
            source.summary,
            source.url,
            source.extracted_at,
            source.source_file
        );
    """

    result = hook.run(sql)

    print("GENERAL_NEWS Silver load completed successfully.")
    print(f"Result: {result}")

def load_market_status():


    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    sql = """
    MERGE INTO FINHUB_DB.SILVER.MARKET_STATUS AS target

    USING (
        SELECT
            b.raw_payload:request_parameters:exchange::STRING AS exchange,
            b.raw_payload:data:holiday::STRING AS holiday,
            b.raw_payload:data:isOpen::BOOLEAN AS is_open,
            b.raw_payload:data:session::STRING AS session,

            CASE
                WHEN TRY_TO_NUMBER(b.raw_payload:data:t::STRING) = 0
                THEN NULL
                ELSE TO_TIMESTAMP_TZ(
                    TRY_TO_NUMBER(b.raw_payload:data:t::STRING)
                )
            END AS status_timestamp,

            b.raw_payload:data:timezone::STRING AS timezone,
            b.raw_payload:extracted_at::TIMESTAMP_TZ AS extracted_at,
            b.file_name AS source_file

        FROM FINHUB_DB.BRONZE.FINHUB_RAW b

        WHERE b.raw_payload:endpoint::STRING = 'market_status'

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY
                b.raw_payload:request_parameters:exchange::STRING
            ORDER BY
                b.raw_payload:extracted_at::TIMESTAMP_TZ DESC,
                b.file_name DESC
        ) = 1
    ) AS source

    ON target.exchange = source.exchange

    WHEN MATCHED THEN
        UPDATE SET
            target.holiday = source.holiday,
            target.is_open = source.is_open,
            target.session = source.session,
            target.status_timestamp = source.status_timestamp,
            target.timezone = source.timezone,
            target.extracted_at = source.extracted_at,
            target.source_file = source.source_file

    WHEN NOT MATCHED THEN
        INSERT (
            exchange,
            holiday,
            is_open,
            session,
            status_timestamp,
            timezone,
            extracted_at,
            source_file
        )
        VALUES (
            source.exchange,
            source.holiday,
            source.is_open,
            source.session,
            source.status_timestamp,
            source.timezone,
            source.extracted_at,
            source.source_file
        );
    """

    result = hook.run(sql)

    print("MARKET_STATUS Silver load completed successfully.")
    print(f"Result: {result}")
def load_market_holiday():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    sql = """
    MERGE INTO FINHUB_DB.SILVER.MARKET_HOLIDAY AS target

    USING (
        SELECT
            item.value:eventName::STRING AS event_name,
            item.value:atDate::DATE AS holiday_date,
            item.value:tradingHour::STRING AS trading_hour,
            b.raw_payload:extracted_at::TIMESTAMP_TZ AS extracted_at,
            b.file_name AS source_file

        FROM FINHUB_DB.BRONZE.FINHUB_RAW b,

        LATERAL FLATTEN(
            INPUT => b.raw_payload:data:data
        ) item

        WHERE b.raw_payload:endpoint::STRING = 'market_holiday'

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY
                item.value:eventName::STRING,
                item.value:atDate::DATE
            ORDER BY
                b.raw_payload:extracted_at::TIMESTAMP_TZ DESC,
                b.file_name DESC
        ) = 1
    ) AS source

    ON target.event_name = source.event_name
    AND target.holiday_date = source.holiday_date

    WHEN MATCHED THEN
        UPDATE SET
            target.trading_hour = source.trading_hour,
            target.extracted_at = source.extracted_at,
            target.source_file = source.source_file

    WHEN NOT MATCHED THEN
        INSERT (
            event_name,
            holiday_date,
            trading_hour,
            extracted_at,
            source_file
        )
        VALUES (
            source.event_name,
            source.holiday_date,
            source.trading_hour,
            source.extracted_at,
            source.source_file
        );
    """

    result = hook.run(sql)

    print("MARKET_HOLIDAY Silver load completed successfully.")
    print(f"Result: {result}")
def load_earnings_calendar():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    sql = """
    MERGE INTO FINHUB_DB.SILVER.EARNINGS_CALENDAR AS target

    USING (
        SELECT
            item.value:symbol::STRING AS symbol,
            item.value:date::DATE AS earnings_date,
            item.value:epsActual::NUMBER(18,6) AS eps_actual,
            item.value:epsEstimate::NUMBER(18,6) AS eps_estimate,
            item.value:hour::STRING AS earnings_hour,
            item.value:quarter::NUMBER AS quarter,
            item.value:revenueActual::NUMBER(20,2) AS revenue_actual,
            item.value:revenueEstimate::NUMBER(20,2) AS revenue_estimate,
            item.value:year::NUMBER AS year,
            b.raw_payload:extracted_at::TIMESTAMP_TZ AS extracted_at,
            b.file_name AS source_file

        FROM FINHUB_DB.BRONZE.FINHUB_RAW b,

        LATERAL FLATTEN(
            INPUT => b.raw_payload:data
        ) item

        WHERE b.raw_payload:endpoint::STRING = 'earnings_calendar'

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY
                item.value:symbol::STRING,
                item.value:date::DATE,
                item.value:year::NUMBER,
                item.value:quarter::NUMBER
            ORDER BY
                b.raw_payload:extracted_at::TIMESTAMP_TZ DESC,
                b.file_name DESC
        ) = 1
    ) AS source

    ON target.symbol = source.symbol
    AND target.earnings_date = source.earnings_date
    AND target.year = source.year
    AND target.quarter = source.quarter

    WHEN MATCHED THEN
        UPDATE SET
            target.eps_actual = source.eps_actual,
            target.eps_estimate = source.eps_estimate,
            target.earnings_hour = source.earnings_hour,
            target.revenue_actual = source.revenue_actual,
            target.revenue_estimate = source.revenue_estimate,
            target.extracted_at = source.extracted_at,
            target.source_file = source.source_file

    WHEN NOT MATCHED THEN
        INSERT (
            symbol,
            earnings_date,
            eps_actual,
            eps_estimate,
            earnings_hour,
            quarter,
            revenue_actual,
            revenue_estimate,
            year,
            extracted_at,
            source_file
        )
        VALUES (
            source.symbol,
            source.earnings_date,
            source.eps_actual,
            source.eps_estimate,
            source.earnings_hour,
            source.quarter,
            source.revenue_actual,
            source.revenue_estimate,
            source.year,
            source.extracted_at,
            source.source_file
        );
    """

    result = hook.run(sql)

    print("EARNINGS_CALENDAR Silver load completed successfully.")
    print(f"Result: {result}")

def load_ipo_calendar():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    sql = """
    MERGE INTO FINHUB_DB.SILVER.IPO_CALENDAR AS target

    USING (
        SELECT
            item.value:symbol::STRING AS symbol,
            item.value:date::DATE AS ipo_date,
            item.value:exchange::STRING AS exchange,
            item.value:name::STRING AS company_name,
            item.value:numberOfShares::NUMBER(20,2) AS number_of_shares,
            item.value:price::STRING AS ipo_price,
            item.value:status::STRING AS status,
            item.value:totalSharesValue::NUMBER(20,2) AS total_shares_value,
            b.raw_payload:extracted_at::TIMESTAMP_TZ AS extracted_at,
            b.file_name AS source_file

        FROM FINHUB_DB.BRONZE.FINHUB_RAW b,

        LATERAL FLATTEN(
            INPUT => b.raw_payload:data
        ) item

        WHERE b.raw_payload:endpoint::STRING = 'ipo_calendar'

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY
                item.value:name::STRING,
                item.value:date::DATE,
                item.value:status::STRING
            ORDER BY
                b.raw_payload:extracted_at::TIMESTAMP_TZ DESC,
                b.file_name DESC
        ) = 1
    ) AS source

    ON target.company_name = source.company_name
    AND target.ipo_date = source.ipo_date
    AND target.status = source.status

    WHEN MATCHED THEN
        UPDATE SET
            target.symbol = source.symbol,
            target.exchange = source.exchange,
            target.number_of_shares = source.number_of_shares,
            target.ipo_price = source.ipo_price,
            target.total_shares_value = source.total_shares_value,
            target.extracted_at = source.extracted_at,
            target.source_file = source.source_file

    WHEN NOT MATCHED THEN
        INSERT (
            symbol,
            ipo_date,
            exchange,
            company_name,
            number_of_shares,
            ipo_price,
            status,
            total_shares_value,
            extracted_at,
            source_file
        )
        VALUES (
            source.symbol,
            source.ipo_date,
            source.exchange,
            source.company_name,
            source.number_of_shares,
            source.ipo_price,
            source.status,
            source.total_shares_value,
            source.extracted_at,
            source.source_file
        );
    """

    result = hook.run(sql)

    print("IPO_CALENDAR Silver load completed successfully.")
    print(f"Result: {result}")

def load_stock_earnings():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    sql = """
    MERGE INTO FINHUB_DB.SILVER.STOCK_EARNINGS AS target

    USING (
        SELECT
            b.raw_payload:request_parameters:symbol::STRING AS symbol,
            item.value:actual::NUMBER(18,6) AS actual_eps,
            item.value:estimate::NUMBER(18,6) AS estimated_eps,
            item.value:period::DATE AS period,
            item.value:quarter::NUMBER AS quarter,
            item.value:surprise::NUMBER(18,6) AS surprise,
            item.value:surprisePercent::NUMBER(18,6) AS surprise_percent,
            item.value:year::NUMBER AS year,
            b.raw_payload:extracted_at::TIMESTAMP_TZ AS extracted_at,
            b.file_name AS source_file

        FROM FINHUB_DB.BRONZE.FINHUB_RAW b

        INNER JOIN FINHUB_DB.SILVER.STOCK_SYMBOLS ss
            ON ss.SYMBOL =
               b.raw_payload:request_parameters:symbol::STRING,

        LATERAL FLATTEN(
            INPUT => b.raw_payload:data
        ) item

        WHERE b.raw_payload:endpoint::STRING = 'stock_earnings'

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY
                b.raw_payload:request_parameters:symbol::STRING,
                item.value:period::DATE
            ORDER BY
                b.raw_payload:extracted_at::TIMESTAMP_TZ DESC,
                b.file_name DESC
        ) = 1
    ) AS source

    ON target.symbol = source.symbol
    AND target.period = source.period

    WHEN MATCHED THEN
        UPDATE SET
            target.actual_eps = source.actual_eps,
            target.estimated_eps = source.estimated_eps,
            target.quarter = source.quarter,
            target.surprise = source.surprise,
            target.surprise_percent = source.surprise_percent,
            target.year = source.year,
            target.extracted_at = source.extracted_at,
            target.source_file = source.source_file

    WHEN NOT MATCHED THEN
        INSERT (
            symbol,
            actual_eps,
            estimated_eps,
            period,
            quarter,
            surprise,
            surprise_percent,
            year,
            extracted_at,
            source_file
        )
        VALUES (
            source.symbol,
            source.actual_eps,
            source.estimated_eps,
            source.period,
            source.quarter,
            source.surprise,
            source.surprise_percent,
            source.year,
            source.extracted_at,
            source.source_file
        );
    """

    result = hook.run(sql)

    print("STOCK_EARNINGS Silver load completed successfully.")
    print(f"Result: {result}")

def load_stock_peers():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    sql = """
    MERGE INTO FINHUB_DB.SILVER.STOCK_PEERS AS target

    USING (
        SELECT
            b.raw_payload:request_parameters:symbol::STRING AS symbol,
            item.value::STRING AS peer_symbol,
            b.raw_payload:extracted_at::TIMESTAMP_TZ AS extracted_at,
            b.file_name AS source_file

        FROM FINHUB_DB.BRONZE.FINHUB_RAW b

        INNER JOIN FINHUB_DB.SILVER.STOCK_SYMBOLS ss
            ON ss.SYMBOL = b.raw_payload:request_parameters:symbol::STRING

        CROSS JOIN LATERAL FLATTEN(
            INPUT => b.raw_payload:data
        ) item

        WHERE b.raw_payload:endpoint::STRING = 'stock_peers'

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY
                b.raw_payload:request_parameters:symbol::STRING,
                item.value::STRING
            ORDER BY
                b.raw_payload:extracted_at::TIMESTAMP_TZ DESC,
                b.file_name DESC
        ) = 1
    ) AS source

    ON target.symbol = source.symbol
    AND target.peer_symbol = source.peer_symbol

    WHEN MATCHED THEN
        UPDATE SET
            target.extracted_at = source.extracted_at,
            target.source_file = source.source_file

    WHEN NOT MATCHED THEN
        INSERT (
            symbol,
            peer_symbol,
            extracted_at,
            source_file
        )
        VALUES (
            source.symbol,
            source.peer_symbol,
            source.extracted_at,
            source.source_file
        );
    """

    result = hook.run(sql)

    print("STOCK_PEERS Silver load completed successfully.")
    print(f"Result: {result}")

def load_stock_profile():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    sql = """
    MERGE INTO FINHUB_DB.SILVER.STOCK_PROFILE AS target

    USING (
        SELECT
            b.raw_payload:data:country::STRING AS country,
            b.raw_payload:data:currency::STRING AS currency,
            b.raw_payload:data:exchange::STRING AS exchange,
            b.raw_payload:data:ipo::DATE AS ipo,
            b.raw_payload:data:logo::STRING AS logo,
            b.raw_payload:data:marketCapitalization::NUMBER(18,4)
                AS market_capitalization,
            b.raw_payload:data:name::STRING AS company_name,
            b.raw_payload:data:shareOutstanding::NUMBER(18,4)
                AS share_outstanding,
            b.raw_payload:data:ticker::STRING AS ticker,
            b.raw_payload:data:weburl::STRING AS website_url,
            b.raw_payload:data:finnhubIndustry::STRING AS finnhub_industry,
            b.raw_payload:extracted_at::TIMESTAMP_TZ AS extracted_at,
            b.file_name AS source_file

        FROM FINHUB_DB.BRONZE.FINHUB_RAW b

            INNER JOIN FINHUB_DB.SILVER.STOCK_SYMBOLS ss
        ON ss.SYMBOL = b.raw_payload:request_parameters:symbol::STRING

        WHERE b.raw_payload:endpoint::STRING = 'stock_profile'

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY b.raw_payload:data:ticker::STRING
            ORDER BY
                b.raw_payload:extracted_at::TIMESTAMP_TZ DESC,
                b.file_name DESC
        ) = 1
    ) AS source

    ON target.ticker = source.ticker

    WHEN MATCHED THEN
        UPDATE SET
            target.country = source.country,
            target.currency = source.currency,
            target.exchange = source.exchange,
            target.ipo = source.ipo,
            target.logo = source.logo,
            target.market_capitalization = source.market_capitalization,
            target.company_name = source.company_name,
            target.share_outstanding = source.share_outstanding,
            target.website_url = source.website_url,
            target.finnhub_industry = source.finnhub_industry,
            target.extracted_at = source.extracted_at,
            target.source_file = source.source_file

    WHEN NOT MATCHED THEN
        INSERT (
            country,
            currency,
            exchange,
            ipo,
            logo,
            market_capitalization,
            company_name,
            share_outstanding,
            ticker,
            website_url,
            finnhub_industry,
            extracted_at,
            source_file
        )
        VALUES (
            source.country,
            source.currency,
            source.exchange,
            source.ipo,
            source.logo,
            source.market_capitalization,
            source.company_name,
            source.share_outstanding,
            source.ticker,
            source.website_url,
            source.finnhub_industry,
            source.extracted_at,
            source.source_file
        );
    """

    result = hook.run(sql)

    print("STOCK_PROFILE Silver load completed successfully.")
    print(f"Result: {result}")

def load_company_news():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    sql = """
    MERGE INTO FINHUB_DB.SILVER.COMPANY_NEWS AS target

    USING (
        SELECT
            item.value:category::STRING AS category,

            TO_TIMESTAMP_TZ(
                item.value:datetime::NUMBER
            ) AS news_timestamp,

            item.value:headline::STRING AS headline,
            item.value:id::NUMBER AS news_id,
            item.value:image::STRING AS image_url,
            item.value:related::STRING AS related,
            item.value:source::STRING AS source,
            item.value:summary::STRING AS summary,
            item.value:url::STRING AS news_url,

            b.raw_payload:request_parameters:symbol::STRING AS symbol,

            b.raw_payload:extracted_at::TIMESTAMP_TZ AS extracted_at,
            b.file_name AS source_file

        FROM FINHUB_DB.BRONZE.FINHUB_RAW b

        INNER JOIN FINHUB_DB.SILVER.STOCK_SYMBOLS ss
            ON ss.SYMBOL =
               b.raw_payload:request_parameters:symbol::STRING,

        LATERAL FLATTEN(
            INPUT => b.raw_payload:data
        ) item

        WHERE b.raw_payload:endpoint::STRING = 'company_news'

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY
                item.value:id::NUMBER,
                b.raw_payload:request_parameters:symbol::STRING
            ORDER BY
                b.raw_payload:extracted_at::TIMESTAMP_TZ DESC,
                b.file_name DESC
        ) = 1
    ) AS source

    ON target.news_id = source.news_id
    AND target.symbol = source.symbol

    WHEN MATCHED THEN
        UPDATE SET
            target.category = source.category,
            target.news_timestamp = source.news_timestamp,
            target.headline = source.headline,
            target.image_url = source.image_url,
            target.related = source.related,
            target.source = source.source,
            target.summary = source.summary,
            target.news_url = source.news_url,
            target.extracted_at = source.extracted_at,
            target.source_file = source.source_file

    WHEN NOT MATCHED THEN
        INSERT (
            category,
            news_timestamp,
            headline,
            news_id,
            image_url,
            related,
            source,
            summary,
            news_url,
            symbol,
            extracted_at,
            source_file
        )
        VALUES (
            source.category,
            source.news_timestamp,
            source.headline,
            source.news_id,
            source.image_url,
            source.related,
            source.source,
            source.summary,
            source.news_url,
            source.symbol,
            source.extracted_at,
            source.source_file
        );
    """

    result = hook.run(sql)

    print("COMPANY_NEWS Silver load completed successfully.")
    print(f"Result: {result}")

def load_forex_symbols():

    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    sql = """
    MERGE INTO FINHUB_DB.SILVER.FOREX_SYMBOLS AS target

    USING (
        SELECT
            item.value:description::STRING AS description,
            item.value:displaySymbol::STRING AS display_symbol,
            item.value:symbol::STRING AS symbol,
            b.raw_payload:extracted_at::TIMESTAMP_TZ AS extracted_at,
            b.file_name AS source_file

        FROM FINHUB_DB.BRONZE.FINHUB_RAW b,

        LATERAL FLATTEN(
            INPUT => b.raw_payload:data
        ) item

        WHERE b.raw_payload:endpoint::STRING = 'forex_symbols'

        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY item.value:symbol::STRING
            ORDER BY
                b.raw_payload:extracted_at::TIMESTAMP_TZ DESC,
                b.file_name DESC
        ) = 1
    ) AS source

    ON target.symbol = source.symbol

    WHEN MATCHED THEN
        UPDATE SET
            target.description = source.description,
            target.display_symbol = source.display_symbol,
            target.extracted_at = source.extracted_at,
            target.source_file = source.source_file

    WHEN NOT MATCHED THEN
        INSERT (
            description,
            display_symbol,
            symbol,
            extracted_at,
            source_file
        )
        VALUES (
            source.description,
            source.display_symbol,
            source.symbol,
            source.extracted_at,
            source.source_file
        );
    """

    result = hook.run(sql)

    print("FOREX_SYMBOLS Silver load completed successfully.")
    print(f"Result: {result}")

def load_stock_symbols():
    hook = SnowflakeHook(
        snowflake_conn_id="finhub_snowflake"
    )

    sql = """
    TRUNCATE TABLE FINHUB_DB.SILVER.STOCK_SYMBOLS;

    INSERT INTO FINHUB_DB.SILVER.STOCK_SYMBOLS
    (
        CURRENCY,
        DESCRIPTION,
        DISPLAY_SYMBOL,
        FIGI,
        FIGI_COMPOSITE,
        ISIN,
        MIC,
        SHARE_CLASS_FIGI,
        SYMBOL,
        SYMBOL2,
        TYPE,
        EXTRACTED_AT,
        SOURCE_FILE
    )
    SELECT
        NULL,
        NULL,
        item.value:symbol::STRING,
        NULL,
        NULL,
        NULL,
        NULL,
        NULL,
        item.value:symbol::STRING,
        NULL,
        NULL,
        raw_payload:extracted_at::TIMESTAMP_NTZ,
        file_name
    FROM FINHUB_DB.BRONZE.FINHUB_RAW,
    LATERAL FLATTEN(input => raw_payload:data) item
    WHERE raw_payload:endpoint::STRING = 'stock_symbol'
      AND file_name = (
          SELECT MAX(file_name)
          FROM FINHUB_DB.BRONZE.FINHUB_RAW
          WHERE raw_payload:endpoint::STRING = 'stock_symbol'
      );
    """

    hook.run(sql)

    print("STOCK_SYMBOLS Silver load completed successfully.")

