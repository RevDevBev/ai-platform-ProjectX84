import json
import os
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])

#lambda function code
def lambda_handler(event, context):
    failures = []

    for record in event["Records"]:
        message_id = record["messageId"]
        try:
            payload = json.loads(record["body"])
            table.put_item(
                Item={ 
                    "message_id": message_id,
                    "payload": json.dumps(payload),
                    "receive_count": int(record["attributes"]["ApproximateReceiveCount"]),
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                },
                ConditionExpression="attribute_not_exists(message_id)",
            )
            print(f"stored {message_id}")
        except ClientError as err:
            if err.response["Error"]["Code"] == "ConditionalCheckFailedException":
                print(f"duplicate {message_id}, skipping")
            else:
                print(f"error on {message_id}: {err}")
                failures.append({"itemIdentifier": message_id})
        except Exception as err:
            print(f"failed {message_id}: {err}")
            failures.append({"itemIdentifier": message_id})

    return {"batchItemFailures": failures}