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