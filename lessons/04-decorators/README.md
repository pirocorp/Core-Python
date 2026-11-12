# 04 — Decorators, Closures, and Cross-Cutting Concerns

**Audience:** Experienced C#/.NET and JavaScript engineers who know OOP, closures, and the GoF design patterns but are new to Python's first-class functions and `@decorator` syntax.

## 1. “Decorator” means more than one thing

The word **decorator** is used in related but different programming traditions. In JavaScript and functional programming, **closure** describes captured lexical state, while **higher-order function (HOF)** describes a function that accepts or returns functions. A Python decorator often uses both mechanisms, but they are not interchangeable terms.

| Term | Precise meaning | What is wrapped? |
|---|---|---|
| **Higher-order function (HOF)** | Any function that **accepts a function as an argument, returns a function, or both** | No wrapping is required: e.g. `map()` is a HOF |
| **Closure** | A function **and its captured lexical environment**; can retain bindings after the defining call returns | The captured environment, not a decorated target |
| **Function wrapper** | A function that invokes another function, optionally adding behavior before/after the invocation | Another callable |
| **Python function decorator** | A callable used to **transform or replace a function definition**, typically by returning a wrapper; written with `@name` | A function object |
| **GoF Decorator Pattern** | A **structural** design pattern that gives an object added behavior by wrapping it with another object implementing a compatible interface | An **object instance**, not inherently a class definition |
| **Function composition** | Combining functions so one function's output feeds the next | No specific `@` syntax or wrapping requirement |

These terms overlap, but are **not synonyms**: closures are a lexical-scoping mechanism, not every HOF creates a closure or is a decorator, and function composition is not the same thing as the GoF Decorator Pattern.

**C# mental model:** In C#, a GoF decorator is commonly a class implementing the same interface as the wrapped object, such as an `ILogger` decorator. In Python, ordinary **functions are first-class objects**: they can be passed, returned, stored in variables, and wrapped without creating an extra class. Consequently, a Python *function decorator* often uses a HOF plus a closure. Both approaches can add behavior, but their APIs and mechanics differ.

## 2. Python function decorator — executable example

This code is the actual [`examples/function_decorators.py`](examples/function_decorators.py) demo:

```python
"""A simple Python function decorator built using a higher-order function.

Run from this lesson directory:
    python examples/function_decorators.py
"""


def log_calls(func):
    """Return a function that invokes func with extra logging."""

    def wrapper():
        # 'func' is captured from log_calls's enclosing scope (a closure).
        print("Before")
        func()
        print("After")

    return wrapper


@log_calls
def hello():
    print("Hello")


if __name__ == "__main__":
    hello()
```

Run from `lessons/04-decorators/`:

```bash
python examples/function_decorators.py
```

**Expected output:**

```text
Before
Hello
After
```

### 2.1 Read the syntax one statement at a time

1. **`def log_calls(func):`** — defines a function taking a parameter called `func`. Python does not require a special syntax such as `Func<>` to pass functions: the caller simply passes a function object.
2. **`def wrapper():`** — defines another function *inside* `log_calls`. This is a **nested function**. Its body does **not** run at the moment the `def` statement executes.
3. **`print("Before")`**, **`func()`**, **`print("After")`** — when `wrapper` eventually runs, it logs, calls the original function, then logs again.
4. **`return wrapper`** — returns the **function object itself**. Notice the absence of parentheses: `wrapper` refers to a function; `wrapper()` would call it immediately.
5. **`@log_calls`** — a decorator **applied to the following function definition**, here `hello`. It asks Python to pass that function to `log_calls` and bind the result back to the name `hello`.
6. **`hello()`** — calls the **decorated function**, which is now the returned `wrapper`. It prints `Before`, calls the original `hello` via `func()`, then prints `After`.

### 2.2 The `@` syntax is only shorthand

These two versions achieve the **same decoration**:

| Decorator syntax | Equivalent explicit assignment |
|---|---|
| `@log_calls` above `def hello(): ...` | Define `hello` normally, then execute `hello = log_calls(hello)` |

The order of events matters:

- **At function definition time:** Python creates the original `hello` function; applies `log_calls(hello)`; and rebinds the name `hello` to the resulting `wrapper` function. This is when the **decorator function** runs.
- **Later, at `hello()` call time:** the wrapper runs; **only then** do `Before`, the original `Hello`, and `After` get printed.

This example is a **function decorator**, not the GoF class-based pattern. The variable `func` survives after `log_calls` returns because the nested `wrapper` **closes over** it. This captured reference is called a **closure**. It is how `wrapper` still knows which original function it must call.

### 2.3 Important limitation of the minimal example

This introductory wrapper accepts **no arguments** and returns no result. It is correct for this particular `hello()` demo, but is **not yet a general-purpose decorator**. Production wrappers typically accept `*args` and `**kwargs`, return the wrapped function's result, and use `functools.wraps` to preserve metadata such as `__name__` and `__doc__`. Sections 7–8 implement and test these improvements rather than hiding their behavior behind demo imports.

The `"After"` line also does **not run if `func()` raises an unhandled exception**. If after-action cleanup must always run, use `try/finally`, as discussed in Lesson 03.

## 3. Closures in JavaScript, Python and C# — the deeper mechanism

A **closure** is a function together with access to the lexical environment in which it was created. A nested function can continue to use a binding from its enclosing scope **after that outer function has returned**. This is a language mechanism; it is **not a synonym** for a higher-order function or for the Decorator Pattern.

The examples in Section 2 involve **all three concepts at once**:

- `log_calls(func)` is a **higher-order function** because it accepts and returns a function.
- Its returned `wrapper` is a **closure** because it refers to the enclosing function's `func` binding after `log_calls` finishes.
- `@log_calls` applies the wrapper as a **Python function decorator**.

They are distinct: a HOF can operate on functions without producing a closure (for example, `map(function, iterable)`), and a closure can be used for encapsulating state without decorating anything.

### 3.1 JavaScript — familiar lexical closure syntax

This is the complete runnable [`examples/closures.js`](examples/closures.js):

