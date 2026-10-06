import logging
import time

from config import STOCK_SYMBOLS

from extractor.api_client import FinnhubAPIError

from extractor.stock_symbol import extract_stock_symbols
from extractor.stock_quote import extract_stock_quote
from extractor.stock_profile import extract_stock_profile
from extractor.stock_peers import extract_stock_peers
from extractor.company_news import extract_company_news
from extractor.stock_earnings import extract_stock_earnings
from extractor.earnings_calendar import extract_earnings_calendar
from extractor.ipo_calendar import extract_ipo_calendar
from extractor.market_status import extract_market_status
from extractor.market_holiday import extract_market_holiday
from extractor.forex_symbols import extract_forex_symbols
from extractor.forex_rates import extract_forex_rates
from extractor.crypto_exchanges import extract_crypto_exchanges
from extractor.crypto_symbols import extract_crypto_symbols
from extractor.general_news import extract_general_news


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    )
)

logger = logging.getLogger(__name__)


BATCH_SIZE = 10
BATCH_DELAY = 10


def run_endpoint(endpoint_name, function, *args, **kwargs):
    """
    Run one endpoint safely.

    Returns:
        True  = successful extraction
        False = failed extraction
    """

    try:
        result = function(*args, **kwargs)

        if result is None:
            logger.warning(
                "Endpoint returned no data: %s",
                endpoint_name
            )
            return False

        logger.info(
            "Endpoint completed: %s",
            endpoint_name
        )

        return True

    except FinnhubAPIError as exc:
        logger.error(
            "Finnhub error in %s: %s",
            endpoint_name,
            exc
        )
        return False

    except Exception as exc:
        logger.exception(
            "Unexpected error in %s: %s",
            endpoint_name,
            exc
        )
        return False


def main():

    logger.info("====================================")
    logger.info("FINNHUB EXTRACTION STARTED")
    logger.info("====================================")

    symbols = STOCK_SYMBOLS

    logger.info(
        "Using fixed stock universe: %s symbols",
        len(symbols)
    )

    failed_endpoints = []
    failed_stock_extractions = []

    # ==========================================
    # 1. STOCK SYMBOL SNAPSHOT
    # ==========================================

    if not run_endpoint(
        "stock_symbol",
        extract_stock_symbols
    ):
        failed_endpoints.append("stock_symbol")

    # ==========================================
    # 2. MARKET DATA
    # ==========================================

    if not run_endpoint(
        "market_status",
        extract_market_status,
        exchange="US"
    ):
        failed_endpoints.append("market_status")

    if not run_endpoint(
        "market_holiday",
        extract_market_holiday,
        exchange="US"
    ):
        failed_endpoints.append("market_holiday")

    # ==========================================
    # 3. GLOBAL CALENDARS
    # ==========================================

    if not run_endpoint(
        "earnings_calendar",
        extract_earnings_calendar
    ):
        failed_endpoints.append("earnings_calendar")

    if not run_endpoint(
        "ipo_calendar",
        extract_ipo_calendar
    ):
        failed_endpoints.append("ipo_calendar")

    # ==========================================
    # 4. FOREX
    # ==========================================

    if not run_endpoint(
        "forex_symbols",
        extract_forex_symbols,
        exchange="oanda"
    ):
        failed_endpoints.append("forex_symbols")

    if not run_endpoint(
        "forex_rates",
        extract_forex_rates,
        base="USD"
    ):
        logger.warning(
            "Forex rates unavailable or restricted."
        )

    # ==========================================
    # 5. CRYPTO
    # ==========================================

    crypto_exchanges = None

    try:

        crypto_exchanges = extract_crypto_exchanges()

        if crypto_exchanges is None:
            failed_endpoints.append(
                "crypto_exchanges"
            )

        else:

            logger.info(
                "Crypto exchanges discovered: %s",
                len(crypto_exchanges)
            )

            for exchange in crypto_exchanges:

                run_endpoint(
                    f"crypto_symbols:{exchange}",
                    extract_crypto_symbols,
                    exchange=exchange
                )

    except Exception as exc:

        logger.exception(
            "Crypto extraction failed: %s",
            exc
        )

        failed_endpoints.append(
            "crypto_exchanges"
        )

    # ==========================================
    # 6. GENERAL NEWS
    # ==========================================

    if not run_endpoint(
        "general_news",
        extract_general_news,
        category="general"
    ):
        failed_endpoints.append("general_news")

    # ==========================================
    # 7. STOCK-LEVEL EXTRACTION
    # ==========================================

    logger.info(
        "Starting extraction for %s symbols...",
        len(symbols)
    )

    total_symbols = len(symbols)
    successful_symbols = 0
    failed_symbols = 0

    for index, symbol in enumerate(
        symbols,
        start=1
    ):

        logger.info(
            "===================================="
        )

        logger.info(
            "Stock %s/%s: %s",
            index,
            total_symbols,
            symbol
        )

        symbol_failed = False

        # --------------------------------------
        # PROFILE
        # --------------------------------------

        if not run_endpoint(
            f"stock_profile:{symbol}",
            extract_stock_profile,
            symbol
        ):
            symbol_failed = True

        # --------------------------------------
        # PEERS
        # --------------------------------------

        if not run_endpoint(
            f"stock_peers:{symbol}",
            extract_stock_peers,
            symbol
        ):
            symbol_failed = True

        # --------------------------------------
        # EARNINGS
        # --------------------------------------

        if not run_endpoint(
            f"stock_earnings:{symbol}",
            extract_stock_earnings,
            symbol
        ):
            symbol_failed = True

        # --------------------------------------
        # QUOTE
        # --------------------------------------

        if not run_endpoint(
            f"stock_quote:{symbol}",
            extract_stock_quote,
            symbol
        ):
            symbol_failed = True

        # --------------------------------------
        # COMPANY NEWS
        # --------------------------------------

        if not run_endpoint(
            f"company_news:{symbol}",
            extract_company_news,
            symbol
        ):
            symbol_failed = True

        if symbol_failed:

            failed_symbols += 1

            failed_stock_extractions.append(
                symbol
            )

            logger.warning(
                "Symbol completed with failures: %s",
                symbol
            )

        else:

            successful_symbols += 1

            logger.info(
                "Symbol completed successfully: %s",
                symbol
            )

        # ======================================
        # BATCH DELAY
        # ======================================

        if index % BATCH_SIZE == 0 and index < total_symbols:

            logger.info(
                "Completed %s/%s symbols.",
                index,
                total_symbols
            )

            logger.info(
                "Batch pause: waiting %s seconds...",
                BATCH_DELAY
            )

            time.sleep(BATCH_DELAY)

    # ==========================================
    # FINAL SUMMARY
    # ==========================================

    logger.info("====================================")
    logger.info("FINNHUB EXTRACTION SUMMARY")
    logger.info("====================================")

    logger.info(
        "Total symbols: %s",
        total_symbols
    )

    logger.info(
        "Successful symbols: %s",
        successful_symbols
    )

    logger.info(
        "Symbols with failures: %s",
        failed_symbols
    )

    if failed_stock_extractions:

        logger.warning(
            "Failed symbols: %s",
            ", ".join(failed_stock_extractions)
        )

    if failed_endpoints:

        logger.warning(
            "Failed global endpoints: %s",
            ", ".join(failed_endpoints)
        )

    logger.info("====================================")
    logger.info("FINNHUB EXTRACTION COMPLETED")
    logger.info("====================================")


if __name__ == "__main__":
    main()