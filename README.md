# Computer Store Helpdesk

A desktop application for a computer-parts store. It routes customers to service
sectors, tracks staff and service progress, and manages the retail parts inventory.
The interface uses Python's built-in Tkinter toolkit; the core structures and
algorithms remain visible in the source for the DASTAL project.

## What users can do

- Register customers for Assembly, Retail, Hardware Repair, Software Repair, or
  General Service.
- See each sector's FIFO waitlist and assign its next customer to available staff.
- Track active service, complete a ticket, and review completed-service history.
- Permanently delete completed tickets from service history.
- Add, edit, and remove staff; view availability and each staff member's active ticket.
- Add, edit, delete, and search PC parts; queue and process restocks.
- Keep inventory and helpdesk tickets when the application is closed and reopened.

## Run from Python

Python 3.10 or later with Tkinter is recommended. Tkinter is included in most
standard Python installations.

```bash
python main.py
```

The desktop application opens by default. To use the older terminal menu:

```bash
python main.py --cli
```

## Build the Windows executable

Build the `.exe` on Windows (PyInstaller does not cross-compile Windows programs
from Linux or macOS):

1. Install Python 3 and ensure the Python Launcher (`py`) is available.
2. From the project folder, run `build_windows.bat`.
3. Find the application at
   `dist\ComputerStoreHelpdesk\ComputerStoreHelpdesk.exe`.
4. Copy the complete `ComputerStoreHelpdesk` folder when distributing the
   one-folder build; do not copy only the `.exe`.

The build script installs PyInstaller from `requirements-build.txt`. The app uses
Tkinter and the Python standard library at runtime and does not require an internet
connection.

## How the code works

1. `main.py` starts the graphical interface by default and retains the terminal
   interface behind `--cli`.
2. `gui.py` builds the Dashboard, Waitlist, Staff, PC Parts, and Service History
   screens. Button actions call the application methods and refresh the relevant
   tables.
3. `app.py` contains `InventorySystem`, which applies the business rules. It assigns
   the oldest waiting ticket to available staff from the same sector, marks that
   staff member busy, and releases them when the ticket is completed.
4. `data_structures.py` contains the course structures used by the app: ArrayList
   for collections, Queue for sector waitlists and restocks, Stack for service and
   undo history, LinkedList for service history, HashTable for SKU/ticket/staff
   lookup, and BinarySearchTree for price indexing.
5. `algorithms.py` supplies linear search, binary search, merge sort, and recursive
   divide-and-conquer nearest-price search for inventory operations.
6. `inventory.py` defines Product, ServiceTicket, and Staff records and JSON/audit
   storage helpers.

## Data location

Application data is stored per user rather than beside the executable:

- Windows: `%APPDATA%\ComputerStoreHelpdesk`
- macOS: `~/Library/Application Support/ComputerStoreHelpdesk`
- Linux: `$XDG_DATA_HOME/ComputerStoreHelpdesk`, or `~/.local/share/ComputerStoreHelpdesk`

The folder contains `inventory.json`, `services.json`, and `audit.log`. Back up this
folder to preserve business data. This prototype stores data locally; it does not
provide multi-user synchronization, authentication, role permissions, or encrypted
records, so it should not be treated as a shared production helpdesk without those
operational controls.

## Tests

```bash
python -m unittest -v test_app.py
```

The tests cover inventory CRUD and validation, DSA operations, waitlist assignment,
service completion and history deletion, CLI numeric-input validation, staff roster
rules, and restoring active/waiting/finished tickets after restart.