```javascript
"use strict";

// JavaScript lexical closure: the nested function retains the count binding.
function makeCounter(start = 0) {
    let count = start;

    return function increment() {
        count += 1;
        return count;
    };
}

const first = makeCounter(10);
const second = makeCounter(0);
console.log("first:", first(), first());
console.log("second:", second());
console.log("first again:", first());

// var creates ONE function-scoped binding shared by all closures.
const late = [];
for (var i = 0; i < 3; i++) {
    late.push(() => i * 3);
}

// let in a for loop gives each iteration a distinct captured binding.
const snapshots = [];
for (let j = 0; j < 3; j++) {
    snapshots.push(() => j * 3);
}
console.log("var loop:", late.map(fn => fn()));
console.log("let loop:", snapshots.map(fn => fn()));
```

Run it with Node.js installed: `node examples/closures.js`.

**Expected output:**

```text
first: 11 12
second: 1
first again: 13
var loop: [ 9, 9, 9 ]
let loop: [ 0, 3, 6 ]
```

The syntax matters:

- `function makeCounter(start = 0)` defines an ordinary JavaScript function with a default argument.
- `let count = start` creates a binding local to each call of `makeCounter`.
- `return function increment() { ... }` **returns a function object**, instead of calling it. `increment` continues to access its enclosed `count` binding later.
- `count += 1` **mutates** the captured binding. The closure does not freeze the initial number.
- `const first = makeCounter(10)` and `const second = makeCounter(0)` are **two separate calls**, so they create **independent** closure environments.

Notice that closures keep **bindings / environments**, not necessarily immutable snapshots of values. The distinction explains both the counter and the loop trap:

- In `for (var i = 0; ... )`, the closures share the **same function-scoped `i`**. After the loop, it is `3`, so all three functions return `9`.
- In `for (let j = 0; ... )`, JavaScript establishes a **new per-iteration binding** for `j`; each closure sees its corresponding `0`, `1` or `2`, and returns `0`, `3`, `6`.
- The `() => expression` syntax is an **arrow function**; `late.push(() => i * 3)` stores a callback for *later*, not the numeric result now. `late.map(fn => fn())` calls each stored function.

This is lexical scope, not JavaScript's `this` binding mechanism: arrow functions also lexically bind `this`, but **`this` capture and lexical variable capture are different concepts**.

### 3.2 Python — closures, `nonlocal` and late binding

Here is the **exact runnable** [`examples/closures.py`](examples/closures.py):

```python
"""Closures: lexical capture, nonlocal state and late-binding loop variables.

Run:
    python examples/closures.py
"""


def make_counter(start: int = 0):
    count = start

    def increment() -> int:
        nonlocal count  # Rebind count in the enclosing make_counter scope.
        count += 1
        return count

    return increment  # Return a function; do NOT invoke increment() here.


def demonstrate_late_binding() -> tuple[list[int], list[int]]:
    late = []
    snapshots = []

    for factor in range(3):  # factor takes 0, 1, then 2.
        late.append(lambda value: factor * value)
        snapshots.append(lambda value, factor=factor: factor * value)

    # The late lambdas all refer to the SAME factor binding, now equal to 2.
    # The default argument is evaluated when each lambda is created.
    return [fn(3) for fn in late], [fn(3) for fn in snapshots]


def main() -> None:
    first = make_counter(10)
    second = make_counter(0)
    print("first:", first(), first())
    print("second:", second())
    print("first again:", first())

    late, snapshots = demonstrate_late_binding()
    print("late:", late)
    print("snapshots:", snapshots)


if __name__ == "__main__":
    main()
```

Run `python examples/closures.py`.

**Expected output:**

```text
first: 11 12
second: 1
first again: 13
late: [6, 6, 6]
snapshots: [0, 3, 6]
```

Read the Python syntax carefully:

1. `def make_counter(start: int = 0):` defines a function with a typed, defaulted parameter. Unlike C# types, the annotation `: int` is not runtime-enforced.
2. `def increment() -> int:` is a **nested function**. `return increment` hands the function object to the caller; `increment()` would call it immediately.
3. `nonlocal count` tells Python that assignments to `count` inside `increment` should **rebind the variable from its nearest enclosing function scope** rather than create a new local variable. Without `nonlocal`, `count += 1` would raise `UnboundLocalError` when invoked, because Python sees the assignment and treats `count` as local.
4. `first = make_counter(10)` and `second = make_counter(0)` create separate captured `count` bindings. As in JavaScript, the state is **per call**.
5. `for factor in range(3):` iterates over `0, 1, 2`, but Python's `for` statement does **not** introduce a new lexical scope per iteration. `late.append(lambda value: factor * value)` captures the **shared `factor` binding**.
6. `lambda value: ...` defines a small anonymous function. `late.append(...)` stores that callable, while `fn(3)` in the comprehension later invokes it.
7. `lambda value, factor=factor: factor * value` deliberately uses a **default argument** evaluated when each lambda is created. Each function therefore stores the current value (`0`, `1` or `2`). This is a *snapshot through a default parameter*, not a new loop scope.
8. `[fn(3) for fn in late]` is a **list comprehension**: call each function, collect the results in a new list. A C# analogy is `late.Select(fn => fn(3)).ToList()`, with different closure semantics around the loop variable.

**Beware:** Python's capture of `factor` is *late binding*: by the time the callbacks run, the loop has finished and `factor == 2`. That is why each returns `6`. This is closely analogous to the old `var`-loop trap in JavaScript; **Python does not offer a direct `let`-per-iteration loop binding**. Explicitly capture with a default parameter or a factory function when you need a distinct value.

### 3.3 C# — captured local variables and the `for` loop trap

C# lambdas can also form closures over local variables:

