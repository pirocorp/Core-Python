# 02 — Threads, Processes, and Async I/O

> **Status:** Outline only — awaiting code transcription, validation, and question-driven expansion.  
> **Source:** *Python – Syntax/OOP and ML*, slide(s) 10 (with 8–9 as prerequisites).

## Why this matters to a senior engineer

`threading`, `multiprocessing`, `concurrent.futures`, `asyncio`; process memory isolation; CPU parallelism vs I/O concurrency; picking a model from workload characteristics.

## Examples present in the source

Slide compares multiprocessing and multithreading conceptually; **no runnable comparison code is provided**, so this module needs a new benchmark and I/O example.

The slide example(s) must be preserved as attributable source material. Before a snippet is presented as runnable, it must be transcribed accurately, checked for errors, and exercised locally. **No runnable code has been asserted for this module in this initial planning pass.**

## Senior-level comparisons and pitfalls

Compare .NET `Task`, async/await, and parallel CPU execution with Python `asyncio`, OS threads, and process pools without claiming semantic equivalence.

## Initial questions to investigate

When does a Python thread help? Why isn't `asyncio` a CPU-parallelism workaround? What data must be serialized between processes?

## Discussion notes (to be filled as we work through the code)

Questions from the learner, technically verified answers, edge cases, and any corrections to presentation examples will be recorded here with the related code.

## Acceptance criteria for the finished lesson

- [ ] Preserve the original slide example (or explicitly state that there is none).
- [ ] Include a separate verified, executable version and expected result.
- [ ] Document Python-specific runtime behavior and failure modes.
- [ ] Include at least one meaningful hands-on exercise and validation steps.
- [ ] Incorporate actual questions and answers raised during the walkthrough.
