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

  depends_on = [data.aws_caller_identity.current]
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
        },
        {
          name  = "DORA_DASHBOARD_VALID_PROJECT_NAMES"
          value = var.dora_dashboard_valid_project_names
        },
        {
          name  = "SPRINT_DASHBOARD_VALID_PROJECT_NAMES"
          value = var.sprint_dashboard_valid_project_names
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