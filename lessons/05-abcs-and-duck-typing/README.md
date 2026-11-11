# 05 — Abstract Base Classes and Interface-Like Contracts

> **Status:** Outline only — awaiting code transcription, validation, and question-driven expansion.  

## Why this matters to a senior engineer

`abc.ABC`, `@abstractmethod`, nominal vs structural subtyping, duck typing, optional `typing.Protocol` extension.

## Examples present in the source

`Shape(ABC)` with abstract `area`/`perimeter` and `Circle`; `PaymentGateway(ABC)` with credit-card/PayPal implementations.

Original reference examples should be preserved independently of our corrections and extensions. Before any referenced snippet is presented as runnable, it must be transcribed accurately, checked for errors, and exercised locally. **This module is an outline and does not yet claim to contain tested runnable examples.**

## Senior-level comparisons and pitfalls

A C# `interface` does not translate one-to-one into Python `ABC`; the reference examples use ABC-based contracts, not a separate Python `interface` keyword.

## Initial questions to investigate

When to use an ABC rather than a Protocol or convention? What does Python enforce at instantiation time?

## Discussion notes (to be filled as we work through the code)

Questions from the learner, technically verified answers, edge cases, and any corrections to presentation examples will be recorded here with the related code.

## Acceptance criteria for the finished lesson

- [ ] Preserve the original reference example (or explicitly state that there is none).
- [ ] Include a separate verified, executable version and expected result.
- [ ] Document Python-specific runtime behavior and failure modes.
- [ ] Include at least one meaningful hands-on exercise and validation steps.
- [ ] Incorporate actual questions and answers raised during the walkthrough.
