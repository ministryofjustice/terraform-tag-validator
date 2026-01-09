resource "aws_s3_bucket" "missing_tags" {
  bucket = "missing-tags-bucket"

  tags = {
    Name = "example-bucket"
  }
}

resource "aws_instance" "partial_tags" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    business-unit = "HMPPS"
    application   = "Example Application"
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
    business-unit    = "InvalidBU"
    application      = "Test App"
    owner            = "wrong-format"
    is-production    = "maybe"
    service-area     = "Test"
    environment-name = "invalid-env"
  }
}
