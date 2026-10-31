---
access: public
updated: 2026-10-01
---
# Ingestion platform overview

## Request flow
Clients send JSON messages to the POST /ingest endpoint of an HTTP API. API Gateway places each message on an SQS queue and returns the message ID at once. A consumer Lambda function reads the queue in batches of five messages and writes each message to a DynamoDB table.

## Failure handling
If the consumer fails on a message, the message becomes visible again after the visibility timeout, which is six times the function timeout. After three failed receives, SQS moves the message to the dead-letter queue. The consumer reports failed messages individually, so the rest of a batch is not retried.

## Duplicate deliveries
SQS delivers messages at least once. The consumer writes with a conditional put on the message ID, so a duplicate is skipped and not stored twice.