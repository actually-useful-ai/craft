#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT HUP INT TERM

grep -q '"$plugin_root/scripts"' "$ROOT/scripts/plugin-parity.sh"
if grep -q -- '-name SKILL.md' "$ROOT/scripts/plugin-parity.sh"; then
  echo "package parity must include non-SKILL files" >&2
  exit 1
fi

write_host() {
  target=$1
  host=$2
  craft_version=$3
  humanize_hash=$4

  printf '%s\tcraft\t%s\tcraft-hash\n' "$host" "$craft_version" >> "$target"
  printf '%s\tintentional-ux\t0.1.0\tux-hash\n' "$host" >> "$target"
  printf '%s\taccessibility\t1.0.0\ta11y-hash\n' "$host" >> "$target"
  if [ "$humanize_hash" != "missing" ]; then
    printf '%s\thumanize\t1.2.0\t%s\n' "$host" "$humanize_hash" >> "$target"
  fi
}

matching="$TMP_DIR/matching.tsv"
write_host "$matching" local 0.3.0 humanize-hash
write_host "$matching" beast 0.3.0 humanize-hash
write_host "$matching" drummer 0.3.0 humanize-hash

matching_output="$TMP_DIR/matching.out"
"$ROOT/scripts/plugin-parity.sh" --fixture "$matching" > "$matching_output"
grep -q 'beast.*craft.*OK' "$matching_output"
grep -q 'drummer.*humanize.*OK' "$matching_output"

drift="$TMP_DIR/drift.tsv"
write_host "$drift" local 0.3.0 humanize-hash
write_host "$drift" beast 0.1.0 humanize-hash
write_host "$drift" drummer 0.3.0 missing

drift_output="$TMP_DIR/drift.out"
if "$ROOT/scripts/plugin-parity.sh" --fixture "$drift" > "$drift_output"; then
  echo "expected drift fixture to fail" >&2
  exit 1
fi
grep -q 'beast.*craft.*DRIFT' "$drift_output"
grep -q 'drummer.*humanize.*MISSING' "$drift_output"

echo "plugin parity fixtures passed"
