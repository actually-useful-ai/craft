# Audit output format

Use a deterministic report ordered by severity, code, path, and line.

```markdown
# Skill and Plugin Audit — YYYY-MM-DD

## Summary
- Roots: N
- Skills: N
- Plugins: N
- Critical: N
- High: N
- Medium: N
- Low: N
- Clean skills: N / N

## Source map
| Package | Canonical source | Commit/version | Installations | State |

## Critical findings
### S001 · Missing frontmatter
- `path/SKILL.md:1` — evidence. **Fix:** concrete action.

## High findings
...

## Suppressed or profile-specific findings
- Rule, profile, and reason for suppression.

## Clean packages
- `path/to/skill`

## Next actions
1. Repair canonical/source and active-install problems.
2. Repair packaging and routing failures.
3. Address maintainability and style opportunistically.
```

If no finding exists for a heading, say `None`; do not omit the severity. Keep raw inventory and hashes separate from the concise user report when they would overwhelm it.
