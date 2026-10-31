import json
import boto3

try:
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    
    resp = client.invoke_model(
            modelId="amazon.titan-embed-text-v2:0",
            body=json.dumps({"inputText": "hello"}),
        )
    vec = json.loads(resp["body"].read())["embedding"]
    print("embeddings OK, dimension:", len(vec))
    
    resp = client.converse(
    modelId="amazon.nova-micro-v1:0",
    messages=[{"role": "user", "content": [{"text": "what is the capital city of Jordan? answer in one word."}]}],
    )
    print("generation OK:", resp["output"]["message"]["content"][0]["text"])
except Exception as err:
    print("generation FAILED:", str(err)[:200])