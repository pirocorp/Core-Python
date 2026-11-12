"""Validate the initial decorator lesson without third-party packages."""
from __future__ import annotations

import asyncio
from contextlib import redirect_stdout
import inspect
from io import StringIO
from inspect import signature
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unittest
from urllib.parse import unquote


LESSON = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LESSON))

from examples import (
    async_decorators,
    closure_introspection,
    closures,
    function_decorators,
    method_and_stdlib_decorators,
    typed_decorators,
)

# These modules intentionally print during decoration (import time).
with redirect_stdout(StringIO()):
    from examples import metadata_and_stacking, parameterized_decorators


class FunctionDecoratorTests(unittest.TestCase):
    def test_decorated_hello_runs_wrapper_and_original(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            function_decorators.hello()
        self.assertEqual(output.getvalue().splitlines(), ["Before", "Hello", "After"])

    def test_higher_order_function_returns_a_function_with_closure(self) -> None:
        output = StringIO()

        def original() -> None:
            print("Called original")

        wrapper = function_decorators.log_calls(original)
        self.assertTrue(callable(wrapper))
        self.assertEqual(output.getvalue(), "")  # Creating it does not call it.
        with redirect_stdout(output):
            wrapper()
        self.assertEqual(
            output.getvalue().splitlines(), ["Before", "Called original", "After"]
        )

    def test_decorated_metadata_is_not_preserved_without_wraps(self) -> None:
        # This is a documented limitation of the simple teaching example.
        self.assertEqual(function_decorators.hello.__name__, "wrapper")

    def test_closure_counters_have_independent_mutable_state(self) -> None:
        first = closures.make_counter(10)
        second = closures.make_counter(0)
        self.assertEqual([first(), first(), second(), first()], [11, 12, 1, 13])

    def test_python_late_binding_and_explicit_snapshot(self) -> None:
        self.assertEqual(
            closures.demonstrate_late_binding(),
            ([6, 6, 6], [0, 3, 6]),
        )

    def test_javascript_closure_example_when_node_is_available(self) -> None:
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is optional; JavaScript demo not executable here")
        result = subprocess.run(
            [node, str(LESSON / "examples" / "closures.js")],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertEqual(
            result.stdout.splitlines(),
            [
                "first: 11 12",
                "second: 1",
                "first again: 13",
                "var loop: [ 9, 9, 9 ]",
                "let loop: [ 0, 3, 6 ]",
            ],
        )
        self.assertEqual(result.stderr, "")

    def test_python_code_in_readme_stays_runnable(self) -> None:
        markdown = (LESSON / "README.md").read_text(encoding="utf-8")
        blocks = re.findall(
            r"^`{3}python\n([\s\S]*?)^`{3}",
            markdown,
            flags=re.MULTILINE,
        )
        # Match examples by their actual definitions, not brittle snippet indices.
        expected_cases = {
            "def log_calls(func):": ["Before", "Hello", "After"],
            "def make_counter(start: int = 0):": [
                "first: 11 12",
                "second: 1",
                "first again: 13",
                "late: [6, 6, 6]",
                "snapshots: [0, 3, 6]",
            ],
            "def my_resource():": [
                "Acquire", "Use: connection", "Release"
            ],
            "async def async_resource():": [
                "Manager created", "Open", "Use: session", "Close"
            ],
            "def repeat(times: int):": [
                "factory: times=2",
                "decorate: greet",
                "main: calling greet",
                "wrapper: 2 call(s)",
                "body: Ada",
                "body: Ada",
                "result: Hello, Ada?",
            ],
            "def trace(label: str):": [
                "factory: outer",
                "factory: inner",
                "decorate: inner",
                "decorate: outer",
                "name: add",
                "doc: Return the sum of a and b.",
                "signature: (a: int, b: int = 1) -> int",
                "runtime signature: (*args, **kwargs) -> int",
                "enter: outer",
                "enter: inner",
                "body: add",
                "exit: inner",
                "exit: outer",
                "result: 7",
            ],
            "def make_accumulator(start: int):": [
                "free vars: ('total',)",
                "captured before: 10",
                "first call: 15",
                "captured after: 15",
                "second call: 101",
                "independent: 16",
            ],
            "def audit(func: Callable[P, R])": [
                "name: calculate",
                "audit: enter calculate",
                "audit: exit calculate",
                "result: 21",
            ],
            "def trace_async(func: Callable[P, Awaitable[R]])": [
                "async function: True",
                "coroutine created",
                "async: enter",
                "body: ok",
                "async: exit",
                "result: done",
                "sync wrapper is async: False",
                "sync wrapper: called",
                "delayed coroutine: True",
                "delayed body",
                "delayed result: late",
                "async: enter",
                "body: error",
                "async: exit",
                "caught: ValueError",
                "async: enter",
                "body: cancel",
                "async: exit",
                "caught: CancelledError",
            ],
            "class Greeter:": [
                "call: greet",
                "method: Hello, Ada",
                "call: describe",
                "class method: Greeter",
                "call: version",
                "static method: 1",
                "property: Hello",
                "normalize: computing",
                "normalized: ABC",
                "cached: ABC",
                "cache: 1 1",
            ],
        }
        self.assertEqual(len(blocks), len(expected_cases))
        seen = set()
        for i, snippet in enumerate(blocks, start=1):
            matching = [key for key in expected_cases if key in snippet]
            self.assertEqual(len(matching), 1, f"Unidentified Python block {i}")
            key = matching[0]
            self.assertNotIn(key, seen, f"Duplicate README block: {key}")
            seen.add(key)
            with self.subTest(example=key):
                output = StringIO()
                with redirect_stdout(output):
                    exec(
                        compile(snippet, f"README.md snippet {i}", "exec", dont_inherit=True),
                        {"__name__": "__main__"},
                    )
                self.assertEqual(output.getvalue().splitlines(), expected_cases[key])
        self.assertEqual(seen, set(expected_cases))

    def test_readme_contains_exact_runnable_python_demo(self) -> None:
        markdown = (LESSON / "README.md").read_text(encoding="utf-8")
        demo = (LESSON / "examples/function_decorators.py").read_text(
            encoding="utf-8"
        ).strip()
        self.assertIn(demo, markdown)
        for example_file in sorted((LESSON / "examples").iterdir()):
            if example_file.suffix not in {".py", ".js"}:
                continue
            example = example_file.read_text(encoding="utf-8").strip()
            self.assertIn(
                example, markdown, f"README drifted from {example_file.name}"
            )

    def test_local_markdown_links_are_valid(self) -> None:
        markdown = (LESSON / "README.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\(([^)]+)\)", markdown)
        self.assertGreater(len(links), 0)
        for link in links:
            if "://" in link or link.startswith("#"):
                continue
            target = (LESSON / unquote(link.split("#", 1)[0])).resolve()
            with self.subTest(link=link):
                self.assertTrue(target.exists(), f"Broken lesson link: {link}")



class AdvancedDecoratorTests(unittest.TestCase):
    def test_repeater_forwards_positional_and_keyword_arguments(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            result = parameterized_decorators.greet("Ada", punctuation="?")
        self.assertEqual(result, "Hello, Ada?")
        self.assertEqual(output.getvalue().splitlines(), [
            "wrapper: 2 call(s)", "body: Ada", "body: Ada"
        ])

    def test_repeater_rejects_invalid_configuration_at_factory_time(self) -> None:
        for count in (0, -3):
            with self.subTest(count=count):
                with self.assertRaisesRegex(ValueError, "times must be"):
                    parameterized_decorators.repeat(count)

    def test_factory_keeps_independent_configuration_and_returns_last_result(self) -> None:
        events = []

        def increment(value: int, *, step: int = 1) -> int:
            events.append(value + step + len(events))
            return events[-1]

        output = StringIO()
        with redirect_stdout(output):
            once = parameterized_decorators.repeat(1)(increment)
            thrice = parameterized_decorators.repeat(3)(increment)
            self.assertEqual(once(4, step=2), 6)
            self.assertEqual(thrice(4, step=2), 9)
        self.assertEqual(events, [6, 7, 8, 9])
        self.assertEqual(output.getvalue().splitlines(), [
            "factory: times=1", "decorate: increment",
            "factory: times=3", "decorate: increment",
            "wrapper: 1 call(s)", "wrapper: 3 call(s)"
        ])

    def test_wraps_preserves_metadata_and_unwrapped_signature(self) -> None:
        decorated = metadata_and_stacking.add
        self.assertEqual(decorated.__name__, "add")
        self.assertEqual(decorated.__doc__, "Return the sum of a and b.")
        self.assertEqual(str(signature(decorated)), "(a: int, b: int = 1) -> int")
        self.assertEqual(
            str(signature(decorated, follow_wrapped=False)),
            "(*args, **kwargs) -> int",
        )
        inner = decorated.__wrapped__
        original = inner.__wrapped__
        self.assertEqual(inner.__code__.co_name, "wrapper")
        self.assertEqual(original.__code__.co_name, "add")
        self.assertIsNot(original, decorated)

    def test_stacked_wrappers_run_outside_in_and_return_result(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            result = metadata_and_stacking.add(3, b=4)
        self.assertEqual(result, 7)
        self.assertEqual(output.getvalue().splitlines(), [
            "enter: outer", "enter: inner", "body: add",
            "exit: inner", "exit: outer"
        ])

    def test_stacked_finally_blocks_do_not_suppress_exceptions(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            @metadata_and_stacking.trace("outer-error")
            @metadata_and_stacking.trace("inner-error")
            def fail() -> None:
                raise RuntimeError("boom")

            with self.assertRaisesRegex(RuntimeError, "boom"):
                fail()

        self.assertEqual(output.getvalue().splitlines(), [
            "factory: outer-error",
            "factory: inner-error",
            "decorate: inner-error",
            "decorate: outer-error",
            "enter: outer-error",
            "enter: inner-error",
            "exit: inner-error",
            "exit: outer-error",
        ])

class ProductionDecoratorTests(unittest.TestCase):
    def test_closure_cells_are_live_and_per_factory_call(self) -> None:
        first = closure_introspection.make_accumulator(10)
        second = closure_introspection.make_accumulator(100)
        self.assertEqual(first.__code__.co_freevars, ("total",))
        self.assertIsNotNone(first.__closure__)
        self.assertEqual(first.__closure__[0].cell_contents, 10)
        self.assertEqual(first(5), 15)
        self.assertEqual(first.__closure__[0].cell_contents, 15)
        self.assertEqual(second(1), 101)
        self.assertEqual(first(1), 16)

    def test_typed_decorator_preserves_signature_contract_and_result(self) -> None:
        self.assertEqual(typed_decorators.calculate.__name__, "calculate")
        self.assertEqual(
            inspect.signature(typed_decorators.calculate),
            inspect.signature(typed_decorators.calculate.__wrapped__),
        )
        out = StringIO()
        with redirect_stdout(out):
            result = typed_decorators.calculate(7, multiplier=3)
        self.assertEqual(result, 21)
        self.assertEqual(out.getvalue().splitlines(), [
            "audit: enter calculate", "audit: exit calculate"
        ])

    def test_typed_decorator_finally_runs_on_error(self) -> None:
        @typed_decorators.audit
        def fail() -> None:
            raise LookupError("problem")

        out = StringIO()
        with redirect_stdout(out), self.assertRaisesRegex(LookupError, "problem"):
            fail()
        self.assertEqual(out.getvalue().splitlines(), [
            "audit: enter fail", "audit: exit fail"
        ])

    def test_sync_wrapper_for_async_does_not_appear_as_coroutine_function(self) -> None:
        self.assertFalse(inspect.iscoroutinefunction(async_decorators.delayed))
        out = StringIO()
        with redirect_stdout(out):
            coroutine = async_decorators.delayed()
            self.assertTrue(inspect.iscoroutine(coroutine))
            self.assertEqual(out.getvalue().splitlines(), ["sync wrapper: called"])
            result = asyncio.run(coroutine)
        self.assertEqual(result, "late")
        self.assertEqual(out.getvalue().splitlines(), [
            "sync wrapper: called", "delayed body"
        ])

    def test_async_wrapper_does_not_execute_until_awaited(self) -> None:
        self.assertTrue(inspect.iscoroutinefunction(async_decorators.work))
        out = StringIO()
        with redirect_stdout(out):
            coroutine = async_decorators.work("ok")
            self.assertEqual(out.getvalue(), "")
            result = asyncio.run(coroutine)
        self.assertEqual(result, "done")
        self.assertEqual(out.getvalue().splitlines(), [
            "async: enter", "body: ok", "async: exit"
        ])

    def test_async_wrapper_propagates_error_after_finally(self) -> None:
        out = StringIO()
        with redirect_stdout(out), self.assertRaisesRegex(ValueError, "boom"):
            asyncio.run(async_decorators.work("error"))
        self.assertEqual(out.getvalue().splitlines(), [
            "async: enter", "body: error", "async: exit"
        ])

    def test_async_wrapper_cancellation_propagates_after_finally(self) -> None:
        async def scenario() -> bool:
            ready = asyncio.Event()
            task = asyncio.create_task(async_decorators.work("cancel", ready))
            await ready.wait()
            self.assertFalse(task.done())
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
            return task.cancelled()

        out = StringIO()
        with redirect_stdout(out):
            cancelled = asyncio.run(scenario())
        self.assertTrue(cancelled)
        self.assertEqual(out.getvalue().splitlines(), [
            "async: enter", "body: cancel", "async: exit"
        ])

    def test_methods_bind_self_cls_and_static_correctly(self) -> None:
        obj = method_and_stdlib_decorators.Greeter("Hello")
        out = StringIO()
        with redirect_stdout(out):
            self.assertEqual(obj.greet("Ada"), "Hello, Ada")
            self.assertEqual(obj.describe(), "Greeter")
            self.assertEqual(obj.version(), 1)
            self.assertEqual(obj.label, "Hello")
        self.assertEqual(out.getvalue().splitlines(), [
            "call: greet", "call: describe", "call: version"
        ])

    def test_lru_cache_reuses_pure_result_and_reports_hits(self) -> None:
        normal = method_and_stdlib_decorators.normalize
        normal.cache_clear()
        out = StringIO()
        with redirect_stdout(out):
            self.assertEqual(normal("  abc "), "ABC")
            self.assertEqual(normal("  abc "), "ABC")
        self.assertEqual(out.getvalue().splitlines(), ["normalize: computing"])
        info = normal.cache_info()
        self.assertEqual((info.hits, info.misses), (1, 1))
        normal.cache_clear()


if __name__ == "__main__":
    unittest.main()
