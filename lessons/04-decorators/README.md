# 04 — Decorators, Closures, and Cross-Cutting Concerns

> **Status:** Outline only — awaiting code transcription, validation, and question-driven expansion.  
> **Source:** *Python – Syntax/OOP and ML*, slide(s) 12, 14–17.

## Why this matters to a senior engineer

First-class functions; closure and evaluation timing; decorator factories; `*args`/`**kwargs`; stacking; `functools.wraps`; sync/async wrappers.

## Examples present in the source

Parameterized `simple_decorator_4_1`, its inner `decorator` and `wrapper`, positional/keyword arguments, a decorated addition function, and output.

The slide example(s) must be preserved as attributable source material. Before a snippet is presented as runnable, it must be transcribed accurately, checked for errors, and exercised locally. **No runnable code has been asserted for this module in this initial planning pass.**

## Senior-level comparisons and pitfalls

Python decorators wrap callable objects; they are not C# attributes, although both can support cross-cutting designs.

## Initial questions to investigate

Why are three nested functions used? When does each function run? Why is `functools.wraps` important?

## Discussion notes (to be filled as we work through the code)

Questions from the learner, technically verified answers, edge cases, and any corrections to presentation examples will be recorded here with the related code.

## Acceptance criteria for the finished lesson

- [ ] Preserve the original slide example (or explicitly state that there is none).
- [ ] Include a separate verified, executable version and expected result.
- [ ] Document Python-specific runtime behavior and failure modes.
- [ ] Include at least one meaningful hands-on exercise and validation steps.
- [ ] Incorporate actual questions and answers raised during the walkthrough.
