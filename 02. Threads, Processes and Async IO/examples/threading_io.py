"""Compare sequential waits and real OS threads using simulated I/O.

No actual network requests are made. Timings are examples, not assertions.
"""
from __future__ import annotations

import argparse
import math
import threading
from queue import Queue
from time import perf_counter, sleep


def validate(requests: int, delay: float) -> None:
    if requests < 1:
        raise ValueError("requests must be >= 1")
    if not math.isfinite(delay) or delay < 0:
        raise ValueError("delay must be finite and >= 0")


def simulated_io(index: int, delay: float) -> str:
    """Model waiting for an I/O response; sleep releases the normal CPython GIL."""
    sleep(delay)
    # An f-string replaces {index} with its value.
    return f"request-{index}:ok"


def run_sequential(requests: int, delay: float) -> list[str]:
    validate(requests, delay)
    return [simulated_io(i, delay) for i in range(requests)]


def run_threads(requests: int, delay: float) -> list[str]:
    validate(requests, delay)
    # Queue is a thread-safe communication channel.
    messages: Queue[tuple[int, str | None, Exception | None]] = Queue()

    def worker(index: int) -> None:
        try:
            messages.put((index, simulated_io(index, delay), None))
        except Exception as exc:
            # Thread.join() does NOT automatically re-raise a worker exception.
            messages.put((index, None, exc))

    # args=(i,) is a single-element tuple; the comma is required.
    threads = [
        threading.Thread(target=worker, args=(i,))
        for i in range(requests)
    ]
    for thread in threads:
        thread.start()  # Schedule the OS thread.
    for thread in threads:
        thread.join()  # Wait for it to finish; not the same as await.

    results: list[str | None] = [None] * requests
    for _ in range(requests):
        index, value, error = messages.get_nowait()
        if error is not None:
            raise RuntimeError(f"Worker {index} failed") from error
        results[index] = value

    if any(value is None for value in results):
        raise RuntimeError("A worker did not produce a result")
    return [value for value in results if value is not None]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requests", type=int, default=3)
    parser.add_argument("--delay", type=float, default=0.2)
    args = parser.parse_args()
    try:
        validate(args.requests, args.delay)
    except ValueError as exc:
        parser.error(str(exc))

    start = perf_counter()
    sequential = run_sequential(args.requests, args.delay)
    serial_seconds = perf_counter() - start

    start = perf_counter()
    threaded = run_threads(args.requests, args.delay)
    threaded_seconds = perf_counter() - start

    if sequential != threaded:
        raise RuntimeError("Threaded and sequential outputs differ")

    print(f"Sequential: {serial_seconds:.3f}s")
    print(f"OS threads: {threaded_seconds:.3f}s")
    print(f"Results match: {sequential == threaded}")
    print("The threads overlap waits; they are not parallel Python CPU loops.")


if __name__ == "__main__":
    main()
