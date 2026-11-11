# 06 — Inheritance, Multiple Inheritance, and MRO

> **Status:** Outline only — awaiting code transcription, validation, and question-driven expansion.  

## Why this matters to a senior engineer

Dynamic method dispatch, `super()`, method-resolution order (MRO), cooperative multiple inheritance, diamond-pattern hazards.

## Examples present in the source

`Animal` / `Dog` single inheritance; `Bird`, `Flyable`, and `Bird(Flyable)` mixin-style example.

Original reference examples should be preserved independently of our corrections and extensions. Before any referenced snippet is presented as runnable, it must be transcribed accurately, checked for errors, and exercised locally. **This module is an outline and does not yet claim to contain tested runnable examples.**

## Senior-level comparisons and pitfalls

Unlike C# class inheritance, Python permits multiple base classes; this requires understanding MRO and constructor cooperation.

## Initial questions to investigate

Which override wins with multiple bases? How does `super()` differ from a direct parent call?

## Discussion notes (to be filled as we work through the code)

Questions from the learner, technically verified answers, edge cases, and any corrections to presentation examples will be recorded here with the related code.

## Acceptance criteria for the finished lesson

- [ ] Preserve the original reference example (or explicitly state that there is none).
- [ ] Include a separate verified, executable version and expected result.
- [ ] Document Python-specific runtime behavior and failure modes.
- [ ] Include at least one meaningful hands-on exercise and validation steps.
- [ ] Incorporate actual questions and answers raised during the walkthrough.
