#!/usr/bin/env bash
# ABOUTME: Provisions an S3 bucket with Object Lock in COMPLIANCE mode and 30-day default retention for immutable backups.
# ABOUTME: COMPLIANCE mode blocks deletion even by the root account; GOVERNANCE mode allows specific principals to bypass.

set -euo pipefail

BUCKET="${1:-prod-backups-immutable}"
REGION="${AWS_REGION:-us-east-1}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
MODE="${MODE:-COMPLIANCE}"

if [[ -z "${AWS_PROFILE:-}" ]]; then
  echo "Set AWS_PROFILE to a profile with s3:CreateBucket and s3:PutObjectLockConfiguration." >&2
  exit 1
fi

# Object Lock requires a versioned bucket created with object-lock enabled at
# creation time. Retrofitting an existing bucket is not supported.
aws --profile "$AWS_PROFILE" s3api create-bucket \
  --bucket "$BUCKET" \
  --region "$REGION" \
  --create-bucket-configuration "LocationConstraint=$REGION" \
  --object-lock-enabled-for-bucket

aws --profile "$AWS_PROFILE" s3api put-public-access-block \
  --bucket "$BUCKET" \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

aws --profile "$AWS_PROFILE" s3api put-bucket-encryption \
  --bucket "$BUCKET" \
  --server-side-encryption-configuration \
    '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'

aws --profile "$AWS_PROFILE" s3api put-object-lock-configuration \
  --bucket "$BUCKET" \
  --object-lock-configuration "{
    \"ObjectLockEnabled\": \"Enabled\",
    \"Rule\": {
      \"DefaultRetention\": {
        \"Mode\": \"$MODE\",
        \"Days\": $RETENTION_DAYS
      }
    }
  }"

# Versioning is implicit when object lock is enabled at creation, but we set
# it explicitly so a future operator cannot disable it without surfacing the
# action in audit logs.
aws --profile "$AWS_PROFILE" s3api put-bucket-versioning \
  --bucket "$BUCKET" \
  --versioning-configuration Status=Enabled

echo "Bucket $BUCKET provisioned with Object Lock ($MODE, $RETENTION_DAYS days)."
echo ""
echo "IMPORTANT: the credential that writes backups must be DIFFERENT from the"
echo "credential the agent uses for normal operations. The agent must not have"
echo "s3:PutBucketLifecycleConfiguration on this bucket or it can shorten the"
echo "retention window."
