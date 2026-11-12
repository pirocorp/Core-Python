# 08 — Composition and Object Collaboration

**Audience:** Senior .NET backend engineers. The design principle is familiar; the emphasis is on Python's **implicit structural compatibility**, its lightweight dependency injection style, runtime contract pitfalls, and ownership.

## 1. Composition does not require inheritance or a DI container

Python composition is ordinary object referencing: a `Car` stores an `Engine`-like collaborator and forwards behavior to it. In C# you might register `IEngine` in `Microsoft.Extensions.DependencyInjection`. Python supports containers but **does not require a framework** for constructor injection: the composition root simply constructs and passes the collaborator.

`from typing import Protocol` imports a standard-library structural typing contract. `EnginePort` documents that a collaborator must expose `start() -> str`; a static checker can verify it. It does **not** cause runtime injection, automatically instantiate an engine, or reject a wrong object at runtime. Python protocols are discussed in Lesson 05.

`self` is the explicit instance parameter; `self.engine = engine` stores a reference, not a copy. An object supplied to the constructor is **not automatically owned by the receiver**; decide who opens, closes and shares its resources. The `f"car: {self.engine.start()}"` syntax interpolates the method's returned text.

## 2. Engine composed into Car: internal construction vs injection

Complete executable `examples/engine_injection.py`:

```python
"""Car/Engine composition with a swappable collaborator."""

from typing import Protocol


class EnginePort(Protocol):
    def start(self) -> str:
        ...


class Engine:
    def start(self) -> str:
        return "engine running"


class FakeEngine:
    def __init__(self) -> None:
        self.calls = 0

    def start(self) -> str:
        self.calls += 1
        return "fake engine"


class Car:
    def __init__(self, engine: EnginePort) -> None:
        self.engine = engine

    def start(self) -> str:
        return f"car: {self.engine.start()}"


class TightlyCoupledCar:
    def __init__(self) -> None:
        self.engine = Engine()

    def start(self) -> str:
        return f"car: {self.engine.start()}"


if __name__ == "__main__":
    print("real:", Car(Engine()).start())
    fake = FakeEngine()
    car = Car(fake)
    print("fake:", car.start())
    print("fake calls:", fake.calls)
    print("constructed internally:", TightlyCoupledCar().start())
```

**Expected output:**

```text
real: car: engine running
fake: car: fake engine
fake calls: 1
constructed internally: car: engine running
```

### Why the two constructors matter

- `TightlyCoupledCar.__init__` *creates* an `Engine` on every instance. Replacing it in tests is awkward and tightly couples production code to the concrete implementation.
- `Car.__init__(engine: EnginePort)` accepts an existing collaborator. `Car(FakeEngine())` works without inheritance from `Engine` or runtime interface registration: it is structurally compatible.
- `FakeEngine.calls` records a test-observable side effect; this is a **manual fake** with behavior, rather than a mocking framework. Each fake object has its own counter.
- The caller can pass the *same* engine instance to several cars or share a singleton. Whether it is thread-safe and when it is disposed are separate architectural decisions.
- An incompatible object will often fail at the point of use (`AttributeError` or `TypeError`), because ordinary Python type annotations do not enforce contracts.

## 3. A backend service with replaceable storage and time

This complete `examples/order_service.py` applies composition to an order-write use case. It separates the policy (validate and accept an order) from external effects (storage and time).

`Callable[[], str]` from `typing` describes a callable with no arguments returning a string, comparable to `Func<string>` in C#. `lambda: "2026-11-12T12:00Z"` is a zero-argument lambda returning a deterministic value; it is a stand-in for a clock. `list[tuple[str, str]]` is a list of two-element tuples; `append` adds an item to the list. `Protocol` is a type description rather than a concrete inherited class. The `raise ValueError` and `raise OSError` statements represent distinct validation and infrastructure failures; `try/except` catches them where the demo chooses to report them.

