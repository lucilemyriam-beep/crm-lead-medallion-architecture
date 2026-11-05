import json
import os
import boto3
import urllib.request
from urllib.parse import unquote_plus

s3 = boto3.client("s3")

def lambda_handler(event, context):
    webhook_url = os.environ["SLACK_WEBHOOK_URL"]
    if isinstance(event, str):
        event = json.loads(event)
    if "Records" in event:
        leads = []
        for record in event["Records"]:
            if record.get("eventSource") != "aws:s3":
                raise ValueError("Unsupported event source")
            bucket = record["s3"]["bucket"]["name"]
            key = unquote_plus(record["s3"]["object"]["key"])
            if not key.startswith("gold/crm_leads/") or not key.endswith(".json"):
                continue
            response = s3.get_object(Bucket=bucket, Key=key)
            leads.append(json.loads(response["Body"].read().decode("utf-8")))
    else:
        leads = [event]
    sent = 0
    for lead in leads:
        required_fields = ["lead_id", "lead_status", "owner_name", "processing_status"]
        missing = [field for field in required_fields if not lead.get(field)]
        if missing:
            raise ValueError(f"Missing required Gold fields: {missing}")
        if lead["processing_status"] != "gold_ready":
            print("Skipping lead that is not Gold-ready")
            continue
        message = {"text": (
            "*New CRM Lead Alert*\n"
            f"*Lead ID:* {lead['lead_id']}\n"
            f"*Event:* {lead.get('event_type', 'N/A')}\n"
            f"*Source:* {lead.get('source', 'N/A')}\n"
            f"*Status:* {lead['lead_status']}\n"
            f"*Lead Owner:* {lead['owner_name']}\n"
            f"*Owner Email:* {lead.get('owner_email', 'N/A')}\n"
            f"*Sales Region:* {lead.get('sales_region', 'N/A')}\n"
            f"*Sales Team:* {lead.get('sales_team', 'N/A')}"
        )}
        request = urllib.request.Request(webhook_url, data=json.dumps(message).encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=10) as response:
            result = response.read().decode("utf-8")
        if result != "ok":
            raise RuntimeError(f"Unexpected Slack response: {result}")
        print(f"Slack notification sent for {lead['lead_id']}")
        sent += 1
    return {"statusCode": 200, "body": json.dumps({"message": "Processing completed", "notifications_sent": sent})}
