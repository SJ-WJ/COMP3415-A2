import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from supplydesk.menu import run_menu
from supplydesk.service import OrderService


class MenuTests(unittest.TestCase):
  
  def setUp(self):
    directory = tempfile.TemporaryDirectory()
    self.addCleanup(directory.cleanup)
    self.service = OrderService(Path(directory.name) / "state.json")

  def run_menu_and_type(self, typed_answers):
    """Run the menu, type the given answers, and return what it printed."""
    printed = io.StringIO()
    with mock.patch("builtins.input", side_effect=typed_answers):
        with contextlib.redirect_stdout(printed):
            run_menu(self.service)
    return printed.getvalue()

  def test_every_menu_option(self):
    view_products = ["1"]
    get_quote = ["2", "", "notebook", "2", "", ""]
    place_order = ["3", "", "mug", "1", "", "", "y"]
    view_history = ["4"]
    find_order = ["5", "ORD-0001"]
    cancel_order = ["6", "ORD-0001", "y"]
    wrong_choice = ["9"]
    exit_menu = ["0"]

    typed_answers = (view_products + get_quote + place_order + view_history + find_order + cancel_order + wrong_choice + exit_menu)
    screen = self.run_menu_and_type(typed_answers)

    self.assertIn("Canvas bag", screen)
    self.assertIn("Total: $10.00", screen)
    self.assertIn("ORD-0001 - placed", screen)
    self.assertIn("ORD-0001 - cancelled", screen)
    self.assertIn("Choose a number from 0 to 6.", screen)
    self.assertIn("Goodbye.", screen)


if __name__ == "__main__":
    unittest.main()