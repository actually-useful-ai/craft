# Capability routing scenarios

Use these fixtures in fresh Codex and Claude Code sessions. Record the resolved
skill path, source version or hash, selected role, fallback, observable result,
and verification. Semantic predictions remain assumed until an actual runtime
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

Expected: Horizon supplies three to seven distinct pre-commit possibilities
with evidence labels and cheap probes. It makes zero outside calls, does not
validate a chosen plan, and does not begin implementation.

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
