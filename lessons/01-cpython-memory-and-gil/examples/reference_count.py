"""Runnable extension of slide 7 (requires CPython for getrefcount)."""

import platform
import sys


def run() -> None:
    if platform.python_implementation() != "CPython":
        print("This example illustrates CPython internals; numbers may differ.")

    a = []
    print(f"After a = []:                 {sys.getrefcount(a)}")

    b = a
    print(f"After b = a:                  {sys.getrefcount(a)}")
    print(f"a is b:                       {a is b}")

    del b
    print(f"After del b:                  {sys.getrefcount(a)}")
    print("Each getrefcount(a) call includes a temporary argument reference.")
    print("Avoid asserting exact numeric counts in production code.")


if __name__ == "__main__":
    run()
