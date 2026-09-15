---
name: ask
description: "Get exactly one bounded outside-model answer with explicit provider and model provenance. Use when Luke explicitly asks to consult, ask, or obtain one second opinion from an external model; also use to configure or verify Craft's portable consultation route. Do not use for a multi-scout Swarm or repository-aware work fan-out."
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
incur usage charges. Run it only when the request explicitly asks to consult one
external model, names a provider/model for one answer, or explicitly invokes
Ask. Chef's Choice, Exemplar, activation, discussion, or reconsideration alone
does not authorize a paid call.

Never send credentials, private keys, broad home-directory content, or an entire
repository. Build the smallest useful brief and disclose only the files or facts
needed for the question. A missing provider is a limitation, not permission to
silently substitute another model.

## Provider selection

- Use native `claude`, `grok`, `zai`, or `ollama` routes only. `anthropic` and
  `xai` are compatibility aliases, not additional voices.
- In Codex/OpenAI, prefer `claude`; in Claude/Anthropic, prefer `grok`.
- Respect an explicit provider choice. An unavailable CLI or login is a failed
  route, never permission to substitute an API, gateway, or different provider.
- The `zai` route uses Claude Code with isolated Z.ai credentials and configuration;
  its underlying model family is GLM, not Anthropic.
- Ollama uses an explicitly configured installed model. Check its model family
  before selecting diverse voices. A cloud-tagged model or remote OLLAMA_HOST
  can send context off-host; local CLI does not itself prove local inference.

See [CLI setup and evidence](references/cli-routes.md) for configuration and
provenance limits. Ask rejects Luna/OpenAI routes. Swarm uses its separate
legacy transport; it is excluded from Ask/Consensus discovery.

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
4. Run `bash "$CRAFT_PLUGIN_ROOT/scripts/ask.sh" --json PROVIDER -` with the
   brief on stdin. The transport uses a fresh scratch directory, disables agent
   tools, and bounds the process lifetime.
5. Report `provider`, `model`, `requested_model`, and `provenance`. A model
   mismatch fails. When the CLI omits the model, label the answer as
   `requested-only`; it cannot count as a verified independent model vote.
   Never turn a requested model or configured provider into reported provenance.
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
