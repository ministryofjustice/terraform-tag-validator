resource "aws_s3_bucket" "valid_all_tags" {
  bucket = "valid-all-tags-bucket"

  tags = {
    business-unit    = var.business_unit
    application      = var.application
    owner            = "${var.team_name}: ${var.infrastructure_support}"
    is-production    = var.is_production
    service-area     = var.service_area
    environment-name = var.environment
  }
}
