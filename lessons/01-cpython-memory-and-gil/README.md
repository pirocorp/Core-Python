# 01 — CPython Memory Model and the GIL

> **Status:** Working lesson for joint review; learner Q&A not yet recorded.
> **Audience:** senior developers with experience in object-oriented and concurrent programming; no introduction to basic programming syntax.

## Learning outcomes

After this lesson you should understand CPython object identity, aliasing and reference counting; the role of the cyclic GC; the traditional CPython GIL and its impact on CPU-heavy threads; the difference between concurrency and parallelism; and the availability of optional **free-threaded CPython** from Python 3.13 onward. Compare these details with .NET/C# rather than assuming equivalent runtime semantics.

## Requirements and quick start

- Ordinary CPython **3.11+**; 3.13+ recommended for inspecting the current GIL status with `sys._is_gil_enabled()`.
- No third-party dependencies. Run from this directory:

```bash
python --version
python examples/reference_count.py
python examples/reference_cycles.py
python examples/factorial_threads.py --n 12000 --repeats 3
python -m unittest discover -s tests -v
```

The alias check should print `True`, an unreachable reference cycle should disappear after `gc.collect()`, the factorial results must match, and all **five unit tests** should pass. Reference-count values, thread durations and GC statistics can vary. Code has been checked on CPython 3.13.5.

## Slide 7 — GIL and reference counting

The original slide includes this REPL example, also preserved verbatim in [source_examples/refcount_slide7.txt](source_examples/refcount_slide7.txt):

```pycon
>>> import sys
>>> a = []
>>> b = a
>>> sys.getrefcount(a)
3
```

1. `a = []` creates a list object, bound to the name `a`.
2. `b = a` creates an **alias** for the same list, not a list copy: `a is b` is `True`.
3. `sys.getrefcount(a)` receives a **temporary argument reference**; on traditional CPython, the simple example therefore reports **3**, even though only `a` and `b` are visible.

The precise count is **not a portable invariant**. More hidden references, interpreter internals, immortal objects and free-threading implementations may affect it. Use `sys.getrefcount` for runtime investigation, not application logic. Compare this with C# reference variables, but remember that .NET does not use ordinary CPython's reference-count-based deallocation algorithm.

Run `python examples/reference_count.py`: it displays the count before and after `b = a` and `del b` and verifies object identity.

### Important addition: cyclic garbage collection

Slide 7 says the object is freed when its reference count reaches zero. This describes the main idea of ordinary CPython reference counting but omits **reference cycles**. A self-referential object can have a nonzero count while no longer reachable from the program. CPython also uses a **cyclic garbage collector** to reclaim many such cycles. Object reclamation does not imply that the OS immediately sees lower process RSS; allocators may retain memory.

`python examples/reference_cycles.py` creates a cycle and observes a weak reference before and after explicit collection. This is **our additional example**, not a slide transcription.

### What the traditional GIL actually protects

The slide's simplified phrase “Race condition Problem => GIL was the solution” concerns the safety of CPython's interpreter/object state (including safe reference-count operations). Traditional CPython generally requires a thread to hold the **Global Interpreter Lock** while executing Python code or accessing objects through the C API. **The GIL is not an application-level lock.** You can still have data races, multi-step update races and inconsistent external I/O. Use synchronization for shared mutable application state.

## Slide 8 — Concurrency is not CPU parallelism

The slide says CPU-bound work is limited by the GIL. Interpret that claim specifically as **ordinary GIL-enabled CPython**. It has multiple OS threads, but only one at a time generally executes Python bytecode. Threads may *interleave*; they do not ordinarily provide multi-core speedup for pure-Python CPU work. Blocking I/O and some native extension operations can **release** the GIL, allowing useful overlap and, in the extension case, possible CPU parallelism.

| Case | GIL-enabled CPython | Consequence |
|---|---|---|
| Pure Python CPU work | Threads alternate bytecode execution | Two threads usually do not give a 2× CPU speedup |
| I/O waits | Thread may release the GIL | Other threads can run during blocking waits |
| Native code that releases GIL | Work can overlap | Avoid blanket claims about every native function |
| Optional free-threaded CPython | Threads can execute Python code simultaneously | Requires thread-safe algorithms and compatible libraries |

The “Single Threaded Execution” phrase on slide 8 is imprecise: a **multithreaded** program really has multiple OS threads, but the GIL restricts concurrent execution of Python bytecode in the standard build.

### Current version context (November 2026)

- **3.13:** optional free-threaded build introduced (initially experimental).
- **3.14:** free-threading officially supported, still **not the default**.
- **3.15:** standard CPython still normally has the GIL. Free-threaded binaries/builds exist; importing incompatible C extensions may re-enable the GIL.
- `sys._is_gil_enabled()`, when available on CPython 3.13+, tells you whether the GIL is currently enabled.
- `sys.getswitchinterval()` normally returns a small *ideal* switching interval (frequently 0.005 s). It is **not** a fixed and fairly distributed CPU time slice. The slide 9 assertion “every thread gets equal 5 ms CPU time and starvation cannot occur” is not guaranteed; scheduling depends on the OS and actual execution.

## Slide 9 — Factorials with two threads

