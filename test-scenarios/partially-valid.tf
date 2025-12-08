# ✅ VALID: S3 bucket with all tags
resource "aws_s3_bucket" "valid_bucket" {
  bucket = "valid-bucket-${formatdate("YYYYMMDDhhmmss", timestamp())}"

  tags = {
    business-unit    = "OPG"
    application      = "Storage Service"
    owner            = "OPG Team: opg@digital.justice.gov.uk"
    is-production    = "true"
    service-area     = "Public Guardian"
    environment-name = "production"
  }
}

# ❌ INVALID: Missing some required tags
resource "aws_s3_bucket" "partial_tags" {
  bucket = "partial-tags-bucket-${formatdate("YYYYMMDDhhmmss", timestamp())}"

  tags = {
    business-unit = "HMCTS"
    application   = "Court System"
    # Missing: owner, is-production, service-area
  }
}

# ❌ INVALID: Empty tag values
resource "aws_dynamodb_table" "empty_values" {
  name         = "empty-values-table"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    business-unit = ""  # Empty value
    application   = "Data Table"
    owner         = "   "  # Whitespace only
    is-production = "false"
    service-area  = "Testing"
  }
}

# ✅ VALID: Lambda with all tags
resource "aws_lambda_function" "valid_lambda" {
  filename      = "lambda.zip"
  function_name = "valid-lambda"
  role          = "arn:aws:iam::123456789012:role/lambda-role"
  handler       = "index.handler"
  runtime       = "python3.12"

  tags = {
    business-unit    = "CICA"
    application      = "Compensation Claims"
    owner            = "CICA Team: cica@digital.justice.gov.uk"
    is-production    = "false"
    service-area     = "Victim Services"
    environment-name = "staging"
  }
}

# ❌ INVALID: Invalid business-unit value
resource "aws_ecr_repository" "invalid_business_unit" {
  name = "invalid-bu-repo"

  tags = {
    business-unit = "RandomUnit"  # Not in allowed list
    application   = "Container Registry"
    owner         = "DevOps: devops@test.com"
    is-production = "true"
    service-area  = "Infrastructure"
  }
}
