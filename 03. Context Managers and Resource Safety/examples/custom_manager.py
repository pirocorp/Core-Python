"""Implement the synchronous context-manager protocol explicitly."""
from __future__ import annotations

from types import TracebackType


class MyContextManager:
    """Log __enter__/__exit__ calls and optionally suppress one exception type."""

    def __init__(
        self,
        name: str,
        events: list[str],
        suppress_type: type[Exception] | None = None,
    ) -> None:
        self.name = name
        self.events = events
        self.suppress_type = suppress_type

    def __enter__(self) -> str:
        # 'as resource' receives THIS return value, not necessarily 'self'.
        self.events.append(f"enter:{self.name}")
        return f"resource:{self.name}"

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> bool:
        # On a normal exit, all three exception arguments are None.
        # On an exceptional exit, Python supplies exception information.
        label = exc_type.__name__ if exc_type is not None else "none"
        self.events.append(f"exit:{self.name}:{label}")

        # A truthy result suppresses an exception raised in the with body.
        # Never suppress everything by accident: match only the allowed type.
        return (
            exc_type is not None
            and self.suppress_type is not None
            and issubclass(exc_type, self.suppress_type)
        )


class FailingEnter:
    """Demonstrate that __exit__ is NOT called if __enter__ raises."""

    def __init__(self, events: list[str]) -> None:
        self.events = events

    def __enter__(self) -> None:
        self.events.append("enter:failed")
        raise RuntimeError("acquisition failed")

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> bool:
        self.events.append("exit:should-not-run")
        return False


def run_nested() -> list[str]:
    events: list[str] = []
    # Multiple managers are nested left to right and released right to left.
    with MyContextManager("outer", events) as outer, MyContextManager(
        "inner", events
    ) as inner:
        events.append(f"body:{outer},{inner}")
    return events


def run_exception(suppress: bool) -> list[str]:
    events: list[str] = []
    try:
        with MyContextManager(
            "guard", events, suppress_type=ValueError if suppress else None
        ):
            events.append("body:raise")
            raise ValueError("demo failure")
    except ValueError:
        events.append("caught:ValueError")
    events.append("after:with")
    return events


def run_failed_enter() -> list[str]:
    events: list[str] = []
    try:
        with FailingEnter(events):
            events.append("body:never-runs")
    except RuntimeError:
        events.append("caught:RuntimeError")
    return events


def run_early_return() -> list[str]:
    events: list[str] = []

    def operation() -> str:
        with MyContextManager("early", events):
            events.append("body:return")
            return "returned"

    events.append(operation())
    return events


def main() -> None:
    for title, events in [
        ("Nested managers", run_nested()),
        ("Exception propagated", run_exception(False)),
        ("Exception suppressed", run_exception(True)),
        ("Failed __enter__", run_failed_enter()),
        ("Early return", run_early_return()),
    ]:
        print(f"{title}: {' | '.join(events)}")


if __name__ == "__main__":
    main()
