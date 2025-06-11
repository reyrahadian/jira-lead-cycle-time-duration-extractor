terraform {
  cloud {
    organization = "MeccaBrands-sandbox"
    workspaces {
      name = "jira-metrics-reporting"
    }
  }
}

# Configure AWS Provider
provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
  default_tags {
    tags = {
      Environment = var.environment
      Application = var.application_name
    }
  }
}