# UML Diagram

```mermaid
classDiagram
    class HelpdeskWindow {
        +refresh_all()
        +add_customer()
        +assign_next()
        +complete_service()
        +manage_inventory()
        +manage_staff()
    }

    class InventorySystem {
        -products: ArrayList
        -waiting_by_sector: Queue
        -active_stack: Stack
        -service_history: LinkedList
        -by_sku: HashTable
        -price_tree: BinarySearchTree
        +join_waitlist()
        +assign_next_customer()
        +complete_service()
        +delete_finished_ticket()
        +add_staff()
        +add/update/delete product()
    }

    class Product {
        +sku: str
        +name: str
        +category: str
        +quantity: int
        +price: float
        +restock_status: str
        +update_status()
    }

    class InventoryStorage {
        +load()
        +save()
    }

    class HelpdeskStorage {
        +load()
        +save()
    }

    class ArrayList
    class LinkedList
    class Stack
    class Queue
    class BinarySearchTree
    class HashTable
    class AuditLog

    HelpdeskWindow --> InventorySystem
    InventorySystem --> Product
    InventorySystem --> InventoryStorage
    InventorySystem --> HelpdeskStorage
    InventorySystem --> ArrayList
    InventorySystem --> LinkedList
    InventorySystem --> Stack
    InventorySystem --> Queue
    InventorySystem --> BinarySearchTree
    InventorySystem --> HashTable
    InventorySystem --> AuditLog