```csharp
using System;
using System.Collections.Generic;

Func<int> MakeCounter(int start = 0)
{
    int count = start;

    return () =>
    {
        count++;  // Captured variable from MakeCounter's scope.
        return count;
    };
}

var first = MakeCounter(10);
var second = MakeCounter(0);

Console.WriteLine($"first: {first()}, {first()}");
Console.WriteLine($"second: {second()}");
Console.WriteLine($"first again: {first()}");

// In a for loop, all lambdas capture the same i variable.
var late = new List<Func<int>>();
for (int i = 0; i < 3; i++)
{
    late.Add(() => i * 3);
}

// Create a NEW local per iteration to preserve the current value.
var snapshots = new List<Func<int>>();
for (int j = 0; j < 3; j++)
{
    int captured = j;
    snapshots.Add(() => captured * 3);
}

Console.WriteLine($"for loop: {string.Join(", ", late.ConvertAll(fn => fn()))}");
Console.WriteLine($"snapshots: {string.Join(", ", snapshots.ConvertAll(fn => fn()))}");
```

**Expected output:**

```text
first: 11, 12
second: 1
first again: 13
for loop: 9, 9, 9
snapshots: 0, 3, 6
```

The C# `Func<int>` delegate returns an `int` without parameters, `() => { ... }` is a lambda with a statement body, and `return () => { ... }` returns a delegate capturing `count`. Each call to `MakeCounter` creates independent captured state. The `for` loop example has the same shared-loop-variable pitfall as JavaScript `var` and Python `for`. The explicit `int captured = j` inside the loop creates a separate binding for each iteration.

**Modern C# nuance:** `foreach` iteration variables have per-iteration capture semantics in modern C#; do **not** generalize the `for` example to all C# loops.

### 3.4 Engineering implications: lifetime, mutation and function identity

| Question | JavaScript | Python | C# |
|---|---|---|---|
| What retains state? | Closure's lexical environment | Closure referencing enclosing bindings (cells) | Compiler-generated closure storage / captured locals |
| Can state change later? | Yes (`let count`) | Yes (`nonlocal count`) | Yes (`count++`) |
| Loop capture pitfall | `var` inside `for` | `for` binding shared by callbacks | `for` loop variable captured by callbacks |
| One possible snapshot fix | `let` per iteration | Default parameter / factory | Local copy inside loop |
| Is a closure the same as a decorator? | No | No | No |

A closure can **extend the lifetime of referenced objects**, because the returned callable still references its captured environment. That is useful for stateful callbacks and configuration, but it can inadvertently keep substantial objects alive longer than intended. Do not mistake a closure for thread-safe state: if several threads or tasks can mutate the same captured value, synchronization or carefully constrained ownership may still be necessary. A closure is also **not automatically a pure function**; these counter examples deliberately mutate state.

**In the `@log_calls` decorator**, the captured value is the original callable `func`. The wrapper can still call it *after* the name `hello` has been rebound to the decorated version. This is the central reason the example works.


## 4. C# higher-order function — the functional counterpart

C# can wrap delegates too, without building a class hierarchy. This is a **functional equivalent of the Python wrapper idea**, not a GoF object decorator:

```csharp
using System;

Func<string> original = () => "Hello";

Func<string> decorated = () =>
{
    Console.WriteLine("Before");
    string result = original();
    Console.WriteLine("After");
    return result;
};

Console.WriteLine(decorated());
```

**Expected output:**

```text
Before
After
Hello
```

**Why the order differs from the Python example:** the C# `original` returns the string `"Hello"` rather than printing it. `Console.WriteLine(decorated())` prints that returned string only **after** `decorated` has printed `Before` and `After`.

Read the C# syntax:

- `Func<string>` is a delegate type for a method taking **no arguments** and returning `string`.
- `() => "Hello"` is a lambda expression (an anonymous function). It is **not executed** when stored in `original`.
- `() => { ... }` is a statement-bodied lambda, another callable that captures the surrounding `original` variable.
- `original()` invokes the original delegate, analogous to `func()` inside Python's wrapper.
- `decorated()` invokes the wrapped delegate. No attributes or interface inheritance are involved.

If a C# delegate must return `void` rather than a value, use `Action` instead of `Func<string>`. Thus, C# supports **higher-order functional composition** too, even though it has no direct language-level equivalent of Python's general-purpose `@function_decorator` syntax.

## 5. GoF Decorator Pattern — the object-oriented counterpart in C#

Here we create an `ILogger` implementation, then wrap the **logger object instance** in another implementation of the same interface. This example includes **all the necessary definitions**, rather than assuming the classes exist elsewhere.

```csharp
using System;

ILogger logger = new ConsoleLogger();
ILogger decorated = new TimestampLoggerDecorator(logger);
decorated.Log("Hello");

public interface ILogger
{
    void Log(string message);
}

public sealed class ConsoleLogger : ILogger
{
    public void Log(string message)
    {
        Console.WriteLine(message);
    }
}

public sealed class TimestampLoggerDecorator : ILogger
{
    private readonly ILogger _inner;

    public TimestampLoggerDecorator(ILogger inner)
    {
        _inner = inner;
    }

    public void Log(string message)
    {
        // Add information, then delegate to the wrapped logger object.
        _inner.Log($"[{DateTimeOffset.UtcNow:O}] {message}");
    }
}
```

**Output:** One line with a dynamically generated UTC timestamp followed by `Hello`, for example `[2026-01-02T03:04:05.0000000+00:00] Hello`. The timestamp changes on every execution.

| C# statement | Meaning |
|---|---|
| `ILogger logger = new ConsoleLogger();` | Create an original **object instance** implementing `ILogger` |
| `new TimestampLoggerDecorator(logger)` | Construct a **different object**, storing the original inside it |
| `: ILogger` | Both classes satisfy the same interface contract |
| `private readonly ILogger _inner;` | Composition: a decorator holds the wrapped object |
| `_inner.Log(...)` | Delegate the call after adding a timestamp |
| `$"..."` and `:O` | C# string interpolation; `O` formats the date/time using the round-trip representation |

Unlike the Python function decorator, the **class** `TimestampLoggerDecorator` is not itself the wrapped target. An **instance** of that class wraps the `ConsoleLogger` instance. The GoF pattern operates on **objects**, while the Python `@log_calls` example transforms a **function binding**.

Both approaches allow behavior to be added without modifying the wrapped implementation, but they are not interchangeable or identical mechanisms.

## 6. `@contextmanager` and `@asynccontextmanager` — decorators that create resource scopes

