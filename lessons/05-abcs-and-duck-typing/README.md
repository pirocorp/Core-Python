# 05 — Abstract Base Classes and Interface-Like Contracts

> **Status:** Outline only — awaiting code transcription, validation, and question-driven expansion.  
> **Source:** *Python – Syntax/OOP and ML*, slide(s) 19–21.

## Why this matters to a senior engineer

`abc.ABC`, `@abstractmethod`, nominal vs structural subtyping, duck typing, optional `typing.Protocol` extension.

## Examples present in the source

`Shape(ABC)` with abstract `area`/`perimeter` and `Circle`; `PaymentGateway(ABC)` with credit-card/PayPal implementations.

The slide example(s) must be preserved as attributable source material. Before a snippet is presented as runnable, it must be transcribed accurately, checked for errors, and exercised locally. **No runnable code has been asserted for this module in this initial planning pass.**

## Senior-level comparisons and pitfalls

A C# `interface` does not translate one-to-one into Python `ABC`; the slides present ABC-based contracts, not a separate Python `interface` keyword.

## Initial questions to investigate

When to use an ABC rather than a Protocol or convention? What does Python enforce at instantiation time?

## Discussion notes (to be filled as we work through the code)

Questions from the learner, technically verified answers, edge cases, and any corrections to presentation examples will be recorded here with the related code.

## Acceptance criteria for the finished lesson

- [ ] Preserve the original slide example (or explicitly state that there is none).
- [ ] Include a separate verified, executable version and expected result.
- [ ] Document Python-specific runtime behavior and failure modes.
- [ ] Include at least one meaningful hands-on exercise and validation steps.
- [ ] Incorporate actual questions and answers raised during the walkthrough.
