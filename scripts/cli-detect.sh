#!/usr/bin/env bash
# cli-detect.sh — Report which external CLI tools are installed and reachable.
# Output: one line per CLI, "name path available reason"
# Usage: bash cli-detect.sh [--json]

set -euo pipefail

JSON="${1:-}"

declare -a CLIS=("codex" "gemini" "cursor-agent" "aider" "ollama" "claude")

emit_text() {
    printf "%-12s %-50s %-10s %s\n" "$1" "$2" "$3" "$4"
}

emit_json_line() {
    printf '  {"name":"%s","path":"%s","available":%s,"reason":"%s"}' "$1" "$2" "$3" "$4"
}

if [[ "$JSON" == "--json" ]]; then
    echo "{\"clis\":["
    first=1
    for cli in "${CLIS[@]}"; do
        if path=$(command -v "$cli" 2>/dev/null); then
            available="true"
            reason="on-path"
        else
            path=""
            available="false"
            reason="not-installed"
        fi
        if [[ $first -eq 0 ]]; then echo ","; fi
        emit_json_line "$cli" "$path" "$available" "$reason"
        first=0
    done
    echo
    echo "]}"
else
    emit_text "name" "path" "available" "reason"
    emit_text "----" "----" "---------" "------"
    for cli in "${CLIS[@]}"; do
        if path=$(command -v "$cli" 2>/dev/null); then
            emit_text "$cli" "$path" "yes" "on-path"
        else
            emit_text "$cli" "(none)" "no" "not-installed"
        fi
    done
fi
