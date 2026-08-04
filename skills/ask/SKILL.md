---
name: ask
description: "Get one bounded outside-model answer with explicit provider and model provenance. Use when Luke explicitly asks to consult, ask, fan out to, or obtain a second opinion from an external model; also use to configure or verify Craft's portable consultation route."
allowed-tools: Read, Bash
---

# /craft:ask

Ask one configured outside model a focused question. The response is advisory
evidence: preserve its provider and model label, then verify any load-bearing
claim with the appropriate source, test, or domain skill.

Resolve `CRAFT_PLUGIN_ROOT` with [the shared script-path rule](../script-paths.md)
before running the bundled transport. Follow the
[capability routing contract](../capability-routing.md) when composing Ask with
another Craft phase.

## Authorization boundary

An outside call sends the constructed prompt beyond the current runtime and may
incur usage charges. Run it only when the request explicitly asks to consult an
external model, names a provider/model, requests fan-out, or explicitly invokes
Ask. Chef's Choice, Exemplar, activation, discussion, or reconsideration alone
does not authorize a paid call.

Never send credentials, private keys, broad home-directory content, or an entire
repository. Build the smallest useful brief and disclose only the files or facts
needed for the question. A missing provider is a limitation, not permission to
silently substitute another model.

## Provider selection

- In Codex or another OpenAI runtime, use `anthropic` by default so the second
  opinion comes from a different model family.
- In Claude or another Anthropic runtime, use `grok` by default so the second
  opinion comes from Grok 4.5.
- In another or unknown runtime, use `grok` unless Luke chooses a provider.
- Use `openai` only when explicitly selected. The route table pins its model and
  reasoning effort.

The transport owns the live route table. Inspect it with
`bash "$CRAFT_PLUGIN_ROOT/scripts/ask.sh" --list`; do not duplicate model IDs in
command projections or other skills.

## Procedure

1. Confirm that an outside call is authorized and name what context will leave
   the current runtime.
2. Reduce the request to one question with the necessary constraints and
   acceptance criteria. Preserve uncertainty rather than steering the model
   toward agreement.
3. Select the provider from the rule above or Luke's explicit choice.
4. Run `bash "$CRAFT_PLUGIN_ROOT/scripts/ask.sh" PROVIDER "QUESTION"`.
   For multiline briefs, pass `-` as the question and pipe the brief on stdin.
5. Report the returned provider and actual model. Treat a model mismatch or
   missing provenance as a failed consultation.
6. Verify consequential claims independently. Preserve useful dissent instead
   of averaging it away.

`--list` and `--status` make no inference calls. A live liveness check requires
the explicit single-provider form `--probe PROVIDER`; there is no all-provider
health sweep.

## Composition

Ask is the executor when the deliverable is an outside-model answer. In a build,
review, or decision task it is an evidence provider and never owns the final
verdict. Chef's Choice may select it only after the authorization boundary is
satisfied. Exemplar may use the result to request one material revision.
Domain, accessibility, legal, and security skills remain authoritative.

Team and fan-out workflows may consume Ask when it is installed, but remain
independently versioned and must retain a native fallback rather than depending
on a private path.
