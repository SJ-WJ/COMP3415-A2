import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from supplydesk.cli import main
from supplydesk.service import OrderService


def item(product_id, quantity):
    return {"product_id": product_id, "quantity": quantity}


class ExpressTests(unittest.TestCase):
  def setUp(self):
    directory = tempfile.TemporaryDirectory()
    self.addCleanup(directory.cleanup)
    self.path = Path(directory.name) / "state.json"
    self.service = OrderService(self.path)

  def test_cr01_examples(self):
    regular = self.service.quote("regular", [item("notebook", 2)], "express")
    self.assertEqual(regular["total_cents"], 2200)

    student = self.service.quote("student", [item("hoodie", 2)], "express")
    self.assertEqual(student["discount_cents"], 800)
    self.assertEqual(student["total_cents"], 8400)

    large = self.service.quote("regular", [item("hoodie", 3)], "express")
    self.assertEqual(large["total_cents"], 13200)

  def test_express_fee_is_never_free(self):
    standard = self.service.quote("regular", [item("hoodie", 3)], "delivery")
    express = self.service.quote("regular", [item("hoodie", 3)], "express")
    self.assertEqual(standard["delivery_cents"], 0)
    self.assertEqual(express["delivery_cents"], 1200)

  def test_other_fulfillment_values_still_rejected(self):
    for value in ["Express", "shipping"]:
        with self.assertRaises(ValueError):
           self.service.quote("regular", [item("mug", 1)], value)

  def test_express_quote_matches_placed_order(self):
    request = ("student", [item("hoodie", 2)], "express")
    quote = self.service.quote(*request)
    order = self.service.place_order(*request)
    self.assertEqual(order["fulfillment"], "express")
    self.assertEqual(order["total_cents"], quote["total_cents"])

  def test_cli_express_example(self):
    printed = io.StringIO()
    with contextlib.redirect_stdout(printed):
      main(["--data", str(self.path), "quote", "--customer", "student",
            "--fulfillment", "express", "--item", "hoodie:2"])
      result = json.loads(printed.getvalue())
      self.assertEqual(result["total_cents"], 8400)


if __name__ == "__main__":
    unittest.main()