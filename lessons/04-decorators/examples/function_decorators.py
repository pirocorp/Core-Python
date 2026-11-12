"""A simple Python function decorator built using a higher-order function.

Run from this lesson directory:
    python examples/function_decorators.py
"""


def log_calls(func):
    """Return a function that invokes func with extra logging."""

    def wrapper():
        # 'func' is captured from log_calls's enclosing scope (a closure).
        print("Before")
        func()
        print("After")

    return wrapper


@log_calls
def hello():
    print("Hello")


if __name__ == "__main__":
    hello()
