# 04 — Decorators, Closures, and Cross-Cutting Concerns

**Development status:** The foundation below is written and tested; parameterized decorators, `*args` / `**kwargs`, stacked decorators, `functools.wraps`, and production sync/async wrappers remain to be developed before this lesson is promoted from `lessons/` to a numbered root directory.

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

This introductory wrapper accepts **no arguments** and returns no result. It is correct for this particular `hello()` demo, but is **not yet a general-purpose decorator**. Production wrappers typically accept `*args` and `**kwargs`, return the wrapped function's result, and use `functools.wraps` to preserve metadata such as `__name__` and `__doc__`. We will implement and test those improvements in the remaining parts of Lesson 04.

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

## 6. How does `@contextmanager` from Lesson 03 fit in?

The previously introduced `@contextmanager` is another **Python decorator**, but it is **special-purpose**: it accepts a generator function with `yield` and returns a callable that creates context managers usable with `with`.

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

The decoration syntax:

```text
@contextmanager
def my_resource():
    ...
```

is equivalent to **defining the generator function** first, then assigning `my_resource = contextmanager(my_resource)`.

But the runtime behavior is *not* the same as the logging wrapper above:

- `@log_calls` returns a normal callable wrapper that calls `func()` every time the decorated function is invoked.
- `@contextmanager` returns a factory for context manager objects. The generator's setup code **starts when the returned manager is entered by `with`**, suspends at `yield` to give a resource to the caller, then resumes for cleanup on exit.
- It **does not automatically wrap a class** or act like the GoF Decorator Pattern merely because it uses the word “decorator”.

### Python decorators are not C# attributes

C# `[SomeAttribute]` generally attaches **metadata** that other infrastructure can inspect or act upon; the attribute alone does not normally replace the method's implementation. In contrast, Python's `@log_calls` *executes a callable at definition time* and can **replace the function binding with a different callable**.

## 7. Quick validation and practice

**Run the Python demonstrations (JavaScript demo is optional):**

```bash
cd lessons/04-decorators
python examples/function_decorators.py
python examples/closures.py
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

## 8. Remaining Lesson 04 roadmap

The next sections to develop are parameterized decorator factories (three nested functions and evaluation timing), deeper closure internals and runtime introspection (`__closure__`, `co_freevars`), arbitrary positional/keyword arguments (`*args` / `**kwargs`), returning the original result, `functools.wraps`, stacked decorators and evaluation order, synchronous versus asynchronous wrappers, and exercises with production concerns such as exception safety and preserving function contracts.

**Additional cross-language references:** [Python execution model (name binding)](https://docs.python.org/3/reference/executionmodel.html), [Python FAQ on late-bound lambdas](https://docs.python.org/3/faq/programming.html#why-do-lambdas-defined-in-a-loop-with-different-values-all-return-the-same-result), [MDN closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures), [C# lambda expressions](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/lambda-expressions).

**Official references:** [Python glossary: decorator](https://docs.python.org/3/glossary.html#term-decorator), [Python language reference: function definitions](https://docs.python.org/3/reference/compound_stmts.html#function-definitions), [Python `contextlib`](https://docs.python.org/3/library/contextlib.html).
