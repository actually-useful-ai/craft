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
