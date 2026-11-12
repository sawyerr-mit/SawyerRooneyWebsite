"""
IndexMinPQ.py

Indexed min priority queue (binary heap). Items are integers 0..n-1, each with a
float key. Supports push, pop-min, contains and update (decrease OR increase key)
in O(log n).
"""


class IndexMinPQ:

    def __init__(self, n: int):
        self.n = n
        self._heap = []                 # heap position : item index
        self._pos = [-1] * n            # item index : heap position (-1 = absent)
        self._key = [None] * n          # item index : key

    def isEmpty(self) -> bool:
        return not self._heap

    def size(self) -> int:
        return len(self._heap)

    def __len__(self):
        return len(self._heap)

    def contains(self, i: int) -> bool:
        self._check(i)
        return self._pos[i] != -1

    def push(self, i: int, key: float):
        self._check(i)
        if self._pos[i] != -1:
            raise ValueError(f'index {i} is already in the queue')
        self._key[i] = key
        self._pos[i] = len(self._heap)
        self._heap.append(i)
        self._swim(self._pos[i])

    def pop(self) -> tuple[int, float]:
        """Remove and return (index, key) with the smallest key."""
        if not self._heap:
            raise IndexError('pop from empty IndexMinPQ')
        top = self._heap[0]
        key = self._key[top]
        last = self._heap.pop()
        self._pos[top] = -1
        self._key[top] = None
        if self._heap:
            self._heap[0] = last
            self._pos[last] = 0
            self._sink(0)
        return top, key

    def peek(self) -> tuple[int, float]:
        top = self._heap[0]
        return top, self._key[top]

    def update(self, i: int, key: float):
        self._check(i)
        if self._pos[i] == -1:
            raise KeyError(f'index {i} is not in the queue')
        self._key[i] = key
        self._swim(self._pos[i])
        self._sink(self._pos[i])

    def keyOf(self, i: int) -> float:
        return self._key[i]

    # ---- internals ------------------------------------------------------
    def _check(self, i: int):
        if not 0 <= i < self.n:
            raise IndexError(f'index {i} out of range 0..{self.n - 1}')

    def _less(self, a: int, b: int) -> bool:
        return self._key[self._heap[a]] < self._key[self._heap[b]]

    def _swap(self, a: int, b: int):
        h = self._heap
        h[a], h[b] = h[b], h[a]
        self._pos[h[a]] = a
        self._pos[h[b]] = b

    def _swim(self, k: int):
        while k > 0:
            parent = (k - 1) // 2
            if self._less(k, parent):
                self._swap(k, parent)
                k = parent
            else:
                break

    def _sink(self, k: int):
        n = len(self._heap)
        while True:
            child = 2 * k + 1
            if child >= n:
                break
            if child + 1 < n and self._less(child + 1, child):
                child += 1
            if self._less(child, k):
                self._swap(k, child)
                k = child
            else:
                break
