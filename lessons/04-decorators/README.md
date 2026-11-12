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

## 9. Quick validation and practice

**Run the Python demonstrations (JavaScript demo is optional):**

```bash
cd lessons/04-decorators
python examples/function_decorators.py
python examples/closures.py
python examples/parameterized_decorators.py
python examples/metadata_and_stacking.py
python -m unittest discover -s tests -v

# Optional, when Node.js is installed:
node examples/closures.js
```

The Python demos and tests use the standard library only. The JavaScript example can be executed with Node.js, but it is not a dependency for the Python lessons. The two C# examples are standalone top-level statement programs; paste either one into a **separate** `Program.cs` in a .NET console project. The Python tests do not compile or execute the C# samples.

**Exercises:**

1. Change `hello()` to print `"Goodbye"`. Predict what happens before executing: what does the decorator change, and what remains the original function body?
2. Remove `@log_calls` and instead assign `hello = log_calls(hello)` **after** the function definition. Confirm that the output is unchanged.
3. Make a second Python function `bye()` with no arguments and apply `@log_calls`. Explain why the same higher-order function can decorate both.
4. For the C# GoF example, wrap the same `ConsoleLogger` instance with **two** decorators. Predict in which order the wrappers execute before running the code.

## 10. Production boundaries

These examples deliberately focus on function decoration, lexical capture, metadata, and call forwarding. Runtime introspection (e.g. `__closure__` and `__code__.co_freevars`), type-safe generic decorators (e.g. `ParamSpec`), synchronous versus asynchronous function wrappers, cancellation, and production instrumentation need dedicated treatment. In particular, wrapping an `async def` function with a synchronous `def` wrapper changes the callable's behavior; `functools.wraps` cannot fix coroutine scheduling or exception-handling mistakes.

**Additional cross-language references:** [Python execution model (name binding)](https://docs.python.org/3/reference/executionmodel.html), [Python FAQ on late-bound lambdas](https://docs.python.org/3/faq/programming.html#why-do-lambdas-defined-in-a-loop-with-different-values-all-return-the-same-result), [MDN closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures), [C# lambda expressions](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/lambda-expressions).

**Official references:** [Python glossary: decorator](https://docs.python.org/3/glossary.html#term-decorator), [Python language reference: function definitions](https://docs.python.org/3/reference/compound_stmts.html#function-definitions), [Python `contextlib`](https://docs.python.org/3/library/contextlib.html).
