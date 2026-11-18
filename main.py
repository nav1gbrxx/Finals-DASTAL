import math
import sys

from app import InventorySystem


def input_text(prompt, allow_blank=False):
    while True:
        value = input(prompt).strip()
        if value or allow_blank:
            return value
        print("Input cannot be empty.")


def input_int(prompt, minimum=0):
    while True:
        try:
            value = int(input(prompt).strip())
            if value < minimum:
                raise ValueError
            return value
        except ValueError:
            print(f"Enter a whole number greater than or equal to {minimum}.")


def input_float(prompt, minimum=0):
    while True:
        try:
            value = float(input(prompt).strip())
            if not math.isfinite(value) or value < minimum:
                raise ValueError
            return value
        except ValueError:
            print(f"Enter a finite number greater than or equal to {minimum}.")


def input_optional_int(prompt, minimum=0):
    while True:
        text = input(prompt).strip()
        if not text:
            return None
        try:
            value = int(text)
            if value < minimum:
                raise ValueError
            return value
        except ValueError:
            print(
                f"Enter a whole number greater than or equal to {minimum}, "
                "or leave blank."
            )


def input_optional_float(prompt, minimum=0):
    while True:
        text = input(prompt).strip()
        if not text:
            return None
        try:
            value = float(text)
            if not math.isfinite(value) or value < minimum:
                raise ValueError
            return value
        except ValueError:
            print(
                f"Enter a finite number greater than or equal to {minimum}, "
                "or leave blank."
            )


def print_product(product):
    if not product:
        print("No product found.")
        return
    print(
        f"{product.sku} | {product.name} | {product.category} | "
        f"Qty: {product.quantity} | Price: P{product.price:.2f} | {product.restock_status}"
    )


def print_products(products):
    if not products:
        print("No products to display.")
        return
    for product in products:
        print_product(product)


def menu():
    print("\n=== NAV1GATE ===")
    print("1. Join customer waitlist")
    print("2. View waiting customers")
    print("3. Assign next customer to a sector")
    print("4. View active customers")
    print("5. Complete customer service")
    print("6. View finished services")
    print("7. View staff")
    print("8. View service history")
    print("9. Add PC part")
    print("10. View PC part by SKU")
    print("11. Update PC part")
    print("12. Delete PC part")
    print("13. List PC parts")
    print("14. Search parts by name/category")
    print("15. Search part by SKU")
    print("16. Sort parts by name")
    print("17. Sort parts by price")
    print("18. Find nearest price")
    print("19. Add restock request")
    print("20. Process restock request")
    print("21. Undo last create/update/delete action")
    print("22. Load sample inventory")
    print("23. Delete finished service ticket")
    print("0. Exit")


def load_sample_data(system):
    sample = [
        ("SKU-100", "Mechanical Keyboard", "Accessories", 12, 2499.00),
        ("SKU-101", "Wireless Mouse", "Accessories", 4, 899.00),
        ("SKU-102", "USB-C Hub", "Accessories", 8, 1299.00),
        ("SKU-103", "27-inch Monitor", "Displays", 3, 8999.00),
        ("SKU-104", "Webcam", "Accessories", 15, 1699.00),
    ]
    added = 0
    for row in sample:
        success, _ = system.create(*row)
        if success:
            added += 1
    print(f"Loaded {added} sample product(s).")


def print_ticket(ticket):
    if not ticket:
        print("No ticket found.")
        return
    staff = f" | Staff: {ticket.staff_id}" if ticket.staff_id else ""
    print(
        f"{ticket.ticket_id} | {ticket.customer_name} | {ticket.sector} | "
        f"{ticket.status}{staff} | {ticket.description}"
    )


def print_sector_menu():
    print("1. Assembly")
    print("2. Retail")
    print("3. Hardware Repair")
    print("4. Software Repair")
    print("5. General Service")