[Lesson 03 — Context Managers and Resource Safety](../../03.%20Context%20Managers%20and%20Resource%20Safety/README.md) uses `@contextmanager` and `@asynccontextmanager` to teach resource lifetime. Their behavior inside `with` belongs to that lesson; **this section explains the decorators themselves**: why `@` changes a function, when its code runs, and how the synchronous and asynchronous variants differ.

### 6.1 A decorator transforms the function definition

A normal generator function (one containing `yield`) does **not** automatically implement the context-manager protocol. The standard-library `contextlib.contextmanager` is a **higher-order function**: it accepts a generator function and returns a function that produces context-manager objects.

```python
from contextlib import contextmanager

@contextmanager
def my_resource():
    print("Acquire")
    try:
        yield "connection"
    finally:
        print("Release")

with my_resource() as resource:
    print(f"Use: {resource}")
```

**Expected output:**

```text
Acquire
Use: connection
Release
```

Here `@contextmanager` is a **Python function decorator**, not a GoF object decorator and not a C# attribute.

These two forms are equivalent:

```text
# Form A — decorator applied during function definition:
@contextmanager
def my_resource():
    ...

# Form B — same transformation written explicitly:
def my_resource():
    ...

my_resource = contextmanager(my_resource)
```

**Trace the evaluation stages:**

1. **Definition time:** Python creates the original generator function `my_resource` and passes that function object into `contextmanager(...)`. The returned wrapper/factory is rebound to the name `my_resource`. **No resource is acquired yet.**
2. **Call time:** `my_resource()` invokes the *decorated* function and returns a **context manager object**, not the string `"connection"`. Its generator's body still has **not** executed.
3. **Enter time:** `with ...` invokes the manager's `__enter__()`, which advances the generator. Code before `yield` runs (`Acquire`); `yield "connection"` supplies the `as resource` value and suspends the generator.
4. **Exit time:** `__exit__()` resumes the generator so the `finally` block executes (`Release`). The `with` body may finish normally or raise an exception.

The returned context manager supplies `__enter__()` / `__exit__()` behavior through `contextlib`. We **do not** define those methods in the generator function. By contrast, if you remove `@contextmanager` and call `with my_resource():`, Python receives a **generator object** without the required context-manager protocol and raises `TypeError`.

**Relationship to closures and HOFs:** `contextmanager` is a reusable higher-order transformation. Its implementation arranges for the original generator function to remain available to the returned factory — conceptually related to the function wrapping and captured references in Sections 2 and 3. You do not need a new class or GoF Decorator Pattern to apply it.

**Resource correctness:** `yield` marks the suspension and handoff; the `try/finally` block provides predictable cleanup. If the `with` body throws, the context manager injects the exception at the suspended `yield`. The `finally` block runs and the exception normally propagates. If the generator catches and intentionally suppresses it, the result may differ. These resource-management semantics are covered in depth in Lesson 03.

### 6.2 Async counterpart: `@asynccontextmanager`

`contextlib.asynccontextmanager` is the **same type of decorating mechanism**, adapted to an **async generator function** (one containing both `async def` and `yield`). It produces objects usable with `async with` and implementing the `__aenter__()` / `__aexit__()` async protocol.

```python
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def async_resource():
    print("Open")
    try:
        await asyncio.sleep(0)  # Stand-in for asynchronous acquisition.
        yield "session"
    finally:
        await asyncio.sleep(0)  # Stand-in for asynchronous release.
        print("Close")

async def main():
    manager = async_resource()
    print("Manager created")
    async with manager as resource:
        print(f"Use: {resource}")

asyncio.run(main())
```

**Expected output:**

```text
Manager created
Open
Use: session
Close
```

- The `@asynccontextmanager` transformation happens **when `async_resource` is defined**, not during a later event-loop iteration. It can be spelled `async_resource = asynccontextmanager(async_resource)` instead.
- The expression `manager = async_resource()` returns an **async context manager object**, without performing the `Open` operation. This is why `Manager created` appears first.
- `async with manager as resource:` **awaits** its enter method, starts the async generator, suspends at `yield` and hands `"session"` to `resource`. On exit, the generator resumes and **awaits cleanup** in `finally`.
- A plain `with` expects the *synchronous* protocol; an `async with` expects the *asynchronous* one. The `@` syntax itself does not supply a synchronous-to-asynchronous conversion.

This section demonstrates **why the decorator syntax works**; Lesson 03 provides the detailed exception-handling, `ExitStack` / `AsyncExitStack` and cancellation behavior needed for production resource safety.

### Python decorators are not C# attributes

C# `[SomeAttribute]` generally attaches **metadata** that other infrastructure can inspect or act upon; the attribute alone does not normally replace the method's implementation. In contrast, Python's `@log_calls` *executes a callable at definition time* and can **replace the function binding with a different callable**.

## 7. Parameterized decorators: factory, decorator, wrapper

A plain decorator such as `@log_calls` receives the target function immediately: `hello = log_calls(hello)`. A **parameterized decorator** such as `@repeat(times=2)` adds another step: first create a decorator configured with `times=2`, *then* apply that decorator to the target. The key difference is **three nested functions**, each with a distinct responsibility.

This is the complete, runnable `examples/parameterized_decorators.py`:

 

```python
"""A parameterized decorator: factory, decoration, and calls."""


def repeat(times: int):
    """Repeat a call and return the result of its final invocation."""
    if times < 1:
        raise ValueError("times must be >= 1")
    print(f"factory: times={times}")

    def decorator(func):
        print(f"decorate: {func.__name__}")

        def wrapper(*args, **kwargs):
            print(f"wrapper: {times} call(s)")
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


@repeat(times=2)
def greet(name: str, *, punctuation: str = "!") -> str:
    print(f"body: {name}")
    return f"Hello, {name}{punctuation}"


if __name__ == "__main__":
    print("main: calling greet")
    print("result:", greet("Ada", punctuation="?"))
```

Run from `lessons/04-decorators/`:



```bash
python examples/parameterized_decorators.py
```

**Expected output:**



```text
factory: times=2
decorate: greet
main: calling greet
wrapper: 2 call(s)
body: Ada
body: Ada
result: Hello, Ada?
```

