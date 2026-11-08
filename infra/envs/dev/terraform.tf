# infra/envs/dev/terraform.tf
# Terraform settings, remote state backend and AWS provider for the claim-dev account.
#
# The account is chosen by the AWS_PROFILE environment variable (locally) or by the
# role GitHub Actions assumes (later). No profile name is written in this code.

terraform {
  required_version = ">= 1.11"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # Backend blocks cannot use variables, so the bucket name is written out.
  # exactly as printed by infra/bootstrap/create-state-bucket.ps1.
  backend "s3" {
    bucket       = "claim-dev-tfstate-238038669096"
    key          = "claim-helper/dev/terraform.tfstate"
    region       = "ap-south-1"
    encrypt      = true
    use_lockfile = true
  }
}

provider "aws" {
  region = "ap-south-1"

  default_tags {
    tags = {
      project    = "claim-helper"
      env        = "dev"
      managed_by = "terraform"
    }
  }
}
