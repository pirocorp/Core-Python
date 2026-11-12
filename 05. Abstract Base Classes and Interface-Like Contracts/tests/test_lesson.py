"""Check Lesson 05 demonstrations, contracts, and embedded documentation."""

import re
import subprocess
import sys
import unittest
from pathlib import Path

LESSON = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LESSON))
from examples.abcs import Shape, Circle, IncompleteShape
from examples.gateways import (
    CardGateway, PayPalGateway, ExternalGateway, PaymentGateway,
    RegisteredWithoutMethods, SupportsCharge,
)

EXPECTED = {
    "abcs.py": [
        "shape: area=12.57, perimeter=12.57",
        "nominal: True",
        "incomplete: TypeError",
        "invalid radius: ValueError"
    ],
    "gateways.py": [
        "checkout: card:150",
        "checkout: paypal:150",
        "external nominal: False",
        "external structural: True",
        "registered nominal: True",
        "registered callable: False",
        "invalid amount: ValueError"
    ]
}


class ContractsTests(unittest.TestCase):
    def test_abcs_are_nominal_and_abstract_at_instantiation(self):
        self.assertTrue(isinstance(Circle(2), Shape))
        self.assertEqual(round(Circle(2).area(), 2), 12.57)
        with self.assertRaises(TypeError):
            IncompleteShape()
        with self.assertRaises(ValueError):
            Circle(0)

    def test_gateway_validation(self):
        self.assertEqual(CardGateway().checkout(150), "card:150")
        self.assertEqual(PayPalGateway().checkout(150), "paypal:150")
        with self.assertRaises(ValueError):
            CardGateway().checkout(0)

    def test_structural_and_virtual_distinctions(self):
        self.assertTrue(isinstance(ExternalGateway(), SupportsCharge))
        self.assertFalse(isinstance(ExternalGateway(), PaymentGateway))
        self.assertTrue(isinstance(RegisteredWithoutMethods(), PaymentGateway))
        self.assertFalse(hasattr(RegisteredWithoutMethods(), "charge"))

    def test_readme_embeds_full_runnable_demos_and_expected_output(self):
        doc = (LESSON / "README.md").read_text(encoding="utf-8")
        blocks = re.findall(r"^```python\n([\s\S]*?)^```", doc, re.M)
        self.assertEqual(len(blocks), len(EXPECTED))
        for index, (filename, expected) in enumerate(EXPECTED.items()):
            with self.subTest(filename=filename):
                source = (LESSON / "examples" / filename).read_text(encoding="utf-8").strip()
                self.assertEqual(blocks[index].strip(), source)
                for code in (source, blocks[index]):
                    run = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
                    self.assertEqual(run.stdout.splitlines(), expected)
                    self.assertEqual(run.stderr, "")

    def test_local_links_resolve(self):
        doc = (LESSON / "README.md").read_text(encoding="utf-8")
        from urllib.parse import unquote
        for link in re.findall(r"\]\(([^)]+)\)", doc):
            if "://" not in link and not link.startswith("#"):
                self.assertTrue((LESSON / unquote(link).split("#")[0]).exists(), link)


if __name__ == "__main__":
    unittest.main()
