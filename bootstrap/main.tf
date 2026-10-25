data "aws_caller_identity" "current" {}

locals {
  account_id   = data.aws_caller_identity.current.account_id
  environments = toset(["dev", "prod"])
}

# ---------- Plan user: read-only, used on pull requests ----------
resource "aws_iam_user" "plan" {
  name = "ci-terraform-plan"
}

resource "aws_iam_user_policy_attachment" "plan_readonly" {
  user       = aws_iam_user.plan.name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

data "aws_iam_policy_document" "plan_state" {
  statement {
    actions   = ["s3:ListBucket"]
    resources = ["arn:aws:s3:::${var.state_bucket}"]
  }
  statement {
    actions   = ["s3:GetObject"]
    resources = ["arn:aws:s3:::${var.state_bucket}/*"]
  }
}

resource "aws_iam_user_policy" "plan_state" {
  name   = "read-terraform-state"
  user   = aws_iam_user.plan.name
  policy = data.aws_iam_policy_document.plan_state.json
}

# ---------- Apply users: one per environment ----------
resource "aws_iam_user" "apply" {
  for_each = local.environments
  name     = "ci-terraform-apply-${each.key}"
}

data "aws_iam_policy_document" "apply" {
  for_each = local.environments

  statement {
    sid       = "ServiceAccess"
    actions   = ["lambda:*", "apigateway:*", "sqs:*", "dynamodb:*", "logs:*", "cloudwatch:*"]
    resources = ["*"]
  }

  statement {
    sid = "ManageEnvironmentRoles"
    actions = [
      "iam:CreateRole",
      "iam:DeleteRole",
      "iam:UpdateRole",
      "iam:TagRole",
      "iam:UntagRole",
      "iam:PutRolePolicy",
      "iam:DeleteRolePolicy",
      "iam:AttachRolePolicy",
      "iam:DetachRolePolicy",
      "iam:UpdateAssumeRolePolicy",
      "iam:PassRole",
    ]
    resources = ["arn:aws:iam::${local.account_id}:role/ingest-${each.key}-*"]
  }

  statement {
    sid       = "ReadIam"
    actions   = ["iam:Get*", "iam:List*"]
    resources = ["*"]
  }

  statement {
    sid       = "StateBucketList"
    actions   = ["s3:ListBucket"]
    resources = ["arn:aws:s3:::${var.state_bucket}"]
  }

  statement {
    sid       = "StateObjects"
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["arn:aws:s3:::${var.state_bucket}/serverless-ingestion/${each.key}/*"]
  }
}

resource "aws_iam_policy" "apply" {
  for_each = local.environments
  name     = "ci-terraform-apply-${each.key}"
  policy   = data.aws_iam_policy_document.apply[each.key].json
}

resource "aws_iam_user_policy_attachment" "apply" {
  for_each   = local.environments
  user       = aws_iam_user.apply[each.key].name
  policy_arn = aws_iam_policy.apply[each.key].arn
}