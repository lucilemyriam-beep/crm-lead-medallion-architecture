# Validation evidence

1. AWS Glue `crm-lead-silver-to-gold`: successful run shown in AWS Glue Runs tab.
2. Gold JSON: verified fields including `lead_id`, `lead_status`, `owner_name`, `sales_region`, `sales_team`, and `processing_status=gold_ready`.
3. S3 event notification: `s3:ObjectCreated:*`, prefix `gold/crm_leads/`, suffix `.json`.
4. Final test: uploaded `crm-final-test.json` (432 bytes) to a Gold lead folder; a new Slack CRM Lead Notifications message appeared at 10:08 AM.

Screenshots intentionally omitted from starter ZIP to avoid publishing account identifiers and contact information. Add only redacted screenshots after review.
