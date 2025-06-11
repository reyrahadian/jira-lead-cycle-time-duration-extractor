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