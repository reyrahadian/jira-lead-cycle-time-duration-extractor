# Create CloudWatch Log Group for Extractor
resource "aws_cloudwatch_log_group" "extractor" {
  name              = "/ecs/${var.application_name}-extractor-${var.environment}"
  retention_in_days = 30

  tags = {
    Name        = "${var.application_name}-extractor-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Create CloudWatch Log Group for Reporting App
resource "aws_cloudwatch_log_group" "reporting" {
  name              = "/ecs/${var.application_name}-reporting-${var.environment}"
  retention_in_days = 30  # Adjust retention period as needed

  tags = {
    Name        = "${var.application_name}-reporting-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}