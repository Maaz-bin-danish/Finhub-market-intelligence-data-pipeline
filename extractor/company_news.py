from datetime import date, timedelta

from .api_client import FinnhubClient
from .common import save_json
from .s3_manager import upload_file
from .checkpoint_manager import (
    get_checkpoint,
    update_checkpoint
)
from .delta_utils import deduplicate_records


ENDPOINT = "/company-news"
ENDPOINT_NAME = "company_news"


def extract_company_news(symbol):
    client = FinnhubClient()

    today = date.today()

    default_from_date = (
        today - timedelta(days=30)
    )

    last_date = get_checkpoint(
        endpoint=ENDPOINT_NAME,
        key=symbol,
        default_value=str(default_from_date)
    )

    params = {
        "symbol": symbol,
        "from": last_date,
        "to": str(today)
    }

    data = client.get(
        ENDPOINT,
        params
    )

    if data is None:
        return None

    if not isinstance(data, list):
        return []

    # Remove duplicate news IDs
    data = deduplicate_records(
        data,
        key_fields=["id"]
    )

    if not data:
        update_checkpoint(
            endpoint=ENDPOINT_NAME,
            key=symbol,
            value=str(today)
        )
        return []

    local_file = save_json(
        endpoint_name=ENDPOINT_NAME,
        data=data,
        params=params
    )

    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")
    timestamp = local_file.stem.split("_")[-1]

    s3_key = (
        f"raw/{year}/{month}/{day}/"
        f"{ENDPOINT_NAME}/{symbol}/"
        f"{ENDPOINT_NAME}_{symbol}_{timestamp}.json"
    )

    upload_file(
        local_file=local_file,
        s3_key=s3_key
    )

    # Update checkpoint ONLY after successful S3 upload
    update_checkpoint(
        endpoint=ENDPOINT_NAME,
        key=symbol,
        value=str(today)
    )

    # Delete temporary local file
    local_file.unlink(
        missing_ok=True
    )

    return data