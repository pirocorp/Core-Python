"""stdlib-only tests: python -m unittest discover -s tests -v"""

import gc
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))

from factorial_threads import factorial, factorial_workload, sequential, threaded
from reference_cycles import make_unreachable_cycle


class FactorialTests(unittest.TestCase):
    def test_corrected_factorial_matches_stdlib(self) -> None:
        for n in (0, 1, 2, 5, 12, 100):
            with self.subTest(n=n):
                self.assertEqual(factorial(n), math.factorial(n))

    def test_negative_input_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            factorial(-1)

    def test_threads_and_sequential_agree(self) -> None:
        _, serial_results = sequential(120, 2)
        _, threaded_results = threaded(120, 2)
        self.assertEqual(serial_results, threaded_results)
        self.assertEqual(threaded_results, [factorial_workload(120, 2)] * 2)


class MemoryTests(unittest.TestCase):
    def test_assignment_is_an_alias_not_a_copy(self) -> None:
        a = []
        before = sys.getrefcount(a)
        b = a
        self.assertIs(a, b)
        self.assertEqual(sys.getrefcount(a), before + 1)
        del b
        self.assertEqual(sys.getrefcount(a), before)

    def test_gc_can_reclaim_unreachable_cycle(self) -> None:
        gc.collect()
        ref = make_unreachable_cycle()
        gc.collect()
        self.assertIsNone(ref())


if __name__ == "__main__":
    unittest.main()
