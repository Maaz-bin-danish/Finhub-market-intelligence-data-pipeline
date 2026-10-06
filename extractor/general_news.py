from .api_client import FinnhubClient
from .common import save_json
from .s3_manager import upload_and_cleanup


ENDPOINT = "/news"
ENDPOINT_NAME = "general_news"


def extract_general_news(category="general"):

    client = FinnhubClient()

    params = {
        "category": category
    }

    data = client.get(
        ENDPOINT,
        params
    )

    if data is None:
        return None

    if not isinstance(data, list):
        return []

    local_file = save_json(
        endpoint_name=ENDPOINT_NAME,
        data=data,
        params=params
    )

    upload_and_cleanup(
        local_file=local_file,
        endpoint_name=ENDPOINT_NAME,
        identifier=category
    )

    return data