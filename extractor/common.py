import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path


logger = logging.getLogger(__name__)


RAW_DATA_DIR = Path(
    "data/raw"
)

RAW_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def create_request_hash(
    endpoint: str,
    params: dict
):
    raw = (
        endpoint
        + json.dumps(
            params,
            sort_keys=True
        )
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


def save_json(
    endpoint_name: str,
    data,
    params: dict
):
    """
    Save temporary extraction file locally.

    This file will later be uploaded
    to S3 and deleted.
    """

    extracted_at = datetime.now(
        timezone.utc
    )

    request_hash = create_request_hash(
        endpoint_name,
        params
    )

    payload = {
        "endpoint": endpoint_name,
        "request_parameters": params,
        "request_hash": request_hash,
        "extracted_at": extracted_at.isoformat(),
        "data": data
    }

    timestamp = extracted_at.strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"{endpoint_name}_"
        f"{timestamp}.json"
    )

    file_path = (
        RAW_DATA_DIR / filename
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            payload,
            file,
            ensure_ascii=False,
            indent=2
        )

    logger.info(
        "Temporary file created: %s",
        file_path
    )

    return file_path