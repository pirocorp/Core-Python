"""New extension (not in slides): refcounts alone cannot reclaim cycles."""

import gc
import weakref


class Node:
    def __init__(self) -> None:
        self.next: Node | None = None


def make_unreachable_cycle() -> weakref.ReferenceType[Node]:
    node = Node()
    node.next = node  # One object references itself.
    return weakref.ref(node)


def run() -> None:
    gc.collect()  # Remove previous unrelated garbage for clarity.
    ref = make_unreachable_cycle()
    print(f"Alive after scope ends: {ref() is not None}")
    unreachable = gc.collect()
    print(f"Alive after gc.collect(): {ref() is not None}")
    print(f"Unreachable objects collected (implementation-dependent): {unreachable}")
    assert ref() is None


if __name__ == "__main__":
    run()
