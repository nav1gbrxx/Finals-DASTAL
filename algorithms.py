def linear_search(items, predicate):
    for index, item in enumerate(items):
        if predicate(item):
            return index, item
    return -1, None


def binary_search(items, target_key, key=lambda item: item):
    low = 0
    high = len(items) - 1
    while low <= high:
        middle = (low + high) // 2
        middle_key = key(items[middle])
        if middle_key == target_key:
            return middle, items[middle]
        if target_key < middle_key:
            high = middle - 1
        else:
            low = middle + 1
    return -1, None


def merge_sort(items, key=lambda item: item):
    if len(items) <= 1:
        return list(items)
    middle = len(items) // 2
    left = merge_sort(items[:middle], key)
    right = merge_sort(items[middle:], key)
    return _merge(left, right, key)


def _merge(left, right, key):
    merged = []
    left_index = 0
    right_index = 0
    while left_index < len(left) and right_index < len(right):
        if key(left[left_index]) <= key(right[right_index]):
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1
    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return merged


def nearest_by_divide_and_conquer(items, target, key=lambda item: item):
    if not items:
        return None
    sorted_items = merge_sort(items, key)
    return _nearest_recursive(sorted_items, target, key, 0, len(sorted_items) - 1)


def _nearest_recursive(items, target, key, low, high):
    if low > high:
        return None
    middle = (low + high) // 2
    item = items[middle]
    item_key = key(item)
    if item_key == target:
        return item
    if target < item_key:
        candidate = _nearest_recursive(items, target, key, low, middle - 1)
    else:
        candidate = _nearest_recursive(items, target, key, middle + 1, high)
    if candidate is None:
        return item
    if abs(key(candidate) - target) < abs(item_key - target):
        return candidate
    return item
