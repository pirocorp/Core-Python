"""Async wrappers: coroutine creation, execution, errors, and cancellation."""

import asyncio
import inspect
from functools import wraps
from typing import Awaitable, Callable, ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")


def trace_async(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print("async: enter")
        try:
            return await func(*args, **kwargs)
        finally:
            print("async: exit")

    return wrapper


def sync_wrapper_for_async(
    func: Callable[P, Awaitable[R]],
) -> Callable[P, Awaitable[R]]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> Awaitable[R]:
        print("sync wrapper: called")
        return func(*args, **kwargs)

    return wrapper


@trace_async
async def work(kind: str, ready: asyncio.Event | None = None) -> str:
    print("body:", kind)
    if kind == "error":
        raise ValueError("boom")
    if kind == "cancel":
        assert ready is not None
        ready.set()
        await asyncio.Event().wait()  # Suspend until the task is cancelled.
    await asyncio.sleep(0)
    return "done"


@sync_wrapper_for_async
async def delayed() -> str:
    print("delayed body")
    return "late"


async def main() -> None:
    print("async function:", inspect.iscoroutinefunction(work))
    coroutine = work("ok")
    print("coroutine created")
    print("result:", await coroutine)

    print("sync wrapper is async:", inspect.iscoroutinefunction(delayed))
    delayed_coroutine = delayed()
    print("delayed coroutine:", inspect.iscoroutine(delayed_coroutine))
    print("delayed result:", await delayed_coroutine)

    try:
        await work("error")
    except ValueError:
        print("caught: ValueError")

    ready = asyncio.Event()
    task = asyncio.create_task(work("cancel", ready))
    await ready.wait()  # Wait until the task has started its body.
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("caught: CancelledError")


if __name__ == "__main__":
    asyncio.run(main())
