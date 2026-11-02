---
access: restricted
updated: 2026-10-18
---
# Data retention policy

## Retention periods
Messages stored in the DynamoDB table are kept for 90 days. Application logs are kept for 30 days. Messages in the dead-letter queue are kept for 14 days.

## Deletion requests
A request to delete personal data must be sent to the security team. Deletion is completed within 30 days and recorded in the audit log.

## Access to personal data
Only members of the security and data protection groups may read stored message payloads that contain personal data. All reads are logged.