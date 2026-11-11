# Initial curriculum — Python for Senior Developers

**Source:** *Python – Syntax/OOP and ML* (Teo Parashkevov), supplied presentation, slides 7–26.  
**Audience:** experienced software engineers; prior proficiency in OOP, concurrency, and application design assumed.  
**Phase:** 1 — map source material into topic skeletons; exercises and annotated source-code transcriptions follow incrementally.

## First nine topics

| # | Topic | Source slides | Original example(s) / evidence |
|---|---|---|---|
| [01](lessons/01-cpython-memory-and-gil/README.md) | CPython Memory Model and the GIL | 7–9 | `sys.getrefcount(a)` with two references; factorial-based CPU-bound thread illustration |
| [02](lessons/02-concurrency-strategies/README.md) | Threads, Processes, and Async I/O | 10 (with 8–9 as prerequisites) | Slide compares multiprocessing and multithreading conceptually; **no runnable comparison code is provided**, so this module needs a new benchmark and I/O example. |
| [03](lessons/03-context-managers/README.md) | Context Managers and Resource Safety | 12–13 | `with open('example.txt', 'r') as file` and a custom `MyContextManager` with `__enter__` / `__exit__`. |
| [04](lessons/04-decorators/README.md) | Decorators, Closures, and Cross-Cutting Concerns | 12, 14–17 | Parameterized `simple_decorator_4_1`, its inner `decorator` and `wrapper`, positional/keyword arguments, a decorated addition function, and output. |
| [05](lessons/05-abcs-and-duck-typing/README.md) | Abstract Base Classes and Interface-Like Contracts | 19–21 | `Shape(ABC)` with abstract `area`/`perimeter` and `Circle`; `PaymentGateway(ABC)` with credit-card/PayPal implementations. |
| [06](lessons/06-inheritance-and-mro/README.md) | Inheritance, Multiple Inheritance, and MRO | 19, 22 | `Animal` / `Dog` single inheritance; `Bird`, `Flyable`, and `Bird(Flyable)` mixin-style example. |
| [07](lessons/07-polymorphism/README.md) | Runtime Polymorphism and Duck Typing | 19, 23 | `Bird.speak`, `Duck(Bird).speak`, and `make_bird_speak(bird)`. |
| [08](lessons/08-composition/README.md) | Composition and Object Collaboration | 19, 24 | `Engine.start()` composed into `Car.start()` via `self.engine`. |
| [09](lessons/09-encapsulation-and-properties/README.md) | Encapsulation, Properties, and Python Conventions | 19, 25 | `Student` with `_name`, `_age`, `@property`, and validated age setter. |

## Pedagogy and quality bar

1. Start from **specific Python implementation concepts** that a senior programmer may not know. Do not re-teach generic programming fundamentals.
2. Every completed lesson will contain: the specific source slide(s); a faithful transcription or explicit description of the slide's example; explanatory notes; a runnable, independently validated version; language/runtime pitfalls; tests and expected output; an exercise; and recorded Q&A.
3. Keep a distinction between **what the slides assert**, **what current Python documentation establishes**, and **our additional engineering recommendations**.
4. Never fabricate source code for slides that do not contain executable code. Mark newly authored demonstrations as such.
5. Record emerging clarifications alongside the relevant example, not in a disconnected chat summary.
6. Do not remove the two legacy folders until the new learning path has been reviewed.

## Specific source corrections we must address during implementation

- **Slides 7–10, GIL:** the slides describe traditional GIL-enabled CPython. CPython 3.13 introduced optional free-threaded builds; this is a crucial modern comparison. The standard build still uses the GIL. The GIL does **not** make arbitrary application state thread-safe.
- **Slide 9, factorial:** the source screenshot appears to reference a local `factorial` accumulator before its initialization; the runnable version must clearly distinguish a faithful source transcription from a corrected implementation. The fixed “5 ms per thread” explanation also requires qualification: interpreter switch intervals do not guarantee equal CPU time or no starvation.
- **Slide 10, concurrency:** a conceptual comparison only. We will write and label new examples to test CPU-bound and I/O-bound behavior.
- **Slides 14–17, decorators:** preserve the source decorator structure, then add an explicitly labeled modern example using `functools.wraps`.
- **Slides 19–25, OOP:** maintain the original class examples but deepen Python-specific topics such as MRO, duck typing, ABCs, and property semantics.
- **Slide 2 mentions dataclasses**, but no dedicated implementation lesson appears later in the supplied presentation. Dataclasses therefore remain a **future extension**, not claimed as a covered slide example.

## Source material deliberately not included in the first phase

- Slides 1–6: introduction, generic language advantages, C/Python I/O and speed comparisons. These can become a performance/reference appendix later if needed; the requested curriculum begins at slide 7.
- Slides 27–33: machine learning, neural networks, LLMs, regression, and clustering. Separate possible learning track, not core Python language mechanics.
- Slide 34: potential advanced capstone (a small compiler), not among the initial nine lessons.

## Reference documentation

- [Python 3 standard library and language documentation](https://docs.python.org/3/)
- [CPython free-threading HOWTO](https://docs.python.org/3/howto/free-threading-python.html)
- [Python threading / GIL background](https://docs.python.org/3/library/threading.html)

## Progress

All nine lessons are **outlined only**. Next milestone: implement and verify lesson 01, retain the slide's reference-counting and factorial examples, and record the user's questions as we walk through them.
