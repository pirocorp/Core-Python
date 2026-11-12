# 05 — Abstract Base Classes and Interface-Like Contracts

**Audience:** Senior C#/.NET engineers learning Python's runtime contract model.

## 1. Mental model: nominal, structural, and dynamic contracts

C# interfaces have a compile-time contract and runtime implementation identity. Python has several distinct mechanisms: an **abstract base class (ABC)** is a nominal runtime relationship, a **typing.Protocol** expresses a structural contract primarily for static checkers, and plain **duck typing** relies on whether an operation succeeds at runtime. No `interface` keyword exists.

An ABC is a class with an `ABCMeta` metaclass (using `ABC` is the normal convenience). Its abstract methods are checked **when an instance is created**, not when the class definition is executed. The class can define concrete methods, fields and reusable behavior. It does not validate return types, method signatures, or arbitrary business semantics at runtime. Even an overriding method with an incompatible signature can satisfy the abstractness check and fail later when invoked.

`from abc import ABC, abstractmethod` imports the standard-library abstract base class marker and a decorator that flags methods as abstract. `from math import pi` imports the mathematical constant π. `self` is the explicitly named instance parameter, unlike C#'s implicit `this`; `self.radius**2` uses Python's exponentiation operator. `: float` and `-> float` are *annotations*, not automatic runtime validation. An empty abstract method body can contain only a docstring; `@abstractmethod` enforces implementation, not the content of the method.

## 2. ABC enforcement and a reusable template method

The following is the **entire independently executable** `examples/abcs.py`. The `describe()` method is a concrete method calling abstract operations: it is a small Template Method pattern. `f"{value:.2f}"` uses Python's f-string formatting to show two digits after the decimal point. `isinstance(obj, Shape)` checks nominal ABC membership; `try/except` handles the indicated errors.

```python
"""Nominal contracts: ABC, abstract methods, concrete template methods."""

from abc import ABC, abstractmethod
from math import pi


class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        """Return the shape's area."""

    @abstractmethod
    def perimeter(self) -> float:
        """Return the shape's perimeter."""

    def describe(self) -> str:
        return f"area={self.area():.2f}, perimeter={self.perimeter():.2f}"


class Circle(Shape):
    def __init__(self, radius: float) -> None:
        if radius <= 0:
            raise ValueError("radius must be positive")
        self.radius = radius

    def area(self) -> float:
        return pi * self.radius**2

    def perimeter(self) -> float:
        return 2 * pi * self.radius


class IncompleteShape(Shape):
    def area(self) -> float:
        return 1.0


if __name__ == "__main__":
    circle = Circle(2)
    print("shape:", circle.describe())
    print("nominal:", isinstance(circle, Shape))
    try:
        IncompleteShape()
    except TypeError:
        print("incomplete: TypeError")
    try:
        Circle(0)
    except ValueError:
        print("invalid radius: ValueError")
```

**Expected output:**

```text
shape: area=12.57, perimeter=12.57
nominal: True
incomplete: TypeError
invalid radius: ValueError
```

## 3. Payment gateways: template validation, Protocol, virtual registration

The entire `examples/gateways.py` models two concrete implementations, an unrelated third-party-compatible object, and a deliberately misleading virtual subclass.

`from typing import Protocol, runtime_checkable` imports Python's structural typing base and an opt-in decorator enabling basic `isinstance` runtime membership checks. **Ordinary `Protocol` is used by static type checkers**; runtime checking via `@runtime_checkable` generally verifies attribute presence, *not parameter and return types or method semantics*. The ellipsis `...` in a protocol body is a legal placeholder for an interface-like method declaration. `getattr(obj, "charge", None)` safely looks up an optional attribute, returning `None` if missing. `callable(...)` checks whether it can be invoked. All money amounts use integer cents to avoid binary floating-point currency errors.

`PaymentGateway.register(RegisteredWithoutMethods)` uses ABC virtual-subclass registration. It can make `isinstance` report **True**, but it does not add missing methods, insert the ABC into the MRO, or turn the class into a concrete implementation. This is a sharp difference from a C# interface implementation. The example prints this failure rather than attempting an invalid charge.

