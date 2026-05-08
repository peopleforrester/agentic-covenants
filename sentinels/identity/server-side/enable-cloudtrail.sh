#!/usr/bin/env bash
# ABOUTME: Provisions a multi-region CloudTrail trail delivering to an Object-Lock S3 bucket with log-file validation.
# ABOUTME: Pair with the immutable-backup bucket from controls/blast-radius/server-side/. Trail name is per-environment.

set -euo pipefail

TRAIL_NAME="${TRAIL_NAME:-agent-audit}"
BUCKET="${BUCKET:-agent-cloudtrail-immutable}"
REGION="${AWS_REGION:-us-east-1}"

if [[ -z "${AWS_PROFILE:-}" ]]; then
  echo "Set AWS_PROFILE to a profile with cloudtrail:CreateTrail and s3:PutBucketPolicy." >&2
  exit 1
fi

# Bucket policy that allows CloudTrail to write but no one to delete.
# Object Lock on the bucket prevents log tampering even with bucket-write.
cat > /tmp/cloudtrail-bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AWSCloudTrailAclCheck",
      "Effect": "Allow",
      "Principal": { "Service": "cloudtrail.amazonaws.com" },
      "Action": "s3:GetBucketAcl",
      "Resource": "arn:aws:s3:::${BUCKET}"
    },
    {
      "Sid": "AWSCloudTrailWrite",
      "Effect": "Allow",
      "Principal": { "Service": "cloudtrail.amazonaws.com" },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::${BUCKET}/AWSLogs/*",
      "Condition": {
        "StringEquals": { "s3:x-amz-acl": "bucket-owner-full-control" }
      }
    }
  ]
}
EOF

aws --profile "$AWS_PROFILE" s3api put-bucket-policy \
  --bucket "$BUCKET" \
  --policy file:///tmp/cloudtrail-bucket-policy.json

aws --profile "$AWS_PROFILE" cloudtrail create-trail \
  --name "$TRAIL_NAME" \
  --s3-bucket-name "$BUCKET" \
  --include-global-service-events \
  --is-multi-region-trail \
  --enable-log-file-validation

aws --profile "$AWS_PROFILE" cloudtrail put-event-selectors \
  --trail-name "$TRAIL_NAME" \
  --event-selectors '[{
    "ReadWriteType": "All",
    "IncludeManagementEvents": true,
    "DataResources": [
      {"Type": "AWS::S3::Object", "Values": ["arn:aws:s3:::"]},
      {"Type": "AWS::Lambda::Function", "Values": ["arn:aws:lambda"]}
    ]
  }]'

aws --profile "$AWS_PROFILE" cloudtrail start-logging --name "$TRAIL_NAME"

echo "CloudTrail $TRAIL_NAME provisioned and logging."
echo ""
echo "Subscribe a SIEM to the trail via EventBridge:"
echo "  aws events put-rule --name agent-cloudtrail-to-siem \\"
echo "    --event-pattern '{\"source\":[\"aws.cloudtrail\"]}' "
