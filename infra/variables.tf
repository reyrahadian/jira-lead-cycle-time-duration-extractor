variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-2"
}

variable "aws_profile" {
  description = "AWS profile to use for authentication"
  type        = string
  default     = "default"
}

variable "cluster_name" {
  description = "Name of the ECS cluster"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., prod, dev, staging)"
  type        = string
  default     = "dev"
}

variable "extractor_ecr_repository_name" {
  description = "Name of the ECR repository for the Jira metrics extractor"
  type        = string
}

variable "reporting_ecr_repository_name" {
  description = "Name of the ECR repository for the reporting application"
  type        = string
}

variable "application_name" {
  description = "Name of the application"
  type        = string
}

variable "vpc_id" {
  description = "ID of the VPC where ECS tasks and EFS will be deployed"
  type        = string
}

variable "subnet_cidrs" {
  type    = list(string)
  default = ["10.0.1.0/24", "10.0.2.0/24"]  # Adjust these based on your VPC CIDR
}

variable "jira_username" {
  description = "Username for Jira authentication"
  type        = string
  sensitive   = true
}

variable "jira_password" {
  description = "Password for Jira authentication"
  type        = string
  sensitive   = true
}

variable "custom_jql" {
  description = "Custom JQL query for Jira metrics extraction"
  type        = string
  default     = ""
}

variable "dora_dashboard_valid_project_names" {
  description = "Comma-separated list of valid project names for DORA dashboard"
  type        = string
  default     = ""
}

variable "sprint_dashboard_valid_project_names" {
  description = "Comma-separated list of valid project names for Sprint dashboard"
  type        = string
  default     = ""
}
