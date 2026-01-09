variable "valid_tags" {
  description = "Valid tags that pass all validation rules"
  type        = map(string)
  default = {
    business-unit    = "Platforms"
    application      = "Tag Enforcement Testing"
    owner            = "COAT Team: coat@digital.justice.gov.uk"
    is-production    = "false"
    service-area     = "Cloud Optimisation"
    environment-name = "development"
  }
}

variable "missing_tags" {
  description = "Tags missing required keys"
  type        = map(string)
  default = {
    Name = "example-bucket"
  }
}

variable "partial_tags" {
  description = "Tags with some required keys missing"
  type        = map(string)
  default = {
    business-unit = "HMPPS"
    application   = "Example Application"
  }
}

variable "invalid_value_tags" {
  description = "Tags with invalid values"
  type        = map(string)
  default = {
    business-unit    = "InvalidBU"
    application      = "Test App"
    owner            = "wrong-format"
    is-production    = "maybe"
    service-area     = "Test"
    environment-name = "invalid-env"
  }
}
