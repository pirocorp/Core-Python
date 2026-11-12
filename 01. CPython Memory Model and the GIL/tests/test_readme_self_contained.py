"""Exercise Lesson 01's copyable code and ensure teaching and demo code match."""
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
            path = unquote(link.split("#", 1)[0])
            with self.subTest(link=link):
                self.assertTrue((LESSON / path).exists(), f"Broken link: {link}")

    def test_all_python_fences_execute_independently(self) -> None:
        markdown = README.read_text(encoding="utf-8")
        snippets = list(re.finditer(
            r"^`{3}python\n([\s\S]*?)^`{3}", markdown, re.MULTILINE
        ))
        self.assertGreaterEqual(len(snippets), 7)
        env = os.environ.copy()
        env["PYTHONPATH"] = str(LESSON) + os.pathsep + env.get("PYTHONPATH", "")
        with TemporaryDirectory(prefix="lesson01-readme-") as temp:
            for number, snippet in enumerate(snippets, start=1):
                line = markdown.count("\n", 0, snippet.start()) + 1
                script = Path(temp) / f"readme_snippet_{number}.py"
                script.write_text(snippet.group(1), encoding="utf-8")
                with self.subTest(snippet=number, line=line):
                    result = subprocess.run(
                        [sys.executable, str(script)],
                        cwd=LESSON,
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    self.assertEqual(
                        result.returncode, 0,
                        f"README.md:{line}:\n{result.stdout}\n{result.stderr}",
                    )

    def test_embedded_demo_implementations_match_sources(self) -> None:
        markdown = README.read_text(encoding="utf-8")
        cases = [
            ("reference_count.py", "def run(", "\n\nif __name__"),
            ("reference_cycles.py", "class Node:", "\n\ndef make_unreachable_cycle("),
            ("reference_cycles.py", "def make_unreachable_cycle(", "\n\nif __name__"),
            ("io_wait_threads.py", "def sequential_waits(", "\n\ndef main("),
            ("factorial_threads.py", "def factorial_workload(", "\n\ndef describe_interpreter("),
        ]
        for filename, start_marker, end_marker in cases:
            source = (LESSON / "examples" / filename).read_text(encoding="utf-8")
            a = source.find(start_marker)
            b = source.find(end_marker, a + len(start_marker))
            self.assertGreaterEqual(a, 0, f"Missing {start_marker}: {filename}")
            self.assertGreater(b, a, f"Missing {end_marker}: {filename}")
            with self.subTest(file=filename, definition=start_marker):
                self.assertIn(source[a:b].strip(), markdown)


if __name__ == "__main__":
    unittest.main()
