# Create EventBridge scheduler for scaling up reporting app at 8:30am AEDT
resource "aws_scheduler_schedule" "reporting_scale_up" {
  name       = "${var.application_name}-reporting-scale-up-${var.environment}"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(30 20 ? * SUN-THU *)"  # 8:30 AM AEDT on weekdays

  target {
    arn      = aws_lambda_function.update_ecs_task_count.arn
    role_arn = aws_iam_role.eventbridge_ecs_role.arn

    input = jsonencode({
      service_name  = "${var.application_name}-reporting-service-${var.environment}"
      desired_count = 1
    })
  }
}

# Create EventBridge scheduler for scaling down reporting app at 6pm AEDT
resource "aws_scheduler_schedule" "reporting_scale_down" {
  name       = "${var.application_name}-reporting-scale-down-${var.environment}"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 7 ? * MON-FRI *)"  # 6 PM AEDT on weekdays

  target {
    arn      = aws_lambda_function.update_ecs_task_count.arn
    role_arn = aws_iam_role.eventbridge_ecs_role.arn

    input = jsonencode({
      service_name  = "${var.application_name}-reporting-service-${var.environment}"
      desired_count = 0
    })
  }
}

# Create EventBridge scheduler for running extractor task at 8am AEDT
resource "aws_scheduler_schedule" "extractor_run" {
  name       = "${var.application_name}-extractor-run-${var.environment}"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 21 ? * SUN-THU *)"  # 8 AM AEDT on weekdays

  target {
    arn      = "arn:aws:scheduler:::aws-sdk:ecs:runTask"
    role_arn = aws_iam_role.eventbridge_ecs_role.arn

    input = jsonencode({
      Cluster        = aws_ecs_cluster.main.name
      TaskDefinition = aws_ecs_task_definition.extractor.arn
      LaunchType     = "FARGATE"
      PlatformVersion = "LATEST"
      NetworkConfiguration = {
        AwsvpcConfiguration = {
          Subnets          = aws_subnet.main[*].id
          SecurityGroups   = [aws_security_group.ecs_tasks.id]
          AssignPublicIp   = "ENABLED"
        }
      }
      Count = 1
    })
  }
}