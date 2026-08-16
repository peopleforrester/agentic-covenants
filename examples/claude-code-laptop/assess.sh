#!/usr/bin/env bash
# ABOUTME: Read-only assessment of a workstation against MATURITY.md levels 0-4.
# ABOUTME: Reports a level per concern, takes the minimum, and names the next action.
set -uo pipefail

# This script changes nothing and needs no privileges. It reads configuration
# and reports what it can verify. Where a requirement cannot be checked from
# the outside it says UNKNOWN rather than guessing, because a maturity claim
# that overstates itself is worse than no claim.

AGENT_HOME="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SETTINGS="$AGENT_HOME/settings.json"

RED=$'\033[0;31m'; YEL=$'\033[0;33m'; GRN=$'\033[0;32m'; DIM=$'\033[2m'; BLD=$'\033[1m'; RST=$'\033[0m'
[ -t 1 ] || { RED=""; YEL=""; GRN=""; DIM=""; BLD=""; RST=""; }

declare -A LEVEL          # concern -> achieved level
declare -A BLOCKER        # concern -> what stops the next level
UNKNOWNS=()

pass() { printf '  %s[ok]%s   %s\n' "$GRN" "$RST" "$1"; }
fail() { printf '  %s[--]%s   %s\n' "$RED" "$RST" "$1"; }
unk()  { printf '  %s[??]%s   %s\n' "$YEL" "$RST" "$1"; UNKNOWNS+=("$1"); }
head2() { printf '\n%s%s%s\n' "$BLD" "$1" "$RST"; }

# jq is optional. Without it, JSON-shape checks degrade to UNKNOWN rather than
# to a false pass.
HAVE_JQ=0
command -v jq >/dev/null 2>&1 && HAVE_JQ=1

json_has() {  # json_has <file> <jq-filter>  -> 0 if filter yields non-null/non-empty
    [ "$HAVE_JQ" -eq 1 ] || return 2
    [ -f "$1" ] || return 1
    local out
    out=$(jq -r "$2 // empty" "$1" 2>/dev/null) || return 1
    [ -n "$out" ]
}

# ---------------------------------------------------------------- identity
head2 "Identity"
id_level=0; id_block="no separate agent credential"

operator_arn=""
if command -v aws >/dev/null 2>&1; then
    operator_arn=$(aws sts get-caller-identity --query Arn --output text 2>/dev/null || true)
fi

if [ -n "${AWS_PROFILE:-}" ] && [ "${AWS_PROFILE}" != "default" ]; then
    pass "AWS_PROFILE is set to a non-default profile (${AWS_PROFILE})"
    id_level=1; id_block="credential lifetime not verified"
elif [ -n "$operator_arn" ]; then
    fail "agent would use the default AWS identity: ${operator_arn##*/}"
else
    unk "no cloud CLI configured; cannot compare agent and operator identity"
fi

if [ -n "${AWS_SESSION_TOKEN:-}" ]; then
    pass "cloud credential is a session token, not a long-lived key"
    [ "$id_level" -ge 1 ] && { id_level=2; id_block="credential not bound to a workload identity"; }
elif [ -n "${AWS_ACCESS_KEY_ID:-}" ]; then
    fail "a long-lived access key is present in the environment"
fi

if [ -f "$AGENT_HOME/agent-identity.json" ] || [ -f "./agent-charter.yaml" ]; then
    pass "an agent registration record is present"
else
    fail "no registration record; the agent is not enumerable (see inventory/)"
    [ "$id_level" -ge 1 ] && id_block="agent is not registered in an inventory"
fi
LEVEL[identity]=$id_level; BLOCKER[identity]=$id_block

# ----------------------------------------------------------- authorization
head2 "Authorization"
az_level=0; az_block="no permission configuration found"

if [ -f "$SETTINGS" ]; then
    pass "permission configuration exists at ${SETTINGS/#$HOME/\~}"

    if json_has "$SETTINGS" '.permissions.defaultMode'; then
        mode=$(jq -r '.permissions.defaultMode' "$SETTINGS")
        case "$mode" in
            bypassPermissions|acceptEdits)
                fail "defaultMode is '$mode', which is allow-by-default"
                az_block="defaultMode '$mode' permits unlisted tools" ;;
            *)
                pass "defaultMode is '$mode'"
                az_level=1; az_block="no PreToolUse hook" ;;
        esac
    elif [ "$HAVE_JQ" -eq 0 ]; then
        unk "jq not installed; cannot inspect defaultMode"
    else
        fail "no defaultMode set; the default posture is not explicit"
    fi

    if json_has "$SETTINGS" '.permissions.deny[]'; then
        pass "explicit deny rules are present"
    else
        fail "no deny rules; nothing is denied outside the default mode"
    fi

    if json_has "$SETTINGS" '.hooks.PreToolUse[]'; then
        pass "a PreToolUse hook is configured"
        az_level=2; az_block="hook not verified to actually deny"
        unk "hook deny path not exercised; run its own test to confirm it blocks"
    else
        fail "no PreToolUse hook; nothing evaluates a call before it runs"
    fi
else
    fail "no permission configuration at ${SETTINGS/#$HOME/\~}"
fi
LEVEL[authorization]=$az_level; BLOCKER[authorization]=$az_block

# ------------------------------------------------------------ blast radius
head2 "Blast radius"
br_level=0; br_block="no sandbox applied at launch"

