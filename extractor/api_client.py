import os
import time
import logging
import requests
from dotenv import load_dotenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(
    PROJECT_ROOT / ".env"
)

logger = logging.getLogger(__name__)

BASE_URL = "https://finnhub.io/api/v1"

API_KEY = os.getenv("FINNHUB_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "FINNHUB_API_KEY is missing."
    )


class FinnhubAPIError(Exception):
    pass


class FinnhubClient:

    def __init__(
        self,
        timeout=30,
        max_retries=5,
        request_delay=0.5       
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.request_delay = request_delay


        self.session = requests.Session()

        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "Finnhub-Data-Pipeline/1.0"
        })

    def get(self, endpoint, params=None):

        params = params.copy() if params else {}
        params["token"] = API_KEY

        url = f"{BASE_URL}{endpoint}"

        for attempt in range(1, self.max_retries + 1):

            try:

                time.sleep(self.request_delay)

                response = self.session.get(
                    url,
                    params=params,
                    timeout=(
                        self.timeout,
                        self.timeout
                    )
                )

                status = response.status_code

                # =========================
                # SUCCESS
                # =========================

                if status == 200:

                    try:
                        return response.json()

                    except ValueError:

                        logger.warning(
                            "Invalid or empty JSON response "
                            "from %s. Skipping.",
                            endpoint
                        )

                        return None

                # =========================
                # INVALID API KEY
                # =========================

                if status == 401:

                    raise FinnhubAPIError(
                        "401 Unauthorized: "
                        "Finnhub API key is invalid."
                    )

                # =========================
                # PLAN RESTRICTION
                # =========================

                if status == 402:

                    logger.warning(
                        "402 Payment/Plan restriction: %s. "
                        "Skipping endpoint.",
                        endpoint
                    )

                    return None

                # =========================
                # FORBIDDEN
                # =========================

                if status == 403:

                    logger.warning(
                        "403 Forbidden: %s. "
                        "Access denied. Skipping endpoint.",
                        endpoint
                    )

                    return None

                # =========================
                # BAD REQUEST
                # =========================

                if status == 400:

                    logger.error(
                        "400 Bad Request: %s",
                        endpoint
                    )

                    return None

                # =========================
                # NOT FOUND
                # =========================

                if status == 404:

                    logger.error(
                        "404 Not Found: %s",
                        endpoint
                    )

                    return None

                # =========================
                # RATE LIMIT
                # =========================

                if status == 429:

                    wait_time = min(
                        60,
                        2 ** attempt
                    )

                    logger.warning(
                        "429 rate limit on %s. "
                        "Retry %s/%s in %s seconds.",
                        endpoint,
                        attempt,
                        self.max_retries,
                        wait_time
                    )

                    time.sleep(wait_time)
                    continue

                # =========================
                # SERVER ERRORS
                # =========================

                if status >= 500:

                    wait_time = min(
                        60,
                        2 ** attempt
                    )

                    logger.warning(
                        "Server error %s on %s. "
                        "Retry %s/%s in %s seconds.",
                        status,
                        endpoint,
                        attempt,
                        self.max_retries,
                        wait_time
                    )

                    time.sleep(wait_time)
                    continue

                # =========================
                # UNEXPECTED STATUS
                # =========================

                logger.error(
                    "Unexpected HTTP status %s from %s",
                    status,
                    endpoint
                )

                return None

            # =============================
            # TIMEOUT
            # =============================

            except requests.exceptions.Timeout:

                wait_time = min(
                    60,
                    2 ** attempt
                )

                logger.warning(
                    "Request timeout for %s. "
                    "Retry %s/%s in %s seconds.",
                    endpoint,
                    attempt,
                    self.max_retries,
                    wait_time
                )

                time.sleep(wait_time)

            # =============================
            # CONNECTION / SSL ERRORS
            # =============================

            except requests.exceptions.ConnectionError as exc:

                wait_time = min(
                    60,
                    2 ** attempt
                )

                logger.warning(
                    "Connection/SSL error for %s: %s. "
                    "Retry %s/%s in %s seconds.",
                    endpoint,
                    str(exc),
                    attempt,
                    self.max_retries,
                    wait_time
                )

                time.sleep(wait_time)

            # =============================
            # OTHER REQUEST ERRORS
            # =============================

            except requests.exceptions.RequestException as exc:

                logger.warning(
                    "Request error for %s: %s. "
                    "Skipping after this attempt.",
                    endpoint,
                    str(exc)
                )

                time.sleep(2)

        # =========================
        # ALL RETRIES FAILED
        # =========================

        logger.error(
            "All %s retries failed for %s. "
            "Skipping endpoint.",
            self.max_retries,
            endpoint
        )

        return None