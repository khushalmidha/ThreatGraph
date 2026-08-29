from collections import deque
import math
import hashlib

class MonotonicDeque:
    """O(1) amortized sliding window maximum"""
    def __init__(self):
        self.dq = deque()

    def add(self, val, timestamp):
        while self.dq and self.dq[-1][0] < val:
            self.dq.pop()
        self.dq.append((val, timestamp))

    def remove_older_than(self, timestamp):
        while self.dq and self.dq[0][1] <= timestamp:
            self.dq.popleft()

    def get_max(self):
        return self.dq[0][0] if self.dq else 0

class FenwickTree:
    """O(log n) prefix sums. Used here conceptually for time-bucketed counts."""
    def __init__(self, size):
        self.tree = [0] * (size + 1)
        self.size = size

    def add(self, i, delta):
        i += 1
        while i <= self.size:
            self.tree[i] += delta
            i += i & (-i)

    def query(self, i):
        s = 0
        i += 1
        while i > 0:
            s += self.tree[i]
            i -= i & (-i)
        return s

    def range_query(self, left, right):
        if left > right: return 0
        return self.query(right) - self.query(left - 1)

class CountMinSketch:
    """Probabilistic data structure for frequency of events"""
    def __init__(self, width=1000, depth=5):
        self.width = width
        self.depth = depth
        self.table = [[0] * width for _ in range(depth)]
        
    def add(self, item, count=1):
        for i in range(self.depth):
            hash_val = int(hashlib.md5(f"{item}{i}".encode()).hexdigest(), 16)
            self.table[i][hash_val % self.width] += count
            
    def estimate(self, item):
        min_est = float('inf')
        for i in range(self.depth):
            hash_val = int(hashlib.md5(f"{item}{i}".encode()).hexdigest(), 16)
            min_est = min(min_est, self.table[i][hash_val % self.width])
        return min_est
