"""Safely acquire a dynamic number of resources with ExitStack."""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import ExitStack, contextmanager


@contextmanager
def acquire(name: str, events: list[str], fail: bool = False) -> Iterator[str]:
    # This records the *attempt*; a later failure may prevent acquisition.
    events.append(f"acquire:{name}")
    if fail:
        # No resource was acquired by this manager; its generator never
        # reached yield, so its own finally is not active.
        raise RuntimeError(f"cannot acquire {name}")

    try:
        yield name
    finally:
        events.append(f"release:{name}")


def run_batch(
    names: tuple[str, ...], fail_on: str | None = None
) -> tuple[list[str], list[str]]:
    """Return event log and successfully acquired names."""
    events: list[str] = []
    acquired: list[str] = []

    try:
        # ExitStack replaces deeply nested with statements when the number
        # of resources is known only at runtime.
        with ExitStack() as stack:
            for name in names:
                # enter_context calls __enter__ and registers __exit__.
                # A later failure releases all previously acquired resources.
                resource = stack.enter_context(
                    acquire(name, events, fail=(name == fail_on))
                )
                acquired.append(resource)
            events.append(f"work:{','.join(acquired)}")
        # Exiting the stack releases resources in LIFO order.
    except RuntimeError as exc:
        events.append(f"error:{exc}")

    return events, acquired


def main() -> None:
    for title, fail_on in [("Success", None), ("Partial acquisition", "db")]:
        events, acquired = run_batch(("file", "db", "socket"), fail_on)
        print(f"{title}: {' | '.join(events)}")
        print(f"Acquired before cleanup: {acquired}")


if __name__ == "__main__":
    main()
