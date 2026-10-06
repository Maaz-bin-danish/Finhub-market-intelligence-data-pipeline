from .api_client import FinnhubClient
from .common import save_json
from .s3_manager import upload_and_cleanup


ENDPOINT = "/stock/market-holiday"
ENDPOINT_NAME = "market_holiday"


def extract_market_holiday(exchange="US"):

    client = FinnhubClient()

    params = {
        "exchange": exchange
    }

    data = client.get(
        ENDPOINT,
        params
    )

    if data is None:
        return None

    local_file = save_json(
        endpoint_name=ENDPOINT_NAME,
        data=data,
        params=params
    )

    upload_and_cleanup(
        local_file=local_file,
        endpoint_name=ENDPOINT_NAME,
        identifier=exchange
    )

    return data