#!/usr/bin/env bash
# ABOUTME: Lists every K8s ServiceAccount that looks like an agent (by namespace prefix or SA name pattern).
# ABOUTME: Output goes to stdout as JSON lines. Feed into the operator-declared cross-reference job to surface shadow agents.

set -euo pipefail

NAMESPACES_PATTERN="${NAMESPACES_PATTERN:-^agent-}"
SA_PATTERNS=(
  "^claude-"
  "-agent$"
  "-bot$"
)

# 1. Namespace-scoped: every SA in any namespace matching the pattern.
mapfile -t AGENT_NAMESPACES < <(
  kubectl get ns -o jsonpath='{.items[*].metadata.name}' \
    | tr ' ' '\n' \
    | grep -E "$NAMESPACES_PATTERN" || true
)

for ns in "${AGENT_NAMESPACES[@]}"; do
  kubectl get sa -n "$ns" -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.creationTimestamp}{"\n"}{end}' \
    | while IFS=$'\t' read -r name ts; do
      [[ -z "$name" ]] && continue
      jq -nc \
        --arg source "k8s-agent-namespace" \
        --arg namespace "$ns" \
        --arg sa_name "$name" \
        --arg created "$ts" \
        '{source:$source, namespace:$namespace, sa_name:$sa_name, created_at:$created}'
    done
done

# 2. SA-name-pattern: SAs across all namespaces whose name matches an agent pattern.
for pattern in "${SA_PATTERNS[@]}"; do
  kubectl get sa -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}{.metadata.name}{"\t"}{.metadata.creationTimestamp}{"\n"}{end}' \
    | awk -F'\t' -v pat="$pattern" '$2 ~ pat { print }' \
    | while IFS=$'\t' read -r ns name ts; do
        [[ -z "$name" ]] && continue
        jq -nc \
          --arg source "k8s-sa-name-pattern" \
          --arg pattern "$pattern" \
          --arg namespace "$ns" \
          --arg sa_name "$name" \
          --arg created "$ts" \
          '{source:$source, pattern:$pattern, namespace:$namespace, sa_name:$sa_name, created_at:$created}'
      done
done
