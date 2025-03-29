output "s3_bucket_id" {
  description = "The ID of the S3 bucket"
  value       = aws_s3_bucket.main.id
}

output "s3_bucket_arn" {
  description = "The ARN of the S3 bucket"
  value       = aws_s3_bucket.main.arn
}

output "ecs_cluster_id" {
  description = "The ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "ecs_cluster_arn" {
  description = "The ARN of the ECS cluster"
  value       = aws_s3_bucket.main.arn
}

output "extractor_ecr_repository_url" {
  description = "The URL of the ECR repository for the Jira metrics extractor"
  value       = aws_ecr_repository.extractor.repository_url
}

output "reporting_ecr_repository_url" {
  description = "The URL of the ECR repository for the reporting application"
  value       = aws_ecr_repository.reporting.repository_url
}