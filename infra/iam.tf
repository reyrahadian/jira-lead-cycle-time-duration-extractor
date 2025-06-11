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

# Update the execution role policy to allow reading SSM parameters
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy_ssm" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess"
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

# Update EventBridge IAM role policy to allow running ECS tasks
resource "aws_iam_role_policy" "eventbridge_ecs_policy" {
  name = "${var.application_name}-eventbridge-ecs-policy-${var.environment}"
  role = aws_iam_role.eventbridge_ecs_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecs:RunTask",
          "iam:PassRole"
        ]
        Resource = [
          aws_ecs_task_definition.extractor.arn,
          aws_iam_role.ecs_execution_role.arn,
          aws_iam_role.ecs_task_role.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ecs:RunTask"
        ]
        Resource = [
          "${replace(aws_ecs_task_definition.extractor.arn, "/:\\d+$/", ":*")}"
        ]
      }
    ]
  })
}