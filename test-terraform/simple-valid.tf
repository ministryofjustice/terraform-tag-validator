terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = "eu-west-2"
  skip_credentials_validation = true
  skip_requesting_account_id  = true
  skip_metadata_api_check     = true
  
  # Use fake credentials for testing
  access_key = "test"
  secret_key = "test"
}

# Example S3 bucket with all required tags
resource "aws_s3_bucket" "example_valid" {
  bucket = "my-test-bucket-valid-${formatdate("YYYYMMDDhhmmss", timestamp())}"

  tags = {
    business-unit = "Platforms"
    application   = "Tag Enforcement Testing"
    owner         = "COAT Team: coat@digital.justice.gov.uk"
    is-production = "false"
    service-area  = "Cloud Optimisation"
  }
}
