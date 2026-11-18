# System Flowchart

```mermaid
flowchart TD
    A([Launch desktop app]) --> B[Load inventory, tickets, staff, and history]
    B --> C[Build indexes and sector queues]
    C --> D[Show Dashboard and tabs]
    D --> E{User action}
    E -->|Register customer| F[Validate customer and service sector]
    F --> G[Enqueue ticket in sector FIFO Queue]
    G --> H[Save ticket data]
    E -->|Assign next| I[Dequeue oldest eligible ticket]
    I --> J[Mark staff busy; add ticket to active Stack]
    J --> H
    E -->|Complete service| K[Mark ticket finished and free staff]
    K --> L[Add to finished Stack and Linked List history]
    L --> H
    E -->|Delete history ticket| Q[Confirm completed ticket]
    Q --> R[Remove from tickets, finished Stack, and Linked List]
    R --> H
    E -->|Manage parts| M[CRUD and search inventory]
    M --> N[Update list, Hash Table, BST, and JSON]
    E -->|Manage staff| O[Edit staff roster and persist]
    E -->|Close| P([End])
    H --> D
    N --> D
    O --> D
