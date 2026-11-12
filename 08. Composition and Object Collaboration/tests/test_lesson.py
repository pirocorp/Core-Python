"""Lesson 08 behavior, boundaries and standalone documentation."""
import re
import subprocess
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote

LESSON = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LESSON))
from examples.engine_injection import Engine, FakeEngine, Car
from examples.order_service import InMemoryOrders, FailingOrders, OrderService
EXPECTED = {
  "engine_injection.py": [
    "real: car: engine running",
    "fake: car: fake engine",
    "fake calls: 1",
    "constructed internally: car: engine running"
  ],
  "order_service.py": [
    "placed: accepted:O-42@2026-11-12T12:00Z",
    "saved: [('O-42', '2026-11-12T12:00Z')]",
    "invalid id: ValueError",
    "storage failure: OSError"
  ]
}


class CompositionTests(unittest.TestCase):
    def test_real_and_fake_collaborators(self):
        self.assertEqual(Car(Engine()).start(), "car: engine running")
        fake = FakeEngine()
        self.assertEqual(Car(fake).start(), "car: fake engine")
        self.assertEqual(fake.calls, 1)

    def test_shared_dependency_identity(self):
        shared = FakeEngine()
        self.assertIs(Car(shared).engine, Car(shared).engine)
        Car(shared).start()
        Car(shared).start()
        self.assertEqual(shared.calls, 2)

    def test_service_records_deterministic_order(self):
        store = InMemoryOrders()
        service = OrderService(store, lambda: "fixed")
        self.assertEqual(service.place("O-1"), "accepted:O-1@fixed")
        self.assertEqual(store.saved, [("O-1", "fixed")])

    def test_invalid_input_never_calls_collaborators(self):
        store = InMemoryOrders()
        calls = []
        service = OrderService(store, lambda: calls.append("clock") or "fixed")
        with self.assertRaises(ValueError):
            service.place("")
        self.assertEqual(calls, [])
        self.assertEqual(store.saved, [])

    def test_storage_error_propagates_without_success_result(self):
        service = OrderService(FailingOrders(), lambda: "fixed")
        with self.assertRaisesRegex(OSError, "storage unavailable"):
            service.place("O-2")

    def test_documentation_contains_executable_exact_examples(self):
        doc = (LESSON / "README.md").read_text(encoding="utf-8")
        blocks = re.findall(r"^```python\n([\s\S]*?)^```", doc, re.M)
        self.assertEqual(len(blocks), len(EXPECTED))
        for (name, lines), block in zip(EXPECTED.items(), blocks):
            with self.subTest(example=name):
                source = (LESSON / "examples" / name).read_text(encoding="utf-8").strip()
                self.assertEqual(block.strip(), source)
                for code in (source, block):
                    result = subprocess.run([sys.executable, "-c", code], text=True, capture_output=True, check=True)
                    self.assertEqual(result.stdout.splitlines(), lines)
                    self.assertEqual(result.stderr, "")

    def test_local_links(self):
        doc = (LESSON / "README.md").read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)]+)\)", doc):
            if "://" not in link and not link.startswith("#"):
                self.assertTrue((LESSON / unquote(link).split("#")[0]).exists(), link)


if __name__ == "__main__":
    unittest.main()
