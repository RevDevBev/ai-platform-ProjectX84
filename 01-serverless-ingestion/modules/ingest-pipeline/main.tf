locals {
  name = "${var.name_prefix}-${var.environment}"
  tags = {
    Environment = var.environment
    Project     = "ai-platform"
  }
}

resource "aws_sqs_queue" "dlq" {
  name = "${local.name}-dlq"
  message_retention_seconds = 1209600
  sqs_managed_sse_enabled = true
  tags = local.tags
}

resource "aws_sqs_queue" "main" {
  name = "${local.name}-queue"
  visibility_timeout_seconds = var.consumer_timeout * 6
  sqs_managed_sse_enabled = true
  
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount = var.max_receive_count
  })
  
  tags = local.tags
}

resource "aws_dynamodb_table" "messages"{
  name = "${local.name}-messages"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "message_id"
  
  attribute {
    name = "message_id"
    type = "S"
    
  }
  
  tags = local.tags
}