```python
"""Constructor injection, fake repositories, and a deterministic clock."""

from typing import Callable, Protocol


class OrderStore(Protocol):
    def save(self, order_id: str, timestamp: str) -> None:
        ...


class InMemoryOrders:
    def __init__(self) -> None:
        self.saved: list[tuple[str, str]] = []

    def save(self, order_id: str, timestamp: str) -> None:
        self.saved.append((order_id, timestamp))


class FailingOrders:
    def save(self, order_id: str, timestamp: str) -> None:
        raise OSError("storage unavailable")


class OrderService:
    def __init__(self, store: OrderStore, clock: Callable[[], str]) -> None:
        self.store = store
        self.clock = clock

    def place(self, order_id: str) -> str:
        if not order_id:
            raise ValueError("order_id is required")
        timestamp = self.clock()
        self.store.save(order_id, timestamp)
        return f"accepted:{order_id}@{timestamp}"


if __name__ == "__main__":
    store = InMemoryOrders()
    service = OrderService(store, lambda: "2026-11-12T12:00Z")
    print("placed:", service.place("O-42"))
    print("saved:", store.saved)
    try:
        service.place("")
    except ValueError:
        print("invalid id: ValueError")
    failed = OrderService(FailingOrders(), lambda: "fixed")
    try:
        failed.place("O-43")
    except OSError:
        print("storage failure: OSError")
```

**Expected output:**

```text
placed: accepted:O-42@2026-11-12T12:00Z
saved: [('O-42', '2026-11-12T12:00Z')]
invalid id: ValueError
storage failure: OSError
```

## 4. Ownership, fault boundaries and design decisions

The service validates `order_id` **before** invoking the clock or store. In production, the repository may involve a connection or transaction; this example intentionally does *not* claim atomicity or retries. If `save` fails, the service propagates `OSError` and does **not** return an accepted result. A real persistence contract may need idempotency keys, transactional boundaries or retry policy; these belong around the infrastructure layer, not in a fake that silently swallows failures.

**Resource lifetimes:** Injecting an already-created connection or client does not automatically transfer ownership. If `OrderService` creates its own client, it is often responsible for closing it; if a caller supplies a shared client, the caller typically controls its lifetime. Use `with` / `async with` and context managers (Lesson 03) where deterministic acquisition/release is needed; avoid adding a `close()` method to every object merely because it holds a reference.

**Python-specific pitfalls:** structural contracts are normally checked only by tooling; mutable fake state can leak between tests unless each test creates a fresh fake; and accidentally using a default argument such as `def __init__(self, engine=FakeEngine())` would create a shared default object **at function definition time**. Prefer explicitly supplied dependencies or `None` with per-instance creation.

| Concern | C# convention | Python idiom |
|---|---|---|
| Constructor injection | `Car(IEngine engine)` | `Car(engine: EnginePort)` |
| Interface-like contract | `interface IEngine` | `Protocol` (optional static tooling) |
| Test double | Mock/NSubstitute/fake | Plain object with compatible methods |
| Container | ASP.NET Core built-in DI | Explicit composition root or optional container |
| Ownership | `IDisposable`/`IAsyncDisposable` | `with`/`async with` and explicit lifetime policy |

## 5. Validation and exercises

```bash
python examples/engine_injection.py
python examples/order_service.py
python -m unittest discover -s tests -v
```

1. Make two `Car` instances use a shared `FakeEngine`; predict the counter after starting each once.
2. Verify that an invalid order ID does **not** call the clock or storage (use simple counters).
3. Inject a store that records a call and then raises; explain why the service must not print or return an accepted outcome.
4. Extend `OrderService` with an injected ID generator, without importing a DI library.
5. Specify who should close a shared database client when two services receive the same instance and how context-manager semantics fit.

**References:** [typing.Protocol](https://docs.python.org/3/library/typing.html#typing.Protocol), [contextlib](https://docs.python.org/3/library/contextlib.html), [unittest](https://docs.python.org/3/library/unittest.html).
