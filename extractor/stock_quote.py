from datetime import date

from .api_client import FinnhubClient
from .common import save_json
from .s3_manager import upload_file


ENDPOINT = "/quote"
ENDPOINT_NAME = "stock_quote"


def extract_stock_quote(symbol):
    client = FinnhubClient()

    params = {
        "symbol": symbol
    }

    data = client.get(
        ENDPOINT,
        params
    )

    if data is None:
        return None

    if not isinstance(data, dict):
        return {}

    if not data:
        return {}

    # Finnhub quote timestamp
    data["symbol"] = symbol

    local_file = save_json(
        ENDPOINT_NAME,
        data,
        params
    )

    today = date.today()

    timestamp = data.get("t")

    if timestamp:
        filename = (
            f"{ENDPOINT_NAME}_"
            f"{symbol}_"
            f"{timestamp}.json"
        )
    else:
        filename = (
            f"{ENDPOINT_NAME}_"
            f"{symbol}_"
            f"{today:%Y%m%d}.json"
        )

    s3_key = (
        f"raw/{today:%Y}/{today:%m}/{today:%d}/"
        f"{ENDPOINT_NAME}/{symbol}/"
        f"{filename}"
    )

    upload_file(
        local_file,
        s3_key
    )

    local_file.unlink(
        missing_ok=True
    )

    return data