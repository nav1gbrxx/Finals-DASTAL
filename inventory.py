from dataclasses import dataclass, asdict
from datetime import datetime
import json
from pathlib import Path


@dataclass
class Product:
    sku: str
    name: str
    category: str
    quantity: int
    price: float
    restock_status: str = "Available"

    def update_status(self):
        self.restock_status = "Restock needed" if self.quantity <= 5 else "Available"


class InventoryStorage:
    def __init__(self, path="inventory.json"):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as file:
            return [Product(**row) for row in json.load(file)]

    def save(self, products):
        with self.path.open("w", encoding="utf-8") as file:
            json.dump([asdict(product) for product in products], file, indent=2)


class AuditLog:
    def __init__(self, path="audit.log"):
        self.path = Path(path)

    def add(self, action, sku):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.path.open("a", encoding="utf-8") as file:
            file.write(f"[{timestamp}] {action}: {sku}\n")


@dataclass
class Staff:
    staff_id: str
    name: str
    sector: str
    available: bool = True


@dataclass
class ServiceTicket:
    ticket_id: str
    customer_name: str
    sector: str
    description: str
    status: str = "Waiting"
    staff_id: str = ""
    created_at: str = ""
    completed_at: str = ""


class HelpdeskStorage:
    def __init__(self, path="services.json"):
        self.path = Path(path)

    def load(self):
        if not self.path.exists():
            return {"tickets": [], "staff": None, "next_ticket_number": 1001}
        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return {
            "tickets": [ServiceTicket(**row) for row in data.get("tickets", [])],
            "staff": (
                [Staff(**row) for row in data["staff"]] if "staff" in data else None
            ),
            "next_ticket_number": data.get("next_ticket_number", 1001),
        }

    def save(self, tickets, next_ticket_number, staff):
        data = {
            "tickets": [asdict(ticket) for ticket in tickets],
            "staff": [asdict(member) for member in staff],
            "next_ticket_number": next_ticket_number,
        }
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
