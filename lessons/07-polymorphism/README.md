# 07 — Runtime Polymorphism and Duck Typing

> **Status:** Outline only — awaiting code transcription, validation, and question-driven expansion.  
> **Source:** *Python – Syntax/OOP and ML*, slide(s) 19, 23.

## Why this matters to a senior engineer

Overriding, substitutability, duck typing, runtime attribute lookup, `Protocol` as a proposed advanced extension.

## Examples present in the source

`Bird.speak`, `Duck(Bird).speak`, and `make_bird_speak(bird)`.

The slide example(s) must be preserved as attributable source material. Before a snippet is presented as runnable, it must be transcribed accurately, checked for errors, and exercised locally. **No runnable code has been asserted for this module in this initial planning pass.**

## Senior-level comparisons and pitfalls

Contrast C# statically checked virtual/interface calls with Python runtime dispatch and optional static checking.

## Initial questions to investigate

Must `Duck` inherit from `Bird` to work with `make_bird_speak`? Where do contracts live?

## Discussion notes (to be filled as we work through the code)

Questions from the learner, technically verified answers, edge cases, and any corrections to presentation examples will be recorded here with the related code.

## Acceptance criteria for the finished lesson

- [ ] Preserve the original slide example (or explicitly state that there is none).
- [ ] Include a separate verified, executable version and expected result.
- [ ] Document Python-specific runtime behavior and failure modes.
- [ ] Include at least one meaningful hands-on exercise and validation steps.
- [ ] Incorporate actual questions and answers raised during the walkthrough.
