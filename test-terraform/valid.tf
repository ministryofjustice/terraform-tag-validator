resource "aws_s3_bucket" "valid_all_tags" {
  bucket = "valid-all-tags-bucket"

  tags = var.valid_tags
}
