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

# Create EFS Mount Target for each subnet
resource "aws_efs_mount_target" "efs_data" {
  count           = 2  # Create a mount target in each subnet
  file_system_id  = aws_efs_file_system.efs_data.id
  subnet_id       = aws_subnet.main[count.index].id
  security_groups = [aws_security_group.efs.id]
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