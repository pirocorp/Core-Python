# 02 — Threads, Processes, and Async I/O

> **Status:** Outline only — awaiting code transcription, validation, and question-driven expansion.  

## Why this matters to a senior engineer

`threading`, `multiprocessing`, `concurrent.futures`, `asyncio`; process memory isolation; CPU parallelism vs I/O concurrency; picking a model from workload characteristics.

## Examples present in the source

Compare multiprocessing and multithreading with new runnable CPU-bound and I/O-bound experiments.

Examples must be checked for errors, made independently runnable, and validated with tests. **This module is an outline and does not yet claim to contain tested runnable examples.**

## Senior-level comparisons and pitfalls

Compare .NET `Task`, async/await, and parallel CPU execution with Python `asyncio`, OS threads, and process pools without claiming semantic equivalence.

## Initial questions to investigate

When does a Python thread help? Why isn't `asyncio` a CPU-parallelism workaround? What data must be serialized between processes?

## Discussion notes (to be filled as we work through the code)

Questions from the learner, technically verified answers, edge cases, and any corrections to presentation examples will be recorded here with the related code.

## Acceptance criteria for the finished lesson

- [ ] Include a clear, validated learner-facing example (or explicitly note that none is available yet).
- [ ] Include a separate verified, executable version and expected result.
- [ ] Document Python-specific runtime behavior and failure modes.
- [ ] Include at least one meaningful hands-on exercise and validation steps.
- [ ] Incorporate actual questions and answers raised during the walkthrough.
