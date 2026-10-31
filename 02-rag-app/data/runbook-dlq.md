---
access: internal
updated: 2026-10-05
---
# Dead-letter queue runbook

## Detection
Check the dead-letter queue depth in the SQS console. Any message there means a failure. Messages are kept for 14 days.

## Investigation
Poll a few messages from the dead-letter queue and read the bodies. Check the consumer logs around the failure time and note the receive count. Classify the cause as bad client data, a consumer bug, or a downstream problem such as DynamoDB throttling.

## Recovery
Fix the cause first. Then use the SQS redrive option to move the messages back to the source queue. Never redrive before the fix, because the messages will fail again and return to the dead-letter queue.