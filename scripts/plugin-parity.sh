#!/bin/sh
set -eu

PLUGINS="craft intentional-ux accessibility humanize"
HOSTS="local beast drummer"

usage() {
  cat <<'EOF'
Usage: plugin-parity.sh [--fixture PATH]

Compare Craft, Intentional UX, Accessibility, and Humanize versions and skill
hashes across this machine, Beast, and Drummer. Drummer is reached through
Beast's SSH alias.

Environment overrides:
  BEAST_HOST       SSH alias for Beast (default: beast)
  DRUMMER_HOST     SSH alias available from Beast (default: drummer)
  SSH_BIN          SSH command (default: ssh)
EOF
}

fixture=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --fixture)
      [ "$#" -ge 2 ] || { echo "--fixture requires a path" >&2; exit 2; }
      fixture=$2
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

PROBE_SCRIPT='set -eu

hash_stream() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum | awk "{print \$1}"
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 | awk "{print \$1}"
  else
    echo "NO_SHA256"
    return 1
  fi
}

for plugin do
  plugin_root="$HOME/plugins/$plugin"
  manifest="$plugin_root/.codex-plugin/plugin.json"
  skills="$plugin_root/skills"

  if [ ! -f "$manifest" ] || [ ! -d "$skills" ]; then
    printf "%s\tMISSING\t-\n" "$plugin"
    continue
  fi

  version=$(sed -n '\''s/^[[:space:]]*"version"[[:space:]]*:[[:space:]]*"\([^"[:space:]]*\)".*/\1/p'\'' "$manifest" | head -n 1)
  skill_files=$(find "$skills" -type f -name SKILL.md -print | LC_ALL=C sort)

  if [ -z "$version" ] || [ -z "$skill_files" ]; then
    printf "%s\tMISSING\t-\n" "$plugin"
    continue
  fi

  skill_hash=$(
    printf "%s\n" "$skill_files" |
      while IFS= read -r skill_file; do
        relative=${skill_file#"$plugin_root"/}
        printf "%s\n" "$relative"
        cat "$skill_file"
      done |
      hash_stream
  )
  printf "%s\t%s\t%s\n" "$plugin" "$version" "$skill_hash"
done'

evaluate() {
  awk -F '\t' -v plugins="$PLUGINS" -v hosts="$HOSTS" '
    BEGIN {
      OFS = "\t"
      plugin_count = split(plugins, plugin_list, " ")
      host_count = split(hosts, host_list, " ")
      print "HOST", "PLUGIN", "VERSION", "SKILL_HASH", "STATUS"
    }
    NF >= 4 {
      key = $1 SUBSEP $2
      versions[key] = $3
      hashes[key] = $4
      present[key] = 1
    }
    END {
      failed = 0
      for (h = 1; h <= host_count; h++) {
        host = host_list[h]
        for (p = 1; p <= plugin_count; p++) {
          plugin = plugin_list[p]
          key = host SUBSEP plugin
          reference = "local" SUBSEP plugin

          version = present[key] ? versions[key] : "-"
          hash = present[key] ? hashes[key] : "-"

          if (!present[key] || version == "MISSING") {
            status = "MISSING"
          } else if (version == "UNREACHABLE") {
            status = "UNREACHABLE"
          } else if (host == "local") {
            status = "REFERENCE"
          } else if (!present[reference] || versions[reference] == "MISSING") {
            status = "NO_REFERENCE"
          } else if (version != versions[reference] || hash != hashes[reference]) {
            status = "DRIFT"
          } else {
            status = "OK"
          }

          print host, plugin, version, hash, status
          if (status != "OK" && status != "REFERENCE") failed = 1
        }
      }
      exit failed
    }
  ' "$1"
}

if [ -n "$fixture" ]; then
  [ -f "$fixture" ] || { echo "fixture not found: $fixture" >&2; exit 2; }
  evaluate "$fixture"
  exit $?
fi

BEAST_HOST=${BEAST_HOST:-beast}
DRUMMER_HOST=${DRUMMER_HOST:-drummer}
SSH_BIN=${SSH_BIN:-ssh}
matrix=$(mktemp "${TMPDIR:-/tmp}/craft-plugin-parity.XXXXXX")
trap 'rm -f "$matrix"' EXIT HUP INT TERM

append_probe() {
  host=$1
  shift
  if output=$(printf '%s\n' "$PROBE_SCRIPT" | "$@"); then
    printf '%s\n' "$output" | awk -F '\t' -v host="$host" 'BEGIN { OFS="\t" } NF == 3 { print host, $1, $2, $3 }' >> "$matrix"
  else
    for plugin in $PLUGINS; do
      printf '%s\t%s\tUNREACHABLE\t-\n' "$host" "$plugin" >> "$matrix"
    done
  fi
}

# shellcheck disable=SC2086
append_probe local sh -s -- $PLUGINS
# shellcheck disable=SC2086
append_probe beast "$SSH_BIN" -o BatchMode=yes -o ConnectTimeout=10 "$BEAST_HOST" sh -s -- $PLUGINS
# shellcheck disable=SC2086
append_probe drummer "$SSH_BIN" -o BatchMode=yes -o ConnectTimeout=10 "$BEAST_HOST" \
  ssh -o BatchMode=yes -o ConnectTimeout=10 "$DRUMMER_HOST" sh -s -- $PLUGINS

evaluate "$matrix"
