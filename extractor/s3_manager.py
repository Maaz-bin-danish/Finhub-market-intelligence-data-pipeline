import json
import logging
from datetime import date
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv
import os


load_dotenv()

logger = logging.getLogger(__name__)


AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")


if not AWS_REGION:
    raise RuntimeError(
        "AWS_REGION is missing from .env"
    )

if not S3_BUCKET:
    raise RuntimeError(
        "S3_BUCKET is missing from .env"
    )


s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION
)


def upload_file(
    local_file: Path,
    s3_key: str
):
    """
    Upload a local file to S3.
    """

    if not local_file.exists():
        raise FileNotFoundError(
            f"File not found: {local_file}"
        )

    try:

        s3_client.upload_file(
            str(local_file),
            S3_BUCKET,
            s3_key
        )

        logger.info(
            "Uploaded to S3: s3://%s/%s",
            S3_BUCKET,
            s3_key
        )

        return True

    except ClientError as exc:

        logger.error(
            "S3 upload failed: %s",
            exc
        )

        raise


def upload_and_cleanup(
    local_file: Path,
    endpoint_name: str,
    identifier: str = None
):
    """
    Upload temporary local JSON to S3
    and delete the local file after successful upload.
    """

    today = date.today()

    timestamp = local_file.stem.split("_")[-1]

    if identifier:
        filename = (
            f"{endpoint_name}_{identifier}_{timestamp}.json"
        )
    else:
        filename = (
            f"{endpoint_name}_{timestamp}.json"
        )

    if identifier:
        s3_key = (
            f"raw/{today:%Y}/{today:%m}/{today:%d}/"
            f"{endpoint_name}/{identifier}/{filename}"
        )
    else:
        s3_key = (
            f"raw/{today:%Y}/{today:%m}/{today:%d}/"
            f"{endpoint_name}/{filename}"
        )

    upload_file(
        local_file=local_file,
        s3_key=s3_key
    )

    local_file.unlink(
        missing_ok=True
    )

    logger.info(
        "Temporary local file deleted: %s",
        local_file
    )

    return s3_key


def save_json(
    data,
    s3_key: str
):
    """
    Directly save JSON data to S3.
    """

    try:

        body = json.dumps(
            data,
            ensure_ascii=False
        )

        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=body.encode("utf-8"),
            ContentType="application/json"
        )

        logger.info(
            "JSON saved to S3: s3://%s/%s",
            S3_BUCKET,
            s3_key
        )

        return True

    except ClientError as exc:

        logger.error(
            "S3 JSON save failed: %s",
            exc
        )

        raise


def get_json(
    s3_key: str
):
    """
    Read JSON from S3.
    Returns None if object does not exist.
    """

    try:

        response = s3_client.get_object(
            Bucket=S3_BUCKET,
            Key=s3_key
        )

        content = response["Body"].read()

        return json.loads(
            content.decode("utf-8")
        )

    except ClientError as exc:

        error_code = exc.response.get(
            "Error",
            {}
        ).get(
            "Code"
        )

        if error_code in (
            "NoSuchKey",
            "404"
        ):
            return None

        logger.error(
            "S3 read failed: %s",
            exc
        )

        raise