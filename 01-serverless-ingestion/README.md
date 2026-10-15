API Gateway HTTP API with POST /ingest that triggers a Python Lambda
- Lambda service runs lambda_function.py 
- tested on events/post-ingest.json
- API Gateway (HTTP API), given the route to the lambda and POST 
- tested on POWERSHELL Invoke-RestMethod -Method Post -Uri "https://wbac7lcind.execute-api.eu-north-1.amazonaws.com//ingest" -ContentType "application/json" -Body '{"name":"magic"}'