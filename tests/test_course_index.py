"""Repository-level checks for the published nine-lesson learning path."""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]


class CurriculumIndexTests(unittest.TestCase):
    def test_root_and_curriculum_links_have_same_nine_published_targets(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        curriculum = (ROOT / "CURRICULUM.md").read_text(encoding="utf-8")
        primary = re.findall(
            r"^[1-9]\. \[[^\]]+\]\(([^)]+/README\.md)\)",
            readme, flags=re.MULTILINE
        )
        outline = re.findall(
            r"^\| \[0[1-9]\]\(([^)]+/README\.md)\)",
            curriculum, flags=re.MULTILINE
        )
        self.assertEqual(len(primary), 9, "Root README needs exactly nine published lessons")
        self.assertEqual(len(outline), 9, "CURRICULUM must list all nine lessons")
        self.assertEqual(set(primary), set(outline), "Root and CURRICULUM links differ")

        for link in primary:
            with self.subTest(link=link):
                resolved = ROOT / unquote(link)
                self.assertTrue(resolved.is_file(), f"Missing published lesson: {resolved}")
                self.assertTrue((resolved.parent / "tests").is_dir())
                self.assertTrue((resolved.parent / "examples").is_dir())

    def test_no_obsolete_outlines_after_publication(self):
        for i, slug in enumerate((
            "05-abcs-and-duck-typing",
            "06-inheritance-and-mro",
            "07-polymorphism",
            "08-composition",
            "09-encapsulation-and-properties",
        ), start=5):
            with self.subTest(lesson=i):
                self.assertFalse((ROOT / "lessons" / slug).exists())

    def test_all_new_demos_are_inlined_and_have_expected_output_blocks(self):
        for number, title in (
            (5, "Abstract Base Classes and Interface-Like Contracts"),
            (6, "Inheritance, Multiple Inheritance and MRO"),
            (7, "Runtime Polymorphism and Duck Typing"),
            (8, "Composition and Object Collaboration"),
            (9, "Encapsulation, Properties and Python Conventions"),
        ):
            folder = ROOT / f"{number:02d}. {title}"
            with self.subTest(lesson=number):
                md = (folder / "README.md").read_text(encoding="utf-8")
                sources = sorted((folder / "examples").glob("*.py"))
                snippets = re.findall(
                    r"^```python\n([\s\S]*?)^```", md, flags=re.MULTILINE
                )
                expected = re.findall(
                    r"^\*\*Expected output:\*\*\s+^```text\n([\s\S]*?)^```",
                    md, flags=re.MULTILINE,
                )
                self.assertEqual(len(sources), 2)
                self.assertEqual(len(snippets), len(sources))
                self.assertEqual(len(expected), len(sources))
                for source in sources:
                    self.assertEqual(
                        sum(code.strip() == source.read_text(encoding="utf-8").strip()
                            for code in snippets),
                        1, f"Source not embedded exactly once: {source}"
                    )


if __name__ == "__main__":
    unittest.main()
