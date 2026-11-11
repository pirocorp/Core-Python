# Core-Python — Python for Senior Developers

A Python-focused learning path for experienced software engineers. **Not** a programming-from-scratch tutorial.

## Learning path

See [CURRICULUM.md](CURRICULUM.md) for the nine initial topics and their Python-specific learning goals.

Start with [01 — CPython Memory Model and the GIL](lessons/01-cpython-memory-and-gil/README.md). Later topics cover concurrency models, context managers, decorators, and Python-specific object-oriented design.

## Learning approach

- Assume professional experience with software engineering, object-oriented design, testing, and concurrent systems (C#/.NET comparisons may be used).
- Explain **Python-specific semantics and implementation trade-offs**, not generic definitions of classes, loops, or inheritance.
- Develop self-contained lessons from the supplied working material, retaining **only learner-facing, verified code and explanations** in the repository.
- Keep preparatory/source snippets outside the repository. Published lessons must be self-contained and include corrected executable examples, tests, and documented behavior.
- As we discuss snippets, record the questions and answers inside the relevant lesson and add runnable, testable examples.

## Current status

The files under `lessons/` are **topic declarations**, not completed lessons. Lesson code will be written and validated **topic by topic**, starting with the GIL. Questions-and-answers sections are placeholders until actual discussions.

The older `00. Hello World/` and `01. ReadText/` folders remain unchanged during this initial planning PR. They can be retired separately after review.
