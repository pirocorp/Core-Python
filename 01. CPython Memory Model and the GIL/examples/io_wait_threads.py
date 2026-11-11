"""Demonstrate that Python threads can overlap *waiting*, without CPU parallelism.

The delay uses time.sleep as a stand-in for blocking I/O. This is not an
actual disk, network or database benchmark. Numbers are illustrative.
"""

from __future__ import annotations

import argparse
from math import isfinite
from threading import Thread
from time import perf_counter, sleep


def sequential_waits(seconds: float) -> float:
    start = perf_counter()
    for _ in range(2):
        sleep(seconds)
    return perf_counter() - start


def threaded_waits(seconds: float) -> float:
    threads = [Thread(target=sleep, args=(seconds,)) for _ in range(2)]
    start = perf_counter()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return perf_counter() - start


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=float, default=0.4)
    args = parser.parse_args()

    if not isfinite(args.seconds) or args.seconds < 0:
        parser.error("--seconds must be a finite, non-negative number")

    sequential = sequential_waits(args.seconds)
    threaded = threaded_waits(args.seconds)

    print(f"Simulated I/O wait per operation: {args.seconds:.3f} s")
    print(f"Two sequential waits: {sequential:.4f} s")
    print(f"Two threaded waits:   {threaded:.4f} s")
    print("Thread speedup here comes from overlapping waits, not CPU parallelism.")
    print("Times vary with OS scheduling and load; do not assert an exact ratio.")


if __name__ == "__main__":
    main()
