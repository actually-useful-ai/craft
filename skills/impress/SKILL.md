---
name: impress
description: Elevate or critique substantive work beyond adequacy by selecting the right expert evaluator, applying domain-specific quality criteria, and removing performative complexity. Use for “impress me,” “make this exceptional,” “flagship,” “go beyond adequate,” “exemplar critique,” or explicit Impress requests; do not trigger for routine polish or mechanical edits.
license: MIT
---

# Impress

Raise the quality target without expanding authorization or manufacturing sophistication.

Impress is an overlay. The task’s domain skill still governs method, evidence, safety, and deliverables. Impress governs what unusually good judgment looks like.

## Modes

- **Overlay** (default): raise the quality target while the governing skill
  plans, builds, edits, or reviews the work.
- **Critique** (`critique` or `--critique`): diagnose why an existing artifact
  is adequate-but-ordinary, identify the smallest exemplar-quality changes,
  and name sophistication that should be removed. Do not apply the changes
  unless the user also authorizes revision.

Critique stays local to quality and restraint. Route factual correctness or
contract validation to Reconsider `--validate`, invalid framing or structural
replacement to Reconsider `--rebuild`, and dependency impact to Reconsider
`--blast`.

## Composition contract

- Preserve the user’s objective, constraints, voice, budget, and authorization boundary.
- Let the most specific domain skill govern execution.
- Load at most one execution dossier and one domain dossier.
- Reuse research already gathered by another skill; do not repeat reconnaissance for theater.
- Do not force agents, tools, dependencies, features, or extra deliverables.
- Do not claim to remember or have inspected a precedent unless it was actually inspected.
- Do not imitate protected expression from a specific work.

When Chef’s Choice is also active, Chef’s Choice selects useful capabilities and Impress sets the quality bar. When Humanize is active, Humanize owns meaning-preserving prose edits. Accessibility and other safety/compliance skills remain authoritative in their domains.

When Intentional UX is active, Intentional UX owns the person-to-outcome task
tuple, state graph, evidence levels, interaction costs, recovery paths, and
experience acceptance checks. Impress uses that evidence to set the quality
target and select one or two high-value improvements; it does not replace the
task graph or promote Assumed evidence to Observed or Measured.

## Process

### 1. Identify the real objective

Infer, when reasonably possible:

- the literal deliverable;
- the underlying purpose;
- the audience or evaluator whose judgment matters;
- the constraints that cannot move;
- the domain in which excellence should be judged.

Ask only when a missing answer would materially change the result or risk crossing authorization boundaries.

### 2. Establish the competent baseline

Determine internally what an ordinary adequate result would contain. Do not print the baseline unless comparison is useful or requested.

### 3. Select exemplar criteria

Load only the references relevant to the task:

- Software engineering: [references/software.md](references/software.md)
- Product and interface design: [references/product-design.md](references/product-design.md)
- Writing and editing: [references/writing.md](references/writing.md)
- Research and analysis: [references/research.md](references/research.md)
- Historical linguistics and etymology: [references/historical-linguistics.md](references/historical-linguistics.md)
- Corpus linguistics: [references/corpus-linguistics.md](references/corpus-linguistics.md)
- Language classification and exploration: [references/language-classification.md](references/language-classification.md)

Read [references/dossier-contract.md](references/dossier-contract.md) only when creating or revising a dossier.

### 4. Choose the highest-value improvements

Choose one or two changes that materially improve usefulness, rigor, clarity, reliability, accessibility, maintainability, explanatory power, or emotional effect. Prefer consequential judgment over a larger feature count.

### 5. Apply the anti-performance filter

Remove or reject:

- verbosity presented as depth;
- unnecessary sections or repeated conclusions;
- ornamental architecture and unexplained abstraction;
- speculative features and gratuitous dependencies;
- generic premium language;
- novelty without a user or evidence benefit;
- visualization that answers no stated question;
- tools, agents, or citations invoked only to look ambitious;
- confidence scores with no interpretable evidence model.

### 6. Run one completion gate

For substantive work, silently ask:

1. Does the result satisfy the actual objective and constraints?
2. Would the selected evaluator notice sound judgment rather than surface polish?
3. Is there one high-value omission that can be fixed within scope?
4. Is every impressive-looking element useful?
5. What can be simplified without losing value?
6. Is each consequential claim supported by evidence or a verifiable acceptance condition?

Revise once when a material issue is found. If evidence remains missing, disclose the limitation instead of inventing polish. Skip the gate for mechanical one-line work.

Use [references/acceptance-tests.md](references/acceptance-tests.md) when
revising routing, composition, or fallback behavior.

## Critique output

When Critique mode is requested, inspect the supplied artifact and begin the
response exactly with `### Merely competent`. Return the three headings below,
at the shown level and in the shown order. Do not add a preface, disclaimer,
evaluator narration, summary, or divider. Ground each point in the artifact and
selected dossier; use `None found` rather than padding an empty section. Put a
material inspection limitation inside `Merely competent` rather than before the
first heading.

### Merely competent

Name the one to three choices that make the work adequate but ordinary. Do not
summarize the whole artifact or treat personal taste as evidence.

### Exemplar opportunities

Rank the one or two smallest changes with the highest practical effect. State
the evaluator-visible benefit and a verifiable acceptance condition.

### Performative sophistication

Name any element that looks ambitious while reducing usefulness, rigor,
clarity, reliability, or fit. Recommend removal or simplification. Do not add
this category merely to complete the template.

If the critique discovers a correctness, framing, or blast-radius problem,
append at most one final line in the form
`Handoff: /craft:reconsider --mode — reason`, choosing the highest-consequence
problem. Otherwise end with the last critique item. Do not turn the critique
itself into a rebuild or validation pass.

## Output behavior

In Overlay mode, deliver the improved result directly. Do not add an “exemplar
score,” narrate the hidden checklist, or congratulate the result for being
impressive. Explain an unrequested improvement only when it materially affects
scope, tradeoffs, or verification. In Critique mode, use the explicit critique
output above and stop before revision unless revision was also authorized.

## Boundaries

Impress never authorizes deployment, deletion, publication, credential use, external messages, purchases, or broader data access. It does not turn “production-ready,” “best practices,” “polish,” or “improve” into automatic triggers; those phrases should route to the relevant execution skill unless the user explicitly asks for an exemplar-quality pass.
