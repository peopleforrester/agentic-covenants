#!/usr/bin/env bash
# ABOUTME: Claude Code PreToolUse hook with deny-then-ask-then-allow precedence.
# ABOUTME: Receives JSON on stdin. Exit 0 = allow. Exit 2 = deny (Claude Code shows the message). Exit other = error.
#
# This is a FILTER, not a BOUNDARY. It raises the cost of the casual and the
# careless path. An adversarial agent with shell access and time gets past it.
# The boundary is the server-side column: RBAC on the target, an admission
# controller, a pre-receive hook, a credential the agent never holds.
# See ../../../framework/BYPASSES.md for the evasion classes this cannot close.

set -euo pipefail

LOG_DIR="${LOG_DIR:-/var/log/agents/claude-code}"
mkdir -p "$LOG_DIR" 2>/dev/null || true

# Hook receives JSON on stdin per Claude Code hook spec.
INPUT="$(cat)"
TOOL_NAME="$(printf '%s' "$INPUT" | jq -r '.tool_name // empty')"
RAW_COMMAND="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')"
FILE_PATH="$(printf '%s' "$INPUT" | jq -r '.tool_input.file_path // empty')"
SESSION_ID="$(printf '%s' "$INPUT" | jq -r '.session_id // "default"')"

deny() {
    local kind="$1"
    local detail="$2"
    printf 'BLOCKED: %s: %s\n' "$kind" "$detail" >&2
    printf '%s DENY %s %s %s=%s command=%s path=%s\n' \
        "$(date -Iseconds)" "$SESSION_ID" "$TOOL_NAME" "$kind" "$detail" \
        "$RAW_COMMAND" "$FILE_PATH" \
        2>/dev/null >> "$LOG_DIR/pre_tool_use.log" || true
    exit 2
}

# ----- Normalization -----
# Patterns match against a normalized copy; the raw string is what gets logged.
# Normalization folds the cheapest evasions into one shape so the pattern list
# does not have to enumerate every spelling of the same command. It closes the
# splitting tricks below and nothing beyond them.
#
#   r""m -rf /            quote splitting
#   r\m -rf /             escape splitting
#   rm${IFS}-rf${IFS}/    $IFS word splitting
#   rm   -rf     /        whitespace padding
normalize() {
    local s="$1"
    s="${s//'""'/}"
    s="${s//"''"/}"
    s="${s//'\'/}"
    s="${s//'${IFS}'/ }"
    s="${s//'$IFS'/ }"
    printf '%s' "$s" | tr '\n\t' '  ' | sed -E 's/[[:space:]]+/ /g; s/^ //; s/ $//'
}

COMMAND="$(normalize "$RAW_COMMAND")"

# ----- Tier-4 hard-deny patterns -----
# These cannot be confirmed past at the client side. The agent must not even
# be asked to run them. Each pattern is a regex applied case-insensitively to
# the normalized command. Case folding matters: `drop table` and `TerraForm
# destroy` are the same instruction to the machine that runs them.
#
# `rm` is handled by the flag parser below rather than by a regex here, because
# -rf, -fr, -Rf, -f -r, and --recursive --force are one command with five
# spellings and a regex per spelling is a list that is always one short.
DENY_PATTERNS=(
  '\bterraform\s+destroy'
  '\bterraform\s+apply.*-auto-approve'
  '\bDROP\s+TABLE'
  '\bDROP\s+DATABASE'
  '\bTRUNCATE\s+TABLE'
  '\bkubectl\s+delete\s+ns'
  '\bkubectl\s+delete\s+namespace'
  '\bkubectl\s+scale\s+.*--replicas=0'
  '\baws\s+s3\s+rb'
  '\baws\s+ec2\s+terminate-instances'
  '\baws\s+rds\s+delete-db-instance'
  '\bgh\s+repo\s+delete'
  '\bgit\s+push\s+(--force|-f)'
  '\bgit\s+reset\s+--hard'
  '\bdd\s+if=/dev/zero\s+of='
  '\bmkfs\b'
  ':\(\)\s*\{\s*:\|:&\s*\};:'
  # Equivalent commands, enumerated in framework/BYPASSES.md as evasions of the
  # patterns above. `find` rooted outside the working tree with a delete action
  # is `rm -rf` with a different name, so it gets the same answer.
  '\bfind\s+(/|~|\$HOME|\$\{HOME\})[^;|&]*(-delete\b|-exec(dir)?\s+(rm|shred)\b|-ok\s+(rm|shred)\b)'
  '\bshred\s+(-[a-z]+\s+)*(/|~|\$HOME)'
)

