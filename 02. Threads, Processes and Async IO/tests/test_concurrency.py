"""Standard-library tests. No timing-based assertions: CI load varies."""
from __future__ import annotations

import asyncio
from pathlib import Path
import sys
import unittest

# Put the lesson's examples directory on the module search path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))

import asyncio_blocking
import asyncio_io
import cpu_pool_comparison
import thread_pool_io
import threading_io


class ThreadingTests(unittest.TestCase):
    def test_threads_match_sequential(self) -> None:
        self.assertEqual(
            threading_io.run_sequential(3, 0),
            threading_io.run_threads(3, 0),
        )

    def test_thread_pool_preserves_order(self) -> None:
        self.assertEqual(
            thread_pool_io.run_pool(4, 0, workers=2),
            [f"request-{i}:ok" for i in range(4)],
        )

    def test_invalid_thread_inputs(self) -> None:
        with self.assertRaises(ValueError):
            threading_io.run_threads(0, 0)
        with self.assertRaises(ValueError):
            thread_pool_io.run_pool(2, 0, workers=0)
        with self.assertRaises(ValueError):
            threading_io.run_sequential(1, -1)


class CpuPoolTests(unittest.TestCase):
    def test_pure_python_work_has_predictable_result(self) -> None:
        expected = sum((i % 97) * (i % 89) for i in range(100))
        self.assertEqual(cpu_pool_comparison.cpu_work(100), expected)

    def test_threads_match_sequential_cpu_results(self) -> None:
        self.assertEqual(
            cpu_pool_comparison.run_sequential(500, 2),
            cpu_pool_comparison.run_threads(500, 2),
        )

    def test_processes_match_sequential_cpu_results(self) -> None:
        # Deliberately small: process startup should not dominate test time.
        self.assertEqual(
            cpu_pool_comparison.run_sequential(500, 2),
            cpu_pool_comparison.run_processes(500, 2),
        )

    def test_invalid_process_inputs(self) -> None:
        with self.assertRaises(ValueError):
            cpu_pool_comparison.run_processes(3, 0)


class AsyncioTests(unittest.IsolatedAsyncioTestCase):
    async def test_gather_and_taskgroup_match_sequential(self) -> None:
        serial = await asyncio_io.run_sequential(3, 0)
        self.assertEqual(await asyncio_io.run_gather(3, 0), serial)
        self.assertEqual(await asyncio_io.run_taskgroup(3, 0), serial)

    async def test_blocking_bridge_has_same_results(self) -> None:
        self.assertEqual(
            await asyncio_blocking.run_bad(2, 0),
            await asyncio_blocking.run_bridged(2, 0),
        )

    async def test_invalid_asyncio_inputs(self) -> None:
        with self.assertRaises(ValueError):
            await asyncio_io.run_gather(0, 0)
        with self.assertRaises(ValueError):
            await asyncio_blocking.run_bridged(1, -1)


if __name__ == "__main__":
    unittest.main()
