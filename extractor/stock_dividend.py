from datetime import date

from .api_client import FinnhubClient
from .common import save_json
from .s3_manager import upload_file
from .delta_utils import deduplicate_records


ENDPOINT = "/stock/dividend"
ENDPOINT_NAME = "stock_dividend"


def extract_stock_dividend(symbol):
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

    if not isinstance(data, list):
        return []

    data = deduplicate_records(
        data,
        key_fields=[
            "symbol",
            "exDate"
        ]
    )

    if not data:
        return []

    local_file = save_json(
        ENDPOINT_NAME,
        data,
        params
    )

    today = date.today()

    s3_key = (
        f"raw/{today:%Y}/{today:%m}/{today:%d}/"
        f"{ENDPOINT_NAME}/{symbol}/"
        f"{ENDPOINT_NAME}_{symbol}_"
        f"{today:%Y%m%d}.json"
    )

    upload_file(
        local_file,
        s3_key
    )

    local_file.unlink(
        missing_ok=True
    )

    return data