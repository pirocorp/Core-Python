# 03 — Context Managers and Resource Safety

> **Status:** Outline only — awaiting code transcription, validation, and question-driven expansion.  
> **Source:** *Python – Syntax/OOP and ML*, slide(s) 12–13.

## Why this matters to a senior engineer

Context-manager protocol; deterministic release; exception paths and suppression; `contextlib`; sync and async context managers.

## Examples present in the source

`with open('example.txt', 'r') as file` and a custom `MyContextManager` with `__enter__` / `__exit__`.

The slide example(s) must be preserved as attributable source material. Before a snippet is presented as runnable, it must be transcribed accurately, checked for errors, and exercised locally. **No runnable code has been asserted for this module in this initial planning pass.**

## Senior-level comparisons and pitfalls

Compare `with` to C# `using` / `IDisposable` while distinguishing exception semantics and Python's `__exit__` return value.

## Initial questions to investigate

When is `__exit__` called? What happens when it returns `True`? How do `with` and `try/finally` relate?

## Discussion notes (to be filled as we work through the code)

Questions from the learner, technically verified answers, edge cases, and any corrections to presentation examples will be recorded here with the related code.

## Acceptance criteria for the finished lesson

- [ ] Preserve the original slide example (or explicitly state that there is none).
- [ ] Include a separate verified, executable version and expected result.
- [ ] Document Python-specific runtime behavior and failure modes.
- [ ] Include at least one meaningful hands-on exercise and validation steps.
- [ ] Incorporate actual questions and answers raised during the walkthrough.
