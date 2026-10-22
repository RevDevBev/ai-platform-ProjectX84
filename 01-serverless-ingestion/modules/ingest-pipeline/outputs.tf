output "queue_url" {
  value = aws_sqs_queue.main.arn
}

output "queue_arn" {
  value = aws_sqs_queue.main.arn
}

output "dlq_arn" {
  value = aws_sqs_queue.dlq.arn
}

output "table_name" {
  value = aws_dynamodb_table.messages.name
}

output "table_arn" {
  value = aws_dynamodb_table.messages.arn
}

output "consumer_function_name" {
  value = aws_lambda_function.consumer.function_name
}
