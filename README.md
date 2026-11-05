# Real-Time CRM Lead Processing | AWS Medallion Architecture

## Overview
A CRM lead-processing pipeline organized into **Bronze (raw ingestion)**, **Silver (validated/enriched)**, and **Gold (business-ready)** layers. The demonstrated final integration publishes Gold records to Amazon S3, invokes AWS Lambda on object creation, and sends notifications to Slack.

## Architecture
```text
CRM webhook → ingestion Lambda → S3 Bronze → SQS → enrichment Lambda → S3 Silver
                                                                    ↓
                                                          AWS Glue ETL job
                                                                    ↓
                                                       S3 Gold (JSON objects)
                                                                    ↓
                                               S3 ObjectCreated event trigger
                                                                    ↓
                                                   notification AWS Lambda
                                                                    ↓
                                                       Slack #crm-lead-alerts
```
Earlier pipeline components are described from project context; only the Silver→Gold Glue and Gold→Slack Lambda scripts are included in this starter repository. Add your original ingestion/enrichment source files before describing this repository as complete source coverage.

## Verified results (November 2026)
- Glue Silver→Gold job completed successfully after correcting an S3 `PutObject` IAM denial.
- Gold JSON contains `processing_status: gold_ready` and owner/team enrichment fields.
- S3 trigger uses `s3:ObjectCreated:*`, prefix `gold/crm_leads/`, suffix `.json`.
- Upload of `crm-final-test.json` succeeded; a new Slack lead notification appeared at 10:08 AM.

## Repository structure
- `src/glue_silver_to_gold.py`: Gold materialization from validated Silver JSON.
- `src/lambda_gold_to_slack.py`: S3 event handling, Gold validation, Slack notification.
- `docs/validation.md`: testing notes and outstanding production hardening.

## Configuration and security
- Replace `YOUR_CRM_S3_BUCKET` in the Glue script with your own bucket or parameterize it.
- Configure `SLACK_WEBHOOK_URL` securely in Lambda (prefer AWS Secrets Manager for production).
- Glue role requires scoped S3 read/write permissions; Lambda role requires scoped `s3:GetObject` for Gold objects and CloudWatch Logs permissions.
- **Never commit** webhook URLs, API tokens, customer data, AWS credentials, or unredacted console screenshots.

## Limitations / future improvements
- This starter reproduces the shared Glue and notification Lambda scripts, not every deployed AWS component.
- Glue currently rewrites output for every qualifying Silver file; consider incremental processing/bookmarks.
- S3 notifications are at-least-once: add idempotency/deduplication to avoid duplicate Slack alerts.
- Add retries, DLQ, automated tests, infrastructure as code, metrics, and secret rotation for production readiness.
- Verify real-world CRM records are not committed to GitHub.
