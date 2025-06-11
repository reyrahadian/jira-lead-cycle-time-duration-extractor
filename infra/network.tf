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