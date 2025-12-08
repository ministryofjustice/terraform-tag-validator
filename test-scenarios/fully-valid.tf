# ✅ S3 bucket with ALL required tags
resource "aws_s3_bucket" "fully_compliant" {
  bucket = "fully-compliant-bucket-${formatdate("YYYYMMDDhhmmss", timestamp())}"

  tags = {
    business-unit    = "Platforms"
    application      = "Tag Enforcement Testing"
    owner            = "COAT Team: coat@digital.justice.gov.uk"
    is-production    = "false"
    service-area     = "Cloud Optimisation"
    environment-name = "test"
    Name             = "Fully Compliant Bucket"
  }
}

# ✅ DynamoDB table with ALL required tags
resource "aws_dynamodb_table" "fully_compliant" {
  name         = "fully-compliant-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    business-unit    = "HMPPS"
    application      = "Data Storage"
    owner            = "Platform Team: platform@digital.justice.gov.uk"
    is-production    = "true"
    service-area     = "Prisons"
    environment-name = "production"
  }
}

# ✅ Lambda function with ALL required tags
resource "aws_lambda_function" "fully_compliant" {
  filename      = "lambda.zip"
  function_name = "fully-compliant-function"
  role          = "arn:aws:iam::123456789012:role/lambda-role"
  handler       = "index.handler"
  runtime       = "python3.12"

  tags = {
    business-unit    = "LAA"
    application      = "Document Processing"
    owner            = "Legal Aid Team: laa@digital.justice.gov.uk"
    is-production    = "false"
    service-area     = "Legal Services"
    environment-name = "development"
  }
}
