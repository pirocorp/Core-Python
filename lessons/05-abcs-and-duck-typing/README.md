# 05 — Abstract Base Classes and Interface-Like Contracts

> **Status:** Outline only — awaiting code transcription, validation, and question-driven expansion.  

## Why this matters to a senior engineer

`abc.ABC`, `@abstractmethod`, nominal vs structural subtyping, duck typing, optional `typing.Protocol` extension.

## Examples present in the source

`Shape(ABC)` with abstract `area`/`perimeter` and `Circle`; `PaymentGateway(ABC)` with credit-card/PayPal implementations.

Examples must be checked for errors, made independently runnable, and validated with tests. **This module is an outline and does not yet claim to contain tested runnable examples.**

## Senior-level comparisons and pitfalls

A C# `interface` does not translate one-to-one into Python `ABC`; use ABC-based contracts, not a separate Python `interface` keyword.

## Initial questions to investigate

When to use an ABC rather than a Protocol or convention? What does Python enforce at instantiation time?

## Discussion notes (to be filled as we work through the code)

Questions from the learner, technically verified answers, edge cases, and any corrections to presentation examples will be recorded here with the related code.

## Acceptance criteria for the finished lesson

- [ ] Include a clear, validated learner-facing example (or explicitly note that none is available yet).
- [ ] Include a separate verified, executable version and expected result.
- [ ] Document Python-specific runtime behavior and failure modes.
- [ ] Include at least one meaningful hands-on exercise and validation steps.
- [ ] Incorporate actual questions and answers raised during the walkthrough.
