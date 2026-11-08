<#
.SYNOPSIS
  One-time bootstrap: creates the S3 bucket that stores Terraform state for ONE AWS account.

.DESCRIPTION
  Terraform needs this bucket to exist before it can run, so it cannot create it itself.
  Run this once per AWS account (claim-dev, later claim-test and claim-prod).
  Safe to re-run: it skips creation if the bucket already exists and re-applies the settings.

  Bucket name pattern: <AccountName>-tfstate-<aws-account-id>

.EXAMPLE
  aws sso login --profile claim-dev
  .\create-state-bucket.ps1 -Profile claim-dev -AccountName claim-dev
#>
param(
  [Parameter(Mandatory = $true)][string]$Profile,
  [Parameter(Mandatory = $true)][string]$AccountName,
  [string]$Region = "ap-south-1"
)

# Check the login and find out which AWS account this profile points to.
$acct = aws sts get-caller-identity --profile $Profile --query Account --output text
if ($LASTEXITCODE -ne 0 -or -not $acct) {
  throw "Could not read your identity. Run: aws sso login --profile $Profile"
}

$bucket = "$AccountName-tfstate-$acct"
Write-Host ""
Write-Host "Profile : $Profile"
Write-Host "Account : $acct"
Write-Host "Region  : $Region"
Write-Host "Bucket  : $bucket"
Write-Host ""

# Safety stop: confirm the account number matches the account you intended.
$answer = Read-Host "Create/configure this bucket in the account above? (yes/no)"
if ($answer -ne "yes") {
  Write-Host "Cancelled. Nothing was changed."
  exit 0
}

# 1. Create the bucket if it does not exist yet.
aws s3api head-bucket --bucket $bucket --profile $Profile 2>$null
if ($LASTEXITCODE -eq 0) {
  Write-Host "Bucket already exists. Skipping creation."
} else {
  Write-Host "Creating bucket..."
  aws s3api create-bucket --bucket $bucket --region $Region `
    --create-bucket-configuration LocationConstraint=$Region --profile $Profile
  if ($LASTEXITCODE -ne 0) { throw "create-bucket failed. See the message above." }
}

# 2. Turn on versioning, so an older state file can be recovered.
Write-Host "Enabling versioning..."
aws s3api put-bucket-versioning --bucket $bucket `
  --versioning-configuration Status=Enabled --profile $Profile
if ($LASTEXITCODE -ne 0) { throw "put-bucket-versioning failed." }

# 3. Block all public access.
Write-Host "Blocking public access..."
aws s3api put-public-access-block --bucket $bucket `
  --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" `
  --profile $Profile
if ($LASTEXITCODE -ne 0) { throw "put-public-access-block failed." }

# 4. Show the result.
Write-Host ""
Write-Host "Verification:"
aws s3api get-bucket-versioning --bucket $bucket --profile $Profile
aws s3api get-public-access-block --bucket $bucket --profile $Profile
Write-Host ""
Write-Host "Done. Use this bucket name in the Terraform backend block: $bucket"