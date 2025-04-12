terraform {
  cloud {
    organization = "MeccaBrands-sandbox"
    workspaces {
      name = "jira-metrics-reporting"
    }
  }
}

# Configure AWS Provider
provider "aws" {
  region = var.aws_region
}

# Add this at the top of your file with other data sources
data "aws_caller_identity" "current" {}

# Create ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = var.cluster_name

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name        = var.cluster_name
    Environment = var.environment
    Application = var.application_name
  }
}

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

# Create Resource Group
resource "aws_resourcegroups_group" "main" {
  name = "${var.application_name}-${var.environment}-group"

  resource_query {
    query = jsonencode({
      ResourceTypeFilters = ["AWS::AllSupported"]
      TagFilters = [
        {
          Key    = "Environment"
          Values = [var.environment]
        },
        {
          Key    = "Application"
          Values = [var.application_name]
        }
      ]
    })
  }

  tags = {
    Name        = "${var.application_name}-${var.environment}-group"
    Environment = var.environment
    Application = var.application_name
  }
}

# Create ECS Task Definition for Reporting App
resource "aws_ecs_task_definition" "reporting" {
  family                   = "${var.application_name}-reporting-${var.environment}"
  requires_compatibilities = ["FARGATE"]
  network_mode            = "awsvpc"
  cpu                     = "1024"
  memory                  = "2048"
  execution_role_arn      = aws_iam_role.ecs_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "reporting-container"
      image     = "${aws_ecr_repository.reporting.repository_url}:latest"
      essential = true

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8050/ || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 10
      }

      mountPoints = [
        {
          sourceVolume  = "efs-data"
          containerPath = "/data"
          readOnly      = true
        }
      ]

      environment = [
        {
          name  = "REPORTING_CSV_PATH"
          value = "/data/jira_metrics.csv"
        },
        {
          name  = "HOST"
          value = "0.0.0.0"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.application_name}-reporting-${var.environment}"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      portMappings = [
        {
          containerPort = 8050
          hostPort      = 8050
          protocol      = "tcp"
        }
      ]
    }
  ])

  volume {
    name = "efs-data"
    efs_volume_configuration {
      file_system_id          = aws_efs_file_system.efs_data.id
      root_directory          = "/"
      transit_encryption      = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.efs_data.id
        iam            = "ENABLED"
      }
    }
  }

  tags = {
    Name        = "${var.application_name}-reporting-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Create ECS Task Execution Role
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.application_name}-ecs-execution-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.application_name}-ecs-execution-role-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Attach AWS managed policy for ECS task execution
resource "aws_iam_role_policy_attachment" "ecs_execution_role_policy" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Create ECS Task Role
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.application_name}-ecs-task-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.application_name}-ecs-task-role-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Add EFS access policy to ECS Task Role
resource "aws_iam_role_policy" "ecs_task_efs_policy" {
  name = "${var.application_name}-ecs-task-efs-policy-${var.environment}"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "elasticfilesystem:ClientMount",
          "elasticfilesystem:ClientWrite",
          "elasticfilesystem:ClientRootAccess"
        ]
        Resource = aws_efs_file_system.efs_data.arn
      }
    ]
  })
}

# Add SSM permissions to the ECS Task Role
resource "aws_iam_role_policy" "ecs_task_ssm_policy" {
  name = "${var.application_name}-ecs-task-ssm-policy-${var.environment}"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssmmessages:CreateControlChannel",
          "ssmmessages:CreateDataChannel",
          "ssmmessages:OpenControlChannel",
          "ssmmessages:OpenDataChannel"
        ]
        Resource = "*"
      }
    ]
  })
}