### A faithful transcription (contains a bug)

The original slide snippet is stored in [source_examples/factorial_slide9.txt](source_examples/factorial_slide9.txt), unchanged:

```python
def factorial(num):
    if num < 0:
        return 0
    elif num == 0:
        return 1
    else:
        for i in range(1,num + 1):
            factorial = factorial*i
        return factorial
```

For a positive input, it raises **`UnboundLocalError`** because the *local* variable `factorial` is read before assignment. The source also returns 0 for negative integers, whereas factorial has no mathematical value there. These are defects of the source code, **not GIL demonstrations**.

### Runnable, corrected code

[examples/factorial_threads.py](examples/factorial_threads.py) starts with:

```python
def factorial(num: int) -> int:
    if num < 0:
        raise ValueError("factorial is undefined for negative integers")
    result = 1
    for i in range(2, num + 1):
        result *= i
    return result
```

It additionally executes **two identical factorial workloads** sequentially and with **two Python threads**, measuring wall-clock time via `time.perf_counter()` and verifying equal results. The slide **does not provide** that thread-launching code: it is explicitly a new extension designed to test the slide's claims.

```bash
python examples/factorial_threads.py --n 12000 --repeats 3
```

Expected structure (not predetermined measured values):

```text
Python: CPython <version>
Thread switch interval: <seconds>
GIL enabled right now: <True/False>     # or API unavailable
Two sequential workloads: <seconds>
Two threaded workloads:   <seconds>
Same results:              True
Result bit-length:         <integer>
Wall-clock timings vary: do not assert a fixed ratio or infer thread safety.
```

**Do not expect a fixed duration or speed ratio.** Scheduling, CPU load, processor, native operations and the interpreter build all matter. In a standard GIL-enabled CPython process, two CPU-heavy Python threads generally provide no substantial speedup and may be slower. That does **not** mean the threads execute as a single indivisible sequential block; bytecode execution can interleave.

### Comparison with C#/.NET

C# `Task.Run` can schedule managed CPU work on different thread-pool threads, which can run on separate cores. Ordinary CPython `threading.Thread` cannot simply be assumed to yield the same pure-Python bytecode parallelism. We will cover processes, `asyncio`, pools and separate interpreters in **Lesson 02**.

## Hands-on lab

1. **Aliases:** Predict and execute the `sys.getrefcount(a)` example. Explain why `b = a` does *not* create a copy and why the observed count includes a temporary reference.
2. **Cycles:** Execute the `reference_cycles.py` example. Explain why reference counting alone is insufficient.
3. **Debug the original source:** Copy the original slide 9 function into a disposable REPL and call `factorial(5)`. Inspect the `UnboundLocalError`, then compare the corrected function's result (`120`) and its negative-input behavior.
4. **Benchmark:** Run the two-thread experiment at least three times. Record Python version, GIL state and timings; explain why relative duration can fluctuate.
5. **Validation:** Run the five stdlib unit tests with `python -m unittest discover -s tests -v`.
6. **Engineering scenario:** A service has 8 CPU cores, expensive Python calculations, and high-volume network requests. Why can you not assume 8 standard CPython threads will parallelize pure-Python calculation? What different concurrency models might you choose for computation and I/O? (A full comparison is Lesson 02.)

### Check your understanding

- Does `b = a` copy the object? Why does `a is b` matter?
- Does a GIL prevent *all* application race conditions?
- Can two Python OS threads exist in the same process even if only one executes bytecode at once?
- Why are I/O-bound and CPU-bound workloads different?
- What does the optional free-threaded runtime change, and what does it **not** guarantee?

### Common failures and pitfalls

- Counting only visible names and asserting `getrefcount(a) == 3` in all programs.
- Assuming the absence of visible references immediately reduces process RSS.
- Assuming the GIL eliminates shared-state races.
- Interpreting the switch interval as a guaranteed 5 ms round-robin schedule.
- Treating small benchmark fluctuations as proof of CPU scalability.
- Confusing the slide's broken factorial function with a threading defect.

## Live walkthrough Q&A

**Not yet populated.** We will save real learner questions, answers, and links to relevant code here as they arise, without inventing questions.

## Documentation (verified against current CPython)

- [`sys`: getrefcount, getswitchinterval, _is_gil_enabled](https://docs.python.org/3.15/library/sys.html)
- [`threading`: GIL performance caveats](https://docs.python.org/3.15/library/threading.html)
- [CPython C API: thread states and GIL](https://docs.python.org/3.15/c-api/threads.html)
- [Python free-threading HOWTO](https://docs.python.org/3.15/howto/free-threading-python.html)
- [Python FAQ: free-threading support](https://docs.python.org/3.15/faq/library.html)
- [`gc`: cyclic garbage collector](https://docs.python.org/3.15/library/gc.html)

## Progress

- [x] Slide examples preserved separately.
- [x] Broken slide 9 factorial explained and corrected independently.
- [x] Reference counting, reference cycle, and CPU-thread code tested on CPython 3.13.5.
- [x] Five automated stdlib unit tests; hands-on exercises.
- [ ] Real user questions and detailed answers recorded after our walkthrough.
- [ ] User-approved lesson completion.