### 7.1 Evaluation order (not the same as call order)

1. **`repeat(times=2)`** executes at **definition time**, returning `decorator`; it prints `factory: times=2`. At this point, there is no call to `greet`.
2. Python creates the original `greet` function object and passes it to that returned `decorator`. The decorator prints `decorate: greet` and returns `wrapper`. Python binds the name `greet` to this wrapper.
3. The `if __name__ == "__main__":` entry point runs when the file is executed as a script. It does **not** run when imported as a module.
4. `greet("Ada", punctuation="?")` calls the **wrapper**, which invokes the captured original function **twice**, forwarding its arguments, then returns the **last invocation's result**.

The decoration can also be expressed as `greet = repeat(times=2)(greet)` after an ordinary function definition. Crucially, the *factory and decorator run once per decorated definition*; the wrapper runs **each time the decorated callable is invoked**.

Compare with C#: a configured C# decorator object might be instantiated with constructor options, then wrap a service; a Python decorator factory instead returns a callable to transform the function **binding** at definition time. Python's `@...` here is executable transformation syntax, **not a C# attribute**.

### 7.2 New syntax: `*args`, `**kwargs`, and keyword-only parameters

- In `def wrapper(*args, **kwargs):`, **`args`** is a tuple collecting the positional arguments supplied to the wrapper. A tuple is an ordered sequence, like a fixed-size read-only container; **`kwargs`** is a dictionary mapping keyword names to argument values. The names `args` and `kwargs` are conventions; the `*` and `**` prefixes carry the meaning.
- In `func(*args, **kwargs)` the operators do the **inverse**: expand the tuple into positional arguments and the dictionary into named arguments. This is the forwarding pattern for generic wrappers; unlike a fixed C# `Func<T...>`, one wrapper can accommodate functions with different signatures.
- `greet(name: str, *, punctuation: str = "!")` uses a **bare `*`** to make `punctuation` *keyword-only*: `greet("Ada", punctuation="?")` works, but `greet("Ada", "?")` is invalid. The `: str` and `-> str` annotations describe types without enforcing them at runtime.
- `for _ in range(times):` repeats `times` times; `_` is a conventional name for an iteration index we intentionally do not use. `result = None` initializes a local variable with Python's null singleton, then each call replaces the value.
- `raise ValueError(...)` rejects invalid decorator configuration **when the factory is evaluated**, not on the first decorated function call.

**Contract boundaries:** This decorator intentionally invokes the original function multiple times, so it can repeat side effects. If the wrapped call raises, repetition stops and the exception propagates; no successful result is returned. It also still loses the target's name and docstring because this first version does **not** use `functools.wraps`. The next example fixes that metadata issue; neither version promises exactly-once semantics.

## 8. Metadata and stacked decorators

A wrapper is a *different function object*. Without intervention, tools that inspect `__name__`, `__doc__` or the callable's signature see the wrapper instead of the intended public API. Python's standard-library **`functools.wraps`** helps by copying relevant metadata and adding a `__wrapped__` reference to the function being wrapped.

`from functools import wraps` imports this metadata helper; `from inspect import signature` imports a standard-library function that describes the parameters and return annotation of a callable. Both are **runtime introspection** tools, not substitutes for static type checking.

This is the complete runnable `examples/metadata_and_stacking.py`:



```python
"""Metadata-preserving wrappers, stacked decorators, and execution order."""

from functools import wraps
from inspect import signature


def trace(label: str):
    """Wrap a function with labeled entry and exit messages."""
    print(f"factory: {label}")

    def decorator(func):
        print(f"decorate: {label}")

        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"enter: {label}")
            try:
                return func(*args, **kwargs)
            finally:
                print(f"exit: {label}")

        return wrapper

    return decorator


@trace("outer")
@trace("inner")
def add(a: int, b: int = 1) -> int:
    """Return the sum of a and b."""
    print("body: add")
    return a + b


if __name__ == "__main__":
    print("name:", add.__name__)
    print("doc:", add.__doc__)
    print("signature:", signature(add))
    print("runtime signature:", signature(add, follow_wrapped=False))
    print("result:", add(3, b=4))
```

Run from the lesson directory:



```bash
python examples/metadata_and_stacking.py
```

**Expected output:**



```text
factory: outer
factory: inner
decorate: inner
decorate: outer
name: add
doc: Return the sum of a and b.
signature: (a: int, b: int = 1) -> int
runtime signature: (*args, **kwargs) -> int
enter: outer
enter: inner
body: add
exit: inner
exit: outer
result: 7
```

### 8.1 Why three different orders appear

- **Decorator expressions** are evaluated **top to bottom**: `trace("outer")` returns a decorator, then `trace("inner")` returns another. This is why both `factory` messages precede the `decorate` messages.
- **Decorator application** is **bottom to top**: first apply the inner decorator to the original `add`, then apply the outer decorator to the result. This is approximately `add = trace("outer")(trace("inner")(add))`; the name `add` is finally rebound to the outer wrapper.
- **At call time**, the outer wrapper is entered first, which enters the inner wrapper, which calls the original body. The wrappers then exit in reverse order. This is the same nesting rule you know from C# middleware pipelines or nested `try/finally` blocks.

### 8.2 `@wraps(func)`, `__wrapped__`, and the real signature

`@wraps(func)` above `def wrapper` is itself a **parameterized decorator**: `wraps(func)` returns a decorator for the wrapper. Internally, `functools.wraps` uses `update_wrapper` to copy selected metadata and set `wrapper.__wrapped__ = func`. It does **not** replace the implementation or re-create the original parameter list.

- `add.__name__` evaluates to `"add"`, and `add.__doc__` retains the original docstring.
- `add.__wrapped__` refers to the **inner wrapper**, while `add.__wrapped__.__wrapped__` refers to the **original undecorated function**. Each use of `@wraps` preserves a link in that chain.
- `inspect.signature(add)` **follows `__wrapped__` by default**, reporting `(a: int, b: int = 1) -> int` for the original callable.
- `inspect.signature(add, follow_wrapped=False)` examines the actual outer wrapper. Its runtime parameters are `(*args, **kwargs)`, although its return annotation is copied from the original by `@wraps`. The displayed signature does **not** mean Python has changed the wrapper's runtime argument binding.

