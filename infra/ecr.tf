# Create ECR Repository for Jira Metrics Extractor
resource "aws_ecr_repository" "extractor" {
  name = var.extractor_ecr_repository_name

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = var.extractor_ecr_repository_name
    Environment = var.environment
    Application = var.application_name
  }
}

# Create ECR Repository for Reporting App
resource "aws_ecr_repository" "reporting" {
  name = var.reporting_ecr_repository_name

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name        = var.reporting_ecr_repository_name
    Environment = var.environment
    Application = var.application_name
  }
}