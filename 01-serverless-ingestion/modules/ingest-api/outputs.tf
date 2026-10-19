output "invoke_url" {
  value = "${aws_apigatewayv2_stage.default.invoke_url}ingest"
}

output "function_name" {
  value = aws_lambda_function.ingest.function_name
}