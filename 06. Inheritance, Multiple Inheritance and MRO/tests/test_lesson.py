"""Lesson 06 MRO invariants and self-contained executable examples."""

import re
import subprocess
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote

LESSON = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LESSON))
from examples.dispatch import Animal, Bird, Dog, Flyable
from examples.diamond import Diamond, Left, Right, Root, inconsistent_hierarchy_fails

EXPECTED = {
  "dispatch.py": [
    "animal: generic sound",
    "dog: generic sound + woof",
    "bird: chirp",
    "fly: flying",
    "bird MRO: Bird > Flyable > Animal > object"
  ],
  "diamond.py": [
    "MRO: Diamond > Left > Right > Root > object",
    "init unwind: ['Root', 'Right', 'Left', 'Diamond']",
    "attributes: L R",
    "method chain: ['Diamond', 'Left', 'Right', 'Root']",
    "inconsistent MRO: True"
  ]
}


class InheritanceTests(unittest.TestCase):
    def test_single_inheritance_and_mixin_dispatch(self):
        self.assertEqual(Dog().speak(), "generic sound + woof")
        self.assertEqual(Bird().fly(), "flying")
        self.assertEqual(Bird.__mro__, (Bird, Flyable, Animal, object))

    def test_diamond_mro_and_cooperative_initialization(self):
        order = []
        obj = Diamond(events=order, left="L", right="R")
        self.assertEqual(Diamond.__mro__, (Diamond, Left, Right, Root, object))
        self.assertEqual(order, ["Root", "Right", "Left", "Diamond"])
        self.assertEqual((obj.left, obj.right), ("L", "R"))
        self.assertEqual(obj.path(), ["Diamond", "Left", "Right", "Root"])

    def test_missing_required_parameters_and_inconsistent_mro(self):
        with self.assertRaises(TypeError):
            Diamond(events=[], left="L")
        with self.assertRaises(TypeError):
            Diamond(events=[], left="L", right="R", surprise=3)
        self.assertTrue(inconsistent_hierarchy_fails())

    def test_demos_are_embedded_and_runnable_in_isolation(self):
        doc = (LESSON / "README.md").read_text(encoding="utf-8")
        blocks = re.findall(r"^```python\n([\s\S]*?)^```", doc, re.M)
        self.assertEqual(len(blocks), len(EXPECTED))
        for (name, output), block in zip(EXPECTED.items(), blocks):
            with self.subTest(name=name):
                source = (LESSON / "examples" / name).read_text(encoding="utf-8").strip()
                self.assertEqual(source, block.strip())
                for script in (source, block):
                    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=True)
                    self.assertEqual(proc.stdout.splitlines(), output)
                    self.assertEqual(proc.stderr, "")

    def test_readme_links(self):
        doc = (LESSON / "README.md").read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)]+)\)", doc):
            if "://" not in link and not link.startswith("#"):
                self.assertTrue((LESSON / unquote(link).split("#")[0]).exists(), link)


if __name__ == "__main__":
    unittest.main()
