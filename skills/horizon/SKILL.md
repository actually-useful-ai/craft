---
name: horizon
description: "Return a short ranked set of consequential opportunities and blind spots before a direction hardens. Use for ‘what ideas do you have?’, ‘what am I missing?’, ‘what else should I consider?’, open-ended possibility finding, or an explicit Horizon request; do not use for routine validation, high-volume domain ideation, or critique of an already chosen plan."
---

# /craft:horizon

Answer the question directly with the few ideas most likely to change the
decision. Open the option space just enough to expose a better objective,
missing lever, ignored risk, or simpler path. Horizon is a deliberative executor
when the requested deliverable is an option set; otherwise it supplies
hypotheses to the governing workflow. It does not implement them or replace the
domain executor.

Follow the [capability routing contract](../capability-routing.md) when composing
Horizon with another Craft phase.

## Boundary with neighboring skills

- Use Horizon before commitment: “What else could this become?” or “What am I
  missing?”
- Use Discuss to evaluate known options, recommend one, or turn a direction into
  a plan.
- Use Reconsider after commitment: “Is this plan actually right?” or “What
  breaks if I do this?”
- Use Exemplar to raise the quality target for the selected work, not to create
  the option set.
- Use Chef's Choice to select capabilities and ambition, not to supply the
  substantive ideas itself.
- Use a domain idea-generator for high-volume domain ideation. Horizon returns
  a few consequential options, not one hundred interchangeable concepts.
- Ask and Swarm add outside-model evidence only when separately authorized.

## Procedure

1. Infer the actual decision, underlying outcome, audience, constraints, and
   current direction from the conversation and inspected evidence. Ask only
   when a missing fact would materially change scope, authorization, or the
   ranking.
2. Inspect only the context that could materially change the opportunity set.
   Do not recursively inventory a workspace for an open-ended prompt.
3. Explore these lenses internally:
   - **Objective:** Is the stated task a proxy for a better outcome?
   - **Adjacency:** What nearby capability, audience, asset, or reuse path has
     unusual leverage?
   - **Inversion:** What becomes possible if a default assumption is removed or
     reversed?
   - **Subtraction:** What can disappear, merge, or become automatic?
   - **Recovery:** Which ignored failure, maintenance burden, or exit path
     changes the design?
4. Rank the three to five possibilities with the greatest expected leverage,
   novelty relative to the current direction, and ability to be tested. Include
   at least one **Opportunity** and one **Blind spot**.
5. Label every item from its evidence:
   - `Observed`: explicitly stated by Luke or directly inspected in the supplied
     material.
   - `Inferred`: a conclusion tied to named observed evidence. State the link;
     do not disguise an unsupported possibility as insight.
   If an idea has no evidence anchor, leave it out of the ranked set and use the
   final experiment to gather the missing evidence.
6. Choose one next experiment: the cheapest discriminating probe that could
   reorder the list or retire its most important uncertainty.
7. Stop at decision support unless the user also asks to plan or build. Do not
   quietly expand scope.

## Output contract

Start with the ranked set; do not preface it with a generic restatement or a
brainstorming disclaimer. Keep each item to the label, the idea, why it changes
the decision, and its evidence anchor:

```text
1. [Opportunity|Blind spot] — [name] [Observed|Inferred]
   [What changes, why it matters now, and the evidence anchor.]
```

Use the shortest set that changes the decision. Do not pad to five, repeat the
current plan under new names, or emit generic advice such as “improve
onboarding,” “add personalization,” or “talk to users” without a specific lever
and evidence anchor.

End with exactly one experiment and one state-appropriate handoff:

```text
Next experiment: [one cheap discriminating probe]
Handoff: [one of Discuss, Compose, or Reconsider, with the reason]
```

- Hand to `/craft:discuss --quick` or `--plan` when a choice or plan remains.
- Hand to `/craft:compose` only when the option is selected and implementation
  is already authorized.
- Hand to `/craft:reconsider` when the direction is already committed and needs
  challenge rather than widening.

## Quality bar

Prefer an idea that changes the objective, leverage, or maintenance curve over
a longer feature list. Surface genuine uncertainty and disagreement. Avoid
generic advice, renamed versions of the current plan, ornamental moonshots,
feature fog, and confidence scores without evidence. When the current direction
is already strongest, say so and rank the evidence gap or failure mode that
could still change that conclusion.

## Composition

- Activate or Discuss may select Horizon when the goal is still fluid; return
  the ranked set to Discuss rather than duplicating its recommendation or plan.
- Chef's Choice may use Horizon to widen the search before selecting a stack;
  return the possibilities to that governor.
- Exemplar may raise the quality bar but cannot turn every possibility into a
  flagship feature.
- Intentional UX owns person-to-outcome paths and observed experience evidence.
- Reconsider tests the chosen direction after Horizon narrows the options.
- Compose begins only after the user asks to act or an existing request already
  authorizes implementation.

Success is a smaller, sharper decision set containing at least one materially
new option or blind spot, one experiment capable of changing the ranking, and a
clean transition into decision, implementation, or challenge.
