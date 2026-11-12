"""Function wrappers on methods, descriptors, and standard-library caching."""

from functools import lru_cache, wraps


def track(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"call: {func.__name__}")
        return func(*args, **kwargs)

    return wrapper


class Greeter:
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    @track
    def greet(self, name: str) -> str:
        return f"{self.prefix}, {name}"

    @classmethod
    @track
    def describe(cls) -> str:
        return cls.__name__

    @staticmethod
    @track
    def version() -> int:
        return 1

    @property
    def label(self) -> str:
        return self.prefix


@lru_cache(maxsize=4)
def normalize(value: str) -> str:
    print("normalize: computing")
    return value.strip().upper()


def main() -> None:
    greeter = Greeter("Hello")
    print("method:", greeter.greet("Ada"))
    print("class method:", Greeter.describe())
    print("static method:", Greeter.version())
    print("property:", greeter.label)
    print("normalized:", normalize("  abc "))
    print("cached:", normalize("  abc "))
    print("cache:", normalize.cache_info().hits, normalize.cache_info().misses)


if __name__ == "__main__":
    main()
