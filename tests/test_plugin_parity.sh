#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)

grep -q 'scripts/fleet.py' "$ROOT/scripts/plugin-parity.sh"
grep -q 'fleet.toml' "$ROOT/scripts/plugin-parity.sh"
output=$($ROOT/scripts/plugin-parity.sh --help)
printf '%s\n' "$output" | grep -q 'manifest-declared plugin fleet'
printf '%s\n' "$output" | grep -q -- '--hosts'

echo "plugin parity compatibility wrapper passed"
