---
access: public
updated: 2026-10-11
---
# Frequently asked questions

## Why was my message not processed?
The API confirms that a message was accepted, not that it was processed. If a message fails three times it is moved to the dead-letter queue. Contact the platform team with the message ID.

## Resending failed messages
Failed messages are not lost. The platform team can redrive messages from the dead-letter queue back to the main queue once the cause is fixed. Do not resend the same message from the client, because this may create duplicates.