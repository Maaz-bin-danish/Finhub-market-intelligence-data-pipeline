import boto3
import json

BUCKET = "finhub-stock-data"
PREFIX = "raw/"

s3 = boto3.client("s3")

total = 0
bad = []
paginator = s3.get_paginator("list_objects_v2")

for page in paginator.paginate(Bucket=BUCKET, Prefix=PREFIX):
    for obj in page.get("Contents", []):
        key = obj["Key"]

        if not key.endswith(".json"):
            continue

        total += 1

        try:
            body = s3.get_object(
                Bucket=BUCKET,
                Key=key
            )["Body"].read()

            json.loads(body)

        except Exception as e:
            bad.append((key, str(e)))

print("Total JSON files scanned:", total)
print("Bad files:", len(bad))

for key, error in bad:
    print(f"{key} -> {error}")
