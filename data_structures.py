from collections import deque


class ArrayList:
    def __init__(self):
        self.items = []

    def append(self, item):
        self.items.append(item)

    def remove(self, item):
        self.items.remove(item)

    def find(self, predicate):
        return [item for item in self.items if predicate(item)]

    def clear(self):
        self.items.clear()

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)


class LinkedNode:
    def __init__(self, value):
        self.value = value
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, value):
        node = LinkedNode(value)
        if not self.head:
            self.head = node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = node

    def to_list(self):
        values = []
        current = self.head
        while current:
            values.append(current.value)
            current = current.next
        return values

    def find(self, predicate):
        matches = []
        current = self.head
        while current:
            if predicate(current.value):
                matches.append(current.value)
            current = current.next
        return matches


class Stack:
    def __init__(self):
        self.items = []

    def push(self, value):
        self.items.append(value)

    def pop(self):
        if self.is_empty():
            return None
        return self.items.pop()

    def peek(self):
        return None if self.is_empty() else self.items[-1]

    def is_empty(self):
        return len(self.items) == 0

    def to_list(self):
        return list(reversed(self.items))


class Queue:
    def __init__(self):
        self.items = deque()

    def enqueue(self, value):
        self.items.append(value)

    def dequeue(self):
        if self.is_empty():
            return None
        return self.items.popleft()

    def peek(self):
        return None if self.is_empty() else self.items[0]

    def is_empty(self):
        return len(self.items) == 0

    def to_list(self):
        return list(self.items)


class BSTNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, key, value):
        if self.root is None:
            self.root = BSTNode(key, value)
        else:
            self._insert(self.root, key, value)

    def _insert(self, node, key, value):
        if key < node.key:
            if node.left is None:
                node.left = BSTNode(key, value)
            else:
                self._insert(node.left, key, value)
        elif key > node.key:
            if node.right is None:
                node.right = BSTNode(key, value)
            else:
                self._insert(node.right, key, value)
        else:
            node.value = value

    def search(self, key):
        node = self.root
        while node:
            if key == node.key:
                return node.value
            node = node.left if key < node.key else node.right
        return None

    def inorder(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.value)
            self._inorder(node.right, result)


class HashTable:
    def __init__(self, size=37):
        self.size = size
        self.buckets = [[] for _ in range(size)]

    def _index(self, key):
        return sum(ord(character) for character in str(key).upper()) % self.size

    def put(self, key, value):
        bucket = self.buckets[self._index(key)]
        for index, (existing_key, _) in enumerate(bucket):
            if existing_key == key:
                bucket[index] = (key, value)
                return
        bucket.append((key, value))

    def get(self, key):
        for existing_key, value in self.buckets[self._index(key)]:
            if existing_key == key:
                return value
        return None

    def remove(self, key):
        bucket = self.buckets[self._index(key)]
        for index, (existing_key, _) in enumerate(bucket):
            if existing_key == key:
                bucket.pop(index)
                return True
        return False
