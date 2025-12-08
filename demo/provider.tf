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
  region = "eu-west-2"
  
  default_tags {
    tags = {
      managed-by = "Terraform"
      repository = "github.com/ministryofjustice/example-service"
    }
  }
}
