# Evidence envelope

Use one compact evidence envelope across the Craft cycle. Update it in place or
carry it forward; do not create a new, conflicting account at every phase.

Record only what changes decisions:

- objective, deliverable, audience, constraints, and authorization boundary;
- selected executor, overlays, governors, auditors, active versions, and any
  fallback actually used;
- decisions and assumptions;
- evidence labeled `Measured`, `Observed`, `Inferred`, `Planned`, or
  `Unavailable`;
- completed checks, failures, gaps, and the next decisive check;
- artifacts or locations needed to reproduce the result;
- final status: `Done`, `Partial`, or `Blocked`.

Use the labels literally. A passing local test is `Measured`; an active package
found in a runtime catalog is `Observed`; an interpretation is `Inferred`; a
check not yet run is `Planned`; and a check the current environment cannot run
is `Unavailable`. Never promote one class into another.

Keep secrets, credentials, raw private prompts, and unrelated machine state out
of the envelope. Preserve dissent and partial failures instead of averaging
them away. At a phase boundary, summarize only `Done`, `Evidence`, `Open`, and
`Next` so the receiving phase can continue without reconstructing the task.
