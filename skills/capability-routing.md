# Capability routing

Craft is the user-facing workflow. Select capabilities from the goal so the
person does not need to remember the catalog.

## Roles and ownership

- **Executor:** one most-specific skill owns the method and deliverable.
- **Overlay:** changes quality, tone, or evaluation without replacing the executor.
- **Governor:** selects or constrains capabilities without expanding authorization.
- **Auditor:** inspects and reports; it does not apply its own findings.

Use one primary executor. Add a capability only when it changes evidence,
reasoning, implementation, or verification. Never stack skills ceremonially.

## Bundled Craft capabilities

| Capability | Role | Select when |
| --- | --- | --- |
| `ask` | Executor or evidence provider | Luke explicitly requests exactly one outside-model answer or names an external provider/model for one answer. It is the executor only when that answer is the deliverable; otherwise it supplies advisory evidence. |
| `swarm` | Executor or evidence provider | Luke explicitly requests a Swarm, a named Swarm size, or many homogeneous Luna scouts. It is paid, read-only breadth sampling; it does not perform repository-aware work or vote on the verdict. |
| `horizon` | Deliberative executor or hypothesis provider | Luke asks for consequential pre-commit ideas, adjacent possibilities, or what may be missing. It widens the frame without validating or implementing a chosen plan. |
| `chefs-choice` | Governor | Luke delegates an ambitious approach with “chef’s choice,” “surprise me,” “go nuts,” or a standalone “hit it,” “do it,” or “get it done.” |
| `exemplar` | Overlay | The request says “impress me,” “exceptional,” “flagship,” “go beyond adequate,” or explicitly asks for Exemplar. Routine polish and mechanical edits do not qualify. |
| `skill-auditor` | Auditor | The target is a skill catalog, plugin package, installation fleet, routing contract, or source/install drift. |
| `skill-creator` | Executor | The task creates, restructures, packages, or modernizes a skill or skill-bearing plugin. |

Chef’s Choice selects useful resources. Exemplar sets the quality bar. Neither
replaces the domain executor, changes permissions, or overrides a safety,
accessibility, legal, or compliance capability.

Ask and Swarm have an additional disclosure and spend boundary. Selecting them
does not authorize a call: the request must explicitly ask for one external
consultation or for a many-scout Swarm, respectively. Horizon, Chef's Choice,
Discuss, Reconsider, “parallelize,” and generic work fan-out do not authorize a
Swarm. Outside output remains advisory until verified, and missing routes never
trigger silent provider substitution.

Keep adjacent parallel capabilities distinct:

- Ask: exactly one bounded outside answer.
- Swarm: many stateless, read-only samples from the canonical Luna route.
- Fanout: heterogeneous CLI or repository-aware work split by independent item.
- Team or Consensus: stateful roles or a small diverse-model council.
- Horizon: internal pre-commit possibilities with no outside call.
- Reconsider: scrutiny of an existing decision or implementation.

## Optional providers

Discover optional providers from the active runtime catalog before promising or
invoking them. Treat source checkouts, installed packages, caches, projections,
and symlinks as different states; prefer the active canonical installation.

- **Intentional UX:** owns person-to-outcome task paths, state transitions,
  interaction cost, recovery, and experience evidence.
- **Accessibility:** owns semantics, keyboard operation, assistive-technology
  exposure, perception, and accessibility verification. Keep public
  Accessibility Dev Kit independently versioned and apply it only to supported
  platforms.
- **Humanize:** owns meaning-preserving edits to user-facing prose.
- **Domain and platform skills:** own their implementation method.

If a provider is unavailable, use the nearest supported evidence standard and
state the limitation. Do not invent a capability or fail an otherwise feasible
task because a brand-name provider is absent.

## Selection sequence

1. Identify the objective, deliverable, audience, constraints, and authorization.
2. Choose the most-specific executor.
3. Add a governor only when the request delegates approach or sequencing.
4. Add overlays only when their trigger and domain apply.
5. Name the verification evidence before implementation.
6. Report the selected stack in one concise line when selection materially
   changes the work.

During completion, preserve ownership: domain evidence remains authoritative;
Intentional UX owns task-path evidence; Accessibility owns access evidence;
Humanize owns prose edits; Exemplar may request one revision but cannot promote
assumed evidence to observed or measured.

## Phase behavior

- `activate` discovers the workspace and active capability surface, then routes.
- `discuss` selects the stack and acceptance evidence.
- `horizon` may widen the option space before `discuss` recommends or plans.
- `compose` executes with one primary owner and the selected overlays.
- `distill` verifies, audits, simplifies, and exposes unresolved evidence gaps.
- `reconsider` challenges the stack, assumptions, and fallbacks.
- `present` checks authorization and delivers the verified result.

Never require Luke to repeat a capability name after the goal and ambition are
clear.