To preserve static typing when writing reusable decorators, a later section can introduce `typing.ParamSpec` and `TypeVar`. These provide information to type checkers; they do not change Python's runtime call protocol.

### 8.3 Exception behavior: wrapping is not suppression

`trace` uses `try/finally`: both `exit` messages run even if the original function raises. The original exception then continues outward. This is like the guaranteed execution of a C# `finally` block, but **no resource ownership or automatic disposal** is implied. Unlike Lesson 03's optional context-manager exception suppression, this wrapper does **not** catch or suppress errors.

### 8.4 Engineering exercises

1. Predict the output when `@repeat(times=2)` changes to `@repeat(times=3)`. Distinguish decoration-time prints from call-time prints.
2. Predict what happens when you invoke `greet("Ada", "?")`. Explain the bare `*` in its signature.
3. Inspect `add.__wrapped__` and `add.__wrapped__.__wrapped__` and identify which wrapper or original function each represents.
4. Reverse the order of `@trace("outer")` and `@trace("inner")`. Predict separately the factory, decoration, call-entry, and finally-exit order.
5. Replace the body of `add` with `raise RuntimeError("boom")`. Confirm that both `finally` blocks execute and the exception is still raised.

## 9. Closure runtime introspection: cells, not frozen values

The `nonlocal` mechanism introduced earlier changes *a binding in an enclosing function scope*. You can inspect the live captured state through function and code attributes. This is useful for debugging decorators and retained state, but you should not build business logic that mutates private closure cells.

This is the full `examples/closure_introspection.py`:



```python
"""Inspect the live lexical bindings retained by a Python closure."""


def make_accumulator(start: int):
    total = start

    def add(delta: int) -> int:
        nonlocal total
        total += delta
        return total

    return add


def main() -> None:
    first = make_accumulator(10)
    second = make_accumulator(100)

    print("free vars:", first.__code__.co_freevars)
    print("captured before:", first.__closure__[0].cell_contents)
    print("first call:", first(5))
    print("captured after:", first.__closure__[0].cell_contents)
    print("second call:", second(1))
    print("independent:", first(1))


if __name__ == "__main__":
    main()
```

Run from this lesson directory: `python examples/closure_introspection.py`.

**Expected output:**



```text
free vars: ('total',)
captured before: 10
first call: 15
captured after: 15
second call: 101
independent: 16
```

- `first.__code__` is the code object for the nested `add` function. Its `co_freevars` tuple lists the names referenced from outer function scopes. A **tuple** is an ordered immutable sequence: here it contains exactly one item, `'total'`.
- `first.__closure__` is the function's tuple of **cell objects** (or `None` for a function without captured cells). A cell holds the *current value of a captured binding*. `cell_contents` lets us inspect that current value.
- The names in `co_freevars` correspond positionally to the cells in `__closure__`; `first.__closure__[0]` therefore represents `total`. The integer goes from 10 to 15 after `first(5)`, proving that this is not a snapshot.
- `second = make_accumulator(100)` captures an *independent* `total` binding. There is no shared global counter.

**C# analogy:** A closure can keep a compiler-generated captured-variable holder alive after the creating method returns. Python explicitly exposes code objects and closure cells for introspection, unlike normal C# delegate use. This is introspection, **not an alternative to encapsulated state or thread synchronization**. In practice, avoid depending on closure-cell indexes when refactoring code: the set and order of free variables can change.

## 10. Generic decorators with `ParamSpec` and `TypeVar`

The `*args`/`**kwargs` wrapper in Section 7 forwards arguments at runtime, but naive annotations do not tell a static type checker what argument types the decorated callable still accepts. Python's standard-library `typing` module provides two relevant mechanisms:

- `Callable` describes an object that can be invoked, with specified parameter and result types, similar in purpose to a C# delegate signature.
- `ParamSpec("P")` creates a **parameter specification variable**: a placeholder for the target function's **entire parameter list**, including positional, keyword-only, and named arguments. `P.args` / `P.kwargs` annotate the wrapper's forwarding parameters. This is more expressive than a single `TypeVar` describing a value type.
- `TypeVar("R")` introduces a type variable for the return value. The same `R` in the input and output signatures tells a type checker that the wrapper preserves the original result type.
- `from functools import wraps` imports the metadata decorator covered in Section 8. Static typing and runtime metadata preservation solve **different** problems.

Full `examples/typed_decorators.py`:



```python
"""Preserve a decorated callable's static parameter and result types."""

from functools import wraps
from typing import Callable, ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")


def audit(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"audit: enter {func.__name__}")
        try:
            return func(*args, **kwargs)
        finally:
            print(f"audit: exit {func.__name__}")

    return wrapper


@audit
def calculate(amount: int, *, multiplier: int = 2) -> int:
    """Multiply an integer amount."""
    return amount * multiplier


def main() -> None:
    print("name:", calculate.__name__)
    print("result:", calculate(7, multiplier=3))


if __name__ == "__main__":
    main()
```

Run: `python examples/typed_decorators.py`.

**Expected output:**



```text
name: calculate
audit: enter calculate
audit: exit calculate
result: 21
```

**Step-by-step:** When Python executes `@audit`, the original `calculate` function becomes the `func` argument. `@wraps(func)` copies metadata onto `wrapper`. `calculate(7, multiplier=3)` invokes the wrapper, which forwards the integer positional argument and the named keyword argument, and returns 21. `finally` always logs exit, even when the original raises; it does **not** suppress exceptions.

**Important distinction:** `ParamSpec` and `TypeVar` communicate a contract to tools such as Pyright or mypy; they do not runtime-validate values or change the actual `(*args, **kwargs)` argument binding on the wrapper. No third-party type checker is required to run this lesson, and the unit tests validate runtime behavior, not static type-checker results. C# generic constraints are compile-time enforced by the C# compiler; ordinary Python type annotations are not runtime checks. When designing a decorator that *changes* accepted parameters or return types, this exact generic signature would be incorrect; use a contract that models the transformation instead.

