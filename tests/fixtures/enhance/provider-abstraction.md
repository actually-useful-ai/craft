## Decision
Do not start implementation yet. Build a service-local provider port only after confirming the two providers’ API contracts and the service’s Python version. There is no reusable local provider implementation available in scope.
Read-only checks completed July 18, 2026: all project code, tests, documentation, and plugin configuration; `<configured-shared-root>` plus documented provider and data-access abstraction modules; a package registry; official Python typing documentation. No edits/packages.

## Build on this / Reuse now
No executable local reuse target exists. `<project-provider-helper>` conditionally loads an optional provider abstraction, selects a named provider, then invokes one normalized operation. Project instructions and documentation describe it as optional shared functionality. `<configured-shared-root>` and the documented modules are absent. Do not copy `<project-provider-helper>`: it combines direct network calls, fixed model choices, and command-line fallback, so it is not a reusable service boundary.

## Learn from
Preserve seam: select named provider, invoke normalized operation; keep provider-specific request/auth/parsing/errors inside adapter. Use small typing.Protocol; Python docs define it for structural subtyping, available since Python 3.8: https://docs.python.org/3/library/typing.html#typing.Protocol checked July 18, 2026. Avoid @runtime_checkable unless truly needed; docs say it checks attribute presence, not signatures: https://docs.python.org/3/library/typing.html#typing.runtime_checkable checked same date.

## Conventional vs niche
Conventional: service-owned dependency-free Protocol + two injected adapters. Stdlib, so license/maintenance N/A; compatibility conditional on Python 3.8+. Niche/specialized: `<optional-multiprovider-package>`. Its registry record reported MIT, Python >=3.8, optional provider extras, version 1.2.0 released Feb 20 2026—recent signal. It covers 10+ providers, routing/failover/tracking, broader than a two-provider service unless centralized capability is needed; registry evidence checked July 18, 2026. No adoption statistic retrieved; labels do not rely on ranking/popularity.

## Considered and skipped
Existing shared provider abstraction: skip immediate reuse because the documented shared location is absent; registry metadata is a lead, exact source/API unverified. Install `<optional-multiprovider-package>`: skipped because it is a broad optional dependency before requirements are known and installation is outside this read-only task. abc.ABC: viable stdlib option, not preferred initially because structural typing reduces coupling; suitable if shared implementation/runtime-enforced construction is needed: https://docs.python.org/3/library/abc.html checked July 18, 2026. Direct provider SDKs were skipped because providers, versions, sync/async/streaming behavior, and errors are unspecified. Copying the project helper was skipped because it combines transport, credentials, calls, and command-line behavior. Accessibility N/A: backend-only, no user-facing surface.

## Gap
Smallest construction: normalized request/response; Provider protocol matching sync/async/streaming; two adapters; composition-root registry/factory; contract tests with fake + mocked transports. Validate Python version, provider identities/official SDKs, credentials/config, retry/timeouts, streaming/cancellation, error model, and whether broader kernel is needed.

## Handoff
Hand to /craft:compose flow: implement a small service-owned Protocol and two adapters; do not reuse the missing shared module or add `<optional-multiprovider-package>` by default. First confirm Python >=3.8 and consult the providers’ official SDK documentation; add fake-provider contract tests and adapter tests. Finish with /craft:reconsider --validate.
