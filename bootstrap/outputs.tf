output "plan_user" {
  value = aws_iam_user.plan.name
}

output "apply_users" {
  value = [for u in aws_iam_user.apply : u.name]
}