## 11. Sync vs async decorators: the point where C# intuition can mislead

A normal Python `def` wrapper around an `async def` function often returns a coroutine object immediately; it does not necessarily produce a callable reported as a coroutine function by `inspect.iscoroutinefunction`, and any sync `try/finally` around that return runs **before** the coroutine body starts. In contrast, an `async def` wrapper that uses `await func(...)` surrounds the *execution* of the asynchronous operation.

This distinction matters for logging, error boundaries, metrics, tracing, cancellation, and retries. Recall from Lesson 02: calling `async def` creates a coroutine object; `asyncio.create_task` schedules that coroutine; `await` drives it (or waits for a task). This differs from C# async methods, which start executing synchronously up to the first incomplete await.

**New imports:** `asyncio` supplies the event loop, `Event` synchronization primitive, and `Task` scheduler. `inspect.iscoroutinefunction` checks whether a callable is recognized as a coroutine function; `inspect.iscoroutine` checks an actual coroutine object. `Awaitable` from `typing` describes a value usable with `await`, while `Callable`, `ParamSpec` and `TypeVar` were introduced above. `functools.wraps` preserves metadata but **does not convert a synchronous wrapper into an async function**.

Full `examples/async_decorators.py`:



```python
"""Async wrappers: coroutine creation, execution, errors, and cancellation."""

import asyncio
import inspect
from functools import wraps
from typing import Awaitable, Callable, ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")


def trace_async(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print("async: enter")
        try:
            return await func(*args, **kwargs)
        finally:
            print("async: exit")

    return wrapper


def sync_wrapper_for_async(
    func: Callable[P, Awaitable[R]],
) -> Callable[P, Awaitable[R]]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Awaitable[R]:
        print("sync wrapper: called")
        return func(*args, **kwargs)

    return wrapper


@trace_async
async def work(kind: str, ready: asyncio.Event | None = None) -> str:
    print("body:", kind)
    if kind == "error":
        raise ValueError("boom")
    if kind == "cancel":
        assert ready is not None
        ready.set()
        await asyncio.Event().wait()  # Suspend until the task is cancelled.
    await asyncio.sleep(0)
    return "done"


@sync_wrapper_for_async
async def delayed() -> str:
    print("delayed body")
    return "late"


async def main() -> None:
    print("async function:", inspect.iscoroutinefunction(work))
    coroutine = work("ok")
    print("coroutine created")
    print("result:", await coroutine)

    print("sync wrapper is async:", inspect.iscoroutinefunction(delayed))
    delayed_coroutine = delayed()
    print("delayed coroutine:", inspect.iscoroutine(delayed_coroutine))
    print("delayed result:", await delayed_coroutine)

    try:
        await work("error")
    except ValueError:
        print("caught: ValueError")

    ready = asyncio.Event()
    task = asyncio.create_task(work("cancel", ready))
    await ready.wait()  # Wait until the task has started its body.
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("caught: CancelledError")


if __name__ == "__main__":
    asyncio.run(main())
```

Run: `python examples/async_decorators.py`.

**Expected output:**



```text
async function: True
coroutine created
async: enter
body: ok
async: exit
result: done
sync wrapper is async: False
sync wrapper: called
delayed coroutine: True
delayed body
delayed result: late
async: enter
body: error
async: exit
caught: ValueError
async: enter
body: cancel
async: exit
caught: CancelledError
```

### 11.1 Trace of the normal path

1. Applying `@trace_async` happens at definition time, but the `async def wrapper` body runs only after its coroutine is awaited or scheduled.
2. `coroutine = work("ok")` creates a coroutine object **without printing** `async: enter`. This is not an `asyncio.Task`.
3. `await coroutine` enters the wrapper, awaits the original function, runs `finally`, and returns `"done"`.
4. `delayed()` has a **synchronous wrapper**. It prints `sync wrapper: called` immediately and returns the undecorated coroutine object. Only `await delayed_coroutine` executes the original `delayed` body. A sync wrapper's `try/finally` around `return func(...)` would **not** cover the actual async execution.
5. `inspect.iscoroutinefunction(delayed)` returns `False` despite `@wraps` and despite the fact that calling it returns a coroutine; frameworks that inspect callable type can behave differently as a result.

### 11.2 Error propagation and cancellation

- `work("error")` raises `ValueError` from inside the awaited body; the async wrapper's `finally` runs **before** the caller's `except ValueError`. This is the async counterpart of C# `try/finally` around an awaited call.
- `asyncio.Event()` creates a one-shot signal. In `work("cancel", ready)`, `ready.set()` tells the caller the coroutine actually started, and `await asyncio.Event().wait()` suspends it indefinitely until cancellation. This avoids timing assumptions or arbitrary sleeps in the test.
- `task = asyncio.create_task(...)` schedules the coroutine as a real `asyncio.Task`. After `await ready.wait()`, `task.cancel()` requests cancellation. The task receives `asyncio.CancelledError` at its suspension point; the wrapper's `finally` executes; then the outer `await task` raises the cancellation.
- `asyncio.CancelledError` inherits from `BaseException` rather than `Exception` in these supported Python versions; `except Exception` will not accidentally swallow it. Catch cancellation only when you can handle it correctly; normally let it propagate after cleanup.
- A `finally` block ensures the cleanup *statement is entered* on ordinary unwind, but an asynchronous cleanup `await` can itself fail or be interrupted by an additional cancellation. Do not claim that every cleanup operation is unconditionally guaranteed to complete; use the ownership patterns in Lesson 03 for resources.

**Production rule:** Use a native `async def` wrapper that awaits the original operation when you must surround the coroutine's execution. When decorating both sync and async callables, provide distinct contracts or choose a callable-aware implementation that handles both deliberately. Do **not** assume a decorator is async-safe solely because it forwards `*args` and `**kwargs`.

## 12. Method binding, descriptors and standard-library decorators

Functions stored on Python classes participate in **descriptor-based binding**. You do not need to implement the descriptor protocol for this lesson, but you must understand the practical effect:

