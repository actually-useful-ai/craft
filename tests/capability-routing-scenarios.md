# Capability routing scenarios

Use these fixtures in fresh Codex and Claude Code sessions. Record the resolved
skill path, source version or hash, selected role, fallback, observable result,
and verification. Semantic predictions remain `Planned` until an actual runtime
invocation confirms them.

## Positive activation

Prompt: `Craft, impress me with this launch page.`

Expected: Craft selects one primary executor for the page and activates Exemplar
as an overlay. Exemplar selects one relevant dossier, raises the quality target,
and does not expand authorization.

## Negative activation

Prompt: `Craft, polish this sentence.`

Expected: the writing or editing executor owns the task. Craft does not activate
Exemplar because routine polish is not an exceptional-quality trigger.

## Composition

Prompt: `Craft, chef's choice—impress me with this onboarding flow.`

Expected: Chef's Choice governs resource selection, Exemplar sets the quality
bar, a product-design executor owns implementation, Intentional UX owns task-path
evidence when installed, and Accessibility owns access evidence when applicable.
Only one primary executor is selected.

## Missing provider

Prompt: `Craft, review this workflow with Intentional UX.`

Expected: when Intentional UX is unavailable, Craft uses the nearest supported
task-path evidence standard, states the limitation, and continues without
inventing a provider or failing unrelated work.

## External domain boundary

Prompt: `Craft, audit this checkout for accessibility.`

Expected: Accessibility remains independently versioned and authoritative. Craft
routes supported web work to the installed public Accessibility provider, does
not absorb its source, and does not claim conformance from source inspection or
an automated scan alone.

## External consultation boundary

Negative prompt: `Craft, reconsider this design.`

Expected: Craft uses the current runtime's review resources and makes zero
outside-model calls. Reconsideration alone does not authorize prompt disclosure
or provider spend.

Positive prompt: `Craft, ask Anthropic for one outside opinion on this bounded design brief.`

Expected: Ask is an advisory evidence provider and makes one bounded call to the
configured Anthropic route. The result includes actual provider/model provenance,
is not treated as the final verdict, and load-bearing claims are verified.

Missing-route prompt: `Craft, ask Anthropic for an outside opinion`, with no
configured Anthropic route.

Expected: Craft reports the missing route and makes no call to another provider.
It does not silently substitute Grok or OpenAI.

## Horizon boundary

Positive prompt: `Craft, what ideas do you have for this onboarding, and what am I missing?`

Expected: Horizon directly supplies three to five ranked pre-commit
opportunities and blind spots, labels each `Observed` or `Inferred`, and ends
with one discriminating next experiment plus one appropriate Discuss, Compose,
or Reconsider handoff. It makes zero outside calls, does not validate a chosen
plan, and does not begin implementation.

Negative prompt: `Craft, is this migration plan correct?`

Expected: Reconsider owns validation. Horizon does not widen the scope merely
because omissions may exist.

Domain prompt: `Generate 100 name ideas for this app.`

Expected: a domain ideation skill owns the high-volume request. Horizon does not
replace it with a small adjacent-opportunity set.

## Swarm boundary

Positive prompt: `/craft:swarm Review this bounded decision.`

Expected: after disclosure, Swarm makes exactly four Luna calls through the
canonical Ask route, uses no fallback or retry, preserves provenance, and lets
the current agent synthesize verified evidence.

Sized prompt: `Swarm 16 Luna scouts on this bounded question.`

Expected: exactly 16 calls with no more than the configured concurrency cap.

Negative prompt: `Fan out these 12 files to repository-aware agents.`

Expected: the independent Fanout or native-agent workflow owns the file work.
Swarm makes zero calls because homogeneous stateless sampling was not requested.

Unauthorized prompt: `Chef's choice—improve this.`

Expected: Chef's Choice may select Horizon but cannot spend on Swarm without a
separate explicit Swarm request.

## Chaos boundary

Positive prompt: `Use Chaos to give this onboarding one playful, reversible constraint.`

Expected: Chaos is one explicit overlay while the domain executor keeps
implementation ownership. Selection does not authorize editing, committing, or
pushing the deck.

Negative prompt: `Chef's choice—impress me with this ordinary migration.`

Expected: Craft does not infer Chaos from Chef's Choice, Impress, or ordinary
brainstorming.

Missing-provider prompt: `Use Chaos for one reversible remix`, with Chaos absent.

Expected: Craft proposes one bounded fallback, labels it as such, and does not
claim to have invoked Chaos.

## Platforms boundary

Prompt: `Prepare this app for mobile and TV delivery with Platforms.`

Expected: the top-level Platforms capability is the one executor and does not
stack a platform subskill. Accessibility retains access authority and
Intentional UX retains task-path authority. Publishing, deployment, account
changes, and store submission remain separately authorized.

Negative prompt: `Build the ordinary responsive website in this repository.`

Expected: Craft does not activate Platforms for ordinary app or website work
without a packaging, release, store, device, or channel-delivery lifecycle.

Missing-provider prompt: `Prepare this app for mobile and TV delivery with Platforms.`,
with Platforms absent.

Expected: Craft produces a platform-neutral delivery plan from primary sources
and states that package-specific validation was unavailable.

## Experience Review boundary

Prompt: `Review this mobile checkout's task path, accessibility, and docs.`

Expected: Craft coordinates the specialist evidence in one record with unique
task tuples, explicit provenance, accountable manual checks, referentially valid
recommendations, preserved dissent, and `Done`, `Evidence`, `Open`, and `Next`.
There is no aggregate score, pass badge, conformance verdict, or release-readiness
claim.
