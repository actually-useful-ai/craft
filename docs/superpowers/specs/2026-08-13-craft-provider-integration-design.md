# Craft Provider Integration Design

## Status

Approved in chat on 2026-08-13. This specification turns Craft into the
front door for Chaos, Platforms, Intentional UX, Accessibility, Mobile, and
Humanize while keeping each specialist package independently versioned.

## Objective

Update Craft so it can select, compose, verify, and fleet-audit the specialist
packages without copying their source or weakening their domain authority.
Add a portable Experience Review handoff that preserves task-path,
accessibility, mobile, and documentation evidence without producing a combined
score or conformance claim.

## Constraints

- Craft remains a self-contained Markdown-and-stdlib workflow package with no
  hard dependency on another plugin.
- One most-specific executor owns implementation. Providers, overlays,
  governors, and auditors do not compete for ownership.
- Specialist packages remain independently versioned and keep their existing
  skill names.
- Provider discovery must distinguish an active installation from a source
  checkout, cache, projection, or stale link.
- Missing providers degrade to named evidence standards and an explicit
  limitation; Craft must not invent a provider or fail unrelated work.
- No provider selection expands authorization, permits an outside call, or
  permits a commit, push, publication, or deployment.
- The change must remain portable across the runtime manifests Craft already
  supports.

## Decision

Integrate the packages as first-class optional providers rather than vendoring
their skills or implementation code into Craft.

| Provider | Craft role | Specialist authority |
| --- | --- | --- |
| Chaos | Explicit creative overlay or executor | One bounded creative constraint or remix; its deck remains external and cannot be modified or pushed without separate authorization. |
| Platforms | Domain executor | Platform intake and sub-routing for mobile, TV, KDP, Pebble, store assets, release planning, and web kiosks. |
| Intentional UX | Evidence provider or review executor | Task tuples, state paths, interaction costs, recovery, and observable success evidence. |
| Accessibility | Evidence provider or review executor | Semantics, keyboard behavior, assistive-technology exposure, perception, manual checks, and accessibility verification. |
| Mobile | Implementation evidence provider | Viewport, touch, motion, responsive layout, and measured Web Vitals evidence. |
| Humanize | Documentation overlay or executor | Meaning-preserving prose review with facts, citations, accessibility text, and technical terminology preserved. |

Craft remains responsible for capability selection, phase progression,
authorization boundaries, evidence-envelope continuity, and final status.

## Routing behavior

### Chaos

Select Chaos only when it is explicitly requested or when the request clearly
asks for a deliberately playful constraint or remix. Do not infer it from
“chef's choice,” “impress me,” ordinary brainstorming, or a request merely
containing the word “chaos.”

Chaos may be the executor when the creative constraint is the deliverable. It
may be an overlay when another domain executor is building the artifact. Its
self-maintaining deck is outside Craft's authorization: selecting Chaos never
authorizes editing, committing, or pushing that deck.

If Chaos is missing, Craft may propose one bounded, reversible creative
constraint and label it as a fallback. It must not claim to have invoked Chaos.

### Platforms

Select the top-level Platforms capability as the single domain executor for
platform-delivery work. Platforms owns its internal intake and sub-routing;
Craft does not separately stack `platforms-mobile`, `platforms-tv`, or another
subskill beside it.

Craft retains the authorization gate for publishing, deployment, account
changes, and store submission. Accessibility remains authoritative for access
claims, and Intentional UX remains authoritative for task-path evidence.

If Platforms is missing, Craft may produce a platform-neutral release or
delivery plan using the declared target's primary documentation and must state
that package-specific validation was unavailable.

### Intentional UX

Preserve the existing ownership boundary. Intentional UX owns the task tuple,
state graph, metric-vector evidence, causal recommendation, trade-offs, and
experience acceptance checks. Craft's Skill Auditor owns source/install drift;
Accessibility owns semantic and assistive-technology compliance.

## Experience Review handoff

Craft coordinates an Experience Review only when the work crosses at least two
of the following evidence domains: task path, accessibility, mobile
implementation, or documentation. A single-domain review stays with its
specialist.

The coordinated sequence is:

1. Intentional UX defines materially different task tuples, affected state
   transitions, outcome, and observable success evidence.
2. Accessibility records automated or inspected findings separately from
   manual verification and retains authority over accessibility conclusions.
3. Mobile adds viewport, touch, motion, layout, and performance evidence only
   where observed or measured.
4. Humanize reviews user-facing documentation non-destructively and does not
   alter facts, citations, technical terms, or accessibility wording without
   human approval.
5. Craft returns one evidence envelope and, when a durable artifact is needed,
   a portable Experience Review record suitable for an existing `report`
   artifact consumer.

### Required record

Every coordinated Experience Review must retain:

- unique task-tuple identifiers and the people, input modes, start, outcome,
  and success evidence for each tuple;
