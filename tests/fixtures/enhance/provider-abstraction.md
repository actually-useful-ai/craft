## Decision
Do not start implementation yet. Build a service-local provider port only after confirming the two providers’ API contracts and the service’s Python version. There is no reusable local provider implementation available in scope.
Read-only checks completed July 18, 2026: all project code, tests, docs, and plugin configuration; configured shared-code root /Users/luke/shared plus documented llm_providers and data_fetching modules; PyPI; official Python typing docs. No edits/packages.

## Build on this / Reuse now
No executable local reuse target exists. scripts/llm-query.py conditionally imports llm_providers.ProviderFactory, calls get_provider(name), then complete(prompt). CLAUDE.md and README document it as optional geepers-kernel functionality. /Users/luke/shared and documented modules are absent. Do not copy llm-query.py: CLI script with direct network calls, hard-coded model choices, CLI fallback—not reusable service boundary.

## Learn from
Preserve seam: select named provider, invoke normalized operation; keep provider-specific request/auth/parsing/errors inside adapter. Use small typing.Protocol; Python docs define it for structural subtyping, available since Python 3.8: https://docs.python.org/3/library/typing.html#typing.Protocol checked July 18, 2026. Avoid @runtime_checkable unless truly needed; docs say it checks attribute presence, not signatures: https://docs.python.org/3/library/typing.html#typing.runtime_checkable checked same date.

## Conventional vs niche
Conventional: service-owned dependency-free Protocol + two injected adapters. Stdlib, so license/maintenance N/A; compatibility conditional on Python 3.8+. Niche/specialized: geepers-kernel ProviderFactory. PyPI reports MIT, Python >=3.8, optional provider extras, version 1.2.0 released Feb 20 2026—recent signal. It covers 10+ providers, routing/failover/tracking, broader than a two-provider service unless centralized capability is needed: https://pypi.org/project/geepers-kernel/ checked July 18, 2026. No adoption statistic retrieved; labels do not rely on ranking/popularity.

## Considered and skipped
Existing shared ProviderFactory: skip immediate reuse because documented shared location absent; registry metadata is a lead, exact source/API unverified. Install geepers-kernel: skipped because broad optional dependency before requirements known and installation outside read-only task. abc.ABC: viable stdlib option, not preferred initially because structural typing reduces coupling; suitable if shared implementation/runtime-enforced construction needed: https://docs.python.org/3/library/abc.html checked July 18, 2026. Direct provider SDKs skipped because providers/versions/sync/async/streaming/errors unspecified. Copy plugin direct-call fallback skipped because it combines transport, credentials, calls, CLI. Accessibility N/A: backend-only, no user-facing surface.

## Gap
Smallest construction: normalized request/response; Provider protocol matching sync/async/streaming; two adapters; composition-root registry/factory; contract tests with fake + mocked transports. Validate Python version, provider identities/official SDKs, credentials/config, retry/timeouts, streaming/cancellation, error model, and whether broader kernel is needed.

## Handoff
Hand to /craft:compose flow: implement small service-owned Protocol and two adapters; do not reuse missing shared module or add geepers-kernel by default. First confirm Python >=3.8 and consult providers’ official SDK docs; add fake-provider contract tests and adapter tests. Finish with /craft:reconsider --validate.
