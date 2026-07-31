# ABOUTME: Terraform provider blocks demonstrating cross-account separation: agent in non-prod, prod in a separate account.
# ABOUTME: The agent role explicitly cannot AssumeRole into prod; production work happens through human-operated pipelines only.

terraform {
  required_version = ">= 1.13.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

# ---- Non-prod account (where the agent's role lives) ----
provider "aws" {
  alias   = "nonprod"
  region  = "us-east-1"
  profile = "nonprod-admin"   # operator credential, not the agent's
}

# ---- Prod account (where prod resources live) ----
provider "aws" {
  alias  = "prod"
  region = "us-east-1"
  assume_role {
    role_arn     = "arn:aws:iam::PROD_ACCOUNT_ID:role/terraform-apply-prod"
    session_name = "terraform-${formatdate("YYYYMMDDhhmmss", timestamp())}"
    # external_id is recommended for cross-account roles to prevent the
    # confused deputy problem.
    external_id = var.prod_external_id
  }
}

variable "prod_external_id" {
  description = "External ID required by the prod account's trust policy."
  type        = string
  sensitive   = true
}

# ---- The agent's role lives in nonprod and CANNOT AssumeRole into prod ----
# The trust policy permits AssumeRoleWithWebIdentity only via the EKS OIDC
# issuer for the non-prod cluster, scoped to a specific ServiceAccount.
resource "aws_iam_role" "claude_code" {
  provider = aws.nonprod
  name     = "claude-code"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRoleWithWebIdentity"
      Principal = { Federated = aws_iam_openid_connect_provider.nonprod_eks.arn }
      Condition = {
        StringEquals = {
          "${replace(aws_iam_openid_connect_provider.nonprod_eks.url, "https://", "")}:sub" = "system:serviceaccount:agent-claude-prod:claude-code"
          "${replace(aws_iam_openid_connect_provider.nonprod_eks.url, "https://", "")}:aud" = "sts.amazonaws.com"
        }
      }
    }]
  })
}

# Explicit deny on the agent's role: it cannot AssumeRole into the prod account.
# This deny is in addition to the absence of an allow; deny-overrides-allow in IAM.
resource "aws_iam_role_policy" "claude_code_no_prod" {
  provider = aws.nonprod
  name     = "no-prod-assume-role"
  role     = aws_iam_role.claude_code.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Deny"
      Action = ["sts:AssumeRole", "sts:AssumeRoleWithWebIdentity", "sts:AssumeRoleWithSAML"]
      Resource = [
        "arn:aws:iam::PROD_ACCOUNT_ID:role/*"
      ]
    }]
  })
}

# (the OIDC provider definition for nonprod_eks lives elsewhere in this module)
resource "aws_iam_openid_connect_provider" "nonprod_eks" {
  provider        = aws.nonprod
  url             = var.nonprod_eks_oidc_url
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [var.nonprod_eks_oidc_thumbprint]
}

variable "nonprod_eks_oidc_url"        { type = string }
variable "nonprod_eks_oidc_thumbprint" { type = string }
