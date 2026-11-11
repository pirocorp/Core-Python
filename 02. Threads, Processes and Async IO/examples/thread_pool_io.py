"""Use ThreadPoolExecutor for blocking I/O and exception propagation."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

from threading_io import simulated_io, validate


def run_pool(requests: int, delay: float, workers: int) -> list[str]:
    validate(requests, delay)
    if workers < 1:
        raise ValueError("workers must be >= 1")

    # 'with' shuts down the pool and waits for submitted work on exit.
    with ThreadPoolExecutor(max_workers=workers) as executor:
        # submit(function, *arguments) schedules a callable and returns a Future.
        futures = [
            executor.submit(simulated_io, index, delay)
            for index in range(requests)
        ]
        # future.result() waits for completion and re-raises worker exceptions.
        # Retrieving futures in input order also restores deterministic results.
        return [future.result() for future in futures]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--requests", type=int, default=4)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--delay", type=float, default=0.2)
    args = parser.parse_args()

    start = perf_counter()
    results = run_pool(args.requests, args.delay, args.workers)
    elapsed = perf_counter() - start
    print(f"Thread pool: {elapsed:.3f}s")
    print(f"Results: {results}")
    print("Pool worker counts limit simultaneous submitted operations.")


if __name__ == "__main__":
    main()
