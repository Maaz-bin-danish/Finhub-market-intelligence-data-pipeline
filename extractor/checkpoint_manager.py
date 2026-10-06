import logging

from .s3_manager import (
    get_json,
    save_json
)


logger = logging.getLogger(__name__)


def checkpoint_key(
    endpoint: str,
    key: str
):
    """
    Build S3 checkpoint path.
    """

    return (
        f"checkpoints/"
        f"{endpoint}/"
        f"{key}.json"
    )


def get_checkpoint(
    endpoint: str,
    key: str,
    default_value: str
):
    """
    Get checkpoint for a specific endpoint/key.
    """

    s3_key = checkpoint_key(
        endpoint,
        key
    )

    checkpoint = get_json(
        s3_key
    )

    if checkpoint is None:

        logger.info(
            "No checkpoint found for %s/%s. "
            "Using default: %s",
            endpoint,
            key,
            default_value
        )

        return default_value

    return checkpoint.get(
        "last_value",
        default_value
    )


def update_checkpoint(
    endpoint: str,
    key: str,
    value: str
):
    """
    Update checkpoint only after
    successful data processing/upload.
    """

    s3_key = checkpoint_key(
        endpoint,
        key
    )

    checkpoint_data = {
        "endpoint": endpoint,
        "key": key,
        "last_value": value
    }

    save_json(
        checkpoint_data,
        s3_key
    )

    logger.info(
        "Checkpoint updated: %s/%s -> %s",
        endpoint,
        key,
        value
    )