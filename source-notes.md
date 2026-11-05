# Additional Lambda source notes

- `src/lambda_webhook_ingestion.py`: transcribed from the supplied CRM webhook ingestion script. Escaped formatting from chat was normalized; logic retained.
- `src/lambda_lead_enrichment.py`: transcribed from the supplied SQS enrichment script, which appeared twice. Added missing `import json` (the supplied snippet calls `json.loads` and `json.dumps`). No other intentional logic changes.
- The ingestion function writes `bronze/crm_event_{lead_id}.json`. The enrichment function expects SQS messages with a top-level `lead_id`; the publisher/bridge connecting Bronze events to this SQS schema is not included in these files. Do not claim the full upstream integration is reproduced by this source package alone.
- The ingestion script has a fixed S3 bucket name; consider using an environment variable before redeploying in another AWS account.
- For public repositories, verify there are no real customer records, webhook URLs, or secrets in any files or screenshots.
