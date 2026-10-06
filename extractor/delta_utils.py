import hashlib
import json


def record_key(record, fields):
    """
    Creates a deterministic unique key for a record.
    """
    values = []

    for field in fields:
        value = record.get(field)

        if value is None:
            value = ""

        values.append(str(value).strip().lower())

    raw_key = "|".join(values)

    return hashlib.sha256(
        raw_key.encode("utf-8")
    ).hexdigest()


def deduplicate_records(records, key_fields):
    """
    Removes duplicate records inside the current API response.
    """
    if not records:
        return []

    seen = set()
    unique_records = []

    for record in records:
        key = record_key(
            record,
            key_fields
        )

        if key in seen:
            continue

        seen.add(key)
        unique_records.append(record)

    return unique_records