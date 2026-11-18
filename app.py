from datetime import datetime
import math

from algorithms import (
    binary_search,
    linear_search,
    merge_sort,
    nearest_by_divide_and_conquer,
)
from data_structures import (
    ArrayList,
    BinarySearchTree,
    HashTable,
    LinkedList,
    Queue,
    Stack,
)
from inventory import (
    AuditLog,
    HelpdeskStorage,
    InventoryStorage,
    Product,
    ServiceTicket,
    Staff,
)


class InventorySystem:
    def __init__(
        self,
        storage_path="inventory.json",
        service_path=None,
        audit_path=None,
    ):
        self.storage = InventoryStorage(storage_path)
        data_directory = self.storage.path.parent
        self.service_storage = HelpdeskStorage(
            service_path or data_directory / "services.json"
        )
        self.audit = AuditLog(audit_path or data_directory / "audit.log")
        self.products = ArrayList()
        self.history = Stack()
        self.orders = Queue()
        self.recently_viewed = LinkedList()
        self.by_sku = HashTable()
        self.price_tree = BinarySearchTree()
        self.categories = set()
        self.sectors = {
            "Assembly",
            "Retail",
            "Hardware Repair",
            "Software Repair",
            "General Service",
        }
        self.waiting_by_sector = {sector: Queue() for sector in self.sectors}
        self.staff = ArrayList()
        self.staff_by_id = HashTable()
        self.tickets = ArrayList()
        self.ticket_by_id = HashTable()
        self.active_stack = Stack()
        self.active_tickets = ArrayList()
        self.finished_stack = Stack()
        self.service_history = LinkedList()
        self.next_ticket_number = 1001
        self._load_default_staff()
        self.load()
        self.load_services()

    def load_services(self):
        stored = self.service_storage.load()
        if stored["staff"] is not None:
            self.staff.clear()
            self.staff_by_id = HashTable()
            for member in stored["staff"]:
                self.staff.append(member)
                self.staff_by_id.put(member.staff_id.upper(), member)
        self.tickets.clear()
        self.ticket_by_id = HashTable()
        self.waiting_by_sector = {sector: Queue() for sector in self.sectors}
        self.active_stack = Stack()
        self.active_tickets.clear()
        self.finished_stack = Stack()
        self.service_history = LinkedList()
        for member in self.staff:
            member.available = True
        self.next_ticket_number = stored["next_ticket_number"]
        for ticket in stored["tickets"]:
            self.tickets.append(ticket)
            self.ticket_by_id.put(ticket.ticket_id.upper(), ticket)
            if ticket.status == "Waiting" and ticket.sector in self.waiting_by_sector:
                self.waiting_by_sector[ticket.sector].enqueue(ticket)
            elif ticket.status == "Active":
                member = self.staff_by_id.get(ticket.staff_id)
                if member:
                    member.available = False
                self.active_stack.push(ticket)
                self.active_tickets.append(ticket)
            elif ticket.status == "Finished":
                self.finished_stack.push(ticket)
                self.service_history.append(ticket)

    def save_services(self):
        self.service_storage.save(
            list(self.tickets), self.next_ticket_number, list(self.staff)
        )

    def _load_default_staff(self):
        default_staff = [
            Staff("ST-01", "Alex", "Assembly"),
            Staff("ST-02", "Bella", "Retail"),
            Staff("ST-03", "Carlos", "Hardware Repair"),
            Staff("ST-04", "Dana", "Software Repair"),
            Staff("ST-05", "Evan", "General Service"),
        ]
        for member in default_staff:
            self.staff.append(member)
            self.staff_by_id.put(member.staff_id, member)

    def load(self):
        self.products.clear()
        self.categories.clear()
        for product in self.storage.load():
            product.update_status()
            self._index_product(product)

    def _index_product(self, product):
        self.products.append(product)
        self.by_sku.put(product.sku.upper(), product)
        self.price_tree.insert(product.price, product)
        self.categories.add(product.category.lower())

    def rebuild_indexes(self):
        self.by_sku = HashTable()
        self.price_tree = BinarySearchTree()
        self.categories.clear()
        for product in self.products:
            self.by_sku.put(product.sku.upper(), product)
            self.price_tree.insert(product.price, product)
            self.categories.add(product.category.lower())

    def save(self):
        self.storage.save(list(self.products))

    def create(self, sku, name, category, quantity, price):
        sku = sku.strip().upper()
        if self.by_sku.get(sku):
            return False, "A product with that SKU already exists."
        try:
            parsed_quantity = int(quantity)
            if float(quantity) != parsed_quantity:
                raise ValueError
            price = float(price)
        except (OverflowError, TypeError, ValueError):
            return False, "Quantity must be a whole number and price must be numeric."
        quantity = parsed_quantity
        if quantity < 0 or price < 0 or not math.isfinite(price):
            return False, "Quantity and price must be finite values of zero or greater."
        product = Product(sku, name.strip(), category.strip(), quantity, price)
        product.update_status()
        self._index_product(product)
        self.history.push(("create", sku, None))
        self.audit.add("Created", sku)
        self.save()
        return True, "Product created."

    def read(self, sku):
        product = self.by_sku.get(sku.strip().upper())
        if product:
            self.recently_viewed.append(product)
        return product

    def update(self, sku, name=None, category=None, quantity=None, price=None):
        product = self.by_sku.get(sku.strip().upper())
        if not product:
            return False, "Product not found."
        try:
            updated_quantity = None
            if quantity is not None:
                updated_quantity = int(quantity)
                if float(quantity) != updated_quantity:
                    raise ValueError
            updated_price = float(price) if price is not None else None
        except (OverflowError, TypeError, ValueError):
            return False, "Quantity must be a whole number and price must be numeric."
        if (
            (updated_quantity is not None and updated_quantity < 0)
            or (
                updated_price is not None
                and (updated_price < 0 or not math.isfinite(updated_price))
            )
        ):
            return False, "Quantity and price must be finite values of zero or greater."
        previous = (
            product.name,
            product.category,
            product.quantity,
            product.price,
        )
        if name is not None:
            product.name = name.strip()
        if category is not None:
            product.category = category.strip()
        if updated_quantity is not None:
            product.quantity = updated_quantity
        if updated_price is not None:
            product.price = updated_price
        product.update_status()
        self.rebuild_indexes()
        self.history.push(("update", sku.strip().upper(), previous))
        self.audit.add("Updated", sku.strip().upper())
        self.save()
        return True, "Product updated."

    def delete(self, sku):
        sku = sku.strip().upper()
        product = self.by_sku.get(sku)
        if not product:
            return False, "Product not found."
        deleted_snapshot = (
            product.sku,
            product.name,
            product.category,
            product.quantity,
            product.price,
        )
        self.products.remove(product)
        self.by_sku.remove(sku)
        self.rebuild_indexes()
        self.history.push(("delete", sku, deleted_snapshot))
        self.audit.add("Deleted", sku)
        self.save()
        return True, "Product deleted."

    def undo_last_action(self):
        if self.history.is_empty():
            return False, "There are no actions to undo."
        action, sku, snapshot = self.history.peek()
        if action not in {"create", "update", "delete"}:
            return False, "The latest action is not an inventory action to undo."
        self.history.pop()
        if action == "create":
            product = self.by_sku.get(sku)
            if product:
                self.products.remove(product)
                self.by_sku.remove(sku)
                self.rebuild_indexes()
                self.save()
                self.audit.add("Undid create", sku)
                return True, f"Undid create action for {sku}; the record was removed."
            return False, "Cannot undo: created product not found."
        if action == "delete":
            _, name, category, quantity, price = snapshot
            product = Product(sku, name, category, quantity, price)
            product.update_status()
            self._index_product(product)
            self.save()
            self.audit.add("Undid delete", sku)
            return True, f"Undid delete action for {sku}; the record was restored."
        product = self.by_sku.get(sku)
        if not product:
            return False, "Cannot undo: updated product not found."
        name, category, quantity, price = snapshot
        product.name = name
        product.category = category
        product.quantity = quantity
        product.price = price
        product.update_status()
        self.rebuild_indexes()
        self.save()
        self.audit.add("Undid update", sku)
        return True, f"Undid update action for {sku}; previous values restored."

    def linear_search_name(self, query):
        query = query.lower()
        index, product = linear_search(
            list(self.products),
            lambda item: query in item.name.lower() or query in item.category.lower(),
        )
        return index, product

    def binary_search_sku(self, sku):
        sorted_products = merge_sort(list(self.products), key=lambda item: item.sku)
        return binary_search(sorted_products, sku.upper(), key=lambda item: item.sku)

    def find_nearest_price(self, target):
        return nearest_by_divide_and_conquer(
            list(self.products), float(target), key=lambda item: item.price
        )

    def list_sorted_by_name(self):
        return merge_sort(list(self.products), key=lambda item: item.name.lower())

    def list_sorted_by_price(self):
        return merge_sort(list(self.products), key=lambda item: item.price)

    def join_waitlist(self, customer_name, sector, description):
        sector = sector.strip().title()
        sector_aliases = {
            "Pc Assembly": "Assembly",
            "Computer Assembly": "Assembly",
            "Buying": "Retail",
            "Purchase": "Retail",
            "Hardware": "Hardware Repair",
            "Software": "Software Repair",
        }
        sector = sector_aliases.get(sector, sector)
        if sector not in self.sectors:
            return False, "Unknown service sector."
        ticket = ServiceTicket(
            ticket_id=f"H-{self.next_ticket_number}",
            customer_name=customer_name.strip(),
            sector=sector,
            description=description.strip(),
            created_at=datetime.now().astimezone().isoformat(timespec="seconds"),
        )
        self.next_ticket_number += 1
        self.waiting_by_sector[sector].enqueue(ticket)
        self.tickets.append(ticket)
        self.ticket_by_id.put(ticket.ticket_id, ticket)
        self.audit.add("Joined waitlist", ticket.ticket_id)
        self.save_services()
        return True, f"Customer joined {sector} waitlist as {ticket.ticket_id}."

    def waiting_count(self, sector=None):
        if sector:
            queue = self.waiting_by_sector.get(sector)
            return len(queue.items) if queue else 0
        return sum(len(queue.items) for queue in self.waiting_by_sector.values())

    def waiting_tickets(self, sector):
        queue = self.waiting_by_sector.get(sector)
        return queue.to_list() if queue else []

    def find_available_staff(self, sector):
        available = []
        for member in self.staff:
            if member.sector == sector and member.available:
                available.append(member)
        return available

    def add_staff(self, name, sector):
        name = name.strip()
        if not name or sector not in self.sectors:
            return False, "Enter a staff name and a valid service sector."
        staff_number = 1
        historical_staff_ids = {ticket.staff_id for ticket in self.tickets}
        while (
            self.staff_by_id.get(f"ST-{staff_number:02d}")
            or f"ST-{staff_number:02d}" in historical_staff_ids
        ):
            staff_number += 1
        member = Staff(f"ST-{staff_number:02d}", name, sector)
        self.staff.append(member)
        self.staff_by_id.put(member.staff_id, member)
        self.save_services()
        self.audit.add("Added staff", member.staff_id)
        return True, f"Added {member.name} ({member.staff_id}) to {sector}."

    def update_staff(self, staff_id, name, sector):
        member = self.staff_by_id.get(staff_id.strip().upper())
        name = name.strip()
        if member is None:
            return False, "Staff member not found."
        if not name or sector not in self.sectors:
            return False, "Enter a staff name and a valid service sector."
        if not member.available and sector != member.sector:
            return False, "A busy staff member cannot be moved to another sector."
        member.name = name
        member.sector = sector
        self.save_services()
        self.audit.add("Updated staff", member.staff_id)
        return True, f"Updated staff member {member.staff_id}."

    def remove_staff(self, staff_id):
        staff_id = staff_id.strip().upper()
        member = self.staff_by_id.get(staff_id)
        if member is None:
            return False, "Staff member not found."
        if not member.available:
            return False, "Complete the assigned service before removing this staff member."
        self.staff.remove(member)
        self.staff_by_id.remove(staff_id)
        self.save_services()
        self.audit.add("Removed staff", staff_id)
        return True, f"Removed staff member {staff_id}."

    def assign_next_customer(self, sector, staff_id=None):
        sector = sector.strip().title()
        queue = self.waiting_by_sector.get(sector)
        if queue is None or queue.is_empty():
            return False, f"No waiting customer in {sector}."

        staff_member = None
        if staff_id:
            candidate = self.staff_by_id.get(staff_id.strip().upper())
            if candidate and candidate.sector == sector and candidate.available:
                staff_member = candidate
        else:
            available = self.find_available_staff(sector)
            if available:
                staff_member = available[0]

        if staff_member is None:
            return False, f"No available staff for {sector}."

        ticket = queue.dequeue()
        ticket.status = "Active"
        ticket.staff_id = staff_member.staff_id
        staff_member.available = False
        self.active_stack.push(ticket)
        self.active_tickets.append(ticket)
        self.audit.add("Assigned customer", ticket.ticket_id)
        self.save_services()
        return True, (
            f"{ticket.ticket_id} for {ticket.customer_name} assigned to "
            f"{staff_member.name} ({staff_member.staff_id})."
        )

    def complete_service(self, ticket_id):
        ticket = self.ticket_by_id.get(ticket_id.strip().upper())
        if ticket is None:
            return False, "Ticket not found."
        if ticket.status != "Active":
            return False, "Only active tickets can be completed."

        staff_member = self.staff_by_id.get(ticket.staff_id)
        if staff_member:
            staff_member.available = True
        ticket.status = "Finished"
        ticket.completed_at = datetime.now().astimezone().isoformat(
            timespec="seconds"
        )
        self.active_tickets.remove(ticket)
        self.active_stack = Stack()
        for active_ticket in self.active_tickets:
            self.active_stack.push(active_ticket)
        self.finished_stack.push(ticket)
        self.service_history.append(ticket)
        self.audit.add("Completed customer service", ticket.ticket_id)
        self.save_services()
        return True, f"{ticket.ticket_id} completed for {ticket.customer_name}."

    def delete_finished_ticket(self, ticket_id):
        ticket = self.ticket_by_id.get(ticket_id.strip().upper())
        if ticket is None:
            return False, "Ticket not found."
        if ticket.status != "Finished":
            return False, "Only finished tickets can be deleted from service history."

        self.tickets.remove(ticket)
        self.ticket_by_id.remove(ticket.ticket_id.upper())
        self.finished_stack.items = [
            item for item in self.finished_stack.items if item is not ticket
        ]
        self.service_history = LinkedList()
        for item in self.finished_stack.items:
            self.service_history.append(item)
        self.audit.add("Deleted service ticket", ticket.ticket_id)
        self.save_services()
        return True, f"{ticket.ticket_id} deleted from service history."

    def active_customers(self):
        return list(self.active_tickets)

    def finished_services(self):
        return self.finished_stack.to_list()

    def list_waiting_queue(self):
        result = []
        for sector in sorted(self.sectors):
            result.extend(self.waiting_by_sector[sector].to_list())
        return result

    def add_restock_order(self, sku):
        product = self.by_sku.get(sku.strip().upper())
        if not product:
            return False, "Product not found."
        self.orders.enqueue(sku.strip().upper())
        self.audit.add("Queued restock", sku.strip().upper())
        return True, "Restock request added to the queue."

    def process_restock_order(self):
        sku = self.orders.dequeue()
        if sku is None:
            return False, "Restock queue is empty."
        product = self.by_sku.get(sku)
        if product:
            product.quantity += 10
            product.update_status()
            self.rebuild_indexes()
            self.save()
            self.audit.add("Processed restock", sku)
            return True, f"Restock processed for {sku}. New quantity: {product.quantity}"
        return False, f"Cannot process missing SKU {sku}."
