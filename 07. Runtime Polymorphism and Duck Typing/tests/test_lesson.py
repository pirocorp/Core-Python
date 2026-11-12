"""Test runtime polymorphism, structural contracts and executable README."""
import re
import subprocess
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote

LESSON = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LESSON))
from examples.duck_typing import Bird, Duck, MechanicalDuck, Silent, WrongSignature, make_bird_speak
from examples.protocols_and_dispatch import Speaker, Robot, InvalidSpeaker, announce, render
EXPECTED = {
  "duck_typing.py": [
    "speak: generic chirp",
    "speak: quack",
    "speak: synthetic quack",
    "unrelated subclass: False",
    "silent: AttributeError",
    "wrong signature: TypeError"
  ],
  "protocols_and_dispatch.py": [
    "announcement: beep",
    "structural: True",
    "presence-only: True",
    "dispatch int: integer:42",
    "dispatch str: string:hi",
    "dispatch float: default:float",
    "bool resolves as int: integer:True"
  ]
}


class PolymorphismTests(unittest.TestCase):
    def test_overrides_and_unrelated_implementations(self):
        self.assertEqual([make_bird_speak(x) for x in (Bird(), Duck(), MechanicalDuck())],
                         ["generic chirp", "quack", "synthetic quack"])
        self.assertFalse(isinstance(MechanicalDuck(), Bird))

    def test_missing_and_incompatible_methods_fail_distinctly(self):
        with self.assertRaises(AttributeError):
            make_bird_speak(Silent())
        with self.assertRaises(TypeError):
            make_bird_speak(WrongSignature())

    def test_protocol_runtime_only_checks_presence(self):
        self.assertTrue(isinstance(Robot(), Speaker))
        self.assertTrue(isinstance(InvalidSpeaker(), Speaker))
        self.assertEqual(announce(Robot()), "announcement: beep")
        with self.assertRaises(TypeError):
            announce(InvalidSpeaker())

    def test_single_dispatch_by_runtime_first_argument(self):
        self.assertEqual(render(42), "integer:42")
        self.assertEqual(render(True), "integer:True")
        self.assertEqual(render("hi"), "string:hi")
        self.assertEqual(render(3.5), "default:float")

    def test_readme_code_matches_both_demos_and_expected_output(self):
        readme = (LESSON / "README.md").read_text(encoding="utf-8")
        blocks = re.findall(r"^```python\n([\s\S]*?)^```", readme, re.M)
        self.assertEqual(len(blocks), 2)
        for (name, expected), block in zip(EXPECTED.items(), blocks):
            with self.subTest(name=name):
                source = (LESSON / "examples" / name).read_text(encoding="utf-8").strip()
                self.assertEqual(block.strip(), source)
                for code in (block, source):
                    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
                    self.assertEqual(proc.stdout.splitlines(), expected)
                    self.assertEqual(proc.stderr, "")

    def test_local_markdown_links(self):
        readme = (LESSON / "README.md").read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)]+)\)", readme):
            if "://" not in link and not link.startswith("#"):
                self.assertTrue((LESSON / unquote(link).split("#")[0]).exists(), link)


if __name__ == "__main__":
    unittest.main()
