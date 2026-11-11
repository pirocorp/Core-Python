"""CPU-bound factorial example for exploring the GIL.

Run it on normal (GIL-enabled) CPython and optionally a free-threaded build.
Timing is observational, never an assertion. All worker results are checked.
"""

from __future__ import annotations

import argparse
import platform
import sys
import threading
from time import perf_counter


def factorial(num: int) -> int:
    """Return num!, raising ValueError for negative inputs."""
    if num < 0:
        raise ValueError("factorial is undefined for negative integers")
    result = 1  # Multiplicative identity; initialize before accumulation.
    for i in range(2, num + 1):
        result *= i
    return result


def factorial_workload(num: int, repeats: int) -> int:
    """Repeat a CPU-bound operation to make the cost measurable."""
    value = 1
    for _ in range(repeats):
        value = factorial(num)
    return value


def sequential(num: int, repeats: int) -> tuple[float, list[int]]:
    start = perf_counter()
    results = [factorial_workload(num, repeats) for _ in range(2)]
    return perf_counter() - start, results


def threaded(num: int, repeats: int) -> tuple[float, list[int]]:
    results: list[int | None] = [None, None]
    errors: list[BaseException | None] = [None, None]

    def worker(index: int) -> None:
        try:
            results[index] = factorial_workload(num, repeats)
        except BaseException as exc:
            # Thread exceptions do not automatically propagate on join().
            errors[index] = exc

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(2)]
    start = perf_counter()
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    for error in errors:
        if error is not None:
            raise RuntimeError("Worker failed") from error
    assert all(result is not None for result in results)
    return perf_counter() - start, [result for result in results if result is not None]


def describe_interpreter() -> None:
    print(f"Python: {platform.python_implementation()} {platform.python_version()}")
    print(f"Thread switch interval: {sys.getswitchinterval():.6f} seconds")
    gil_probe = getattr(sys, "_is_gil_enabled", None)  # CPython 3.13+
    if gil_probe is None:
        print("GIL status: API unavailable on this interpreter")
    else:
        print(f"GIL enabled right now: {gil_probe()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=12000)
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()
    if args.n < 0 or args.repeats < 1:
        parser.error("--n must be >= 0 and --repeats must be >= 1")

    describe_interpreter()
    sequential_time, sequential_results = sequential(args.n, args.repeats)
    threaded_time, threaded_results = threaded(args.n, args.repeats)
    assert threaded_results == sequential_results
    print(f"Two sequential workloads: {sequential_time:.4f} s")
    print(f"Two threaded workloads:   {threaded_time:.4f} s")
    print(f"Same results:              {threaded_results == sequential_results}")
    print(f"Result bit-length:         {threaded_results[0].bit_length()}")
    print("Wall-clock timings vary: do not assert a fixed ratio or infer thread safety.")


if __name__ == "__main__":
    main()
