# 04 — Decorators, Closures, and Cross-Cutting Concerns

**Development status:** The foundation below is written and tested; parameterized decorators, `*args` / `**kwargs`, stacked decorators, `functools.wraps`, and production sync/async wrappers remain to be developed before this lesson is promoted from `lessons/` to a numbered root directory.

**Audience:** Experienced C#/.NET engineers who know OOP and the GoF design patterns but are new to Python's first-class functions and `@decorator` syntax.

## 1. “Decorator” means more than one thing

The word **decorator** is used in two related but different programming traditions. The specific functional-programming term you may be looking for is **higher-order function (HOF)**.

| Term | Precise meaning | What is wrapped? |
|---|---|---|
| **Higher-order function (HOF)** | Any function that **accepts a function as an argument, returns a function, or both** | No wrapping is required: e.g. `map()` is a HOF |
| **Function wrapper** | A function that invokes another function, optionally adding behavior before/after the invocation | Another callable |
| **Python function decorator** | A callable used to **transform or replace a function definition**, typically by returning a wrapper; written with `@name` | A function object |
| **GoF Decorator Pattern** | A **structural** design pattern that gives an object added behavior by wrapping it with another object implementing a compatible interface | An **object instance**, not inherently a class definition |
| **Function composition** | Combining functions so one function's output feeds the next | No specific `@` syntax or wrapping requirement |

These terms overlap, but are **not synonyms**: not every HOF is a decorator, and function composition is not the same thing as the GoF Decorator Pattern.

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

## 3. C# higher-order function — the functional counterpart

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

## 4. GoF Decorator Pattern — the object-oriented counterpart in C#

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

## 5. How does `@contextmanager` from Lesson 03 fit in?

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

## 6. Quick validation and practice

**Run the Python demonstration:**

```bash
cd lessons/04-decorators
python examples/function_decorators.py
python -m unittest discover -s tests -v
```

The Python demo and tests use the standard library only. The two C# examples are standalone top-level statement programs; paste either one into a **separate** `Program.cs` in a .NET console project. The Python tests do not compile or execute the C# samples.

**Exercises:**

1. Change `hello()` to print `"Goodbye"`. Predict what happens before executing: what does the decorator change, and what remains the original function body?
2. Remove `@log_calls` and instead assign `hello = log_calls(hello)` **after** the function definition. Confirm that the output is unchanged.
3. Make a second Python function `bye()` with no arguments and apply `@log_calls`. Explain why the same higher-order function can decorate both.
4. For the C# GoF example, wrap the same `ConsoleLogger` instance with **two** decorators. Predict in which order the wrappers execute before running the code.

## 7. Remaining Lesson 04 roadmap

The next sections to develop are parameterized decorator factories (three nested functions and evaluation timing), closures and captured state, arbitrary positional/keyword arguments (`*args` / `**kwargs`), returning the original result, `functools.wraps`, stacked decorators and evaluation order, synchronous versus asynchronous wrappers, and exercises with production concerns such as exception safety and preserving function contracts.

**Official references:** [Python glossary: decorator](https://docs.python.org/3/glossary.html#term-decorator), [Python language reference: function definitions](https://docs.python.org/3/reference/compound_stmts.html#function-definitions), [Python `contextlib`](https://docs.python.org/3/library/contextlib.html).
