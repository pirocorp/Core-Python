"""Demonstrate why blocking operations should not run in the event loop."""
from __future__ import annotations

import argparse
import asyncio
import math
from time import perf_counter, sleep


def validate(requests: int, delay: float) -> None:
    if requests < 1 or not math.isfinite(delay) or delay < 0:
        raise ValueError("requests must be >= 1 and delay must be finite and >= 0")


async def bad_blocking(index: int, delay: float) -> str:
    # A coroutine runs on the event-loop thread until it yields at an await.
    # time.sleep() blocks THAT thread, even if CPython releases the GIL.
    # Therefore other scheduled asyncio Tasks cannot progress during this wait.
    sleep(delay)  # BAD: blocks the event-loop thread until sleep finishes.
    return f"request-{index}:ok"


async def bridge_blocking(index: int, delay: float) -> str:
    # to_thread() runs a synchronous/blocking callable in a worker thread.
    # 'await' yields control while that thread waits.
    await asyncio.to_thread(sleep, delay)
    return f"request-{index}:ok"


async def run_bad(requests: int, delay: float) -> list[str]:
    validate(requests, delay)
    return list(await asyncio.gather(
        *(bad_blocking(i, delay) for i in range(requests))
    ))


async def run_bridged(requests: int, delay: float) -> list[str]:
    validate(requests, delay)
    return list(await asyncio.gather(
        *(bridge_blocking(i, delay) for i in range(requests))
    ))


async def demo(requests: int, delay: float) -> None:
    start = perf_counter()
    bad = await run_bad(requests, delay)
    blocked_time = perf_counter() - start

    start = perf_counter()
    bridged = await run_bridged(requests, delay)
    bridged_time = perf_counter() - start
    if bad != bridged:
        raise RuntimeError("Inconsistent responses")

    print(f"Blocking the event loop: {blocked_time:.3f}s")
    print(f"asyncio.to_thread():     {bridged_time:.3f}s")
    print(f"Same results: {bad == bridged}")
    print("Do not call time.sleep() in a coroutine on the event-loop thread.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requests", type=int, default=3)
    parser.add_argument("--delay", type=float, default=0.2)
    args = parser.parse_args()
    asyncio.run(demo(args.requests, args.delay))


if __name__ == "__main__":
    main()
