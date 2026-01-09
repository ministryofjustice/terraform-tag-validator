variable "application" {
  description = "Name of Application you are deploying"
  default     = "Tag Enforcement Testing"
}

variable "business_unit" {
  description = "Area of the MOJ responsible for the service"
  default     = "Platforms"
}

variable "team_name" {
  description = "The name of your development team"
  default     = "COAT"
}

variable "environment" {
  description = "The type of environment you're deploying to"
  default     = "development"
}

variable "infrastructure_support" {
  description = "The team responsible for managing the infrastructure. Should be of the form team-email"
  default     = "coat@digital.justice.gov.uk"
}

variable "is_production" {
  description = "Whether this is a production environment"
  default     = "false"
}

variable "service_area" {
  description = "The full name of the Service Area in which your team is based"
  default     = "Cloud Optimisation"
}

# Invalid values for testing validation failures

variable "invalid_business_unit" {
  description = "Invalid business unit value for testing"
  default     = "InvalidBU"
}

variable "invalid_owner" {
  description = "Invalid owner format for testing"
  default     = "wrong-format"
}

variable "invalid_is_production" {
  description = "Invalid is-production value for testing"
  default     = "maybe"
}

variable "invalid_environment" {
  description = "Invalid environment value for testing"
  default     = "invalid-env"
}
