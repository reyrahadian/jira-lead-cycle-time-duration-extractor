variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-2"
}

variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
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
