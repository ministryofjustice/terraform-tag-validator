resource "aws_s3_bucket" "missing_tags" {
  bucket = "missing-tags-bucket"

  tags = {
    Name = var.application
  }
}

resource "aws_instance" "partial_tags" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    business-unit = var.business_unit
    application   = var.application
  }
}

resource "aws_dynamodb_table" "invalid_values" {
  name         = "invalid-values-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    business-unit    = var.invalid_business_unit
    application      = var.application
    owner            = var.invalid_owner
    is-production    = var.invalid_is_production
    service-area     = var.service_area
    environment-name = var.invalid_environment
  }
}
