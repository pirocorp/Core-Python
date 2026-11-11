# 03 — Context Managers and Resource Safety

> **Status:** Outline only — awaiting code transcription, validation, and question-driven expansion.  

## Why this matters to a senior engineer

Context-manager protocol; deterministic release; exception paths and suppression; `contextlib`; sync and async context managers.

## Examples present in the source

`with open('example.txt', 'r') as file` and a custom `MyContextManager` with `__enter__` / `__exit__`.

Original reference examples should be preserved independently of our corrections and extensions. Before any referenced snippet is presented as runnable, it must be transcribed accurately, checked for errors, and exercised locally. **This module is an outline and does not yet claim to contain tested runnable examples.**

## Senior-level comparisons and pitfalls

Compare `with` to C# `using` / `IDisposable` while distinguishing exception semantics and Python's `__exit__` return value.

## Initial questions to investigate

When is `__exit__` called? What happens when it returns `True`? How do `with` and `try/finally` relate?

## Discussion notes (to be filled as we work through the code)

Questions from the learner, technically verified answers, edge cases, and any corrections to presentation examples will be recorded here with the related code.

## Acceptance criteria for the finished lesson

- [ ] Preserve the original reference example (or explicitly state that there is none).
- [ ] Include a separate verified, executable version and expected result.
- [ ] Document Python-specific runtime behavior and failure modes.
- [ ] Include at least one meaningful hands-on exercise and validation steps.
- [ ] Incorporate actual questions and answers raised during the walkthrough.
