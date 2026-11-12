# Curriculum — Python for Senior Developers

**Audience:** Experienced software engineers familiar with OOP, concurrency, and application design.  
**Approach:** Learn Python-specific semantics, runtime behavior, idioms, and trade-offs without repeating introductory programming concepts.

## Repository organization

- **Developed lessons:** numbered, human-readable directories at the repository root, so they appear in the main GitHub file listing.
- **Future topics:** draft outlines may be kept separately until sufficiently complete for publication at the repository root.
- Lesson numbering and the curriculum are maintained consistently when a topic is published.
- Internal lesson resources (examples, tests, diagrams) stay inside that lesson's directory.

## Initial learning path

| # | Topic | Core reference examples |
|---|---|---|
| [01](01.%20CPython%20Memory%20Model%20and%20the%20GIL/README.md) | CPython Memory Model and the GIL | `sys.getrefcount(a)` with aliases, factorial-based CPU-bound thread comparison |
| [02](02.%20Threads,%20Processes%20and%20Async%20IO/README.md) | Threads, Processes, and Async I/O | OS threads, ThreadPoolExecutor, ProcessPoolExecutor, asyncio, TaskGroup and blocking-I/O pitfalls |
| [03](03.%20Context%20Managers%20and%20Resource%20Safety/README.md) | Context Managers and Resource Safety | Files, `__enter__` / `__exit__`, exception suppression, `contextlib`, `ExitStack`, async context managers |
| [04](04.%20Decorators,%20Closures%20and%20Cross-Cutting%20Concerns/README.md) | Decorators, Closures, and Cross-Cutting Concerns | Decorator factories, closure cells, wraps and stacking, ParamSpec typing, sync/async wrappers, method binding, cancellation |
| [05](05.%20Abstract%20Base%20Classes%20and%20Interface-Like%20Contracts/README.md) | Abstract Base Classes and Interface-Like Contracts | `Shape(ABC)`, `Circle`, payment gateways |
| [06](06.%20Inheritance%2C%20Multiple%20Inheritance%20and%20MRO/README.md) | Inheritance, Multiple Inheritance, and MRO | `Animal` / `Dog`, `Bird` / `Flyable` |
| [07](07.%20Runtime%20Polymorphism%20and%20Duck%20Typing/README.md) | Runtime Polymorphism and Duck Typing | `Bird.speak`, `Duck.speak`, `make_bird_speak` |
| [08](08.%20Composition%20and%20Object%20Collaboration/README.md) | Composition and Object Collaboration | `Engine` composed into `Car` |
| [09](09.%20Encapsulation%2C%20Properties%20and%20Python%20Conventions/README.md) | Encapsulation, Properties, and Python Conventions | `Student`, `@property`, validated setter |

## Quality standard for each lesson

1. Assume programming experience, **not prior Python experience**. Define runtime-specific vocabulary (GIL, MRO, descriptors, etc.) before relying on it.
2. Source/reference snippets are **preparation material only**; do **not** commit them to the repository. Publish only corrected, verified runnable examples, explanations, exercises, and expected outputs.
3. Include Python-specific semantics, practical engineering comparisons with C#/.NET when helpful, pitfalls, expected output, validation commands, tests, and exercises.
4. Integrate technically verified clarifications into the relevant explanation, executable code or exercise. Do not add a separate Q&A section when it merely repeats the lesson or documents editing decisions.
5. Treat language guarantees and CPython-specific implementation details separately.
6. Use normal ```python``` blocks for copyable Python code. Show expected results separately. Avoid interactive-console transcript fences that can render poorly.
7. Keep lesson headings focused on **technical subjects**, without attribution to the original materials.
8. Do not include development-progress checklists, editing history, or reviewer-approval status in learner-facing lesson documentation; track those in GitHub PRs/issues instead.

## Implementation decisions

- **GIL and memory management:** contrast ordinary GIL-enabled CPython with optional free-threading (3.13+) and explain reference-counting, cyclic garbage collection and application synchronization.
- **Factorial:** use a correctly initialized accumulator and a defined policy for negative inputs. A nominal thread-switch interval does not guarantee equal CPU time or prevent starvation.
- **Concurrency:** compare CPU-heavy and I/O-heavy workloads using verified Python exercises, not preliminary notes.
- **Decorators:** teach decorator factories and wrappers, including `functools.wraps`, with validated examples.
- **OOP:** demonstrate and test method-resolution order, duck typing, abstract base classes, composition, descriptors and property behavior beyond generic OOP definitions.
- **Dataclasses:** included in the initial outline only as a possible extension; develop as its own topic if appropriate.

## Future directions

- General language comparisons and performance benchmarking could form a technical appendix.
- Machine learning, neural networks, LLMs, regression and clustering should be a separate learning track.
- A small language parser or compiler could become an advanced capstone.

## Official documentation

- [Python documentation](https://docs.python.org/3/)
- [CPython free-threading HOWTO](https://docs.python.org/3/howto/free-threading-python.html)
- [Python threading reference](https://docs.python.org/3/library/threading.html)
