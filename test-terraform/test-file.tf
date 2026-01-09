resource "aws_s3_bucket" "test_empty_owner" {
  bucket = "my-test-bucket-empty-owner"

  tags = {
    business-unit  = "Platforms"
    application    = "Tag Enforcement Testing"
    owner          = "COAT Team: coat@digital.justice.gov.uk"
    is-production  = "false"
    service-area   = "Cloud Optimisation"
  }
}

# Example EC2 instance with empty owner tag
resource "aws_instance" "test_empty_values" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    business-unit  = "HMPPS"
    application    = "Example Application"
    owner          = ""
    is-production  = "true"
    service-area   = "Prisons"
    Name           = " "
  }
}