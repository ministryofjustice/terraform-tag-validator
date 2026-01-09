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
  
  access_key = "test"
  secret_key = "test"
}

# Example S3 bucket missing required tags - testing detailed PR comments
resource "aws_s3_bucket" "example_missing_tags" {
  bucket = "my-test-bucket-invalid"

  tags = {
    Name = "example-bucket"
    # Missing: business-unit, application, owner, is-production, service-area
  }
}

# Example EC2 instance with some tags but not all
resource "aws_instance" "example_partial_tags" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    business-unit = "HMPPS"
    application   = "Example Application"
    Name          = "example-instance"
    # Missing: owner, is-production, service-area
  }
}

# Example RDS instance with invalid business-unit value
resource "aws_db_instance" "example_invalid_value" {
  identifier        = "example-db"
  engine            = "mysql"
  instance_class    = "db.t3.micro"
  allocated_storage = 20

  tags = {
    business-unit  = "InvalidUnit"  # Invalid value - not in allowed list
    application    = "Database"
    owner          = "Team: team@test.com"
    is-production  = "false"
    service-area   = "Data"
  }
}
