"""Validate the initial decorator lesson without third-party packages."""
from __future__ import annotations

from contextlib import redirect_stdout
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

from examples import closures, function_decorators

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
                        compile(snippet, f"README.md snippet {i}", "exec"),
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
        for filename in ("closures.py", "closures.js", "parameterized_decorators.py", "metadata_and_stacking.py"):
            example = (LESSON / "examples" / filename).read_text(
                encoding="utf-8"
            ).strip()
            self.assertIn(example, markdown, f"README drifted from {filename}")

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

if __name__ == "__main__":
    unittest.main()
