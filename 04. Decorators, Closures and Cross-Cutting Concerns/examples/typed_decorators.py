"""Preserve a decorated callable's static parameter and result types."""

from functools import wraps
from typing import Callable, ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")


def audit(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"audit: enter {func.__name__}")
        try:
            return func(*args, **kwargs)
        finally:
            print(f"audit: exit {func.__name__}")

    return wrapper


@audit
def calculate(amount: int, *, multiplier: int = 2) -> int:
    """Multiply an integer amount."""
    return amount * multiplier


def main() -> None:
    print("name:", calculate.__name__)
    print("result:", calculate(7, multiplier=3))


if __name__ == "__main__":
    main()
