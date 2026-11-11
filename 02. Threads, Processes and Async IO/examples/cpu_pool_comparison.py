"""Compare sequential, thread-pool and process-pool pure-Python CPU work.

The process pool uses the explicit 'spawn' start method to behave consistently
on Windows/macOS/Linux. It may be slower for small tasks due to startup and IPC.
"""
from __future__ import annotations

import argparse
import multiprocessing
import platform
import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from time import perf_counter


def cpu_work(iterations: int) -> int:
    """Deliberately CPU-bound Python loop with a deterministic result."""
    if iterations < 0:
        raise ValueError("iterations must be >= 0")
    total = 0
    for i in range(iterations):
        total += (i % 97) * (i % 89)
    return total


def validate(iterations: int, jobs: int) -> None:
    if iterations < 0 or jobs < 1:
        raise ValueError("iterations must be >= 0 and jobs must be >= 1")


def run_sequential(iterations: int, jobs: int) -> list[int]:
    validate(iterations, jobs)
    return [cpu_work(iterations) for _ in range(jobs)]


def run_threads(iterations: int, jobs: int) -> list[int]:
    validate(iterations, jobs)
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        return list(executor.map(cpu_work, [iterations] * jobs))


# '-> list[int]' is a return type hint: an ordered list of integers.
# It resembles C# 'List<int>', but Python does not enforce hints at runtime.
def run_processes(iterations: int, jobs: int) -> list[int]:
    validate(iterations, jobs)
    # Each worker is a separate process with its own interpreter and memory.
    # get_context("spawn") returns a context for the fresh-interpreter start method.
    # It does NOT start any worker yet and avoids relying on Unix 'fork'.
    context = multiprocessing.get_context("spawn")
    # Create a pool with up to 'jobs' separate worker processes.
    # mp_context=context makes it use the selected "spawn" start method.
    # 'as executor' receives the pool object returned by __enter__().
    # Leaving 'with' waits for submitted work and shuts down the pool.
    with ProcessPoolExecutor(max_workers=jobs, mp_context=context) as executor:
        # map() submits calls; results cross process boundaries via serialization.
        # list() collects them in input order (the workers may finish out of order).
        return list(executor.map(cpu_work, [iterations] * jobs))


def measure(func, iterations: int, jobs: int) -> tuple[float, list[int]]:
    start = perf_counter()
    results = func(iterations, jobs)
    return perf_counter() - start, results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=1_500_000)
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args()
    try:
        validate(args.iterations, args.jobs)
    except ValueError as exc:
        parser.error(str(exc))

    print(f"Runtime: {platform.python_implementation()} {platform.python_version()}")
    gil_enabled = getattr(sys, "_is_gil_enabled", None)
    print(f"GIL enabled: {gil_enabled() if gil_enabled is not None else 'unknown'}")

    serial_time, serial = measure(run_sequential, args.iterations, args.jobs)
    thread_time, threads = measure(run_threads, args.iterations, args.jobs)
    process_time, processes = measure(run_processes, args.iterations, args.jobs)

    if not (serial == threads == processes):
        raise RuntimeError("Different execution models returned different results")

    print(f"Sequential: {serial_time:.3f}s")
    print(f"Threads:    {thread_time:.3f}s")
    print(f"Processes:  {process_time:.3f}s")
    print(f"Same results: {serial == threads == processes}")
    print("Compare multiple runs; process startup and CPU quotas affect timings.")


# Mandatory for spawn-based multiprocessing: prevents recursive worker creation.
if __name__ == "__main__":
    main()