- A normal function accessed through an instance becomes a **bound method**; Python supplies the instance as `self`.
- `@classmethod` creates a descriptor that supplies the **class** as `cls`. In our example, `@track` first wraps the underlying function; `@classmethod` then turns that wrapper into a class method.
- `@staticmethod` creates a descriptor that leaves the function unbound; Python does not inject `self` or `cls`.
- `@property` creates a descriptor exposing a getter as an attribute read rather than a call: `greeter.label`, not `greeter.label()`. Think of a C# property getter, but remember Python's attribute access goes through the descriptor protocol.
- `@lru_cache(maxsize=4)` is a parameterized standard-library decorator from `functools`, implementing bounded memoization. It caches results by argument combinations and exposes `cache_info()` for hits and misses. This is a real example of a library-provided wrapper, not a GoF object decorator.

Here is all of `examples/method_and_stdlib_decorators.py`:



```python
"""Function wrappers on methods, descriptors, and standard-library caching."""

from functools import lru_cache, wraps


def track(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"call: {func.__name__}")
        return func(*args, **kwargs)

    return wrapper


class Greeter:
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    @track
    def greet(self, name: str) -> str:
        return f"{self.prefix}, {name}"

    @classmethod
    @track
    def describe(cls) -> str:
        return cls.__name__

    @staticmethod
    @track
    def version() -> int:
        return 1

    @property
    def label(self) -> str:
        return self.prefix


@lru_cache(maxsize=4)
def normalize(value: str) -> str:
    print("normalize: computing")
    return value.strip().upper()


def main() -> None:
    greeter = Greeter("Hello")
    print("method:", greeter.greet("Ada"))
    print("class method:", Greeter.describe())
    print("static method:", Greeter.version())
    print("property:", greeter.label)
    print("normalized:", normalize("  abc "))
    print("cached:", normalize("  abc "))
    print("cache:", normalize.cache_info().hits, normalize.cache_info().misses)


if __name__ == "__main__":
    main()
```

Run: `python examples/method_and_stdlib_decorators.py`.

**Expected output:**



```text
call: greet
method: Hello, Ada
call: describe
class method: Greeter
call: version
static method: 1
property: Hello
normalize: computing
normalized: ABC
cached: ABC
cache: 1 1
```

Observe: `greeter.greet("Ada")` calls the tracked wrapper with `self` injected, so the wrapper's `*args` forwards the instance as the first positional argument. `Greeter.describe()` passes `cls` to its wrapped function; `Greeter.version()` does not. The `label` property reads `self.prefix` without parentheses. The second `normalize("  abc ")` returns the cached value; it does not print `normalize: computing` a second time.

**Production cautions for `lru_cache`:** Only cache results when the function is semantically safe to memoize; impure operations and time-sensitive values can return stale or incorrect results. Cache arguments must be hashable. Method caches can retain references to `self` through their keys. The cache data structure is synchronized, but concurrent cache misses can compute the same value more than once. Caching is not an exactly-once execution guarantee. An `async def` function should not normally be wrapped in `lru_cache`, because caching coroutine objects for repeated awaits is incorrect.

## 13. Verification, exercises, and completion standard

From the repository root (after publication), run all demo programs and the unit tests:



```bash
cd "04. Decorators, Closures and Cross-Cutting Concerns"
python examples/function_decorators.py
python examples/closures.py
python examples/parameterized_decorators.py
python examples/metadata_and_stacking.py
python examples/closure_introspection.py
python examples/typed_decorators.py
python examples/async_decorators.py
python examples/method_and_stdlib_decorators.py
python -m unittest discover -s tests -v
# Optional: node examples/closures.js
```

The examples need only the Python 3.11+ standard library; the optional JavaScript comparison needs Node.js. Every Python code block above is a standalone, copyable program whose output is checked in the tests; the test suite also verifies that the embedded source matches the demonstration files.

**Exercises (predict, run, and explain):**

1. Extend the typed `audit` decorator to record errors *without suppressing* them. Compare `try/finally` versus `try/except/raise/finally`.
2. For `trace_async`, explain the difference between `work("ok")`, `await work("ok")` and `asyncio.create_task(work("ok"))`. Identify which values are coroutine objects, results, and Tasks.
3. Cancel an in-flight decorated operation and explain why the inner `finally` runs before the outer cancellation handler.
4. Explain why `inspect.signature` can report the original parameter list while `inspect.signature(..., follow_wrapped=False)` shows `(*args, **kwargs)`.
5. Use `__closure__` to observe an accumulator's changing value; explain why its state is not safe for unrestricted concurrent mutation.
6. Reorder `@track` and `@classmethod` and determine why arbitrary decorator ordering is not guaranteed to work: `classmethod` creates a descriptor, not an ordinary function (and behavior can differ by Python release).
7. Apply `@lru_cache` to an async function and identify why reusing the cached coroutine object on a second await is invalid. Treat this as a **negative demonstration**, not a recommended implementation.

**Completion criteria:** This lesson teaches definition-time transformation, argument/result contract, stacked evaluation, closures and cells, metadata, generic typing, synchronous/asynchronous wrapper semantics, cancellation, descriptor binding, caching caveats, and production failure paths. No implementation is hidden in an unshown demo; all snippets and expected outputs are regression-tested. The lesson does not claim to be a complete survey of every decorator in the Python ecosystem.

**Additional cross-language references:** [Python execution model (name binding)](https://docs.python.org/3/reference/executionmodel.html), [Python FAQ on late-bound lambdas](https://docs.python.org/3/faq/programming.html#why-do-lambdas-defined-in-a-loop-with-different-values-all-return-the-same-result), [MDN closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures), [C# lambda expressions](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/lambda-expressions).

**Official references:** [Python glossary: decorator](https://docs.python.org/3/glossary.html#term-decorator), [Python language reference: function definitions](https://docs.python.org/3/reference/compound_stmts.html#function-definitions), [`functools`](https://docs.python.org/3/library/functools.html), [`inspect`](https://docs.python.org/3/library/inspect.html), [`typing`](https://docs.python.org/3/library/typing.html), [`asyncio`](https://docs.python.org/3/library/asyncio.html), [`contextlib`](https://docs.python.org/3/library/contextlib.html).
