# Create EventBridge scheduler for scaling up reporting app at 8am AEST
resource "aws_scheduler_schedule" "reporting_scale_up_8am" {
  name       = "${var.application_name}-reporting-scale-up-8am-${var.environment}"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 22 ? * SUN-THU *)"  # 8 AM AEST on weekdays (22:00 UTC previous day)

  target {
    arn      = aws_lambda_function.update_ecs_task_count.arn
    role_arn = aws_iam_role.eventbridge_ecs_role.arn

    input = jsonencode({
      service_name  = "${var.application_name}-reporting-service-${var.environment}"
      desired_count = 1
    })
  }
}

# Create EventBridge scheduler for scaling down reporting app at 6pm AEST
resource "aws_scheduler_schedule" "reporting_scale_down_6pm" {
  name       = "${var.application_name}-reporting-scale-down-6pm-${var.environment}"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 8 ? * MON-FRI *)"  # 6 PM AEST on weekdays (08:00 UTC)

  target {
    arn      = aws_lambda_function.update_ecs_task_count.arn
    role_arn = aws_iam_role.eventbridge_ecs_role.arn

    input = jsonencode({
      service_name  = "${var.application_name}-reporting-service-${var.environment}"
      desired_count = 0
    })
  }
}

# Create EventBridge scheduler for running extractor task at 8am AEST
resource "aws_scheduler_schedule" "extractor_run_8am" {
  name       = "${var.application_name}-extractor-run-8am-${var.environment}"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 22 ? * SUN-THU *)"  # 8 AM AEST on weekdays (22:00 UTC previous day)

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