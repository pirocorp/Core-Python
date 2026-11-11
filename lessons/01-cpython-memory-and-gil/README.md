# 01 — CPython Memory Model and the GIL

> **Status:** Outline only — awaiting code transcription, validation, and question-driven expansion.  
> **Source:** *Python – Syntax/OOP and ML*, slide(s) 7–9.

## Why this matters to a senior engineer

CPython object identity and reference counting; why the GIL exists in traditional CPython; bytecode execution and switching; CPU-bound vs I/O-bound workloads; free-threaded CPython (3.13+).

## Examples present in the source

`sys.getrefcount(a)` with two references; factorial-based CPU-bound thread illustration

The slide example(s) must be preserved as attributable source material. Before a snippet is presented as runnable, it must be transcribed accurately, checked for errors, and exercised locally. **No runnable code has been asserted for this module in this initial planning pass.**

## Senior-level comparisons and pitfalls

Do not map the C# CLR or .NET ThreadPool model directly onto CPython. The default CPython GIL, process isolation, and optional free-threaded builds change architecture decisions.

## Initial questions to investigate

What exactly does `sys.getrefcount` count? Is the GIL a general thread-safety guarantee? Is a 5 ms switch interval a fixed per-thread time slice?

## Discussion notes (to be filled as we work through the code)

Questions from the learner, technically verified answers, edge cases, and any corrections to presentation examples will be recorded here with the related code.

## Acceptance criteria for the finished lesson

- [ ] Preserve the original slide example (or explicitly state that there is none).
- [ ] Include a separate verified, executable version and expected result.
- [ ] Document Python-specific runtime behavior and failure modes.
- [ ] Include at least one meaningful hands-on exercise and validation steps.
- [ ] Incorporate actual questions and answers raised during the walkthrough.
