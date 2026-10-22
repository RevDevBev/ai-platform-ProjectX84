locals {
  name = "${var.name_prefix}-${var.environment}"
  tags = {
    Environment = var.environment
    Project     = "ai-platform"
  }
}

resource "aws_sqs_queue" "dlq" {
  name                      = "${local.name}-dlq"
  message_retention_seconds = 1209600
  sqs_managed_sse_enabled   = true
  tags                      = local.tags
}

resource "aws_sqs_queue" "main" {
  name                       = "${local.name}-queue"
  visibility_timeout_seconds = var.consumer_timeout * 6
  sqs_managed_sse_enabled    = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = var.max_receive_count
  })

  tags = local.tags
}

resource "aws_dynamodb_table" "messages" {
  name         = "${local.name}-messages"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "message_id"

  attribute {
    name = "message_id"
    type = "S"

  }

  tags = local.tags
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

  }
}

resource "aws_iam_role" "consumer" {
  name               = "${local.name}-consumer-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
  tags               = local.tags
}

resource "aws_iam_role_policy_attachment" "consumer_logs" {
  role       = aws_iam_role.consumer.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "consumer" {
  statement {
    actions   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
    resources = [aws_sqs_queue.main.arn]
  }
  statement {
    actions   = ["dynamodb:PutItem"]
    resources = [aws_dynamodb_table.messages.arn]
  }
}

resource "aws_iam_role_policy" "consumer" {
  name   = "consumer-access"
  role   = aws_iam_role.consumer.id
  policy = data.aws_iam_policy_document.consumer.json
}


data "archive_file" "consumer_zip" {
  type        = "zip"
  source_file = var.consumer_source_file
  output_path = "${path.module}/build/${local.name}-consumer.zip"
}

resource "aws_lambda_function" "consumer" {
  function_name    = "${local.name}-consumer"
  role             = aws_iam_role.consumer.arn
  runtime          = var.runtime
  handler          = "consumer.lambda_handler"
  filename         = data.archive_file.consumer_zip.output_path
  source_code_hash = data.archive_file.consumer_zip.output_base64sha256
  timeout          = var.consumer_timeout
  tags             = local.tags

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.messages.name
    }
  }
}

resource "aws_lambda_event_source_mapping" "consumer" {
  event_source_arn        = aws_sqs_queue.main.arn
  function_name           = aws_lambda_function.consumer.arn
  batch_size              = var.batch_size
  function_response_types = ["ReportBatchItemFailures"]

  depends_on = [aws_iam_role_policy.consumer]
}

