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
