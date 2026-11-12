# 06 — Inheritance, Multiple Inheritance, and Method Resolution Order

**Audience:** Senior C# developers familiar with single inheritance and interface implementation. Focus: Python's multiple **implementation** inheritance, dynamic lookup and cooperative extension points.

## 1. The distinction from the C# type hierarchy

A Python class may inherit from **multiple concrete or mixin classes**: `class Bird(Flyable, Animal)`. Unlike the C# pattern `class Bird : Animal, IFlyable`, *both* Python bases can contribute behavior and state. Python resolves method/attribute lookup via an ordered **MRO (method-resolution order)**. This order is not simply “look at the left parent, then all its parents, then the right parent”: in the presence of diamonds Python uses **C3 linearization**, respecting local base order and the relative order of ancestor dependencies.

Python attribute lookup is dynamic. `self.speak()` resolves against the runtime instance class and its MRO. An override is not declared with a required C# `override` keyword. An annotation such as `-> str` documents a type but does not enforce it.

## 2. Single inheritance plus a behavior mixin

This is the entire runnable `examples/dispatch.py`. `class Dog(Animal)` inherits from a single base; `super().speak()` delegates to the **next method after Dog in the active MRO**. `class Bird(Flyable, Animal)` puts the fly behavior mixin before the animal base. `Bird.__mro__` is a tuple of the concrete runtime lookup sequence; `cls.__name__` accesses each class name. `" > ".join(...)` joins strings from a generator expression into one output line.

```python
"""Ordinary inheritance, mixins and method lookup order."""


class Animal:
    def speak(self) -> str:
        return "generic sound"


class Dog(Animal):
    def speak(self) -> str:
        return f"{super().speak()} + woof"


class Flyable:
    def fly(self) -> str:
        return "flying"


class Bird(Flyable, Animal):
    def speak(self) -> str:
        return "chirp"


if __name__ == "__main__":
    animal = Animal()
    dog = Dog()
    bird = Bird()
    print("animal:", animal.speak())
    print("dog:", dog.speak())
    print("bird:", bird.speak())
    print("fly:", bird.fly())
    print("bird MRO:", " > ".join(cls.__name__ for cls in Bird.__mro__))
```

**Expected output:**

```text
animal: generic sound
dog: generic sound + woof
bird: chirp
fly: flying
bird MRO: Bird > Flyable > Animal > object
```

## 3. The diamond: `super()` is not “direct parent call”

The complete `examples/diamond.py` constructs a diamond. Its linearization is `Diamond → Left → Right → Root → object`. This means that when `Left.path()` executes `super().path()` on a `Diamond` instance, the next method is **Right.path**, *not* `Root.path`. The meaning of `super()` depends on the calling class **and the concrete instance's MRO**. It is a proxy that resumes lookup at a particular point in the MRO; it does not instantiate a parent.

The same rule applies to `__init__`. The `**kwargs` parameter collects extra named arguments into a dictionary; `super().__init__(events=events, **kwargs)` forwards the untouched arguments to the next initializer. `*, left: str, events: list[str]` makes those arguments keyword-only. `list[str]` is Python's built-in generic syntax for a list of strings; `events.append(...)` mutates that list. `["Left", *super().path()]` uses starred iterable unpacking **inside a list literal**; it inserts the superclass chain's elements after `"Left"`.

The constructor does the *calls* Diamond → Left → Right → Root and appends to `events` only **after each nested call returns**. Therefore the visible unwind order is reversed. This is deliberately analogous to nested C# constructor/middleware calls, although C# does not support multiple concrete base-class inheritance.

