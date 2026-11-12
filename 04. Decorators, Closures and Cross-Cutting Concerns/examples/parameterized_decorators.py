"""A parameterized decorator: factory, decoration, and calls."""


def repeat(times: int):
    """Repeat a call and return the result of its final invocation."""
    if times < 1:
        raise ValueError("times must be >= 1")
    print(f"factory: times={times}")

    def decorator(func):
        print(f"decorate: {func.__name__}")

        def wrapper(*args, **kwargs):
            print(f"wrapper: {times} call(s)")
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator


@repeat(times=2)
def greet(name: str, *, punctuation: str = "!") -> str:
    print(f"body: {name}")
    return f"Hello, {name}{punctuation}"


if __name__ == "__main__":
    print("main: calling greet")
    print("result:", greet("Ada", punctuation="?"))
