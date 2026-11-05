import sys
import boto3
import json
from datetime import datetime, timezone
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
job = Job(glueContext)
job.init(args["JOB_NAME"], args)
s3 = boto3.client("s3")

# Set CRM_S3_BUCKET as an AWS Glue job parameter or replace with your bucket.
BUCKET = "YOUR_CRM_S3_BUCKET"
SILVER_PREFIX = "silver/enriched/"
GOLD_PREFIX = "gold/crm_leads/"
paginator = s3.get_paginator("list_objects_v2")
processed = 0
for page in paginator.paginate(Bucket=BUCKET, Prefix=SILVER_PREFIX):
    for obj in page.get("Contents", []):
        key = obj["Key"]
        if "lead_owner_lookup/" in key or not key.endswith(".json"):
            continue
        response = s3.get_object(Bucket=BUCKET, Key=key)
        lead = json.loads(response["Body"].read().decode("utf-8"))
        if lead.get("processing_status") != "validated":
            continue
        lead_id = lead.get("lead_id")
        if not lead_id:
            continue
        gold_record = {
            "lead_id": lead_id,
            "event_type": lead.get("event_type"),
            "source": lead.get("source"),
            "lead_status": lead.get("status"),
            "owner_id": lead.get("owner_id"),
            "owner_name": lead.get("owner_name"),
            "owner_email": lead.get("owner_email"),
            "sales_region": lead.get("sales_region"),
            "sales_team": lead.get("sales_team"),
            "processing_status": "gold_ready",
            "silver_processed_at": lead.get("processed_at"),
            "gold_processed_at": datetime.now(timezone.utc).isoformat(),
        }
        message_file = key.rsplit("/", 1)[-1]
        gold_key = f"{GOLD_PREFIX}{lead_id}/{message_file}"
        s3.put_object(Bucket=BUCKET, Key=gold_key, Body=json.dumps(gold_record), ContentType="application/json")
        print(f"Gold record saved: s3://{BUCKET}/{gold_key}")
        processed += 1
print(f"Total Gold records written: {processed}")
job.commit()
