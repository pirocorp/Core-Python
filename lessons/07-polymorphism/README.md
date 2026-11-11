# 07 — Runtime Polymorphism and Duck Typing

> **Status:** Outline only — awaiting code transcription, validation, and question-driven expansion.  

## Why this matters to a senior engineer

Overriding, substitutability, duck typing, runtime attribute lookup, `Protocol` as a proposed advanced extension.

## Examples present in the source

`Bird.speak`, `Duck(Bird).speak`, and `make_bird_speak(bird)`.

Examples must be checked for errors, made independently runnable, and validated with tests. **This module is an outline and does not yet claim to contain tested runnable examples.**

## Senior-level comparisons and pitfalls

Contrast C# statically checked virtual/interface calls with Python runtime dispatch and optional static checking.

## Initial questions to investigate

Must `Duck` inherit from `Bird` to work with `make_bird_speak`? Where do contracts live?

## Discussion notes (to be filled as we work through the code)

Questions from the learner, technically verified answers, edge cases, and any corrections to presentation examples will be recorded here with the related code.

## Acceptance criteria for the finished lesson

- [ ] Include a clear, validated learner-facing example (or explicitly note that none is available yet).
- [ ] Include a separate verified, executable version and expected result.
- [ ] Document Python-specific runtime behavior and failure modes.
- [ ] Include at least one meaningful hands-on exercise and validation steps.
- [ ] Incorporate actual questions and answers raised during the walkthrough.
