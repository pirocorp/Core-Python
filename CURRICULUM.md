# Curriculum — Python for Senior Developers

**Audience:** Experienced software engineers familiar with OOP, concurrency, and application design.  
**Approach:** Learn Python-specific semantics, runtime behavior, idioms, and trade-offs without repeating introductory programming concepts.

## Repository organization

- **Developed lessons:** numbered, human-readable directories at the repository root, so they appear in the main GitHub file listing.
- **Planned topics:** outlines in `lessons/`; promote a topic to the repository root when it has substantive learner-facing documentation and executable exercises.
- Lesson numbering and the curriculum are maintained consistently when a topic is published.
- Internal lesson resources (examples, tests, diagrams) stay inside that lesson's directory.

## Initial learning path

| # | Topic | Core reference examples |
|---|---|---|
| [01](01. CPython Memory Model and the GIL/README.md) | CPython Memory Model and the GIL | `sys.getrefcount(a)` with aliases, factorial-based CPU-bound thread comparison |
| [02](lessons/02-concurrency-strategies/README.md) | Threads, Processes, and Async I/O | Multiprocessing and multithreading concepts; runnable comparisons to be developed |
| [03](lessons/03-context-managers/README.md) | Context Managers and Resource Safety | `with open(...)`, custom `MyContextManager` with `__enter__` / `__exit__` |
| [04](lessons/04-decorators/README.md) | Decorators, Closures, and Cross-Cutting Concerns | Parameterized decorator factory, nested wrapper, positional/keyword arguments |
| [05](lessons/05-abcs-and-duck-typing/README.md) | Abstract Base Classes and Interface-Like Contracts | `Shape(ABC)`, `Circle`, payment gateways |
| [06](lessons/06-inheritance-and-mro/README.md) | Inheritance, Multiple Inheritance, and MRO | `Animal` / `Dog`, `Bird` / `Flyable` |
| [07](lessons/07-polymorphism/README.md) | Runtime Polymorphism and Duck Typing | `Bird.speak`, `Duck.speak`, `make_bird_speak` |
| [08](lessons/08-composition/README.md) | Composition and Object Collaboration | `Engine` composed into `Car` |
| [09](lessons/09-encapsulation-and-properties/README.md) | Encapsulation, Properties, and Python Conventions | `Student`, `@property`, validated setter |

## Quality standard for each lesson

1. Assume programming experience, **not prior Python experience**. Define runtime-specific vocabulary (GIL, MRO, descriptors, etc.) before relying on it.
2. Source/reference snippets are **preparation material only**; do **not** commit them to the repository. Publish only corrected, verified runnable examples, explanations, exercises, and expected outputs.
3. Include Python-specific semantics, practical engineering comparisons with C#/.NET when helpful, pitfalls, expected output, validation commands, tests, and exercises.
4. Integrate technically verified clarifications into the relevant explanation, executable code or exercise. Do not add a separate Q&A section when it merely repeats the lesson or documents editing decisions.
5. Treat language guarantees and CPython-specific implementation details separately.
6. Use normal ```python``` blocks for copyable Python code. Show expected results separately. Avoid interactive-console transcript fences that can render poorly.
7. Keep lesson headings focused on **technical subjects**, without attribution to the original materials.

## Implementation decisions

- **GIL and memory management:** contrast ordinary GIL-enabled CPython with optional free-threading (3.13+) and explain reference-counting, cyclic garbage collection and application synchronization.
- **Factorial:** use a correctly initialized accumulator and a defined policy for negative inputs. A nominal thread-switch interval does not guarantee equal CPU time or prevent starvation.
- **Concurrency:** compare CPU-heavy and I/O-heavy workloads using verified Python exercises, not preliminary notes.
- **Decorators:** teach decorator factories and wrappers, including `functools.wraps`, with validated examples.
- **OOP:** deepen method-resolution order, duck typing, abstract base classes and property behavior beyond generic OOP definitions.
- **Dataclasses:** included in the initial outline only as a possible extension; develop as its own topic if appropriate.

## Future directions

- General language comparisons and performance benchmarking could form a technical appendix.
- Machine learning, neural networks, LLMs, regression and clustering should be a separate learning track.
- A small language parser or compiler could become an advanced capstone.

## Official documentation

- [Python documentation](https://docs.python.org/3/)
- [CPython free-threading HOWTO](https://docs.python.org/3/howto/free-threading-python.html)
- [Python threading reference](https://docs.python.org/3/library/threading.html)

## Progress

Lesson 01 includes working examples, tests and a guided walkthrough, but remains **open for learner questions**. Lessons 02–09 are outlines awaiting their full implementations.
