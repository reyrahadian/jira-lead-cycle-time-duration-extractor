# Create SSM Parameters for Jira credentials
resource "aws_ssm_parameter" "jira_username" {
  name        = "/${var.application_name}/${var.environment}/jira_username"
  description = "Jira username for metrics extractor"
  type        = "SecureString"
  value       = var.jira_username

  tags = {
    Environment = var.environment
    Application = var.application_name
  }
}

resource "aws_ssm_parameter" "jira_password" {
  name        = "/${var.application_name}/${var.environment}/jira_password"
  description = "Jira password for metrics extractor"
  type        = "SecureString"
  value       = var.jira_password

  tags = {
    Environment = var.environment
    Application = var.application_name
  }
}

resource "aws_ssm_parameter" "custom_jql" {
  name        = "/${var.application_name}/${var.environment}/custom_jql"
  description = "Custom JQL for metrics extractor"
  type        = "String"
  value       = var.custom_jql

  tags = {
    Environment = var.environment
    Application = var.application_name
  }
}

resource "aws_ssm_parameter" "dora_dashboard_valid_project_names" {
  name        = "/${var.application_name}/${var.environment}/dora_dashboard_valid_project_names"
  description = "Comma-separated list of valid project names for DORA dashboard"
  type        = "String"
  value       = var.dora_dashboard_valid_project_names

  tags = {
    Environment = var.environment
    Application = var.application_name
  }
}

resource "aws_ssm_parameter" "sprint_dashboard_valid_project_names" {
  name        = "/${var.application_name}/${var.environment}/sprint_dashboard_valid_project_names"
  description = "Comma-separated list of valid project names for Sprint dashboard"
  type        = "String"
  value       = var.sprint_dashboard_valid_project_names

  tags = {
    Environment = var.environment
    Application = var.application_name
  }
}