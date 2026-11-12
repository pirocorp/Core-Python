"""Validate the initial decorator lesson without third-party packages."""
from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import re
import sys
import unittest
from urllib.parse import unquote


LESSON = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LESSON))

from examples import function_decorators


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

    def test_python_code_in_readme_stays_runnable(self) -> None:
        markdown = (LESSON / "README.md").read_text(encoding="utf-8")
        blocks = re.findall(
            r"^`{3}python\n([\s\S]*?)^`{3}",
            markdown,
            flags=re.MULTILINE,
        )
        self.assertEqual(len(blocks), 2)
        for i, snippet in enumerate(blocks, start=1):
            with self.subTest(snippet=i):
                output = StringIO()
                with redirect_stdout(output):
                    exec(compile(snippet, f"README.md snippet {i}", "exec"), {})
                if i == 1:
                    self.assertEqual(
                        output.getvalue().splitlines(),
                        ["Before", "Hello", "After"],
                    )
                elif i == 2:
                    self.assertEqual(
                        output.getvalue().splitlines(),
                        ["Acquire", "Use: connection", "Release"],
                    )

    def test_readme_contains_exact_runnable_python_demo(self) -> None:
        markdown = (LESSON / "README.md").read_text(encoding="utf-8")
        demo = (LESSON / "examples/function_decorators.py").read_text(
            encoding="utf-8"
        ).strip()
        self.assertIn(demo, markdown)

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