# Create EFS File System
resource "aws_efs_file_system" "efs_data" {
  creation_token = "${var.application_name}-efs-${var.environment}"
  encrypted      = true

  tags = {
    Name        = "${var.application_name}-efs-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Update subnets to enable auto-assign public IP
resource "aws_subnet" "main" {
  count                   = 2
  vpc_id                 = var.vpc_id
  cidr_block             = var.subnet_cidrs[count.index]
  availability_zone      = "${var.aws_region}${count.index == 0 ? "a" : "b"}"
  map_public_ip_on_launch = true  # Enable auto-assign public IP

  tags = {
    Name        = "${var.application_name}-subnet-${var.environment}-${count.index + 1}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Create EFS Mount Target for each subnet
resource "aws_efs_mount_target" "efs_data" {
  count           = 2  # Create a mount target in each subnet
  file_system_id  = aws_efs_file_system.efs_data.id
  subnet_id       = aws_subnet.main[count.index].id
  security_groups = [aws_security_group.efs.id]
}

# Update Security Group for EFS
resource "aws_security_group" "efs" {
  name        = "${var.application_name}-efs-sg-${var.environment}"
  description = "Security group for EFS mount targets"
  vpc_id      = var.vpc_id

  ingress {
    description     = "NFS from ECS tasks"
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name        = "${var.application_name}-efs-sg-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Update Security Group for ECS Tasks
resource "aws_security_group" "ecs_tasks" {
  name        = "${var.application_name}-ecs-tasks-sg-${var.environment}"
  description = "Security group for ECS tasks"
  vpc_id      = var.vpc_id

  # Allow public inbound traffic to container port
  ingress {
    from_port   = 8050
    to_port     = 8050
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow public inbound traffic to container port"
  }

  # Allow EFS traffic
  ingress {
    from_port       = 2049
    to_port         = 2049
    protocol        = "tcp"
    self            = true
    description     = "Allow NFS traffic between ECS tasks"
  }

  # Allow inbound traffic from ALB
  ingress {
    from_port       = 8050
    to_port         = 8050
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Allow inbound traffic from ALB"
  }

  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = {
    Name        = "${var.application_name}-ecs-tasks-sg-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Update ALB Security Group
resource "aws_security_group" "alb" {
  name        = "${var.application_name}-alb-sg-${var.environment}"
  description = "Security group for ALB"
  vpc_id      = var.vpc_id

  # Allow inbound HTTP traffic
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP inbound traffic"
  }

  # Allow outbound traffic to container port
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow outbound traffic to containers"
  }

  tags = {
    Name        = "${var.application_name}-alb-sg-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Update ALB to use both subnets
resource "aws_lb" "main" {
  name               = "${var.application_name}-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = aws_subnet.main[*].id  # Use all subnets

  tags = {
    Name        = "${var.application_name}-alb-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Create ALB Target Group
resource "aws_lb_target_group" "reporting" {
  name        = "${var.application_name}-tg-${var.environment}"
  port        = 8050
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval           = 60
    matcher            = "200"
    path               = "/"
    port               = "8050"
    timeout            = 30
    unhealthy_threshold = 5
  }

  deregistration_delay = 60

  tags = {
    Name        = "${var.application_name}-tg-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Create ALB Listener
resource "aws_lb_listener" "front_end" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.reporting.arn
  }
}

# Update ECS Service to enable execute command
resource "aws_ecs_service" "reporting_app" {
  name            = "${var.application_name}-reporting-service-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.reporting.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  enable_execute_command = true  # Enable ECS Exec

  network_configuration {
    subnets          = aws_subnet.main[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }

  depends_on = [aws_lb_listener.front_end]

  load_balancer {
    target_group_arn = aws_lb_target_group.reporting.arn
    container_name   = "reporting-container"
    container_port   = 8050
  }

  tags = {
    Name        = "${var.application_name}-reporting-service-${var.environment}"
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

# Create EFS Access Point
resource "aws_efs_access_point" "efs_data" {
  file_system_id = aws_efs_file_system.efs_data.id

  root_directory {
    path = "/data"
    creation_info {
      owner_gid   = 1000
      owner_uid   = 1000
      permissions = "755"
    }
  }

  tags = {
    Name        = "${var.application_name}-efs-ap-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

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

# Create ECS Task Definition for Jira Metrics Extractor
resource "aws_ecs_task_definition" "extractor" {
  family                   = "${var.application_name}-extractor-${var.environment}"
  requires_compatibilities = ["FARGATE"]
  network_mode            = "awsvpc"
  cpu                     = "1024"
  memory                  = "2048"
  execution_role_arn      = aws_iam_role.ecs_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "extractor-container"
      image     = "${aws_ecr_repository.extractor.repository_url}:latest"
      essential = true

      environment = [
        {
          name  = "OUTPUT_PATH"
          value = "/data/jira_metrics.csv"
        }
      ]

      secrets = [
        {
          name      = "JIRA_USERNAME"
          valueFrom = aws_ssm_parameter.jira_username.arn
        },
        {
          name      = "JIRA_PASSWORD"
          valueFrom = aws_ssm_parameter.jira_password.arn
        },
        {
          name      = "CUSTOM_JQL"
          valueFrom = aws_ssm_parameter.custom_jql.arn
        }
      ]

      mountPoints = [
        {
          sourceVolume  = "efs-data"
          containerPath = "/data"
          readOnly      = false
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.application_name}-extractor-${var.environment}"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  volume {
    name = "efs-data"
    efs_volume_configuration {
      file_system_id          = aws_efs_file_system.efs_data.id
      root_directory          = "/"
      transit_encryption      = "ENABLED"
      authorization_config {
        access_point_id = aws_efs_access_point.efs_data.id
        iam            = "ENABLED"
      }
    }
  }

  tags = {
    Name        = "${var.application_name}-extractor-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Create ECS Service for Jira Metrics Extractor
resource "aws_ecs_service" "extractor" {
  name            = "${var.application_name}-extractor-service-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.extractor.arn
  desired_count   = 0  # Set to 0 since this will be triggered by EventBridge
  launch_type     = "FARGATE"

  enable_execute_command = true

  network_configuration {
    subnets          = aws_subnet.main[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = true
  }

  tags = {
    Name        = "${var.application_name}-extractor-service-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

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

# Update the execution role policy to allow reading SSM parameters
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy_ssm" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess"
}

# Lambda function to update ECS service task count
resource "aws_lambda_function" "update_ecs_task_count" {
  filename      = data.archive_file.lambda_zip.output_path
  function_name = "${var.application_name}-update-ecs-task-count-${var.environment}"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  runtime       = "python3.11"
  timeout       = 30

  environment {
    variables = {
      ECS_CLUSTER = aws_ecs_cluster.main.name
    }
  }

  tags = {
    Name        = "${var.application_name}-update-ecs-task-count-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Create zip file for Lambda function
data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "${path.module}/lambda/update_ecs_task_count.zip"

  source {
    content = <<EOF
import os
import boto3
import json

def handler(event, context):
    # Get the ECS cluster name from environment variable
    cluster_name = os.environ['ECS_CLUSTER']

    # Get the service name and desired count from the event
    service_name = event.get('service_name')
    desired_count = event.get('desired_count')

    if not service_name or desired_count is None:
        return {
            'statusCode': 400,
            'body': json.dumps('Missing required parameters: service_name or desired_count')
        }

    try:
        # Create ECS client
        ecs = boto3.client('ecs')

        # Update the service
        response = ecs.update_service(
            cluster=cluster_name,
            service=service_name,
            desiredCount=int(desired_count)
        )

        return {
            'statusCode': 200,
            'body': json.dumps(f'Successfully updated {service_name} to {desired_count} tasks')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error updating service: {str(e)}')
        }
EOF
    filename = "index.py"
  }
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "${var.application_name}-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.application_name}-lambda-role-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# IAM policy for Lambda to update ECS services
resource "aws_iam_role_policy" "lambda_ecs_policy" {
  name = "${var.application_name}-lambda-ecs-policy-${var.environment}"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService",
          "ecs:DescribeServices"
        ]
        Resource = "*"
      }
    ]
  })
}

# CloudWatch Logs policy for Lambda
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Create EventBridge scheduler for scaling up extractor at 8am
resource "aws_scheduler_schedule" "extractor_scale_up_8am" {
  name       = "${var.application_name}-extractor-scale-up-8am-${var.environment}"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 8 ? * MON-FRI *)"  # 8 AM UTC on weekdays

  target {
    arn      = aws_lambda_function.update_ecs_task_count.arn
    role_arn = aws_iam_role.eventbridge_ecs_role.arn

    input = jsonencode({
      service_name  = "${var.application_name}-extractor-service-${var.environment}"
      desired_count = 1
    })
  }
}

# Create EventBridge scheduler for scaling down extractor at 10am
resource "aws_scheduler_schedule" "extractor_scale_down_10am" {
  name       = "${var.application_name}-extractor-scale-down-10am-${var.environment}"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 10 ? * MON-FRI *)"  # 10 AM UTC on weekdays

  target {
    arn      = aws_lambda_function.update_ecs_task_count.arn
    role_arn = aws_iam_role.eventbridge_ecs_role.arn

    input = jsonencode({
      service_name  = "${var.application_name}-extractor-service-${var.environment}"
      desired_count = 0
    })
  }
}

# Create IAM role for EventBridge to invoke Lambda
resource "aws_iam_role" "eventbridge_ecs_role" {
  name = "${var.application_name}-eventbridge-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.application_name}-eventbridge-role-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Add permission for EventBridge to invoke Lambda
resource "aws_iam_role_policy" "eventbridge_lambda_policy" {
  name = "${var.application_name}-eventbridge-lambda-policy-${var.environment}"
  role = aws_iam_role.eventbridge_ecs_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = [
          aws_lambda_function.update_ecs_task_count.arn
        ]
      }
    ]
  })
}

# Create EventBridge scheduler for scaling up reporting app at 8am
resource "aws_scheduler_schedule" "reporting_scale_up_8am" {
  name       = "${var.application_name}-reporting-scale-up-8am-${var.environment}"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 8 ? * MON-FRI *)"  # 8 AM UTC on weekdays

  target {
    arn      = aws_lambda_function.update_ecs_task_count.arn
    role_arn = aws_iam_role.eventbridge_ecs_role.arn

    input = jsonencode({
      service_name  = "${var.application_name}-reporting-service-${var.environment}"
      desired_count = 1
    })
  }
}

# Create EventBridge scheduler for scaling down reporting app at 6pm
resource "aws_scheduler_schedule" "reporting_scale_down_6pm" {
  name       = "${var.application_name}-reporting-scale-down-6pm-${var.environment}"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 18 ? * MON-FRI *)"  # 6 PM UTC on weekdays

  target {
    arn      = aws_lambda_function.update_ecs_task_count.arn
    role_arn = aws_iam_role.eventbridge_ecs_role.arn

    input = jsonencode({
      service_name  = "${var.application_name}-reporting-service-${var.environment}"
      desired_count = 0
    })
  }
}