```python
"""ABC nominal contracts, structural Protocols, and virtual registration."""

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount_cents: int) -> str:
        """Charge an amount expressed as whole cents."""

    def checkout(self, amount_cents: int) -> str:
        if amount_cents <= 0:
            raise ValueError("amount must be positive")
        return self.charge(amount_cents)


class CardGateway(PaymentGateway):
    def charge(self, amount_cents: int) -> str:
        return f"card:{amount_cents}"


class PayPalGateway(PaymentGateway):
    def charge(self, amount_cents: int) -> str:
        return f"paypal:{amount_cents}"


class ExternalGateway:
    def charge(self, amount_cents: int) -> str:
        return f"external:{amount_cents}"


@runtime_checkable
class SupportsCharge(Protocol):
    def charge(self, amount_cents: int) -> str:
        ...


class RegisteredWithoutMethods:
    pass


PaymentGateway.register(RegisteredWithoutMethods)


if __name__ == "__main__":
    for gateway in (CardGateway(), PayPalGateway()):
        print("checkout:", gateway.checkout(150))
    external = ExternalGateway()
    print("external nominal:", isinstance(external, PaymentGateway))
    print("external structural:", isinstance(external, SupportsCharge))
    print("registered nominal:", isinstance(RegisteredWithoutMethods(), PaymentGateway))
    print("registered callable:", callable(getattr(RegisteredWithoutMethods(), "charge", None)))
    try:
        CardGateway().checkout(0)
    except ValueError:
        print("invalid amount: ValueError")
```

**Expected output:**

```text
checkout: card:150
checkout: paypal:150
external nominal: False
external structural: True
registered nominal: True
registered callable: False
invalid amount: ValueError
```

## 4. Important engineering rules and failure modes

- **Choose an ABC** when you own a nominal hierarchy and need instantiation-time abstract-method enforcement and potentially shared implementation. An ABC alone is not a secure validation boundary.
- **Choose a Protocol** when call sites should accept independent implementations based on shape, such as test doubles or third-party SDK adapters. A type checker can verify signatures; the default Python interpreter does not.
- **Use duck typing** for simple, local boundaries when a formal nominal or static contract would not improve maintainability. The failed operation may raise `AttributeError` or `TypeError`.
- **Avoid broad `except AttributeError`** around a collaborator call; this can hide errors *inside* the collaborator. Validate the boundary or let a meaningful exception surface.
- **ABC abstract properties:** `@property` over `@abstractmethod` defines an abstract read-only property; the order of decorators matters. As in Lesson 04, a decorator transforms a function definition.
- **Default implementations do not guarantee substitutability:** even if a subclass satisfies all abstract members, it can still violate business invariants. Test observable behavior (contract tests), not only `isinstance`.

### C# mapping

| C# mechanism | Closest Python facility | Difference |
|---|---|---|
| `interface IPaymentGateway` | `Protocol` or `ABC` | Protocol is structural for tools; ABC is nominal runtime enforcement |
| `abstract class Shape` | `class Shape(ABC)` | ABC abstractness enforced at instantiation, not during compilation |
| Explicit interface implementation | No direct equivalent | Use adaptors, Protocols or nominal classes |
| `is` or `as` interface type | `isinstance` for ABC | Virtual subclass registration can make this check surprisingly broad |
| Generic constraint on interface | `TypeVar` bound / Protocol | Static analysis optional, no implicit runtime constraint enforcement |

## 5. Validation and exercises

From this lesson directory run:

```bash
python examples/abcs.py
python examples/gateways.py
python -m unittest discover -s tests -v
```

1. Add `Rectangle(Shape)` and derive expected area and perimeter for width=3, height=4. Show that omitting `perimeter` prevents instantiation.
2. Replace `ExternalGateway.charge` with a mismatched signature; explain why `isinstance(x, SupportsCharge)` is not a complete contract test.
3. Explain which gateway types can be passed to a function expecting `SupportsCharge` according to a static checker, and what changes under plain runtime Python.
4. Implement a single contract-test helper that checks a successful charge and the `checkout(0)` error for every nominal payment gateway.
5. Explain why `PaymentGateway.register(...)` should not be used to "fix" an incompatible third-party SDK.

**Official reference:** [abc](https://docs.python.org/3/library/abc.html), [typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol), [data model](https://docs.python.org/3/reference/datamodel.html).

