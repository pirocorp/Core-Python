# 09 — Encapsulation, Properties, and Python Conventions

> **Status:** Outline only — awaiting code transcription, validation, and question-driven expansion.  
> **Source:** *Python – Syntax/OOP and ML*, slide(s) 19, 25.

## Why this matters to a senior engineer

Conventions (`_name`), name mangling (`__name`), managed properties, invariants, descriptors as an optional deep dive.

## Examples present in the source

`Student` with `_name`, `_age`, `@property`, and validated age setter.

The slide example(s) must be preserved as attributable source material. Before a snippet is presented as runnable, it must be transcribed accurately, checked for errors, and exercised locally. **No runnable code has been asserted for this module in this initial planning pass.**

## Senior-level comparisons and pitfalls

Python's underscore conventions and runtime object model do not provide identical access enforcement to C# `private`/`protected`.

## Initial questions to investigate

Does a leading underscore make a field private? What does a property protect? What are Python's descriptor mechanics?

## Discussion notes (to be filled as we work through the code)

Questions from the learner, technically verified answers, edge cases, and any corrections to presentation examples will be recorded here with the related code.

## Acceptance criteria for the finished lesson

- [ ] Preserve the original slide example (or explicitly state that there is none).
- [ ] Include a separate verified, executable version and expected result.
- [ ] Document Python-specific runtime behavior and failure modes.
- [ ] Include at least one meaningful hands-on exercise and validation steps.
- [ ] Incorporate actual questions and answers raised during the walkthrough.
