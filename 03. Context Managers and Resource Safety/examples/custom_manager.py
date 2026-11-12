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

        # suppress_type is OUR optional constructor parameter, not a Python
        # keyword. Passing suppress_type=ValueError stores the ValueError
        # CLASS (not ValueError("message"), which would be an instance).
        # None means no exception type is allowed to be suppressed.
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
        # Important: there is no "catch" statement inside this method.
        # When code inside 'with' raises an exception, Python's 'with'
        # mechanism AUTOMATICALLY calls __exit__ BEFORE the outer
        # 'except ValueError:' handler gets a chance to run.
        #
        # For 'raise ValueError("demo failure")', Python supplies:
        #   exc_type      -> ValueError (the exception CLASS)
        #   exc_value     -> ValueError("demo failure") (the exception OBJECT)
        #   exc_traceback -> the traceback describing where it happened
        # On normal exit, all three are None.
        label = exc_type.__name__ if exc_type is not None else "none"
        self.events.append(f"exit:{self.name}:{label}")

        # Python decides what happens NEXT based on this return value:
        #   True  -> the 'with' statement suppresses the pending exception;
        #            execution continues AFTER the 'with' block, so the
        #            outer 'except ValueError:' is NOT executed.
        #   False -> Python propagates the exception, allowing the outer
        #            'except ValueError:' to catch it.
        #
        # Example: if suppress_type=ValueError and the body raises ValueError,
        # all three checks below are True, so __exit__ returns True.
        # We restrict suppression to the configured class (and subclasses).
        return (
            # Did an exception occur in the body of 'with'?
            exc_type is not None
            # Did the caller configure a type to suppress?
            and self.suppress_type is not None
            # Is the raised exception of that class or one of its subclasses?
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

    # Python's 'try/except' is the equivalent of C# 'try/catch'.
    try:
        # If suppress=True, the manager stores the ValueError CLASS.
        # If suppress=False, it stores None and will NOT suppress errors.
        with MyContextManager(
            "guard", events, suppress_type=ValueError if suppress else None
        ):
            events.append("body:raise")

            # 1. 'raise' is Python's equivalent of C# 'throw'.
            # 2. Python interrupts the 'with' body at this line.
            # 3. Before reaching the outer 'except', Python calls the
            #    active manager's __exit__(ValueError, exception, traceback).
            # 4. __exit__ returns True (suppress=True) or False (suppress=False).
            raise ValueError("demo failure")

    except ValueError:
        # Reached ONLY when __exit__ returned False (or another falsy value).
        # When __exit__ returned True, Python ALREADY suppressed the error.
        events.append("caught:ValueError")

    # In both cases execution eventually continues here.
    # The remaining statements inside the 'with' body are NOT resumed.
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
