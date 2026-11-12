"""Lesson 09 properties, descriptors, slots, and executable documentation."""
import re
import subprocess
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote

LESSON = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LESSON))
from examples.student_properties import Student
from examples.descriptors_and_slots import Endpoint, SlottedPoint, ValidatedPort
EXPECTED = {
  "student_properties.py": [
    "student: Ada 20",
    "updated: 21",
    "id: S-42",
    "name mangled: True",
    "negative age: ValueError",
    "bool age: TypeError",
    "read-only name: AttributeError"
  ],
  "descriptors_and_slots.py": [
    "port: 443",
    "storage: {'_port': 443}",
    "class descriptor: ValidatedPort",
    "invalid port: ValueError",
    "point: 2 3",
    "slot restriction: AttributeError"
  ]
}


class EncapsulationTests(unittest.TestCase):
    def test_property_validation_and_state_preservation(self):
        obj = Student("Ada", 20)
        obj.age = 21
        self.assertEqual(obj.age, 21)
        with self.assertRaises(ValueError):
            obj.age = -1
        with self.assertRaises(ValueError):
            obj.age = 151
        with self.assertRaises(TypeError):
            obj.age = True
        self.assertEqual(obj.age, 21)
        with self.assertRaises(AttributeError):
            obj.name = "New"

    def test_name_mangling_is_not_access_control(self):
        obj = Student("Ada", 20)
        self.assertEqual(obj.identifier(), "S-42")
        self.assertEqual(getattr(obj, "_Student__student_id"), "S-42")
        obj._age = -500  # Deliberate bypass of public API; no security boundary.
        self.assertEqual(obj.age, -500)

    def test_data_descriptor_storage_and_validation(self):
        ep = Endpoint(443)
        self.assertEqual(ep.__dict__, {"_port": 443})
        self.assertIsInstance(Endpoint.port, ValidatedPort)
        with self.assertRaises(ValueError):
            ep.port = 0
        with self.assertRaises(ValueError):
            ep.port = True
        self.assertEqual(ep.port, 443)

    def test_slots_restrict_new_fields_but_not_existing_mutation(self):
        point = SlottedPoint(2, 3)
        point.x = 9
        self.assertEqual(point.x, 9)
        self.assertFalse(hasattr(point, "__dict__"))
        with self.assertRaises(AttributeError):
            point.color = "blue"

    def test_readme_embeds_exact_self_executing_python_code(self):
        readme = (LESSON / "README.md").read_text(encoding="utf-8")
        blocks = re.findall(r"^```python\n([\s\S]*?)^```", readme, re.M)
        self.assertEqual(len(blocks), len(EXPECTED))
        for (name, expected), block in zip(EXPECTED.items(), blocks):
            with self.subTest(name=name):
                source = (LESSON / "examples" / name).read_text(encoding="utf-8").strip()
                self.assertEqual(source, block.strip())
                for code in (source, block):
                    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
                    self.assertEqual(result.stdout.splitlines(), expected)
                    self.assertEqual(result.stderr, "")

    def test_local_markdown_links_are_valid(self):
        readme = (LESSON / "README.md").read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)]+)\)", readme):
            if "://" not in link and not link.startswith("#"):
                self.assertTrue((LESSON / unquote(link).split("#")[0]).exists(), link)


if __name__ == "__main__":
    unittest.main()
