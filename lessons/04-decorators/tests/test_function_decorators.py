"""Validate the initial decorator lesson without third-party packages."""
from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
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
        self.assertEqual(len(blocks), 4)
        for i, snippet in enumerate(blocks, start=1):
            with self.subTest(snippet=i):
                output = StringIO()
                with redirect_stdout(output):
                    # Execute the copied example as a stand-alone script,
                    # including its if __name__ == "__main__" entry point.
                    exec(
                        compile(snippet, f"README.md snippet {i}", "exec"),
                        {"__name__": "__main__"},
                    )
                if i == 1:
                    self.assertEqual(
                        output.getvalue().splitlines(),
                        ["Before", "Hello", "After"],
                    )
                elif i == 2:
                    self.assertEqual(
                        output.getvalue().splitlines(),
                        [
                            "first: 11 12",
                            "second: 1",
                            "first again: 13",
                            "late: [6, 6, 6]",
                            "snapshots: [0, 3, 6]",
                        ],
                    )
                elif i == 3:
                    self.assertEqual(
                        output.getvalue().splitlines(),
                        ["Acquire", "Use: connection", "Release"],
                    )
                elif i == 4:
                    self.assertEqual(
                        output.getvalue().splitlines(),
                        ["Manager created", "Open", "Use: session", "Close"],
                    )

    def test_readme_contains_exact_runnable_python_demo(self) -> None:
        markdown = (LESSON / "README.md").read_text(encoding="utf-8")
        demo = (LESSON / "examples/function_decorators.py").read_text(
            encoding="utf-8"
        ).strip()
        self.assertIn(demo, markdown)
        for filename in ("closures.py", "closures.js"):
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


if __name__ == "__main__":
    unittest.main()
