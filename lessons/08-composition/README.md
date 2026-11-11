# 08 — Composition and Object Collaboration

> **Status:** Outline only — awaiting code transcription, validation, and question-driven expansion.  

## Why this matters to a senior engineer

Object composition, dependency injection, substitutable collaborators, testing seams, composition vs inheritance.

## Examples present in the source

`Engine.start()` composed into `Car.start()` via `self.engine`.

Examples must be checked for errors, made independently runnable, and validated with tests. **This module is an outline and does not yet claim to contain tested runnable examples.**

## Senior-level comparisons and pitfalls

Apply familiar C# composition/DI principles using Python constructor injection and duck-typed dependencies.

## Initial questions to investigate

What is the cost of constructing `Engine()` internally? How can dependencies be injected/tested?

## Discussion notes (to be filled as we work through the code)

Questions from the learner, technically verified answers, edge cases, and any corrections to presentation examples will be recorded here with the related code.

## Acceptance criteria for the finished lesson

- [ ] Include a clear, validated learner-facing example (or explicitly note that none is available yet).
- [ ] Include a separate verified, executable version and expected result.
- [ ] Document Python-specific runtime behavior and failure modes.
- [ ] Include at least one meaningful hands-on exercise and validation steps.
- [ ] Incorporate actual questions and answers raised during the walkthrough.
