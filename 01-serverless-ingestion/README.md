# Serverless event-driven ingestion (AWS + Terraform)

An HTTP endpoint that accepts JSON messages, buffers them in a queue, and
stores them in DynamoDB. Built with Terraform modules and deployed to a `dev`
environment with remote state.

## Architecture

```mermaid
flowchart LR
  Client -->|POST /ingest| APIGW[API Gateway HTTP API]
  APIGW -->|SendMessage| SQS[SQS queue]
  SQS -->|batch, partial failures| Consumer[Lambda consumer]
  Consumer -->|conditional PutItem| DDB[(DynamoDB)]
  SQS -. after 3 failed receives .-> DLQ[Dead-letter queue]
```

## Design decisions

- **Queue between API and worker:** the API returns as soon as SQS accepts the
  message, so spikes are absorbed and a slow or failing consumer doesn't break
  the client.
- **At-least-once delivery, so idempotent writes:** the consumer uses a
  conditional put on `message_id`; redelivered messages are skipped.
- **Partial batch responses:** only failed messages return to the queue.
- **Dead-letter queue:** messages that fail 3 times are parked for inspection.
- **Visibility timeout = 6 x consumer timeout**, because one timeout covers a
  whole batch.
- **Least-privilege IAM:** the consumer can read one queue and `PutItem` on one
  table; API Gateway can `SendMessage` to one queue.

## Behaviour I tested

| Test | Result |
|---|---|
| Valid message through the API | Stored in DynamoDB |
| Invalid JSON through the API | Client gets success, message retried 3 times, lands in the DLQ |
| Same message delivered twice | One item stored, duplicate skipped |
| Batch with one bad record | Only the bad record reported as failed |

## Repository layout

```
modules/ingest-pipeline/   queue, DLQ, table, consumer, API integration
envs/dev/                  dev deployment (provider, S3 backend, module call)
consumer.py                SQS consumer Lambda
```

## Deploy

```
cd envs/dev
terraform init
terraform plan
terraform apply
```

Requires an AWS CLI profile and an S3 bucket for remote state (edit the backend
block in `envs/dev/versions.tf`).

## Not built yet / what I'd improve

- Authorization and throttling on the endpoint (it is currently open)
- Alarms on DLQ depth and queue age
- Separate AWS accounts and state per environment (test, prod)
- A CI/CD pipeline (plan on PR, gated deploy)
- Request validation at the API so bad input is rejected with a 400