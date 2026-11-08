# infra/envs/dev/main.tf
# First resources for claim-dev: a private bucket for uploaded letters.
# Everything uploaded is deleted automatically after 30 days (privacy by default).

data "aws_caller_identity" "current" {}

locals {
  uploads_bucket_name = "claim-dev-uploads-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket" "uploads" {
  bucket = local.uploads_bucket_name
}

resource "aws_s3_bucket_public_access_block" "uploads" {
  bucket                  = aws_s3_bucket.uploads.id
  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "uploads" {
  bucket = aws_s3_bucket.uploads.id

  rule {
    id     = "delete-after-30-days"
    status = "Enabled"

    filter {}

    expiration {
      days = 30
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}
