"""Closures: lexical capture, nonlocal state and late-binding loop variables.

Run:
    python examples/closures.py
"""


def make_counter(start: int = 0):
    count = start

    def increment() -> int:
        nonlocal count  # Rebind count in the enclosing make_counter scope.
        count += 1
        return count

    return increment  # Return a function; do NOT invoke increment() here.


def demonstrate_late_binding() -> tuple[list[int], list[int]]:
    late = []
    snapshots = []

    for factor in range(3):  # factor takes 0, 1, then 2.
        late.append(lambda value: factor * value)
        snapshots.append(lambda value, factor=factor: factor * value)

    # The late lambdas all refer to the SAME factor binding, now equal to 2.
    # The default argument is evaluated when each lambda is created.
    return [fn(3) for fn in late], [fn(3) for fn in snapshots]


def main() -> None:
    first = make_counter(10)
    second = make_counter(0)
    print("first:", first(), first())
    print("second:", second())
    print("first again:", first())

    late, snapshots = demonstrate_late_binding()
    print("late:", late)
    print("snapshots:", snapshots)


if __name__ == "__main__":
    main()
