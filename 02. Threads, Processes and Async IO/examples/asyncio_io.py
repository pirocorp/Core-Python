"""Compare sequential awaits, gather and TaskGroup for simulated async I/O.

Requires Python 3.11+ because TaskGroup is used.
"""
from __future__ import annotations

import argparse
import asyncio
import math
from time import perf_counter


def validate(requests: int, delay: float) -> None:
    if requests < 1:
        raise ValueError("requests must be >= 1")
    if not math.isfinite(delay) or delay < 0:
        raise ValueError("delay must be finite and >= 0")


# 'async def' declares a coroutine function; calling it creates a coroutine object.
# Unlike a typical C# async Task<T> call, its body does not start on invocation.
# '-> str' annotates the value produced when the coroutine is awaited.
async def simulated_io(index: int, delay: float) -> str:
    # 'await' suspends this coroutine while the event loop runs other tasks.
    # asyncio.sleep(delay) is non-blocking (similar to C# Task.Delay).
    await asyncio.sleep(delay)
    return f"request-{index}:ok"


async def run_sequential(requests: int, delay: float) -> list[str]:
    validate(requests, delay)
    results: list[str] = []
    for i in range(requests):
        results.append(await simulated_io(i, delay))
    return results


async def run_gather(requests: int, delay: float) -> list[str]:
    validate(requests, delay)
    # create_task() schedules each coroutine on the same event loop.
    tasks = [asyncio.create_task(simulated_io(i, delay)) for i in range(requests)]
    # '*' unpacks a list into positional arguments for asyncio.gather().
    return list(await asyncio.gather(*tasks))


async def run_taskgroup(requests: int, delay: float) -> list[str]:
    validate(requests, delay)
    # TaskGroup (3.11+) waits for children and manages failure/cancellation.
    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(simulated_io(i, delay)) for i in range(requests)]
    # Once the 'async with' block exits successfully, every task has completed.
    return [task.result() for task in tasks]


async def timed(coroutine) -> tuple[float, list[str]]:
    start = perf_counter()
    value = await coroutine
    return perf_counter() - start, value


async def demo(requests: int, delay: float) -> None:
    validate(requests, delay)
    t1, serial = await timed(run_sequential(requests, delay))
    t2, gathered = await timed(run_gather(requests, delay))
    t3, grouped = await timed(run_taskgroup(requests, delay))
    if not (serial == gathered == grouped):
        raise RuntimeError("The results differ")

    print(f"Sequential await: {t1:.3f}s")
    print(f"gather():         {t2:.3f}s")
    print(f"TaskGroup:        {t3:.3f}s")
    print(f"Same results: {serial == gathered == grouped}")
    print("These tasks overlap I/O waits; they do not create extra OS threads.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requests", type=int, default=3)
    parser.add_argument("--delay", type=float, default=0.2)
    args = parser.parse_args()
    # asyncio.run() creates/drives/closes an event loop at the application edge.
    asyncio.run(demo(args.requests, args.delay))


if __name__ == "__main__":
    main()
