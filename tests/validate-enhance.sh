#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
skill="$repo_root/skills/enhance/SKILL.md"
fixture_dir="$repo_root/tests/fixtures/enhance"

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  exit 1
}

test -f "$skill" || fail "Enhance skill is not discoverable"
test "$(sed -n '1p' "$skill")" = "---" || fail "missing opening frontmatter"
test "$(sed -n '2p' "$skill")" = "name: enhance" || fail "invalid skill name"
grep -Eq '^description: Use when ' "$skill" || fail "invalid discovery description"
test "$(sed -n '4p' "$skill")" = "---" || fail "missing closing frontmatter"

grep -Fq 'project instructions, configuration, environment references, and documentation' "$skill" ||
  fail "shared-code root discovery is not platform-neutral and explicit"

for heading in '### Reuse now' '### Learn from' '### Conventional vs niche' \
  '### Considered and skipped' '### Gap'; do
  grep -Fq "$heading" "$skill" || fail "skill missing $heading"
done

if grep -Eq 'Luke|~/|/home/|dreamer|ProviderFactory|WebSearch|WebFetch|Claude|(^|[^[:alnum:]_])(Task|Explore)([^[:alnum:]_]|$)' "$skill"; then
  fail "skill contains personal, provider-specific, or platform-specific content"
fi

for name in provider-abstraction drag-and-drop command-palette; do
  fixture="$fixture_dir/$name.md"
  test -f "$fixture" || fail "missing post-skill fixture: $name"

  for heading in 'Reuse now' 'Learn from' 'Conventional vs niche' \
    'Considered and skipped' 'Gap'; do
    grep -Eiq "^#{2,3} .*${heading}" "$fixture" || fail "$name missing $heading"
  done

  grep -Eiq '(evidence|checks completed|checked)( date| checked|:)?[^\n]*(20[0-9]{2}-[0-9]{2}-[0-9]{2}|[A-Z][a-z]+ [0-9]{1,2}, 20[0-9]{2}|[0-9]{1,2} [A-Z][a-z]{2} 20[0-9]{2})' "$fixture" ||
    fail "$name missing an evidence date"
  grep -Eq 'https?://[^ )]+' "$fixture" ||
    fail "$name missing a source reference"
  grep -Eq 'No files were changed\.|No edits/packages\.' "$fixture" ||
    fail "$name missing explicit read-only behavior"
  grep -Fq '/craft:compose' "$fixture" ||
    fail "$name missing Craft compose handoff"
done

printf 'PASS: Enhance skill and 3 post-skill fixtures satisfy the contract\n'