- affected state transitions;
- metric or finding provenance labeled `Measured`, `Observed`, or `Assumed`;
- accessibility report reference, finding count, manual-check count, and each
  manual check's owner, environment/input mode, status, evidence or written
  not-applicable justification, and due date when unresolved;
- mobile evidence tied to a target route or component and task tuple;
- documentation-review status and source references;
- recommendations tied to an existing task tuple and containing causal
  evidence, confidence, what would change confidence, trade-off, remediation,
  owner, status, and verification method;
- preserved dissent or unresolved trade-offs;
- `Done`, `Evidence`, `Open`, and `Next` handoff fields.

IDs must be unique. Recommendation references must resolve to an existing task
tuple. Declared counts must match their corresponding arrays. Manual
verification is complete only when at least one declared check exists and each
check has a recorded disposition with the required evidence.

### Evidence boundaries

- No aggregate accessibility or UX score is permitted.
- No pass badge, WCAG-conformance verdict, or release-readiness claim is
  permitted.
- A completed manual-verification ledger means only that every declared check
  has a disposition.
- Source inspection and static fixtures cannot be labeled as a passed keyboard,
  switch, or screen-reader walkthrough.
- Fitts, Core Web Vitals, timing, or geometry values are `Measured` only when
  the measurement and environment are recorded.
- Craft cannot raise the evidence level supplied by a specialist.

The canonical machine-readable schema and typed API remain the responsibility
of Accessibility Devkit. Craft documents and tests the handoff contract but
does not duplicate that schema.

## Fleet bill of materials

Add Chaos, Platforms, and Mobile to `fleet.toml` alongside the already tracked
Craft, Team, Intentional UX, Accessibility, and Humanize packages.

- Platforms declares only the runtime manifests it actually ships.
- Mobile declares only the runtime manifests it actually ships.
- Chaos declares Claude support only until its own repository adds portable
  manifests; unsupported runtimes remain explicit rather than simulated.
- Package refs must be immutable reviewed tags. If a provider has no suitable
  tag, leave it out of the released BOM and report that release blocker rather
  than pinning a moving branch.
- Documentation must list all BOM packages and distinguish manifest support
  from runtime activation.

No legacy link is retired merely because a provider was added to the BOM.

## Documentation

Update Craft's public documentation and repository guidance to describe:

- the expanded optional-provider catalog;
- positive and negative triggers for Chaos and Platforms;
- the Experience Review sequence and evidence boundaries;
- fleet coverage for Chaos, Platforms, and Mobile;
- independent versioning and missing-provider behavior.

Do not claim the specialist packages are bundled or that installing Craft
installs them.

## Tests and acceptance criteria

The implementation is accepted when:

1. Routing tests cover positive, negative, composition, missing-provider, and
   authorization-boundary cases for Chaos and Platforms.
2. Tests prove a coordinated Experience Review preserves specialist ownership,
   required provenance, manual-check accountability, referential integrity,
   dissent, and the no-score boundary.
3. Fleet tests and documentation cover every newly declared package and reject
   unsupported manifest claims or mutable refs.
4. Existing capability-routing, manifest, utility-script, enhancement,
   navigation, and fleet behavior remains green.
5. The package's skill/helper counts do not change.
6. The implementation adds no runtime dependency and vendors no source from the
   specialist repositories.

Runtime semantic scenarios remain `Planned` until exercised in fresh supported
clients; structural tests cannot promote them to `Observed` or `Measured`.

## Files expected to change

- `skills/capability-routing.md`
- `skills/evidence-envelope.md`
- `skills/activate/SKILL.md`
- `skills/discuss/SKILL.md`
- `skills/compose/SKILL.md`
- `skills/distill/SKILL.md`
- `skills/reconsider/SKILL.md`
- `skills/present/SKILL.md`
- `skills/experience-review.md` as a shared reference, not a discoverable skill
- `fleet.toml`
- `README.md`
- `CLAUDE.md`
- `docs/plugin-parity.md`
- routing, fleet, manifest, and documentation tests or fixtures as required

The implementation plan may narrow this list when an existing shared contract
already propagates behavior without editing every phase skill.

## Non-goals

- Copying Chaos, Platforms, Intentional UX, Accessibility, Mobile, or Humanize
  source into Craft.
- Adding a new discoverable Craft skill or changing the public skill count.
- Adding a Python package, database, editor, report viewer, storage service, or
  cross-repository runtime dependency.
- Implementing or changing the Accessibility Devkit JSON Schema in this
  repository.
- Publishing a release, tagging, pushing, opening a pull request, or changing
  installed plugin copies.

## Rollout and rollback

Land the routing and handoff documentation with deterministic regression tests.
Run the full local suite under Python 3.11 or newer, because the fleet
controller uses the standard-library `tomllib` module. Verify discovery and
composition manually in fresh clients before release.

Rollback is a normal revert of the feature commits. Since no specialist source
is vendored and no installation is changed, rollback does not require data
migration or package removal.
