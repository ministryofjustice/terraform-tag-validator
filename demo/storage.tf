# Production S3 bucket for document storage
resource "aws_s3_bucket" "documents" {
  bucket = "moj-laa-document-storage-prod"

  tags = {
    business-unit    = "LAA"
    application      = "Legal Aid Application System"
    owner            = "LAA Digital Team: laa-digital@digital.justice.gov.uk"
    is-production    = "true"
    service-area     = "Legal Services"
    environment-name = "production"
    component        = "document-storage"
    source-code      = "github.com/ministryofjustice/laa-apply-for-legal-aid"
  }
}

# S3 bucket versioning for compliance
resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id

  versioning_configuration {
    status = "Enabled"
  }
}

# DynamoDB table for application state
resource "aws_dynamodb_table" "application_state" {
  name         = "laa-applications-prod"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "application_id"
  range_key    = "created_at"

  attribute {
    name = "application_id"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  tags = {
    business-unit    = "LAA"
    application      = "Legal Aid Application System"
    owner            = "LAA Digital Team: laa-digital@digital.justice.gov.uk"
    is-production    = "true"
    service-area     = "Legal Services"
    environment-name = "production"
    component        = "application-database"
    source-code      = "github.com/ministryofjustice/laa-apply-for-legal-aid"
  }
}