sandbox_tool=""
case "$(uname -s)" in
    Linux)  command -v bwrap >/dev/null 2>&1 && sandbox_tool="bubblewrap" ;;
    Darwin) command -v sandbox-exec >/dev/null 2>&1 && sandbox_tool="sandbox-exec" ;;
esac

if [ -n "$sandbox_tool" ]; then
    pass "a sandbox mechanism is available ($sandbox_tool)"
else
    fail "no sandbox mechanism available on this platform"
fi

if [ -x "./launch-agent" ] || [ -x "$AGENT_HOME/launch-agent" ]; then
    pass "a launch wrapper is present"
    [ -n "$sandbox_tool" ] && { br_level=2; br_block="sandbox inheritance by child processes not verified"; }
    unk "child-process inheritance not verified; spawn a subshell and re-test"
else
    fail "no launch wrapper; a sandbox not applied at launch is not applied"
fi

if [ -n "${AGENT_EGRESS_ALLOWLIST:-}" ]; then
    pass "an egress allowlist is declared"
else
    fail "no egress restriction; the agent can reach any host the operator can"
fi
LEVEL[blast-radius]=$br_level; BLOCKER[blast-radius]=$br_block

# --------------------------------------------------------- approval gating
head2 "Approval gating"
ag_level=0; ag_block="no tiered approval configuration"

if [ -f "$AGENT_HOME/tier-config.yaml" ] || [ -f "./tier-config.yaml" ]; then
    pass "a tiered approval configuration is present"
    ag_level=2; ag_block="no out-of-band path for the highest tier"
    if [ -n "${AGENT_OOB_APPROVAL_URL:-}" ]; then
        pass "an out-of-band approval endpoint is configured"
        ag_level=3; ag_block="approval timing not recorded, so fatigue is unmeasured"
    else
        fail "no out-of-band approval; the top tier approves on the agent's own machine"
    fi
else
    fail "no tiered approval; every action carries the same friction"
fi
LEVEL[approval-gating]=$ag_level; BLOCKER[approval-gating]=$ag_block

# ------------------------------------------------------------ supply chain
head2 "Supply chain"
sc_level=0; sc_block="MCP servers are not allowlisted"

mcp_cfg=""
for candidate in "$AGENT_HOME/mcp-allowlist.json" "./mcp-allowlist.json"; do
    [ -f "$candidate" ] && { mcp_cfg="$candidate"; break; }
done

if [ -n "$mcp_cfg" ]; then
    pass "an MCP allowlist is present (${mcp_cfg/#$HOME/\~})"
    sc_level=1; sc_block="allowlist entries are not hash-pinned"
    if json_has "$mcp_cfg" '..|.sha256? // empty'; then
        pass "allowlist entries carry hash pins"
        sc_level=3; sc_block="tool-description drift is not detected on load"
    else
        fail "allowlist is path-based only; substituting a binary at that path passes"
    fi
else
    fail "no MCP allowlist; any MCP server the config names will launch"
fi

if json_has "$SETTINGS" '.mcpServers' ; then
    n=$(jq -r '.mcpServers | keys | length' "$SETTINGS" 2>/dev/null || echo "?")
    printf '  %s[--]%s   %s MCP server(s) configured; each is untrusted remote code\n' "$DIM" "$RST" "$n"
fi
LEVEL[supply-chain]=$sc_level; BLOCKER[supply-chain]=$sc_block

# ------------------------------------------------------- level 4 modifiers
head2 "Observability (gates Level 4 for every concern)"
observed=1
if [ -f "$AGENT_HOME/vector.toml" ] || [ -n "${AGENT_LOG_SINK:-}" ]; then
    pass "decisions are shipped off the machine"
else
    fail "no off-box log shipping; deleting the local log destroys the record"
    observed=0
fi
if [ -f "$AGENT_HOME/.killswitch-drill" ]; then
    pass "a kill-switch drill has been recorded"
else
    fail "no kill-switch drill recorded; time-to-stop is estimated, not measured"
    observed=0
fi

# ------------------------------------------------------------------ report
head2 "Result"

overall=99; binding=""
for concern in identity authorization blast-radius approval-gating supply-chain; do
    lvl=${LEVEL[$concern]}
    [ "$observed" -eq 0 ] && [ "$lvl" -gt 3 ] && lvl=3
    printf '  %-18s Level %d   %s%s%s\n' "$concern" "$lvl" "$DIM" "${BLOCKER[$concern]}" "$RST"
    if [ "$lvl" -lt "$overall" ]; then overall=$lvl; binding=$concern; fi
done

printf '\n  %sOverall: Level %d%s   (the minimum, not the average)\n' "$BLD" "$overall" "$RST"
printf '  Binding concern: %s%s%s\n' "$BLD" "$binding" "$RST"
printf '  Next action: %s\n' "${BLOCKER[$binding]}"

if [ ${#UNKNOWNS[@]} -gt 0 ]; then
    printf '\n  %s%d requirement(s) could not be verified from outside:%s\n' "$YEL" "${#UNKNOWNS[@]}" "$RST"
    for u in "${UNKNOWNS[@]}"; do printf '    - %s\n' "$u"; done
    printf '  These are not passes. Verify them by hand before claiming the level.\n'
fi

printf '\n  Model and verification criteria: %s\n' "$(dirname "$0")/MATURITY.md"
exit 0