```python
"""C3 linearization and cooperative multiple-inheritance initialization."""


class Root:
    def __init__(self, *, events: list[str], **kwargs) -> None:
        if kwargs:
            raise TypeError("unexpected keyword arguments")
        self.events = events
        events.append("Root")

    def path(self) -> list[str]:
        return ["Root"]


class Left(Root):
    def __init__(self, *, left: str, events: list[str], **kwargs) -> None:
        self.left = left
        super().__init__(events=events, **kwargs)
        events.append("Left")

    def path(self) -> list[str]:
        return ["Left", *super().path()]


class Right(Root):
    def __init__(self, *, right: str, events: list[str], **kwargs) -> None:
        self.right = right
        super().__init__(events=events, **kwargs)
        events.append("Right")

    def path(self) -> list[str]:
        return ["Right", *super().path()]


class Diamond(Left, Right):
    def __init__(self, *, events: list[str], **kwargs) -> None:
        super().__init__(events=events, **kwargs)
        events.append("Diamond")

    def path(self) -> list[str]:
        return ["Diamond", *super().path()]


def inconsistent_hierarchy_fails() -> bool:
    class X:
        pass

    class Y:
        pass

    class A(X, Y):
        pass

    class B(Y, X):
        pass

    try:
        class Impossible(A, B):
            pass
    except TypeError:
        return True
    return False


if __name__ == "__main__":
    events: list[str] = []
    item = Diamond(events=events, left="L", right="R")
    print("MRO:", " > ".join(cls.__name__ for cls in Diamond.__mro__))
    print("init unwind:", events)
    print("attributes:", item.left, item.right)
    print("method chain:", item.path())
    print("inconsistent MRO:", inconsistent_hierarchy_fails())
```

**Expected output:**

```text
MRO: Diamond > Left > Right > Root > object
init unwind: ['Root', 'Right', 'Left', 'Diamond']
attributes: L R
method chain: ['Diamond', 'Left', 'Right', 'Root']
inconsistent MRO: True
```

## 4. C3 consistency, failure paths, and engineering choices

The `inconsistent_hierarchy_fails()` helper is included in full above. `A(X, Y)` demands that X precede Y; `B(Y, X)` demands the reverse. Python refuses to construct `Impossible(A, B)` with `TypeError`, because no consistent MRO exists. The rejection happens during class definition. A bare `pass` is a syntactic no-op allowed in an otherwise empty class body.

**Common mistakes:**

- **Calling `Root.__init__(self, ...)` directly** from multiple branches bypasses cooperative MRO traversal; the same shared ancestor may be initialized twice. Use consistent `super()` across *all* cooperating classes.
- **Dropping `**kwargs`** in one class can break a diamond, because that class may no longer pass parameters required by the next class in the runtime MRO.
- **Assuming `super()` means “the lexical parent”** is wrong for multiple inheritance. Trace `type(obj).__mro__` first.
- **Confusing mixin and composition:** a small stateless mixin can supply reusable behavior; injecting a collaborator (Lesson 08) is usually easier when dependencies have state or independent lifetimes.
- **C3 is a language guarantee**, not merely a CPython implementation quirk. The MRO is observable through `__mro__` and the class method `mro()`.
- `__init__` initializes an already allocated object; `__new__` creates it. This course's cooperative examples focus on ordinary `__init__` cooperation, not custom allocation.

| C# | Python | Important difference |
|---|---|---|
| `base.Method()` | `super().method()` | Python continues at next MRO entry, not necessarily a direct base |
| `virtual` + `override` | Runtime attribute lookup | No required override keyword; misnaming silently creates a new method |
| Single class + interfaces | Multiple implementation inheritance | Python can inherit concrete behavior from several bases |
| Constructor chaining | Cooperative `super().__init__` | All participants must honor forwarding conventions |

## 5. Validation and exercises

```bash
python examples/dispatch.py
python examples/diamond.py
python -m unittest discover -s tests -v
```

1. Swap `class Diamond(Left, Right)` to `Diamond(Right, Left)`. Predict the new MRO, constructor unwind and `path()` before running.
2. Remove `super().__init__` from `Left`. Predict which initializer is skipped and which attributes are missing.
3. Extend `Flyable` with a `land()` method and create another class that overrides it; explain the selected method using `__mro__`.
4. Explain why `Impossible(A, B)` must fail *before* any object is instantiated.
5. Describe when an injected collaborator is safer than another stateful mixin.

**References:** [Python class inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance), [`super`](https://docs.python.org/3/library/functions.html#super), [MRO / C3](https://docs.python.org/3/howto/mro.html).
