"""Inspect the live lexical bindings retained by a Python closure."""


def make_accumulator(start: int):
    total = start

    def add(delta: int) -> int:
        nonlocal total
        total += delta
        return total

    return add


def main() -> None:
    first = make_accumulator(10)
    second = make_accumulator(100)

    print("free vars:", first.__code__.co_freevars)
    print("captured before:", first.__closure__[0].cell_contents)
    print("first call:", first(5))
    print("captured after:", first.__closure__[0].cell_contents)
    print("second call:", second(1))
    print("independent:", first(1))


if __name__ == "__main__":
    main()
