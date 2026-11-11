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
    self.path = Path(directory.name) / "state.json"
    self.service = OrderService(self.path)

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

  # Invalid or exceptional behaviour
  def test_rejected_order_changes_nothing(self):
    self.service.place_order("regular", [item("mug", 1)])
    before = self.path.read_bytes()
    with self.assertRaises(ValueError):
        self.service.place_order("regular", [item("mug", 1), item("laptop", 1)])
    self.assertEqual(self.path.read_bytes(), before)
    self.assertEqual(self.stock("mug"), 7)

# Behaviour to preserve
  def test_quote_matches_placed_order(self):
    request = ("student", [item("hoodie", 2)], "delivery")
    quote = self.service.quote(*request)
    order = self.service.place_order(*request)
    self.assertEqual(quote["total_cents"], 7800)
    self.assertEqual(order["total_cents"], quote["total_cents"])
    self.assertEqual(order["items"], quote["items"])
  
if __name__ == "__main__":
  unittest.main()