import json

def lambda_handler(event, context):
    body = json.loads(event.get("body") or "{}")
    print("received:", body)
    return {
        "statusCode": 200,
        "body": json.dumps({"ok": True, "echo": body}),
    }