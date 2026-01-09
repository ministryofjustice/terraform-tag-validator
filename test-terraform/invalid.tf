resource "aws_s3_bucket" "missing_tags" {
  bucket = "missing-tags-bucket"

  tags = var.missing_tags
}

resource "aws_instance" "partial_tags" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = var.partial_tags
}

resource "aws_dynamodb_table" "invalid_values" {
  name         = "invalid-values-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = var.invalid_value_tags
}
