"""Build a reusable context manager with contextlib.contextmanager."""
from __future__ import annotations

from contextlib import contextmanager, nullcontext, suppress
from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory


# @contextmanager is a decorator: it makes this yield-based function usable
# with 'with'. Decorator syntax and internals are covered in Lesson 04.
@contextmanager
def traced_resource(name: str, events: list[str]) -> Iterator[str]:
    """A generator-based context manager must yield exactly one resource."""
    events.append(f"acquire:{name}")
    try:
        yield f"resource:{name}"  # __enter__ returns the yielded value.
    finally:
        # On exceptions, control resumes at 'yield' with the exception.
        # This finally executes before the exception propagates.
        events.append(f"release:{name}")


def run_traced(fail: bool = False) -> list[str]:
    events: list[str] = []
    try:
        with traced_resource("cache", events) as resource:
            events.append(f"use:{resource}")
            if fail:
                raise ValueError("work failed")
    except ValueError:
        events.append("caught:ValueError")
    return events


def run_suppress() -> list[str]:
    events: list[str] = []
    # An optional cache file may already be absent. That is not a failure.
    # Use a fresh temporary directory so the demo is deterministic and never
    # touches user files. Do not manufacture an error with 'raise' here.
    with TemporaryDirectory(prefix="context-suppress-demo-") as directory:
        missing_cache = Path(directory) / "optional-cache.txt"
        # Only FileNotFoundError is ignored. PermissionError and other
        # unexpected failures are still propagated to the caller.
        with suppress(FileNotFoundError):
            events.append("attempt:optional-cache")
            missing_cache.unlink()  # Raises FileNotFoundError for a missing path.
        events.append("continue:without-cache")
    return events


def run_optional(enabled: bool) -> list[str]:
    events: list[str] = []
    # nullcontext is a no-op stand-in for an optional context manager.
    # This avoids duplicating the same with body in an if/else branch.
    manager = traced_resource("optional", events) if enabled else nullcontext("direct")
    with manager as resource:
        events.append(f"use:{resource}")
    return events


def main() -> None:
    for title, events in [
        ("Normal generator manager", run_traced()),
        ("Exception in generator manager", run_traced(True)),
        ("Selective suppression", run_suppress()),
        ("Optional manager on", run_optional(True)),
        ("Optional manager off", run_optional(False)),
    ]:
        print(f"{title}: {' | '.join(events)}")


if __name__ == "__main__":
    main()
