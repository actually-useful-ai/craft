# Experience Review contract

Coordinate an Experience Review only when work crosses at least two evidence
domains: task path, accessibility, mobile implementation, or documentation. A
single-domain review stays with its specialist.

## Ownership and sequence

1. **Intentional UX** defines materially different task tuples, affected state
   transitions, outcomes, and observable success evidence.
2. **Accessibility** records inspected or automated findings separately from
   manual checks and retains authority over accessibility conclusions.
3. **Mobile** contributes viewport, touch, motion, layout, and performance
   evidence only where observed or measured.
4. **Humanize** reviews user-facing documentation without changing facts,
   citations, technical terms, or accessibility wording without approval.
5. **Craft** carries one evidence envelope and returns the handoff fields
   `Done`, `Evidence`, `Open`, and `Next`.

## Required record

Return one portable report record. When the user requested or approved file
output, persist it as a durable report artifact at an authorized repository
path. Otherwise return the complete record inline, mark artifact persistence
`Open`, and name the proposed destination, owner, and caller-owned persistence
step in `Next`. Do not describe the inline record as a durable artifact or write
one silently. Retain:

- unique task tuple IDs, people, input mode, start, outcome, success evidence,
  and affected state transitions;
- each finding or metric labeled `Measured`, `Observed`, or `Assumed`, with the
  original specialist provenance preserved;
- accessibility report reference, finding count, manual-check count, and every
  manual check's owner, environment or input mode, status, evidence or written
  not-applicable justification, plus a due date when unresolved;
- mobile evidence linked to a target route or component and an existing task
  tuple;
- documentation-review status and documentation source references;
- every recommendation linked to an existing task tuple, with causal evidence,
  confidence, what would change confidence, trade-off, remediation, owner,
  status, and verification method;
- dissent and unresolved trade-offs.

IDs must be unique. Every recommendation reference must resolve to an existing
task tuple. Declared counts must match their corresponding arrays. Manual
verification is complete only when at least one declared manual check exists
and every check has a disposition with its required evidence.

## Evidence boundaries

- No aggregate score.
- No pass badge.
- No WCAG-conformance verdict.
- No release-readiness claim.
- A completed manual ledger means only that every declared check has a
  disposition.
- Static source or fixtures cannot be evidence of a passed keyboard, switch, or
  screen-reader walkthrough.
- Values are `Measured` only when the method and environment are recorded.
- Craft cannot promote evidence beyond the class supplied by a specialist.

Accessibility Devkit owns any canonical schema and typed API. Craft owns this
coordination contract and does not duplicate that machine-readable schema.
