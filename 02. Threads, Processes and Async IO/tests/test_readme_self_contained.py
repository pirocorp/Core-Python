"""Make Lesson 02's README reproducible and synchronized with runnable demos.

Every Python code block is saved to a *real Python script*, not eval'ed in a
REPL. This matters in particular for ProcessPoolExecutor(spawn), whose
workers must be able to import the __main__ module.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from urllib.parse import unquote


LESSON = Path(__file__).resolve().parents[1]
README = LESSON / "README.md"


class DocumentationTests(unittest.TestCase):
    def test_readme_local_links_exist(self) -> None:
        markdown = README.read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)]+)\)", markdown):
            if "://" in link or link.startswith("#"):
                continue
            with self.subTest(link=link):
                path = unquote(link.split("#", 1)[0])
                self.assertTrue((LESSON / path).exists(), f"Broken link: {link}")

    def test_all_python_code_fences_run_as_saved_scripts(self) -> None:
        markdown = README.read_text(encoding="utf-8")
        snippets = list(re.finditer(
            r"^`{3}python\n([\s\S]*?)^`{3}", markdown, re.MULTILINE
        ))
        self.assertGreaterEqual(len(snippets), 13)

        # The lesson imports examples as an implicit namespace package.
        env = os.environ.copy()
        env["PYTHONPATH"] = str(LESSON) + os.pathsep + env.get("PYTHONPATH", "")
        with TemporaryDirectory(prefix="lesson02-readme-") as directory:
            for index, snippet in enumerate(snippets, start=1):
                line = markdown.count("\n", 0, snippet.start()) + 1
                path = Path(directory) / f"readme_snippet_{index}.py"
                path.write_text(snippet.group(1), encoding="utf-8")
                with self.subTest(block=index, line=line):
                    result = subprocess.run(
                        [sys.executable, str(path)],
                        cwd=LESSON,
                        env=env,
                        text=True,
                        capture_output=True,
                        timeout=45,
                    )
                    self.assertEqual(
                        result.returncode, 0,
                        f"README.md:{line}:\n{result.stdout}\n{result.stderr}",
                    )

    def test_coroutine_task_example_output_matches_readme(self) -> None:
        """Prevent confusion about Coroutine, Task and returned value."""
        markdown = README.read_text(encoding="utf-8")
        start = markdown.index("### 6.1 Three distinct things:")
        end = markdown.index("### 6.2 Complete", start)
        section = markdown[start:end]
        code = re.search(r"^`{3}python\n([\s\S]*?)^`{3}", section, re.MULTILINE)
        expected = re.search(r"^`{3}text\n([\s\S]*?)^`{3}", section, re.MULTILINE)
        self.assertIsNotNone(code)
        self.assertIsNotNone(expected)
        result = subprocess.run(
            [sys.executable, "-c", code.group(1)],
            cwd=LESSON,
            text=True,
            capture_output=True,
            timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), expected.group(1).strip())

    def test_demo_implementations_embedded_verbatim(self) -> None:
        markdown = README.read_text(encoding="utf-8")
        cases = [
            ("threading_io.py", "def run_sequential(", "\n\ndef main("),
            ("thread_pool_io.py", "def run_pool(", "\n\ndef main("),
            ("cpu_pool_comparison.py", "def cpu_work(", "\n\ndef validate("),
            ("cpu_pool_comparison.py", "def validate(", "\n\ndef run_sequential("),
            ("cpu_pool_comparison.py", "def run_sequential(", "\n\ndef run_threads("),
            ("cpu_pool_comparison.py", "def run_threads(", "\n\n# '-> list[int]'"),
            ("cpu_pool_comparison.py", "def run_processes(", "\n\ndef measure("),
            ("asyncio_io.py", "async def simulated_io(", "\n\nasync def run_sequential("),
            ("asyncio_io.py", "async def run_sequential(", "\n\nasync def timed("),
            ("asyncio_blocking.py", "async def bad_blocking(", "\n\nasync def run_bad("),
            ("asyncio_blocking.py", "async def run_bad(", "\n\nasync def demo("),
        ]
        for file, start_marker, end_marker in cases:
            source = (LESSON / "examples" / file).read_text(encoding="utf-8")
            start = source.find(start_marker)
            end = source.find(end_marker, start + len(start_marker))
            self.assertGreaterEqual(start, 0, f"Missing {start_marker} in {file}")
            self.assertGreater(end, start, f"Missing {end_marker} in {file}")
            with self.subTest(file=file, function=start_marker):
                excerpt = source[start:end].strip()
                self.assertIn(excerpt, markdown, f"README drifted from {file}")


if __name__ == "__main__":
    unittest.main()
