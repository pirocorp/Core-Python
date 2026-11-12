"""Smoke-test every runnable Python fence in the lesson documentation.

Each snippet gets its own namespace and a temporary sample file. This catches
missing imports, unbound variables, syntax errors and exceptions in copyable
README examples, rather than only testing the separate examples/ scripts.
"""
from __future__ import annotations

from contextlib import chdir, redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
from urllib.parse import unquote
import unittest


LESSON = Path(__file__).resolve().parents[1]
README = LESSON / "README.md"


class ReadmeSnippetTests(unittest.TestCase):
    def test_local_markdown_links_point_to_existing_files(self) -> None:
        markdown = README.read_text(encoding="utf-8")
        links = re.findall(r"\]\(([^)]+)\)", markdown)
        self.assertGreater(len(links), 0, "README should link to examples")

        for link in links:
            if "://" in link or link.startswith("#"):
                continue
            local = unquote(link.split("#", 1)[0])
            with self.subTest(link=link):
                target = (LESSON / local).resolve()
                self.assertTrue(target.exists(), f"Broken README link: {link}")

    def test_embedded_demo_implementations_match_the_source_files(self) -> None:
        """Prevent teaching code from drifting away from runnable demos."""
        markdown = README.read_text(encoding="utf-8")
        embedded_functions = [
            (
                "custom_manager.py",
                "from __future__ import annotations",
                "\n\nclass FailingEnter:",
            ),
            (
                "contextlib_tools.py",
                "@contextmanager\ndef traced_resource",
                "\n\ndef run_traced",
            ),
            (
                "async_managers.py",
                "@asynccontextmanager\nasync def async_resource",
                "\n\nasync def run_connection",
            ),
            (
                "contextlib_tools.py",
                "def run_traced(",
                "\n\ndef run_suppress(",
            ),
            (
                "contextlib_tools.py",
                "def run_suppress(",
                "\n\ndef run_optional(",
            ),
            (
                "contextlib_tools.py",
                "def run_optional(enabled:",
                "\n\ndef main()",
            ),
            (
                "file_resources.py",
                "def write_and_read(",
                "\n\ndef main(",
            ),
            (
                "custom_manager.py",
                "class FailingEnter:",
                "\n\ndef run_nested(",
            ),
            (
                "custom_manager.py",
                "def run_nested(",
                "\n\ndef run_exception(",
            ),
            (
                "custom_manager.py",
                "def run_exception(",
                "\n\ndef run_failed_enter(",
            ),
            (
                "custom_manager.py",
                "def run_failed_enter(",
                "\n\ndef run_early_return(",
            ),
            (
                "custom_manager.py",
                "def run_early_return(",
                "\n\ndef main(",
            ),
            (
                "exit_stack.py",
                "@contextmanager\ndef acquire(",
                "\n\ndef run_batch(",
            ),
            (
                "exit_stack.py",
                "def run_batch(",
                "\n\ndef main(",
            ),
            (
                "async_managers.py",
                "class AsyncConnection:",
                "\n\n# @asynccontextmanager",
            ),
            (
                "async_managers.py",
                "async def run_connection(",
                "\n\nasync def run_async_stack(",
            ),
            (
                "async_managers.py",
                "async def run_async_stack(",
                "\n\nasync def run_async_error(",
            ),
            (
                "async_managers.py",
                "async def run_async_error(",
                "\n\nasync def run_cancellation(",
            ),
            (
                "async_managers.py",
                "async def run_cancellation(",
                "\n\nasync def main(",
            ),
        ]
        for filename, start_marker, end_marker in embedded_functions:
            source = (LESSON / "examples" / filename).read_text(encoding="utf-8")
            start = source.find(start_marker)
            end = source.find(end_marker, start + len(start_marker))
            self.assertGreaterEqual(start, 0, f"Source start missing: {filename}")
            self.assertGreater(end, start, f"Source end missing: {filename}")
            excerpt = source[start:end].strip()
            with self.subTest(example=filename):
                self.assertIn(
                    excerpt,
                    markdown,
                    f"README example no longer matches examples/{filename}",
                )

    def test_exitstack_intro_has_correct_lifo_output(self) -> None:
        """The copyable Database/Cache illustration must match its output."""
        markdown = README.read_text(encoding="utf-8")
        start = markdown.index("### 8.1 Start small: Database and Cache")
        end = markdown.index("### 8.2 Start from the actual", start)
        section = markdown[start:end]
        code_match = re.search(r"```python\n([\s\S]*?)```", section)
        output_match = re.search(r"```text\n([\s\S]*?)```", section)
        self.assertIsNotNone(code_match)
        self.assertIsNotNone(output_match)
        stdout = StringIO()
        with redirect_stdout(stdout):
            exec(compile(code_match.group(1), "lesson03:ExitStack-intro", "exec"), {})
        self.assertEqual(stdout.getvalue().strip(), output_match.group(1).strip())

    def test_documented_python_snippets_are_runnable_independently(self) -> None:
        markdown = README.read_text(encoding="utf-8")
        snippets = list(
            re.finditer(r"^`{3}python\n([\s\S]*?)^`{3}", markdown, re.MULTILINE)
        )
        self.assertGreater(len(snippets), 0, "README must include Python examples")

        # Python 3 implicit namespace packages allow 'from examples.x import y'
        # when running inside the lesson directory (or with LESSON on sys.path).
        sys.path.insert(0, str(LESSON))
        try:
            with TemporaryDirectory(prefix="lesson03-readme-") as directory:
                sample = Path(directory) / "example.txt"
                sample.write_text("Example file contents", encoding="utf-8")
                with chdir(directory):
                    for number, match in enumerate(snippets, start=1):
                        line = markdown.count("\n", 0, match.start()) + 1
                        with self.subTest(snippet=number, line=line):
                            code = compile(
                                match.group(1), f"README.md:{line}", "exec"
                            )
                            stdout = StringIO()
                            stderr = StringIO()
                            with redirect_stdout(stdout), redirect_stderr(stderr):
                                exec(code, {"__name__": "__main__"})
        finally:
            sys.path.remove(str(LESSON))


if __name__ == "__main__":
    unittest.main()
