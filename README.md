# Core-Python — Python for Senior Developers

A Python-focused learning path for experienced software engineers. **Not** a programming-from-scratch tutorial.

## Learning path

See [CURRICULUM.md](CURRICULUM.md) for the nine initial topics and their Python-specific learning goals.

### Published lessons (repository root)

1. [CPython Memory Model and the GIL](01.%20CPython%20Memory%20Model%20and%20the%20GIL/README.md) — complete lesson with runnable examples, tests, diagram, and explanations.
2. [Threads, Processes, and Async I/O](02.%20Threads,%20Processes%20and%20Async%20IO/README.md) — blocking I/O, thread/process pools, event-loop programming, runnable examples and tests.
3. [Context Managers and Resource Safety](03.%20Context%20Managers%20and%20Resource%20Safety/README.md) — deterministic cleanup, exception handling, ExitStack, async with, runnable examples and tests.
4. [Decorators, Closures and Cross-Cutting Concerns](04.%20Decorators,%20Closures%20and%20Cross-Cutting%20Concerns/README.md) — decorators, closure cells, metadata, typed and async wrappers, method binding, and production safety with runnable examples and tests.
5. [Abstract Base Classes and Interface-Like Contracts](05.%20Abstract%20Base%20Classes%20and%20Interface-Like%20Contracts/README.md) — ABC, Protocol, nominal versus structural contracts, virtual registration, payment gateways.
6. [Inheritance, Multiple Inheritance and MRO](06.%20Inheritance%2C%20Multiple%20Inheritance%20and%20MRO/README.md) — MRO, super(), C3, cooperative diamond initialization and failure modes.
7. [Runtime Polymorphism and Duck Typing](07.%20Runtime%20Polymorphism%20and%20Duck%20Typing/README.md) — dynamic method dispatch, duck typing, Protocol and singledispatch.
8. [Composition and Object Collaboration](08.%20Composition%20and%20Object%20Collaboration/README.md) — constructor injection, test doubles, external-service boundaries and ownership.
9. [Encapsulation, Properties and Python Conventions](09.%20Encapsulation%2C%20Properties%20and%20Python%20Conventions/README.md) — properties, validation, name mangling, descriptors and __slots__.

The **root of this repository** contains each developed course lesson as its own numbered, human-readable directory. The nine initial lessons are published as complete modules; future topics may begin as outlines before promotion. This makes practical lessons visible immediately in GitHub's file browser.

## Learning approach

- Assume professional experience with software engineering, object-oriented design, testing, and concurrent systems (C#/.NET comparisons may be used).
- Explain **Python-specific semantics and implementation trade-offs**, not generic definitions of classes, loops, or inheritance.
- **Explain imports when first introduced:** say what each unfamiliar standard-library or third-party name provides. For familiar, language-agnostic concepts (such as a list, queue, iterator, or basic utility function), **one short identification is enough**. For Python-specific concepts (such as context managers, decorators, `asyncio` constructs, or an unusual API contract), add a **concise why/when/how explanation** and a runnable example where needed. Avoid repeating the explanation in every later snippet; refer to the earlier section instead.
- Distinguish imported **library names** from **our own helpers**: show local helper implementations in the lesson before relying on their behavior, with copyable imports and expected output.
- Develop self-contained lessons from the supplied working material, retaining **only learner-facing, verified code and explanations** in the repository.
- Keep preparatory/source snippets outside the repository. Published lessons must be self-contained and include corrected executable examples, tests, and documented behavior.
- As we review code, incorporate useful clarifications directly into the relevant explanation or example; avoid repetitive Q&A transcripts and editorial notes.

## Current status

All nine initial modules are developed and live at the repository root. Any future outlines should be created only when a new topic is planned.

The repository contains only the senior-level course; earlier introductory example projects have been retired.
