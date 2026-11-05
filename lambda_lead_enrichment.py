import json  # Added: required by json.loads/json.dumps in the supplied script.
import os
import boto3
from datetime import datetime, timezone

s3 = boto3.client("s3")

BUCKET = os.environ["S3_BUCKET"]
PREFIX = os.environ["S3_OUTPUT_PREFIX"]
LOOKUP_KEY = os.environ["LEAD_OWNER_LOOKUP_KEY"]


def load_lead_owners():
    response = s3.get_object(Bucket=BUCKET, Key=LOOKUP_KEY)
    owners = json.loads(response["Body"].read().decode("utf-8"))
    return owners


def lambda_handler(event, context):
    print("CRM lead enrichment started")
    lead_owners = load_lead_owners()

    for record in event.get("Records", []):
        message = json.loads(record["body"])
        lead_id = message.get("lead_id")
        event_type = message.get("event_type")

        if not lead_id:
            raise ValueError("Missing lead_id")
        owner_info = lead_owners.get(lead_id, {})
        enriched_lead = {
            "lead_id": lead_id,
            "event_type": event_type,
            "source": message.get("source", "crm"),
            "status": message.get("status", "new"),
            "processing_status": "validated",
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
        enriched_lead.update(owner_info)

        key = f"{PREFIX}{lead_id}/{record['messageId']}.json"
        s3.put_object(
            Bucket=BUCKET,
            Key=key,
            Body=json.dumps(enriched_lead),
            ContentType="application/json"
        )
        print(f"Saved validated lead to s3://{BUCKET}/{key}")

    return {
        "statusCode": 200,
        "body": "CRM lead messages processed"
    }
