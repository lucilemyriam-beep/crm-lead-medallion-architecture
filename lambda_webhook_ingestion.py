import json
import boto3
import logging

s3 = boto3.client("s3")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

BUCKET_NAME = "crm-lead-medallion-593271843946"


def lambda_handler(event, context):
    try:
        # API Gateway sends the webhook body as a JSON string.
        if "body" in event:
            body = event["body"]
            payload = json.loads(body) if isinstance(body, str) else body
        else:
            # Allows direct Lambda testing.
            payload = event

        crm_event = payload.get("event", {})

        # Only process newly created leads.
        if (
            crm_event.get("object_type") != "lead"
            or crm_event.get("action") != "created"
        ):
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Event ignored"})
            }

        lead_id = crm_event.get("lead_id")

        if not lead_id or not lead_id.startswith("lead_"):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing or invalid lead_id"})
            }

        # Save the webhook payload to the Bronze layer.
        file_key = f"bronze/crm_event_{lead_id}.json"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_key,
            Body=json.dumps(payload).encode("utf-8"),
            ContentType="application/json"
        )

        logger.info("Lead stored in S3: %s", lead_id)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Lead successfully ingested",
                "lead_id": lead_id,
                "s3_key": file_key
            })
        }

    except (json.JSONDecodeError, TypeError, AttributeError):
        logger.warning("Invalid webhook JSON payload")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON payload"})
        }

    except Exception:
        logger.exception("CRM lead ingestion failed")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Internal server error"})
        }
