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

resource "aws_apigatewayv2_api" "ingest" {
  name          = "${local.name}-api"
  protocol_type = "HTTP"
  tags          = local.tags
}

resource "aws_apigatewayv2_integration" "sqs" {
  api_id                 = aws_apigatewayv2_api.ingest.id
  integration_type       = "AWS_PROXY"
  integration_subtype    = "SQS-SendMessage"
  credentials_arn        = aws_iam_role.apigw_sqs.arn
  payload_format_version = "1.0"

  request_parameters = {
    QueueUrl    = aws_sqs_queue.main.url
    MessageBody = "$request.body"
  }
}

resource "aws_apigatewayv2_route" "post_ingest" {
  api_id    = aws_apigatewayv2_api.ingest.id
  route_key = "POST /ingest"
  target    = "integrations/${aws_apigatewayv2_integration.sqs.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.ingest.id
  name        = "$default"
  auto_deploy = true
  tags        = local.tags
}

data "aws_iam_policy_document" "apigw_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "apigw_sqs" {
  name               = "${local.name}-apigw-sqs-role"
  assume_role_policy = data.aws_iam_policy_document.apigw_assume.json
  tags               = local.tags
}

data "aws_iam_policy_document" "apigw_sqs" {
  statement {
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.main.arn]
  }
}

resource "aws_iam_role_policy" "apigw_sqs" {
  name   = "send-to-queue"
  role   = aws_iam_role.apigw_sqs.id
  policy = data.aws_iam_policy_document.apigw_sqs.json
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