def choose_sector():
    print_sector_menu()
    return {
        "1": "Assembly",
        "2": "Retail",
        "3": "Hardware Repair",
        "4": "Software Repair",
        "5": "General Service",
    }.get(input_text("Choose sector: "), "")


def main():
    system = InventorySystem()
    while True:
        menu()
        choice = input_text("Choose an option: ")
        if choice == "0":
            print("Goodbye!")
            break
        if choice == "1":
            name = input_text("Customer name: ")
            sector = choose_sector()
            if not sector:
                print("Invalid sector.")
                continue
            description = input_text("Service needed: ")
            print(system.join_waitlist(name, sector, description)[1])
        elif choice == "2":
            sector = choose_sector()
            if sector:
                tickets = system.waiting_tickets(sector)
                print(f"\nWaiting in {sector}:")
                print([ticket.ticket_id for ticket in tickets] or "No customers waiting")
        elif choice == "3":
            sector = choose_sector()
            if sector:
                print(system.assign_next_customer(sector)[1])
        elif choice == "4":
            print("Active customers:")
            for ticket in system.active_customers():
                print_ticket(ticket)
        elif choice == "5":
            print(system.complete_service(input_text("Ticket ID: ").upper())[1])
        elif choice == "6":
            print("Finished services:")
            for ticket in system.finished_services():
                print_ticket(ticket)
        elif choice == "7":
            print("Staff:")
            for member in system.staff:
                status = "Available" if member.available else "Busy"
                print(f"{member.staff_id} | {member.name} | {member.sector} | {status}")
        elif choice == "8":
            print("Service history:")
            for ticket in system.service_history.to_list():
                print_ticket(ticket)
        elif choice == "9":
            sku = input_text("SKU: ")
            name = input_text("Name: ")
            category = input_text("Category: ")
            quantity = input_int("Quantity: ")
            price = input_float("Price: ")
            print(system.create(sku, name, category, quantity, price)[1])
        elif choice == "10":
            print_product(system.read(input_text("SKU: ")))
        elif choice == "11":
            sku = input_text("SKU: ")
            product = system.read(sku)
            if not product:
                print("Product not found.")
                continue
            print_product(product)
            name = input_text("New name (blank to keep): ", allow_blank=True)
            category = input_text("New category (blank to keep): ", allow_blank=True)
            quantity = input_optional_int("New quantity (blank to keep): ")
            price = input_optional_float("New price (blank to keep): ")
            _, message = system.update(
                sku,
                name if name else None,
                category if category else None,
                quantity,
                price,
            )
            print(message)
        elif choice == "12":
            print(system.delete(input_text("SKU: "))[1])
        elif choice == "13":
            print_products(list(system.products))
        elif choice == "14":
            _, product = system.linear_search_name(input_text("Name or category: "))
            print_product(product)
        elif choice == "15":
            index, product = system.binary_search_sku(input_text("SKU: "))
            print_product(product)
            if index == -1:
                print("Binary search completed: SKU not found.")
        elif choice == "16":
            print_products(system.list_sorted_by_name())
        elif choice == "17":
            print_products(system.list_sorted_by_price())
        elif choice == "18":
            target = input_float("Target price: ")
            print_product(system.find_nearest_price(target))
        elif choice == "19":
            print(system.add_restock_order(input_text("SKU: "))[1])
        elif choice == "20":
            print(system.process_restock_order()[1])
        elif choice == "21":
            _, message = system.undo_last_action()
            print(message)
        elif choice == "22":
            load_sample_data(system)
        elif choice == "23":
            ticket_id = input_text("Finished ticket ID: ").upper()
            if input_text("Permanently delete this ticket? (y/N): ").lower() == "y":
                print(system.delete_finished_ticket(ticket_id)[1])
            else:
                print("Ticket deletion cancelled.")
        else:
            print("Invalid menu option.")


if __name__ == "__main__":
    if "--cli" in sys.argv:
        main()
    else:
        from gui import main as gui_main

        gui_main()
