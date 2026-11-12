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
