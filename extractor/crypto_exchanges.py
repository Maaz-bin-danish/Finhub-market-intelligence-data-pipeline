from .api_client import FinnhubClient
from .common import save_json
from .s3_manager import upload_and_cleanup


ENDPOINT = "/crypto/exchange"
ENDPOINT_NAME = "crypto_exchanges"


def extract_crypto_exchanges():

    client = FinnhubClient()

    data = client.get(
        ENDPOINT
    )

    if data is None:
        return None

    if not isinstance(data, list):
        return []

    params = {}

    local_file = save_json(
        endpoint_name=ENDPOINT_NAME,
        data=data,
        params=params
    )

    upload_and_cleanup(
        local_file=local_file,
        endpoint_name=ENDPOINT_NAME
    )

    return data