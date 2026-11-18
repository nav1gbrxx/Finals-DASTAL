# Test Report

## Test environment

- Language: Python 3
- Test runner: Python `unittest`
- Persistence: temporary-directory JSON file
- Command: `python3 -m unittest -v test_app.py`

## Tested cases

| ID | Scenario | Expected result | Status |
|---|---|---|---|
| TC-01 | Create a product | Product is added and persisted | Pass |
| TC-02 | Read a product by SKU | Correct product is returned | Pass |
| TC-03 | Update quantity | Quantity and restock status change | Pass |
| TC-04 | Reload saved inventory | Saved values remain available | Pass |
| TC-05 | Delete a product | Product is removed and persistence updated | Pass |
| TC-06 | Linked List operations | Nodes remain in insertion order | Pass |
| TC-07 | Stack LIFO behavior | Last pushed value is popped first | Pass |
| TC-08 | Queue FIFO behavior | First enqueued value is dequeued first | Pass |
| TC-09 | BST search and inorder traversal | Key and sorted traversal are correct | Pass |
| TC-10 | Hash Table put/get/remove | SKU lookup and removal work | Pass |
| TC-11 | Linear search | Matching item is found | Pass |
| TC-12 | Merge sort | Items are sorted by selected key | Pass |
| TC-13 | Binary search | Target is located in sorted data | Pass |
| TC-14 | Divide-and-conquer nearest search | Closest price is returned | Pass |
| TC-15 | Create/update/delete undo | Previous state is restored or the created record is removed | Pass |
| TC-16 | Helpdesk waitlist | Customer enters the selected sector queue | Pass |
| TC-17 | Helpdesk assignment | Available sector staff becomes busy and ticket becomes active | Pass |
| TC-18 | Helpdesk completion | Ticket becomes finished and staff becomes available | Pass |
| TC-19 | Helpdesk persistence | Waiting, active, finished tickets and staff state survive restart | Pass |
| TC-20 | Staff roster | Staff changes persist and busy staff cannot be removed | Pass |
| TC-21 | Service-history deletion | Finished ticket is removed from history and persistence | Pass |
| TC-22 | Ticket deletion guard | Waiting and active tickets cannot be deleted | Pass |
| TC-23 | CLI update validation | Invalid, negative, and non-finite numeric input is rejected | Pass |
| TC-24 | Active stack consistency | Completed tickets are removed from the active stack | Pass |

## Conclusion

The automated tests cover data structures, algorithms, inventory validation, ticket
lifecycle and deletion, staff roster rules, and persistence. Launch `python main.py`
separately to demonstrate the graphical interface.
