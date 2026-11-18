import tempfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import unittest
from unittest.mock import patch

from algorithms import binary_search, linear_search, merge_sort, nearest_by_divide_and_conquer
from app import InventorySystem
from data_structures import BinarySearchTree, HashTable, LinkedList, Queue, Stack
from main import input_optional_float, input_optional_int


class InventoryTest(unittest.TestCase):
    def test_crud_and_persistence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inventory.json"
            system = InventorySystem(str(path))
            self.assertTrue(system.create("A-1", "Keyboard", "Accessories", 7, 1500)[0])
            self.assertEqual(system.read("A-1").name, "Keyboard")
            self.assertTrue(system.update("A-1", quantity=3)[0])
            self.assertEqual(system.read("A-1").quantity, 3)
            reloaded = InventorySystem(str(path))
            self.assertEqual(reloaded.read("A-1").restock_status, "Restock needed")
            self.assertTrue(reloaded.delete("A-1")[0])
            self.assertIsNone(reloaded.read("A-1"))

    def test_required_data_structures(self):
        linked = LinkedList()
        linked.append("one")
        linked.append("two")
        self.assertEqual(linked.to_list(), ["one", "two"])

        stack = Stack()
        stack.push("old")
        stack.push("new")
        self.assertEqual(stack.pop(), "new")

        queue = Queue()
        queue.enqueue("first")
        queue.enqueue("second")
        self.assertEqual(queue.dequeue(), "first")

        tree = BinarySearchTree()
        tree.insert(20, "B")
        tree.insert(10, "A")
        self.assertEqual(tree.search(10), "A")
        self.assertEqual(tree.inorder(), ["A", "B"])

        table = HashTable()
        table.put("A1", "Keyboard")
        self.assertEqual(table.get("A1"), "Keyboard")
        self.assertTrue(table.remove("A1"))

    def test_search_sort_and_divide_and_conquer(self):
        values = [("A", 500), ("B", 100), ("C", 300)]
        self.assertEqual(linear_search(values, lambda item: item[0] == "C")[1], ("C", 300))

        sorted_values = merge_sort(values, key=lambda item: item[1])
        self.assertEqual([item[0] for item in sorted_values], ["B", "C", "A"])
        self.assertEqual(binary_search(sorted_values, 300, key=lambda item: item[1])[1], ("C", 300))
        self.assertEqual(nearest_by_divide_and_conquer(values, 275, key=lambda item: item[1]), ("C", 300))

    def test_create_update_delete_and_undo(self):
        with tempfile.TemporaryDirectory() as directory:
            system = InventorySystem(str(Path(directory) / "inventory.json"))
            self.assertTrue(system.create("U-1", "Phone", "Devices", 10, 20000)[0])
            self.assertIn("devices", system.categories)
            self.assertTrue(system.update("U-1", name="Tablet", quantity=2)[0])
            self.assertTrue(system.undo_last_action()[0])
            product = system.read("U-1")
            self.assertEqual(product.name, "Phone")
            self.assertEqual(product.quantity, 10)
            self.assertTrue(system.delete("U-1")[0])
            self.assertTrue(system.undo_last_action()[0])
            self.assertIsNotNone(system.read("U-1"))

    def test_inventory_rejects_negative_and_nonfinite_values(self):
        with tempfile.TemporaryDirectory() as directory:
            system = InventorySystem(str(Path(directory) / "inventory.json"))
            self.assertTrue(system.create("A-1", "Keyboard", "Accessories", 2, 1500)[0])

            self.assertFalse(system.create("A-2", "Mouse", "Accessories", -1, 500)[0])
            self.assertFalse(system.create("A-4", "Mouse", "Accessories", 1.5, 500)[0])
            self.assertFalse(system.create("A-3", "Mouse", "Accessories", 1, float("inf"))[0])
            self.assertFalse(system.update("A-1", quantity=-1)[0])
            self.assertFalse(system.update("A-1", quantity=1.5)[0])
            self.assertFalse(system.update("A-1", price=float("nan"))[0])
            self.assertEqual(system.read("A-1").quantity, 2)
            self.assertEqual(system.read("A-1").price, 1500)

    def test_ticket_actions_do_not_break_inventory_undo(self):
        with tempfile.TemporaryDirectory() as directory:
            system = InventorySystem(str(Path(directory) / "inventory.json"))
            self.assertTrue(
                system.create("H-1001", "Test part", "Accessories", 1, 10)[0]
            )
            success, _ = system.join_waitlist("Jamie", "Assembly", "Build a PC")
            self.assertTrue(success)

            success, message = system.undo_last_action()

            self.assertTrue(success, message)
            self.assertIsNone(system.by_sku.get("H-1001"))
            self.assertIsNotNone(system.ticket_by_id.get("H-1001"))

    def test_completed_tickets_are_removed_from_active_stack(self):
        with tempfile.TemporaryDirectory() as directory:
            system = InventorySystem(str(Path(directory) / "inventory.json"))
            system.join_waitlist("Jamie", "Assembly", "Build a PC")
            system.join_waitlist("Morgan", "Retail", "Choose a graphics card")
            system.assign_next_customer("Assembly")
            system.assign_next_customer("Retail")
            self.assertEqual(len(system.active_stack.items), 2)

            self.assertTrue(system.complete_service("H-1001")[0])

            self.assertEqual(
                [ticket.ticket_id for ticket in system.active_stack.to_list()],
                ["H-1002"],
            )

    def test_optional_cli_numeric_inputs_retry_invalid_values(self):
        output = StringIO()
        with redirect_stdout(output), patch(
            "builtins.input", side_effect=["bad", "-2", "4"]
        ):
            self.assertEqual(input_optional_int("Quantity: "), 4)
        with redirect_stdout(output), patch(
            "builtins.input", side_effect=["inf", "-1.0", "7.5"]
        ):
            self.assertEqual(input_optional_float("Price: "), 7.5)
        with patch("builtins.input", return_value=""):
            self.assertIsNone(input_optional_int("Quantity: "))
            self.assertIsNone(input_optional_float("Price: "))

    def test_helpdesk_waitlist_assignment_and_completion(self):
        with tempfile.TemporaryDirectory() as directory:
            system = InventorySystem(str(Path(directory) / "inventory.json"))
            success, message = system.join_waitlist(
                "Jamie", "Assembly", "Build a gaming PC"
            )
            self.assertTrue(success)
            ticket_id = message.split()[-1].rstrip(".")
            success, _ = system.assign_next_customer("Assembly")
            self.assertTrue(success)
            ticket = system.ticket_by_id.get(ticket_id)
            self.assertEqual(ticket.status, "Active")
            self.assertFalse(system.staff_by_id.get(ticket.staff_id).available)
            self.assertTrue(system.complete_service(ticket_id)[0])
            self.assertEqual(ticket.status, "Finished")
            self.assertTrue(system.staff_by_id.get(ticket.staff_id).available)

    def test_helpdesk_state_persists_across_restarts(self):
        with tempfile.TemporaryDirectory() as directory:
            inventory_path = Path(directory) / "inventory.json"
            first_run = InventorySystem(str(inventory_path))
            first_run.join_waitlist("Morgan", "Retail", "Help choosing a graphics card")
            ticket_id = list(first_run.tickets)[0].ticket_id

            second_run = InventorySystem(str(inventory_path))
            self.assertEqual(second_run.waiting_count("Retail"), 1)
            self.assertTrue(second_run.assign_next_customer("Retail")[0])

            third_run = InventorySystem(str(inventory_path))
            self.assertEqual(third_run.active_customers()[0].ticket_id, ticket_id)
            self.assertFalse(third_run.staff_by_id.get("ST-02").available)
            self.assertTrue(third_run.complete_service(ticket_id)[0])

            final_run = InventorySystem(str(inventory_path))
            self.assertEqual(final_run.finished_services()[0].ticket_id, ticket_id)
            self.assertTrue(final_run.staff_by_id.get("ST-02").available)

    def test_delete_finished_ticket_updates_history_and_persistence(self):
        with tempfile.TemporaryDirectory() as directory:
            inventory_path = Path(directory) / "inventory.json"
            system = InventorySystem(str(inventory_path))
            system.join_waitlist("Morgan", "Retail", "Help choosing a graphics card")
            ticket_id = list(system.tickets)[0].ticket_id
            system.assign_next_customer("Retail")
            system.complete_service(ticket_id)

            success, message = system.delete_finished_ticket(ticket_id.lower())

            self.assertTrue(success, message)
            self.assertIsNone(system.ticket_by_id.get(ticket_id))
            self.assertEqual(system.finished_services(), [])
            self.assertEqual(system.service_history.to_list(), [])
            self.assertIsNone(InventorySystem(str(inventory_path)).ticket_by_id.get(ticket_id))

    def test_waiting_and_active_tickets_cannot_be_deleted(self):
        with tempfile.TemporaryDirectory() as directory:
            system = InventorySystem(str(Path(directory) / "inventory.json"))
            system.join_waitlist("Morgan", "Retail", "Help choosing a graphics card")
            ticket_id = list(system.tickets)[0].ticket_id

            success, message = system.delete_finished_ticket(ticket_id)

            self.assertFalse(success)
            self.assertIn("Only finished tickets", message)
            self.assertTrue(system.assign_next_customer("Retail")[0])
            success, message = system.delete_finished_ticket(ticket_id)
            self.assertFalse(success)
            self.assertIn("Only finished tickets", message)
            self.assertIsNotNone(system.ticket_by_id.get(ticket_id))

    def test_staff_roster_persists_and_busy_staff_cannot_be_removed(self):
        with tempfile.TemporaryDirectory() as directory:
            inventory_path = Path(directory) / "inventory.json"
            system = InventorySystem(str(inventory_path))
            success, _ = system.add_staff("Riley", "Retail")
            self.assertTrue(success)
            member = system.staff_by_id.get("ST-06")
            self.assertEqual(member.name, "Riley")

            system.join_waitlist("Taylor", "Retail", "Choose a CPU")
            system.assign_next_customer("Retail")
            self.assertFalse(system.remove_staff("ST-02")[0])

            reloaded = InventorySystem(str(inventory_path))
            self.assertIsNotNone(reloaded.staff_by_id.get("ST-06"))
            self.assertFalse(reloaded.staff_by_id.get("ST-02").available)


if __name__ == "__main__":
    unittest.main()
