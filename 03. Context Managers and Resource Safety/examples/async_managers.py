"""Asynchronous context managers, dynamic cleanup, and cancellation."""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager
from types import TracebackType


class AsyncConnection:
    """An async context manager with awaited acquisition and release."""

    def __init__(self, name: str, events: list[str]) -> None:
        self.name = name
        self.events = events

    async def __aenter__(self) -> str:
        await asyncio.sleep(0)  # Simulate non-blocking I/O on acquisition.
        self.events.append(f"open:{self.name}")
        return self.name

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> bool:
        await asyncio.sleep(0)  # Simulate non-blocking I/O on release.
        self.events.append(f"close:{self.name}")
        return False  # Propagate any body exception.


# @asynccontextmanager is a decorator for async generator-based managers.
# Its @ syntax and transformation mechanics are explained in Lesson 04.
@asynccontextmanager
async def async_resource(name: str, events: list[str]) -> AsyncIterator[str]:
    """An async generator-based manager; yield exactly one value."""
    events.append(f"open:{name}")
    try:
        await asyncio.sleep(0)
        yield name
    finally:
        # The async finally is awaited even if the body is cancelled.
        await asyncio.sleep(0)
        events.append(f"close:{name}")


async def run_connection() -> list[str]:
    events: list[str] = []
    async with AsyncConnection("db", events) as name:
        events.append(f"use:{name}")
    return events


async def run_async_stack() -> list[str]:
    events: list[str] = []
    async with AsyncExitStack() as stack:
        for name in ("db", "cache"):
            resource = await stack.enter_async_context(async_resource(name, events))
            events.append(f"registered:{resource}")
        events.append("work")
    return events


async def run_async_error() -> list[str]:
    events: list[str] = []
    try:
        async with async_resource("db", events):
            events.append("body:raise")
            raise ValueError("operation failed")
    except ValueError:
        events.append("caught:ValueError")
    return events


async def run_cancellation() -> list[str]:
    """Cancel a task while it owns a resource; awaited finally still runs."""
    events: list[str] = []
    entered = asyncio.Event()
    never_complete = asyncio.Event()

    async def operation() -> None:
        async with async_resource("stream", events):
            entered.set()
            await never_complete.wait()

    task = asyncio.create_task(operation())
    await entered.wait()  # Ensure resource ownership before cancellation.
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        events.append("caught:CancelledError")
    return events


async def main() -> None:
    for title, events in [
        ("Async class", await run_connection()),
        ("AsyncExitStack", await run_async_stack()),
        ("Async exception", await run_async_error()),
        ("Cancellation", await run_cancellation()),
    ]:
        print(f"{title}: {' | '.join(events)}")


if __name__ == "__main__":
    asyncio.run(main())
