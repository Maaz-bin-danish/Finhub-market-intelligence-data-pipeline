from .api_client import FinnhubClient
from .common import save_json


ENDPOINT = "/forex/rates"


def extract_forex_rates(
    base="USD"
):

    client = FinnhubClient()

    params = {
        "base": base
    }

    data = client.get(
    ENDPOINT,
    params
    )

    if data is None:
        return None

    save_json(
        "forex_rates",
        data,
        params
    )

    return data