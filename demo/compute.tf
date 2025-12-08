# Lambda function for document processing
resource "aws_lambda_function" "document_processor" {
  filename      = "document-processor.zip"
  function_name = "laa-document-processor-prod"
  role          = aws_iam_role.lambda_role.arn
  handler       = "index.handler"
  runtime       = "python3.12"
  timeout       = 60
  memory_size   = 512

  environment {
    variables = {
      ENVIRONMENT = "production"
      S3_BUCKET   = aws_s3_bucket.documents.id
    }
  }

  tags = {
    business-unit    = "LAA"
    application      = "Legal Aid Application System"
    owner            = "LAA Digital Team: laa-digital@digital.justice.gov.uk"
    is-production    = "true"
    service-area     = "Legal Services"
    environment-name = "production"
    component        = "document-processor"
    source-code      = "github.com/ministryofjustice/laa-apply-for-legal-aid"
  }
}

# IAM role for Lambda
resource "aws_iam_role" "lambda_role" {
  name = "laa-document-processor-role-prod"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    business-unit    = "LAA"
    application      = "Legal Aid Application System"
    owner            = "LAA Digital Team: laa-digital@digital.justice.gov.uk"
    is-production    = "true"
    service-area     = "Legal Services"
    environment-name = "production"
    component        = "iam"
    source-code      = "github.com/ministryofjustice/laa-apply-for-legal-aid"
  }
}

# ECR repository for container images
resource "aws_ecr_repository" "api" {
  name                 = "laa-api-prod"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    business-unit    = "LAA"
    application      = "Legal Aid Application System"
    owner            = "LAA Digital Team: laa-digital@digital.justice.gov.uk"
    is-production    = "true"
    service-area     = "Legal Services"
    environment-name = "production"
    component        = "container-registry"
    source-code      = "github.com/ministryofjustice/laa-apply-for-legal-aid"
  }
}
