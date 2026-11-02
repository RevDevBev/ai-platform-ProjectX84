---
access: public
updated: 2026-10-12
---
# Ingestion API reference

## POST /ingest
Send a JSON body to POST /ingest. The API places the body on a queue and returns a message ID. A successful response means the message was accepted, not that it has been processed.

## Response codes
ERR-4001 means the request body is not valid JSON. ERR-4291 means the client exceeded the rate limit and should retry later with backoff. ERR-5003 means the queue is temporarily unavailable. Clients should treat ERR-5003 as retryable.

## Rate limits
Each client may send up to 50 requests per second, with bursts of up to 100. Requests above the limit receive HTTP 429 with the code ERR-4291.