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
