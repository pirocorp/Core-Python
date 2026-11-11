# 06 — Inheritance, Multiple Inheritance, and MRO

> **Status:** Outline only — awaiting code transcription, validation, and question-driven expansion.  

## Why this matters to a senior engineer

Dynamic method dispatch, `super()`, method-resolution order (MRO), cooperative multiple inheritance, diamond-pattern hazards.

## Examples present in the source

`Animal` / `Dog` single inheritance; `Bird`, `Flyable`, and `Bird(Flyable)` mixin-style example.

Examples must be checked for errors, made independently runnable, and validated with tests. **This module is an outline and does not yet claim to contain tested runnable examples.**

## Senior-level comparisons and pitfalls

Unlike C# class inheritance, Python permits multiple base classes; this requires understanding MRO and constructor cooperation.

## Initial questions to investigate

Which override wins with multiple bases? How does `super()` differ from a direct parent call?

## Discussion notes (to be filled as we work through the code)

Questions from the learner, technically verified answers, edge cases, and any corrections to presentation examples will be recorded here with the related code.

## Acceptance criteria for the finished lesson

- [ ] Include a clear, validated learner-facing example (or explicitly note that none is available yet).
- [ ] Include a separate verified, executable version and expected result.
- [ ] Document Python-specific runtime behavior and failure modes.
- [ ] Include at least one meaningful hands-on exercise and validation steps.
- [ ] Incorporate actual questions and answers raised during the walkthrough.
