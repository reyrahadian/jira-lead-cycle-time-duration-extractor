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