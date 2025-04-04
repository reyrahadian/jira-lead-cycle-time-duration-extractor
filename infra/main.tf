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
  cpu                     = 256
  memory                  = 512
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
  cpu                     = 256
  memory                  = 512
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

# Create EventBridge rule to trigger the Jira metrics extractor
resource "aws_cloudwatch_event_rule" "extractor_schedule" {
  name                = "${var.application_name}-extractor-schedule-${var.environment}"
  description         = "Schedule for running the Jira metrics extractor every 4 hours during business hours"
  schedule_expression = "cron(0 6-18/4 ? * MON-FRI *)"  # Run every 4 hours between 6 AM and 6 PM on weekdays

  tags = {
    Name        = "${var.application_name}-extractor-schedule-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Create EventBridge rules for scaling down and up
resource "aws_cloudwatch_event_rule" "scale_down_end_of_day" {
  name                = "${var.application_name}-scale-down-end-day-${var.environment}"
  description         = "Scale down ECS services at 6 PM on weekdays"
  schedule_expression = "cron(0 18 ? * MON-FRI *)"  # 6 PM UTC

  tags = {
    Name        = "${var.application_name}-scale-down-end-day-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

resource "aws_cloudwatch_event_rule" "scale_up_start_of_day" {
  name                = "${var.application_name}-scale-up-start-day-${var.environment}"
  description         = "Scale up ECS services at 6 AM on weekdays"
  schedule_expression = "cron(0 6 ? * MON-FRI *)"   # 6 AM UTC

  tags = {
    Name        = "${var.application_name}-scale-up-start-day-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

resource "aws_cloudwatch_event_rule" "scale_down_weekend" {
  name                = "${var.application_name}-scale-down-weekend-${var.environment}"
  description         = "Scale down ECS services on weekends"
  schedule_expression = "cron(0 0 ? * SAT *)"  # Midnight Saturday UTC

  tags = {
    Name        = "${var.application_name}-scale-down-weekend-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Create IAM role for EventBridge
resource "aws_iam_role" "eventbridge_ecs_role" {
  name = "${var.application_name}-eventbridge-ecs-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.application_name}-eventbridge-ecs-role-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Create IAM policy for EventBridge to update ECS services
resource "aws_iam_role_policy" "eventbridge_ecs_policy" {
  name = "${var.application_name}-eventbridge-ecs-policy-${var.environment}"
  role = aws_iam_role.eventbridge_ecs_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService"
        ]
        Resource = [
          aws_ecs_service.reporting_app.id,
          aws_ecs_service.extractor.id
        ]
      }
    ]
  })
}

# Create inline Lambda function code
data "archive_file" "lambda_scale_ecs" {
  type        = "zip"
  output_path = "${path.module}/lambda/scale_ecs.zip"

  source {
    content  = <<-EOF
      const AWS = require("aws-sdk");
      const ecs = new AWS.ECS();

      exports.handler = async (event) => {
          const clusterName = process.env.CLUSTER_NAME;
          const serviceName = process.env.SERVICE_NAME;

          const desiredCount = event.action === "scale_up" ? 1 : 0;

          const params = {
              cluster: clusterName,
              service: serviceName,
              desiredCount: desiredCount
          };

          try {
              await ecs.updateService(params).promise();
              console.log("Successfully " + (event.action === "scale_up" ? "scaled up" : "scaled down") + " service " + serviceName + " in cluster " + clusterName);
              return {
                  statusCode: 200,
                  body: "Service " + serviceName + " " + (event.action === "scale_up" ? "scaled up" : "scaled down") + " successfully"
              };
          } catch (error) {
              console.error("Error updating service:", error);
              throw error;
          }
      };
    EOF
    filename = "index.js"
  }
}

# Update Lambda function to use the archive_file data source
resource "aws_lambda_function" "scale_ecs" {
  filename         = data.archive_file.lambda_scale_ecs.output_path
  source_code_hash = data.archive_file.lambda_scale_ecs.output_base64sha256
  function_name    = "${var.application_name}-scale-ecs-${var.environment}"
  role            = aws_iam_role.lambda_scale_ecs_role.arn
  handler         = "index.handler"
  runtime         = "nodejs18.x"
  timeout         = 30

  environment {
    variables = {
      CLUSTER_NAME = aws_ecs_cluster.main.name
      SERVICE_NAME = aws_ecs_service.reporting_app.name
    }
  }

  tags = {
    Name        = "${var.application_name}-scale-ecs-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Create IAM role for Lambda
resource "aws_iam_role" "lambda_scale_ecs_role" {
  name = "${var.application_name}-lambda-scale-ecs-role-${var.environment}"

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
    Name        = "${var.application_name}-lambda-scale-ecs-role-${var.environment}"
    Environment = var.environment
    Application = var.application_name
  }
}

# Create IAM policy for Lambda to update ECS services and write logs
resource "aws_iam_role_policy" "lambda_scale_ecs_policy" {
  name = "${var.application_name}-lambda-scale-ecs-policy-${var.environment}"
  role = aws_iam_role.lambda_scale_ecs_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:UpdateService"
        ]
        Resource = [
          aws_ecs_service.reporting_app.id,
          aws_ecs_service.extractor.id
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${aws_lambda_function.scale_ecs.function_name}:*"
        ]
      }
    ]
  })
}

# Keep only these Lambda-based targets
resource "aws_cloudwatch_event_target" "lambda_scale_down_end_of_day" {
  rule      = aws_cloudwatch_event_rule.scale_down_end_of_day.name
  target_id = "ScaleDownECSLambda"
  arn       = aws_lambda_function.scale_ecs.arn
  input     = jsonencode({
    action = "scale_down"
  })
}

resource "aws_cloudwatch_event_target" "lambda_scale_up_start_of_day" {
  rule      = aws_cloudwatch_event_rule.scale_up_start_of_day.name
  target_id = "ScaleUpECSLambda"
  arn       = aws_lambda_function.scale_ecs.arn
  input     = jsonencode({
    action = "scale_up"
  })
}

resource "aws_cloudwatch_event_target" "lambda_scale_down_weekend" {
  rule      = aws_cloudwatch_event_rule.scale_down_weekend.name
  target_id = "ScaleDownECSWeekendLambda"
  arn       = aws_lambda_function.scale_ecs.arn
  input     = jsonencode({
    action = "scale_down"
  })
}

# Add Lambda permissions for EventBridge
resource "aws_lambda_permission" "scale_down_end_of_day" {
  statement_id  = "AllowEventBridgeScaleDownEndDay"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scale_ecs.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scale_down_end_of_day.arn
}

resource "aws_lambda_permission" "scale_up_start_of_day" {
  statement_id  = "AllowEventBridgeScaleUpStartDay"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scale_ecs.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scale_up_start_of_day.arn
}

resource "aws_lambda_permission" "scale_down_weekend" {
  statement_id  = "AllowEventBridgeScaleDownWeekend"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scale_ecs.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.scale_down_weekend.arn
}
