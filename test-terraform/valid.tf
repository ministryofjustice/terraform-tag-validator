resource "aws_s3_bucket" "valid_all_tags" {
  bucket = "valid-all-tags-bucket"

  tags = {
    business-unit    = "Platforms"
    application      = "Tag Enforcement Testing"
    owner            = "COAT Team: coat@digital.justice.gov.uk"
    is-production    = "false"
    service-area     = "Cloud Optimisation"
    environment-name = "development"
  }
}
