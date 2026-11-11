from pathlib import Path
import tempfile
import unittest

from supplydesk.service import OrderService


def item(product_id, quantity):
    return {"product_id": product_id, "quantity": quantity}


class SafetyNetTests(unittest.TestCase):
  def setUp(self):
    directory = tempfile.TemporaryDirectory()
    self.addCleanup(directory.cleanup)
    self.service = OrderService(Path(directory.name) / "state.json")

  def stock(self, product_id):
    return next(p["stock"] for p in self.service.catalog()
                if p["product_id"] == product_id)

  # Normal behaviour
  def test_place_order_deducts_stock_and_numbers_orders(self):
    first = self.service.place_order("regular", [item("notebook", 3)])
    second = self.service.place_order("regular", [item("notebook", 2)])
    self.assertEqual(first["order_id"], "ORD-0001")
    self.assertEqual(second["order_id"], "ORD-0002")
    self.assertEqual(first["status"], "placed")
    self.assertEqual(self.stock("notebook"), 15)

  # Boundary behaviour
  def test_student_discount_at_exactly_5000(self):
    quote = self.service.quote("student", [item("bag", 2)])
    self.assertEqual(quote["discount_cents"], 500)

  
if __name__ == "__main__":
  unittest.main()