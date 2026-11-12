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
import unittest


LESSON = Path(__file__).resolve().parents[1]
README = LESSON / "README.md"


class ReadmeSnippetTests(unittest.TestCase):
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
