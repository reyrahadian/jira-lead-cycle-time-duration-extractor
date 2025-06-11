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