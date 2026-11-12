# 07 — Runtime Polymorphism and Duck Typing

**Audience:** Experienced .NET backend engineers. This lesson concerns Python's call-site flexibility, dynamic resolution, optional structural typing and explicit type-dispatch alternatives—not an introduction to polymorphism.

## 1. A method is selected on the runtime object

In C#, the compiler resolves which members are legal and virtual dispatch selects an implementation. In ordinary Python, `bird.speak()` dynamically looks up `speak` on `bird`'s type and its MRO (Lesson 06). The parameter name `bird` **does not restrict its type** and an annotation alone would not enforce a runtime check.

The term **duck typing** means accepting objects based on behavior needed by the operation, regardless of declared inheritance. An unrelated object can satisfy an operation without subclassing `Bird`. This does not imply that **all** objects work: errors arise at the call site if the attribute is absent or its signature is incompatible.

The next file is complete runnable `examples/duck_typing.py`. `class Duck(Bird)` demonstrates nominal inheritance with override; `MechanicalDuck` is unrelated yet can be passed to `make_bird_speak`. `class Silent: pass` uses `pass`, Python's no-op statement required for an empty class body. `try/except AttributeError` handles missing lookup, while `TypeError` captures calling a method with an incompatible argument list. `isinstance(obj, Bird)` tests nominal type membership, **not** behavioral compatibility.

```python
"""Override dispatch, unrelated duck-typed objects, and runtime failures."""


class Bird:
    def speak(self) -> str:
        return "generic chirp"


class Duck(Bird):
    def speak(self) -> str:
        return "quack"


class MechanicalDuck:
    def speak(self) -> str:
        return "synthetic quack"


class Silent:
    pass


class WrongSignature:
    def speak(self, volume: int) -> str:
        return f"volume={volume}"


def make_bird_speak(bird) -> str:
    return bird.speak()


if __name__ == "__main__":
    for bird in (Bird(), Duck(), MechanicalDuck()):
        print("speak:", make_bird_speak(bird))
    print("unrelated subclass:", isinstance(MechanicalDuck(), Bird))
    try:
        make_bird_speak(Silent())
    except AttributeError:
        print("silent: AttributeError")
    try:
        make_bird_speak(WrongSignature())
    except TypeError:
        print("wrong signature: TypeError")
```

**Expected output:**

```text
speak: generic chirp
speak: quack
speak: synthetic quack
unrelated subclass: False
silent: AttributeError
wrong signature: TypeError
```

## 2. Protocol for static structural typing; dispatch by explicit type

`from typing import Protocol, runtime_checkable` declares a structural interface for static type checkers. The code's `Speaker` protocol asks for a zero-argument `speak` returning `str`. The function annotation `announce(speaker: Speaker) -> str` allows Pyright/mypy to check compatibility without requiring a nominal base class. The Python interpreter does **not** reject an incompatible annotation automatically. The `@runtime_checkable` decorator allows `isinstance(obj, Speaker)`, but this runtime check is **only a shallow member-presence check**; it does not guarantee a compatible signature. `InvalidSpeaker` deliberately demonstrates that pitfall.

`from functools import singledispatch` imports a standard-library decorator creating a generic function that dispatches based on the **type of its first argument**. It is different from ordinary duck typing and different from C# compile-time method overload selection. `@render.register` registers the function's annotated first parameter type; `@render.register(str)` specifies a type explicitly. `def _(value: int)` is just a function named `_` by convention, used because the registry retains the implementation. `type(value).__name__` inspects the actual runtime type. `bool` subclasses `int` in Python, so `render(True)` selects the `int` implementation unless a more specific `bool` registration is added.

Full `examples/protocols_and_dispatch.py`:

```python
"""Structural annotations versus functools single-dispatch on runtime type."""

from functools import singledispatch
from typing import Protocol, runtime_checkable


@runtime_checkable
class Speaker(Protocol):
    def speak(self) -> str:
        ...


class Robot:
    def speak(self) -> str:
        return "beep"


class InvalidSpeaker:
    def speak(self, *, volume: int) -> str:
        return str(volume)


def announce(speaker: Speaker) -> str:
    return f"announcement: {speaker.speak()}"


@singledispatch
def render(value: object) -> str:
    return f"default:{type(value).__name__}"


@render.register
def _(value: int) -> str:
    return f"integer:{value}"


@render.register(str)
def _(value: str) -> str:
    return f"string:{value}"


if __name__ == "__main__":
    print(announce(Robot()))
    print("structural:", isinstance(Robot(), Speaker))
    print("presence-only:", isinstance(InvalidSpeaker(), Speaker))
    print("dispatch int:", render(42))
    print("dispatch str:", render("hi"))
    print("dispatch float:", render(3.5))
    print("bool resolves as int:", render(True))
```

**Expected output:**

```text
announcement: beep
structural: True
presence-only: True
dispatch int: integer:42
dispatch str: string:hi
dispatch float: default:float
bool resolves as int: integer:True
```

## 3. Choosing a contract boundary

| Concern | Python mechanism | C# comparison |
|---|---|---|
| Open-ended collaborator that has `speak()` | Plain duck typing | Structural behavior at runtime, no C# compile-time equivalent |
| Static checking across packages | `Protocol` | Interface-like checking, **structural**, optional tool |
| Nominal runtime membership / shared behavior | `ABC` (Lesson 05) | Interface or abstract base class, with different enforcement |
| Switch by runtime value's type | `singledispatch` | Type-based dispatch; unlike overloads selected at compile time |
| Multiple implementations through one call site | Ordinary dynamic method lookup | Virtual dispatch but no explicit `virtual` required |

**Failure modes and production semantics:**

- `hasattr(x, "speak")` or runtime `isinstance(x, Speaker)` is insufficient to prove the method has the right signature, returns the right type, or is safe. `WrongSignature` and `InvalidSpeaker` demonstrate this concretely.
- Prefer **EAFP** (“easier to ask forgiveness than permission”) where appropriate: call the collaborator and handle only errors you can actually recover from. Do not blanket-catch `AttributeError` inside a complex operation, because it may hide an unrelated bug thrown inside the collaborator's own code.
- The [Liskov substitution principle](https://en.wikipedia.org/wiki/Liskov_substitution_principle) applies to behavior, not mere method names. A duck-typed `speak()` implementation must still meet its caller's semantic expectations.
- `singledispatch` dispatches on the **first argument only** and respects registered type specificity. It does not select by keyword count or every parameter type. For an instance method use `functools.singledispatchmethod`, which dispatches on its first non-`self`/`cls` argument.

## 4. Validation and exercises

```bash
python examples/duck_typing.py
python examples/protocols_and_dispatch.py
python -m unittest discover -s tests -v
```

1. Remove `Duck(Bird)` inheritance but keep `speak()`; predict `make_bird_speak` and `isinstance(x, Bird)` independently.
2. Give `WrongSignature.speak` a default `volume=5`; explain why the same operation now works.
3. Give `Robot.speak()` an `int` return value; explain which checks detect the problem: runtime `isinstance`, ordinary execution, and a static checker.
4. Register a new `bool` handler and predict how it affects `render(True)` and `render(42)`.
5. Write a contract test that requires a speaker's result to be a nonempty string, independent of inheritance.

**References:** [typing and Protocol](https://docs.python.org/3/library/typing.html), [functools.singledispatch](https://docs.python.org/3/library/functools.html#functools.singledispatch), [Python data model](https://docs.python.org/3/reference/datamodel.html).
