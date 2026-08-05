# Software engineering

## Evaluator

A senior engineer reviewing the change six months later, after the original context has faded.

## Governing principle

Use the smallest architecture that makes the important failures difficult.

## Exemplar signals

- Fits the existing architecture and conventions.
- Makes contracts and failure modes explicit.
- Tests the highest-risk behavior rather than performing coverage.
- Uses precise names and stable interfaces.
- Preserves observability and recovery paths where operations require them.
- Removes speculative abstractions and duplicate infrastructure.
- Leaves a change that is easy to review, operate, and reverse.

## Expert-noticed distinctions

- Correctness versus apparent completeness.
- Retryable versus terminal failure.
- Compatibility versus accidental current behavior.
- Operational evidence versus a successful local demo.
- Necessary abstraction versus a one-use wrapper.

## Anti-patterns

- New dependencies for behavior already available in the project.
- Framework rewrites presented as cleanup.
- Generic repositories, managers, factories, or helpers with one caller.
- Happy-path tests that miss the stated risk.
- “Production-ready” claims without deployment, failure, and rollback evidence.

## Acceptance checks

- The requested behavior is verified.
- Relevant failure modes have tests or explicit manual checks.
- The diff is no larger than its value requires.
- New interfaces have a concrete current consumer.
- The result can be explained without relying on cleverness.
