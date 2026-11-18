import os
import math
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from algorithms import merge_sort
from app import InventorySystem


APP_NAME = "Computer Store Helpdesk"
SECTORS = (
    "Assembly",
    "Retail",
    "Hardware Repair",
    "Software Repair",
    "General Service",
)


def get_data_directory():
    if sys.platform == "win32":
        app_data = os.environ.get("APPDATA")
        root = Path(app_data) if app_data else Path.home() / "AppData" / "Roaming"
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        xdg_data = os.environ.get("XDG_DATA_HOME")
        root = Path(xdg_data) if xdg_data else Path.home() / ".local" / "share"
    directory = root / APP_NAME.replace(" ", "")
    directory.mkdir(parents=True, exist_ok=True)
    return directory


class HelpdeskWindow:
    def __init__(self, root, system):
        self.root = root
        self.system = system
        self.root.title(f"{APP_NAME} | Service and Inventory")
        self.root.geometry("1220x780")
        self.root.minsize(1000, 650)
        self._configure_style()
        self._build_layout()
        self.refresh_all()

    def _configure_style(self):
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TFrame", background="#f3f6fa")
        style.configure("TLabel", background="#f3f6fa", foreground="#172b4d")
        style.configure(
            "Title.TLabel",
            font=("Segoe UI", 20, "bold"),
            background="#12304a",
            foreground="white",
        )
        style.configure(
            "Subtitle.TLabel",
            font=("Segoe UI", 10),
            background="#12304a",
            foreground="#d6e4f0",
        )
        style.configure("Header.TFrame", background="#12304a")
        style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1)
        style.configure("CardTitle.TLabel", background="white", foreground="#52677d")
        style.configure(
            "CardValue.TLabel",
            background="white",
            foreground="#12304a",
            font=("Segoe UI", 22, "bold"),
        )
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TNotebook.Tab", padding=(14, 8), font=("Segoe UI", 10))

    def _build_layout(self):
        header = ttk.Frame(self.root, style="Header.TFrame", padding=(22, 16))
        header.pack(fill="x")
        ttk.Label(header, text=APP_NAME, style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Customer Routing, Staff Workload, Service History, and PC-parts Stock",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=(14, 8))
        self.dashboard_tab = ttk.Frame(self.notebook, padding=12)
        self.waitlist_tab = ttk.Frame(self.notebook, padding=12)
        self.staff_tab = ttk.Frame(self.notebook, padding=12)
        self.inventory_tab = ttk.Frame(self.notebook, padding=12)
        self.history_tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.waitlist_tab, text="Waitlist")
        self.notebook.add(self.staff_tab, text="Staff")
        self.notebook.add(self.inventory_tab, text="PC Parts")
        self.notebook.add(self.history_tab, text="Service History")
        self._build_dashboard()
        self._build_waitlist()
        self._build_staff()
        self._build_inventory()
        self._build_history()
        self.status = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status, anchor="w", padding=(16, 8)).pack(
            fill="x"
        )

    def _tree(self, parent, columns, headings, widths=None):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)
        tree = ttk.Treeview(frame, columns=columns, show="headings", selectmode="browse")
        for index, (column, heading) in enumerate(zip(columns, headings)):
            tree.heading(column, text=heading)
            tree.column(
                column,
                width=widths[index] if widths else 130,
                anchor="w",
                stretch=True,
            )
        vertical = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        horizontal = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
        tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        return tree

    def _build_dashboard(self):
        cards = ttk.Frame(self.dashboard_tab)
        cards.pack(fill="x", pady=(0, 12))
        self.metrics = {}
        for title, key in (
            ("Waiting", "waiting"),
            ("In service", "active"),
            ("Completed", "finished"),
            ("PC parts", "parts"),
        ):
            card = ttk.Frame(cards, style="Card.TFrame", padding=(16, 12))
            card.pack(side="left", fill="x", expand=True, padx=(0, 10))
            ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
            value = ttk.Label(card, text="0", style="CardValue.TLabel")
            value.pack(anchor="w", pady=(3, 0))
            self.metrics[key] = value

        body = ttk.Panedwindow(self.dashboard_tab, orient="horizontal")
        body.pack(fill="both", expand=True)
        queue_frame = ttk.Labelframe(body, text="Queues by service sector", padding=10)
        active_frame = ttk.Labelframe(body, text="Customers currently in service", padding=10)
        body.add(queue_frame, weight=1)
        body.add(active_frame, weight=2)
        self.dashboard_queues = self._tree(
            queue_frame,
            ("sector", "waiting", "available"),
            ("Sector", "Waiting", "Staff available"),
            (180, 90, 120),
        )
        ttk.Button(
            queue_frame,
            text="Assign next in selected sector",
            style="Primary.TButton",
            command=self.assign_dashboard_selection,
        ).pack(anchor="e", pady=(8, 0))
        self.dashboard_active = self._tree(
            active_frame,
            ("ticket", "customer", "sector", "staff", "request"),
            ("Ticket", "Customer", "Sector", "Staff", "Service needed"),
            (95, 140, 135, 95, 220),
        )
        ttk.Button(
            active_frame,
            text="Complete selected service",
            command=self.complete_dashboard_selection,
        ).pack(anchor="e", pady=(8, 0))

    def _build_waitlist(self):
        form = ttk.Labelframe(self.waitlist_tab, text="Register a customer", padding=12)
        form.pack(fill="x", pady=(0, 12))
        ttk.Label(form, text="Customer name").grid(row=0, column=0, sticky="w")
        self.customer_name = ttk.Entry(form, width=25)
        self.customer_name.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(4, 8))
        ttk.Label(form, text="Service sector").grid(row=0, column=1, sticky="w")
        self.customer_sector = ttk.Combobox(
            form, values=SECTORS, state="readonly", width=22
        )
        self.customer_sector.current(0)
        self.customer_sector.grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=(4, 8))
        ttk.Label(form, text="What does the customer need?").grid(
            row=0, column=2, sticky="w"
        )
        self.customer_request = ttk.Entry(form)
        self.customer_request.grid(row=1, column=2, sticky="ew", padx=(0, 12), pady=(4, 8))
        ttk.Button(
            form,
            text="Add to waitlist",
            style="Primary.TButton",
            command=self.add_customer,
        ).grid(row=1, column=3, sticky="ew", pady=(4, 8))
        form.columnconfigure(2, weight=1)

        filters = ttk.Frame(self.waitlist_tab)
        filters.pack(fill="x", pady=(0, 8))
        ttk.Label(filters, text="Show sector:").pack(side="left")
        self.waitlist_filter = ttk.Combobox(
            filters, values=("All sectors", *SECTORS), state="readonly", width=22
        )
        self.waitlist_filter.current(0)
        self.waitlist_filter.pack(side="left", padx=8)
        self.waitlist_filter.bind("<<ComboboxSelected>>", lambda _event: self.refresh_waitlist())
        self.waitlist_tree = self._tree(
            self.waitlist_tab,
            ("ticket", "customer", "sector", "since", "request"),
            ("Ticket", "Customer", "Sector", "Waiting since", "Service needed"),
            (95, 150, 145, 190, 300),
        )
        buttons = ttk.Frame(self.waitlist_tab)
        buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(
            buttons,
            text="Assign next for selected sector",
            style="Primary.TButton",
            command=self.assign_waitlist_selection,
        ).pack(side="left")
        ttk.Label(
            buttons,
            text="Assignment always calls the earliest waiting ticket in that sector.",
        ).pack(side="left", padx=12)

    def _build_staff(self):
        ttk.Label(
            self.staff_tab,
            text="Manage the store roster. Availability updates automatically during service.",
        ).pack(anchor="w", pady=(0, 10))
        self.staff_tree = self._tree(
            self.staff_tab,
            ("id", "name", "sector", "status", "current_ticket"),
            ("Staff ID", "Name", "Service sector", "Availability", "Active ticket"),
            (120, 180, 210, 150, 140),
        )
        buttons = ttk.Frame(self.staff_tab)
        buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(buttons, text="Add staff", command=self.add_staff).pack(side="left")
        ttk.Button(buttons, text="Edit selected", command=self.edit_staff).pack(
            side="left", padx=6
        )
        ttk.Button(buttons, text="Remove selected", command=self.remove_staff).pack(
            side="left"
        )

    def _build_inventory(self):
        searchbar = ttk.Frame(self.inventory_tab)
        searchbar.pack(fill="x", pady=(0, 7))
        ttk.Label(searchbar, text="Search mode:").pack(side="left")
        self.inventory_search_mode = ttk.Combobox(
            searchbar,
            values=("Name / category / SKU", "Exact SKU (binary search)"),
            state="readonly",
            width=25,
        )
        self.inventory_search_mode.current(0)
        self.inventory_search_mode.pack(side="left", padx=(7, 12))
        self.inventory_search_mode.bind(
            "<<ComboboxSelected>>", lambda _event: self.refresh_inventory()
        )
        ttk.Label(searchbar, text="Search:").pack(side="left")
        self.inventory_search = ttk.Entry(searchbar, width=32)
        self.inventory_search.pack(side="left", padx=(8, 12))
        self.inventory_search.bind("<KeyRelease>", lambda _event: self.refresh_inventory())
        ttk.Label(searchbar, text="Target price:").pack(side="left")
        self.target_price = ttk.Entry(searchbar, width=12)
        self.target_price.pack(side="left", padx=(7, 4))
        ttk.Button(
            searchbar, text="Find nearest", command=self.find_nearest_product
        ).pack(side="left")
        toolbar = ttk.Frame(self.inventory_tab)
        toolbar.pack(fill="x", pady=(0, 10))
        ttk.Button(toolbar, text="Add part", command=self.add_product).pack(side="left", padx=3)
        ttk.Button(toolbar, text="Edit selected", command=self.edit_product).pack(
            side="left", padx=3
        )
        ttk.Button(toolbar, text="Delete selected", command=self.delete_product).pack(
            side="left", padx=3
        )
        ttk.Button(toolbar, text="Queue restock", command=self.queue_restock).pack(
            side="left", padx=3
        )
        ttk.Button(toolbar, text="Receive +10 units", command=self.process_restock).pack(
            side="left", padx=3
        )
        self.inventory_tree = self._tree(
            self.inventory_tab,
            ("sku", "name", "category", "quantity", "price", "status"),
            ("SKU", "Part", "Category", "Quantity", "Price", "Stock status"),
            (120, 220, 150, 95, 120, 140),
        )
        self.inventory_tree.heading(
            "name", text="Part (click to sort)", command=lambda: self.sort_inventory("name")
        )
        self.inventory_tree.heading(
            "price", text="Price (click to sort)", command=lambda: self.sort_inventory("price")
        )
        self.inventory_tree.tag_configure("low", foreground="#a53030")
        self.inventory_sort_key = "name"

    def _build_history(self):
        ttk.Label(
            self.history_tab,
            text="Completed customer services, newest first.",
        ).pack(anchor="w", pady=(0, 10))
        self.history_tree = self._tree(
            self.history_tab,
            ("ticket", "customer", "sector", "staff", "completed", "request"),
            ("Ticket", "Customer", "Sector", "Staff", "Completed at", "Service needed"),
            (100, 145, 145, 100, 190, 300),
        )
        ttk.Button(
            self.history_tab,
            text="Delete selected ticket",
            command=self.delete_history_ticket,
        ).pack(anchor="e", pady=(8, 0))

    def _set_status(self, message):
        self.status.set(message)

    def refresh_all(self):
        self.refresh_dashboard()
        self.refresh_waitlist()
        self.refresh_staff()
        self.refresh_inventory()
        self.refresh_history()

    def _replace_rows(self, tree, rows):
        children = tree.get_children()
        if children:
            tree.delete(*children)
        for item_id, values, tags in rows:
            tree.insert("", "end", iid=item_id, values=values, tags=tags)

    def refresh_dashboard(self):
        self.metrics["waiting"].configure(text=str(self.system.waiting_count()))
        self.metrics["active"].configure(text=str(len(self.system.active_tickets)))
        self.metrics["finished"].configure(text=str(len(self.system.service_history.to_list())))
        self.metrics["parts"].configure(text=str(len(self.system.products)))
        queue_rows = []
        for sector in sorted(self.system.sectors):
            available = len(self.system.find_available_staff(sector))
            queue_rows.append(
                (sector, (sector, self.system.waiting_count(sector), available), ())
            )
        self._replace_rows(self.dashboard_queues, queue_rows)
        active_rows = []
        for ticket in self.system.active_customers():
            member = self.system.staff_by_id.get(ticket.staff_id)
            active_rows.append(
                (
                    ticket.ticket_id,
                    (
                        ticket.ticket_id,
                        ticket.customer_name,
                        ticket.sector,
                        member.name if member else ticket.staff_id,
                        ticket.description,
                    ),
                    (),
                )
            )
        self._replace_rows(self.dashboard_active, active_rows)

    def refresh_waitlist(self):
        selected_sector = self.waitlist_filter.get() if hasattr(self, "waitlist_filter") else "All sectors"
        tickets = []
        sectors = [selected_sector] if selected_sector in self.system.sectors else sorted(self.system.sectors)
        for sector in sectors:
            tickets.extend(self.system.waiting_tickets(sector))
        rows = [
            (
                ticket.ticket_id,
                (
                    ticket.ticket_id,
                    ticket.customer_name,
                    ticket.sector,
                    ticket.created_at.replace("T", " ") if ticket.created_at else "",
                    ticket.description,
                ),
                (),
            )
            for ticket in tickets
        ]
        self._replace_rows(self.waitlist_tree, rows)

    def refresh_staff(self):
        active_by_staff = {
            ticket.staff_id: ticket.ticket_id for ticket in self.system.active_customers()
        }
        rows = []
        for member in self.system.staff:
            rows.append(
                (
                    member.staff_id,
                    (
                        member.staff_id,
                        member.name,
                        member.sector,
                        "Available" if member.available else "Busy",
                        active_by_staff.get(member.staff_id, ""),
                    ),
                    (),
                )
            )
        self._replace_rows(self.staff_tree, rows)

    def _selected_staff(self):
        selected = self.staff_tree.selection()
        if not selected:
            messagebox.showinfo("Select a staff member", "Select a staff member first.")
            return None
        return self.system.staff_by_id.get(selected[0])

    def add_staff(self):
        self._staff_dialog()

    def edit_staff(self):
        member = self._selected_staff()
        if member:
            self._staff_dialog(member)

    def _staff_dialog(self, member=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit staff member" if member else "Add staff member")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        form = ttk.Frame(dialog, padding=18)
        form.pack(fill="both", expand=True)
        ttk.Label(form, text="Staff name").grid(row=0, column=0, sticky="w", pady=5)
        name_entry = ttk.Entry(form, width=32)
        name_entry.insert(0, member.name if member else "")
        name_entry.grid(row=0, column=1, padx=(12, 0), pady=5)
        ttk.Label(form, text="Service sector").grid(row=1, column=0, sticky="w", pady=5)
        sector = ttk.Combobox(form, values=SECTORS, state="readonly", width=29)
        sector.set(member.sector if member else SECTORS[0])
        sector.grid(row=1, column=1, padx=(12, 0), pady=5)

        def save_staff():
            if member:
                success, message = self.system.update_staff(
                    member.staff_id, name_entry.get(), sector.get()
                )
            else:
                success, message = self.system.add_staff(name_entry.get(), sector.get())
            if not success:
                messagebox.showerror("Could not save staff member", message, parent=dialog)
                return
            dialog.destroy()
            self._set_status(message)
            self.refresh_all()

        actions = ttk.Frame(form)
        actions.grid(row=2, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(actions, text="Cancel", command=dialog.destroy).pack(
            side="right", padx=(8, 0)
        )
        ttk.Button(actions, text="Save", style="Primary.TButton", command=save_staff).pack(
            side="right"
        )
        dialog.bind("<Return>", lambda _event: save_staff())
        dialog.bind("<Escape>", lambda _event: dialog.destroy())

    def remove_staff(self):
        member = self._selected_staff()
        if not member:
            return
        if messagebox.askyesno(
            "Remove staff member",
            f"Remove {member.name} ({member.staff_id}) from the roster?",
            parent=self.root,
        ):
            success, message = self.system.remove_staff(member.staff_id)
            if success:
                self._set_status(message)
                self.refresh_all()
            else:
                messagebox.showerror("Could not remove staff member", message)

    def refresh_inventory(self):
        if not hasattr(self, "inventory_tree"):
            return
        query = self.inventory_search.get().strip().casefold()
        if (
            query
            and self.inventory_search_mode.get() == "Exact SKU (binary search)"
        ):
            _, product = self.system.binary_search_sku(query.upper())
            products = [product] if product else []
        else:
            products = list(self.system.products)
        if query and self.inventory_search_mode.get() != "Exact SKU (binary search)":
            products = [
                product
                for product in products
                if query in product.sku.casefold()
                or query in product.name.casefold()
                or query in product.category.casefold()
            ]
        if self.inventory_sort_key == "price":
            products = merge_sort(products, key=lambda product: product.price)
        else:
            products = merge_sort(products, key=lambda product: product.name.casefold())
        rows = []
        for product in products:
            rows.append(
                (
                    product.sku,
                    (
                        product.sku,
                        product.name,
                        product.category,
                        product.quantity,
                        f"P {product.price:,.2f}",
                        product.restock_status,
                    ),
                    ("low",) if product.quantity <= 5 else (),
                )
            )
        self._replace_rows(self.inventory_tree, rows)

    def sort_inventory(self, key):
        self.inventory_sort_key = key
        self.refresh_inventory()

    def find_nearest_product(self):
        value = self.target_price.get().strip()
        try:
            target = float(value)
        except ValueError:
            messagebox.showwarning("Invalid price", "Enter a numeric target price.")
            return
        if not math.isfinite(target) or target < 0:
            messagebox.showwarning(
                "Invalid price", "Target price must be finite and cannot be negative."
            )
            return
        product = self.system.find_nearest_price(target)
        if not product:
            messagebox.showinfo("No inventory", "Add PC parts before searching prices.")
            return
        self.inventory_search.delete(0, "end")
        self.inventory_search_mode.current(0)
        self.refresh_inventory()
        self.inventory_tree.selection_set(product.sku)
        self.inventory_tree.focus(product.sku)
        self.inventory_tree.see(product.sku)
        self._set_status(
            f"Nearest price to P {target:,.2f}: {product.name} at P {product.price:,.2f}."
        )

    def refresh_history(self):
        rows = []
        for ticket in reversed(self.system.service_history.to_list()):
            member = self.system.staff_by_id.get(ticket.staff_id)
            rows.append(
                (
                    ticket.ticket_id,
                    (
                        ticket.ticket_id,
                        ticket.customer_name,
                        ticket.sector,
                        member.name if member else ticket.staff_id,
                        ticket.completed_at.replace("T", " ") if ticket.completed_at else "",
                        ticket.description,
                    ),
                    (),
                )
            )
        self._replace_rows(self.history_tree, rows)

    def delete_history_ticket(self):
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showinfo("Select a ticket", "Select a service-history ticket first.")
            return
        ticket_id = selected[0]
        if not messagebox.askyesno(
            "Delete service ticket",
            f"Permanently delete {ticket_id} from service history?",
            parent=self.root,
        ):
            return
        success, message = self.system.delete_finished_ticket(ticket_id)
        if success:
            self._set_status(message)
            self.refresh_all()
        else:
            messagebox.showerror("Could not delete ticket", message)

    def add_customer(self):
        name = self.customer_name.get().strip()
        request = self.customer_request.get().strip()
        sector = self.customer_sector.get()
        if not name or not request:
            messagebox.showwarning("Missing information", "Enter the customer name and service needed.")
            return
        success, message = self.system.join_waitlist(name, sector, request)
        if not success:
            messagebox.showerror("Could not add customer", message)
            return
        self.customer_name.delete(0, "end")
        self.customer_request.delete(0, "end")
        self.customer_name.focus_set()
        self._set_status(message)
        self.refresh_all()

    def _selected_sector(self, tree):
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Select a sector", "Select a service sector first.")
            return None
        values = tree.item(selected[0], "values")
        return values[0] if tree is self.dashboard_queues else values[2]

    def assign_dashboard_selection(self):
        sector = self._selected_sector(self.dashboard_queues)
        if sector:
            self._assign_next(sector)

    def assign_waitlist_selection(self):
        sector = self._selected_sector(self.waitlist_tree)
        if sector:
            self._assign_next(sector)

    def _assign_next(self, sector):
        success, message = self.system.assign_next_customer(sector)
        if success:
            self._set_status(message)
            self.refresh_all()
        else:
            messagebox.showinfo("Assignment unavailable", message)

    def complete_dashboard_selection(self):
        selected = self.dashboard_active.selection()
        if not selected:
            messagebox.showinfo("Select a customer", "Select an active service first.")
            return
        self._complete_ticket(selected[0])

    def _complete_ticket(self, ticket_id):
        success, message = self.system.complete_service(ticket_id)
        if success:
            self._set_status(message)
            self.refresh_all()
        else:
            messagebox.showerror("Could not complete service", message)

    def _selected_product(self):
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showinfo("Select a part", "Select a PC part first.")
            return None
        return self.system.by_sku.get(selected[0])

    def add_product(self):
        self._product_dialog()

    def edit_product(self):
        product = self._selected_product()
        if product:
            self._product_dialog(product)

    def _product_dialog(self, product=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit PC part" if product else "Add PC part")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        form = ttk.Frame(dialog, padding=18)
        form.pack(fill="both", expand=True)
        fields = (
            ("SKU", product.sku if product else ""),
            ("Part name", product.name if product else ""),
            ("Category", product.category if product else ""),
            ("Quantity", str(product.quantity) if product else "0"),
            ("Price", str(product.price) if product else "0.00"),
        )
        entries = {}
        for row, (label, initial) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=5)
            entry = ttk.Entry(form, width=34)
            entry.insert(0, initial)
            entry.grid(row=row, column=1, sticky="ew", padx=(12, 0), pady=5)
            entries[label] = entry
        if product:
            entries["SKU"].configure(state="disabled")

        def save_product():
            sku = product.sku if product else entries["SKU"].get().strip()
            name = entries["Part name"].get().strip()
            category = entries["Category"].get().strip()
            try:
                quantity = int(entries["Quantity"].get())
                price = float(entries["Price"].get())
            except ValueError:
                messagebox.showerror("Invalid number", "Quantity must be a whole number and price must be numeric.", parent=dialog)
                return
            if not sku or not name or not category or quantity < 0 or price < 0:
                messagebox.showwarning(
                    "Check the details",
                    "Complete all fields. Quantity and price must be zero or greater.",
                    parent=dialog,
                )
                return
            if product:
                success, message = self.system.update(
                    sku, name=name, category=category, quantity=quantity, price=price
                )
            else:
                success, message = self.system.create(sku, name, category, quantity, price)
            if not success:
                messagebox.showerror("Could not save part", message, parent=dialog)
                return
            dialog.destroy()
            self._set_status(message)
            self.refresh_all()

        actions = ttk.Frame(form)
        actions.grid(row=len(fields), column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(actions, text="Cancel", command=dialog.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(actions, text="Save", style="Primary.TButton", command=save_product).pack(
            side="right"
        )
        dialog.bind("<Return>", lambda _event: save_product())
        dialog.bind("<Escape>", lambda _event: dialog.destroy())

    def delete_product(self):
        product = self._selected_product()
        if not product:
            return
        if messagebox.askyesno(
            "Delete PC part",
            f"Delete {product.name} ({product.sku}) from inventory?",
            parent=self.root,
        ):
            success, message = self.system.delete(product.sku)
            if success:
                self._set_status(message)
                self.refresh_all()
            else:
                messagebox.showerror("Could not delete part", message)

    def queue_restock(self):
        product = self._selected_product()
        if not product:
            return
        success, message = self.system.add_restock_order(product.sku)
        if success:
            self._set_status(message)
            messagebox.showinfo(
                "Restock queued",
                f"{product.sku} is in the restock queue. Process the queue when stock arrives.",
            )
        else:
            messagebox.showerror("Could not queue restock", message)

    def process_restock(self):
        success, message = self.system.process_restock_order()
        if success:
            self._set_status(message)
            self.refresh_all()
        else:
            messagebox.showinfo("Restock queue", message)


def main():
    data_directory = get_data_directory()
    system = InventorySystem(
        storage_path=data_directory / "inventory.json",
        service_path=data_directory / "services.json",
        audit_path=data_directory / "audit.log",
    )
    root = tk.Tk()
    HelpdeskWindow(root, system)
    root.mainloop()


if __name__ == "__main__":
    main()
