---
access: restricted
updated: 2026-10-10
---
# Access and security policy

## CI credentials
The pipeline uses three IAM users. The plan user is read-only and runs on pull requests. The dev and prod apply users are limited to their own environment's role names and state path. Apply keys are stored as GitHub environment secrets and are rotated every 90 days.

## Production access
Production changes go through a pull request, a passing plan and a manual deployment step. Direct pushes to the main branch are not allowed.