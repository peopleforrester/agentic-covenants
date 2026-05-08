#!/usr/bin/env bash
# ABOUTME: Wires AWS IAM Access Analyzer findings to EventBridge to a SIEM-shipping Lambda.
# ABOUTME: Run per-region (Access Analyzer is regional). Requires events:PutRule and events:PutTargets in the operator's profile.

set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
RULE_NAME="${RULE_NAME:-access-analyzer-findings}"
LAMBDA_ARN="${LAMBDA_ARN:-}"

if [[ -z "${AWS_PROFILE:-}" ]]; then
  echo "Set AWS_PROFILE to a profile with events:PutRule." >&2
  exit 1
fi
if [[ -z "$LAMBDA_ARN" ]]; then
  echo "Set LAMBDA_ARN to the SIEM-shipping Lambda's ARN." >&2
  exit 1
fi

aws --profile "$AWS_PROFILE" --region "$REGION" events put-rule \
  --name "$RULE_NAME" \
  --description "Access Analyzer findings to SIEM" \
  --event-pattern '{"source":["aws.access-analyzer"],"detail-type":["Access Analyzer Finding"]}' \
  --state ENABLED

aws --profile "$AWS_PROFILE" --region "$REGION" events put-targets \
  --rule "$RULE_NAME" \
  --targets "Id=1,Arn=$LAMBDA_ARN"

# Lambda must have permission to be invoked by EventBridge. Add this once per
# Lambda, not per region.
aws --profile "$AWS_PROFILE" --region "$REGION" lambda add-permission \
  --function-name "$LAMBDA_ARN" \
  --statement-id "${RULE_NAME}-invoke" \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn "arn:aws:events:${REGION}:$(aws --profile "$AWS_PROFILE" sts get-caller-identity --query Account --output text):rule/${RULE_NAME}" \
  2>/dev/null || true   # idempotent: already-exists is fine

echo "EventBridge rule $RULE_NAME wired to $LAMBDA_ARN in $REGION."
echo "Repeat for every region where Access Analyzer is enabled."
