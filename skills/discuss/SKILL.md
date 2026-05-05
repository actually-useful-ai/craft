---
name: discuss
description: "Deliberate, debate, plan, or research before doing the work. Use when you need to think before you act."
allowed-tools: Read, Grep, Glob, Bash, Agent, WebSearch, WebFetch
---

# /craft:discuss

Think before you build. This is the deliberation phase of the craft cycle (`discuss → compose → distill → reconsider → present`).

## Modes

| Mode | When to use |
|------|-------------|
| `--quick` (default) | Fast brainstorm. Two-paragraph response with options + a recommendation. |
| `--debate` | Adversarial debate with at least one critic agent and one supporter. Preserves dissent. |
| `--plan` | Structured plan: scope, sequence, acceptance criteria, assumptions, risks. |
| `--research` | Parallel research fan-out across web/academic/data sources. Aggregates and dedupes. |

## How it picks

If the input is a question and short, `--quick`. If it contains "should we" or compares options, `--debate`. If it asks "how do we build X" with implementation depth, `--plan`. If it asks "what's known about X" or names a topic to investigate, `--research`.

## Procedure

1. **Frame** — restate the question in one sentence. Identify the mode (default `--quick` if unclear).
2. **Think** — based on mode:
   - `--quick`: One pass. Two paragraphs. Recommendation + main tradeoff.
   - `--debate`: Launch `craft-critic` and `craft-scout` in parallel. Optionally `craft-validator`. Each produces a position. Synthesize.
   - `--plan`: Launch `craft-planner` to produce a structured plan. Validate against codebase patterns via `craft-scout`.
   - `--research`: Launch `craft-searcher` and `craft-fetcher` in parallel. Each fans out to multiple sources. Aggregate, dedupe, rank by relevance.
3. **Output** — to stdout. For `--plan` and `--research`, also archive to `~/craft/reports/by-date/YYYY-MM-DD/discuss-<topic>.md`.

## Output format

For `--quick`:
```
## Recommendation
[one or two sentences with the main tradeoff]
```

For `--debate`:
```
## Decision: [one-line]
### Position A (craft-scout)
[claim + evidence]
### Position B (craft-critic)
[counterargument + evidence]
### Synthesis
[verdict with dissent preserved]
```

For `--plan`:
```
## Scope
## Sequence
## Acceptance criteria
## Assumptions and risks
```

For `--research`:
```
## Findings
| Source | Claim | Evidence |
|--------|-------|----------|
## Top three takeaways
```

## Handoffs

`/craft:compose` to start building. `/craft:reconsider` if you want to challenge the deliberation result. `/team` for council debate on big decisions.

## Anti-patterns

- Asking `--debate` mode to settle low-stakes questions — use `--quick` instead.
- Using `--research` when the answer is already in the codebase — use `recon` style search via `craft-searcher` directly.
- Treating a `--plan` output as final without `/craft:reconsider`.
