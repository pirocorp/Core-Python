"""Metadata-preserving wrappers, stacked decorators, and execution order."""

from functools import wraps
from inspect import signature


def trace(label: str):
    """Wrap a function with labeled entry and exit messages."""
    print(f"factory: {label}")

    def decorator(func):
        print(f"decorate: {label}")

        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"enter: {label}")
            try:
                return func(*args, **kwargs)
            finally:
                print(f"exit: {label}")

        return wrapper

    return decorator


@trace("outer")
@trace("inner")
def add(a: int, b: int = 1) -> int:
    """Return the sum of a and b."""
    print("body: add")
    return a + b


if __name__ == "__main__":
    print("name:", add.__name__)
    print("doc:", add.__doc__)
    print("signature:", signature(add))
    print("runtime signature:", signature(add, follow_wrapped=False))
    print("result:", add(3, b=4))
