"""Deterministic, standard-library-only tests for context manager semantics."""
from __future__ import annotations

import sys
from pathlib import Path
import unittest

# Import the runnable examples without installing a package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))

import async_managers
import contextlib_tools
import custom_manager
import exit_stack
import file_resources


class FileResourceTests(unittest.TestCase):
    def test_file_roundtrip_closes_resource(self) -> None:
        text, closed = file_resources.write_and_read("hello 🐍\n")
        self.assertEqual(text, "hello 🐍\n")
        self.assertTrue(closed)

    def test_file_closes_when_body_raises(self) -> None:
        closed, message = file_resources.close_after_exception()
        self.assertTrue(closed)
        self.assertEqual(message, "simulated processing failure")


class CustomContextManagerTests(unittest.TestCase):
    def test_nested_contexts_unwind_in_reverse_order(self) -> None:
        self.assertEqual(
            custom_manager.run_nested(),
            [
                "enter:outer",
                "enter:inner",
                "body:resource:outer,resource:inner",
                "exit:inner:none",
                "exit:outer:none",
            ],
        )

    def test_unsuppressed_exception_propagates(self) -> None:
        self.assertEqual(
            custom_manager.run_exception(suppress=False),
            [
                "enter:guard",
                "body:raise",
                "exit:guard:ValueError",
                "caught:ValueError",
                "after:with",
            ],
        )

    def test_matching_exception_is_suppressed(self) -> None:
        self.assertEqual(
            custom_manager.run_exception(suppress=True),
            [
                "enter:guard",
                "body:raise",
                "exit:guard:ValueError",
                "after:with",
            ],
        )

    def test_suppression_is_selective(self) -> None:
        events: list[str] = []
        with self.assertRaisesRegex(RuntimeError, "different"):
            with custom_manager.MyContextManager(
                "guard", events, suppress_type=ValueError
            ):
                raise RuntimeError("different")
        self.assertEqual(events, ["enter:guard", "exit:guard:RuntimeError"])

    def test_failed_enter_does_not_call_exit(self) -> None:
        self.assertEqual(
            custom_manager.run_failed_enter(),
            ["enter:failed", "caught:RuntimeError"],
        )

    def test_early_return_still_calls_exit(self) -> None:
        self.assertEqual(
            custom_manager.run_early_return(),
            ["enter:early", "body:return", "exit:early:none", "returned"],
        )

    def test_exception_unwinds_all_entered_managers(self) -> None:
        events: list[str] = []
        with self.assertRaises(ZeroDivisionError):
            with custom_manager.MyContextManager("outer", events):
                with custom_manager.MyContextManager("inner", events):
                    raise ZeroDivisionError("oops")
        self.assertEqual(
            events,
            [
                "enter:outer",
                "enter:inner",
                "exit:inner:ZeroDivisionError",
                "exit:outer:ZeroDivisionError",
            ],
        )


class ContextlibTests(unittest.TestCase):
    def test_generator_manager_cleans_up_normally(self) -> None:
        self.assertEqual(
            contextlib_tools.run_traced(),
            ["acquire:cache", "use:resource:cache", "release:cache"],
        )

    def test_generator_manager_cleans_up_on_error(self) -> None:
        self.assertEqual(
            contextlib_tools.run_traced(True),
            [
                "acquire:cache",
                "use:resource:cache",
                "release:cache",
                "caught:ValueError",
            ],
        )

    def test_suppress_only_ignores_expected_error(self) -> None:
        self.assertEqual(
            contextlib_tools.run_suppress(),
            ["attempt:optional-cache", "continue:without-cache"],
        )

    def test_optional_context_is_usable_both_ways(self) -> None:
        self.assertEqual(
            contextlib_tools.run_optional(True),
            ["acquire:optional", "use:resource:optional", "release:optional"],
        )
        self.assertEqual(contextlib_tools.run_optional(False), ["use:direct"])


class ExitStackTests(unittest.TestCase):
    def test_dynamic_acquisition_and_reverse_cleanup(self) -> None:
        events, acquired = exit_stack.run_batch(("file", "db", "socket"))
        self.assertEqual(acquired, ["file", "db", "socket"])
        self.assertEqual(
            events,
            [
                "acquire:file",
                "acquire:db",
                "acquire:socket",
                "work:file,db,socket",
                "release:socket",
                "release:db",
                "release:file",
            ],
        )

    def test_partial_acquisition_failure_releases_prior_resources(self) -> None:
        events, acquired = exit_stack.run_batch(
            ("file", "db", "socket"), fail_on="db"
        )
        self.assertEqual(acquired, ["file"])
        self.assertEqual(
            events,
            [
                "acquire:file",
                "acquire:db",
                "release:file",
                "error:cannot acquire db",
            ],
        )

    def test_first_acquisition_failure_has_no_release(self) -> None:
        events, acquired = exit_stack.run_batch(("file",), fail_on="file")
        self.assertEqual(acquired, [])
        self.assertEqual(events, ["acquire:file", "error:cannot acquire file"])


class AsyncContextManagerTests(unittest.IsolatedAsyncioTestCase):
    async def test_async_class_acquire_and_release(self) -> None:
        self.assertEqual(
            await async_managers.run_connection(),
            ["open:db", "use:db", "close:db"],
        )

    async def test_async_stack_unwinds_in_reverse_order(self) -> None:
        self.assertEqual(
            await async_managers.run_async_stack(),
            [
                "open:db",
                "registered:db",
                "open:cache",
                "registered:cache",
                "work",
                "close:cache",
                "close:db",
            ],
        )

    async def test_async_generator_closes_on_error(self) -> None:
        self.assertEqual(
            await async_managers.run_async_error(),
            ["open:db", "body:raise", "close:db", "caught:ValueError"],
        )

    async def test_async_class_does_not_suppress_exception(self) -> None:
        events: list[str] = []
        with self.assertRaises(ValueError):
            async with async_managers.AsyncConnection("db", events):
                raise ValueError("operation failed")
        self.assertEqual(events, ["open:db", "close:db"])

    async def test_cancellation_still_runs_async_cleanup(self) -> None:
        self.assertEqual(
            await async_managers.run_cancellation(),
            ["open:stream", "close:stream", "caught:CancelledError"],
        )


if __name__ == "__main__":
    unittest.main()