for pattern in "${DENY_PATTERNS[@]}"; do
  if printf '%s' "$COMMAND" | grep -qiE "$pattern"; then
    deny "deny-pattern" "$pattern"
  fi
done

# ----- rm flag analysis -----
# Parse the flags instead of pattern-matching them, so flag order, flag case,
# combined flags, separated flags, and long flags all reach the same verdict.
#
# The policy line: a recursive delete aimed at an absolute path, $HOME, or ~ is
# denied. The same delete aimed inside the working tree (`rm -rf ./node_modules`)
# is ordinary work and is allowed. A hook that denies both is an outage.
segment_is_recursive_root_rm() {
    local segment="$1"
    local -a tokens=()
    local tok base flags
    local seen_rm=0 recursive=0 root_target=0

    read -r -a tokens <<< "$segment"
    if (( ${#tokens[@]} == 0 )); then
        return 1
    fi

    for tok in "${tokens[@]}"; do
        tok="${tok//'"'/}"
        tok="${tok//"'"/}"
        if [[ -z "$tok" ]]; then
            continue
        fi
        if (( seen_rm == 0 )); then
            # Skip leading env assignments and wrappers such as sudo, and match
            # on the basename so /bin/rm counts.
            base="${tok##*/}"
            if [[ "${base,,}" == "rm" ]]; then
                seen_rm=1
            fi
            continue
        fi
        case "${tok,,}" in
            --recursive|--no-preserve-root)
                recursive=1
                ;;
            --*)
                ;;
            -*)
                flags="${tok,,}"
                if [[ "${flags#-}" == *r* ]]; then
                    recursive=1
                fi
                ;;
            /*|'~'*|'$home'*|'${home}'*)
                root_target=1
                ;;
        esac
    done

    if (( seen_rm == 1 && recursive == 1 && root_target == 1 )); then
        return 0
    fi
    return 1
}

# Judge each simple command on its own, so `rm -r ./build && ls /etc` is not
# read as a recursive delete of /etc.
while IFS= read -r segment; do
    if segment_is_recursive_root_rm "$segment"; then
        deny "recursive-delete" "rm -r aimed at an absolute path, \$HOME, or ~: ${segment}"
    fi
done < <(printf '%s\n' "$COMMAND" | sed -E 's/[;|&]/\n/g')

# ----- Obfuscation defenses -----
# Catches the trivial cases. Not a guarantee. An adversarial agent has more
# obfuscation options than a regex list can enumerate.
OBFUSCATION_PATTERNS=(
  '\bbase64\s+(--decode|-d|-D)\b'
  '\beval\s+\$\('
  '\bbash\s+-c\s+\$\('
  '\bsh\s+-c\s+\$\('
  '\bpython3?\s+-c\s+["\x27]exec\('
  '\bcurl\s+[^|]+\|\s*(bash|sh)\b'
  '\bwget\s+[^|]+\|\s*(bash|sh)\b'
  '\bxargs\s+rm\b'
  # Env-variable indirection: binding a destructive binary to a name so the
  # pattern list never sees the binary. Heuristic, and it will occasionally
  # deny a harmless assignment.
  '(^|[^[:alnum:]_])[A-Za-z_][A-Za-z0-9_]*=['\''"]?(/[A-Za-z0-9_./-]*/)?(rm|shred|mkfs)\b'
)

for pattern in "${OBFUSCATION_PATTERNS[@]}"; do
  if printf '%s' "$COMMAND" | grep -qiE "$pattern"; then
    deny "obfuscation" "$pattern"
  fi
done

# ----- Protected write paths -----
# Editing Terraform state or production Terraform by hand is the documented
# stand-in for running `terraform destroy`, and the Edit and Write tools carry a
# file path rather than a command. Only the detectable cases are covered. Adjust
# these to your own repository layout; they are not a substitute for the
# server-side pre-receive hook or for filesystem ownership.
PROTECTED_PATH_PATTERNS=(
  '\.tfstate(\.backup)?$'
  '(^|/)(infrastructure|infra|terraform|deploy)/prod(uction)?/.*\.(tf|tfvars)$'
)

if [[ -n "$FILE_PATH" ]]; then
  for pattern in "${PROTECTED_PATH_PATTERNS[@]}"; do
    if printf '%s' "$FILE_PATH" | grep -qE "$pattern"; then
      deny "protected-path" "$pattern"
    fi
  done
fi

# ----- Allow with logging -----
printf '%s ALLOW %s %s command=%s path=%s\n' \
  "$(date -Iseconds)" "$SESSION_ID" "$TOOL_NAME" "$RAW_COMMAND" "$FILE_PATH" \
  2>/dev/null >> "$LOG_DIR/pre_tool_use.log" || true

exit 0
