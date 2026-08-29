import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from collections import deque
from traffic.feature_extractor.algorithms import MonotonicDeque

def test_sliding_window_benchmark():
    # Generate 10000 events
    events = [i for i in range(10000)]
    
    # Naive max over sliding window of size 1000
    start_naive = time.perf_counter()
    window = deque()
    naive_maxes = []
    for val in events:
        window.append(val)
        if len(window) > 1000:
            window.popleft()
        naive_maxes.append(max(window))
    end_naive = time.perf_counter()
    naive_duration = end_naive - start_naive
    
    # Monotonic Deque max over sliding window
    start_opt = time.perf_counter()
    md = MonotonicDeque()
    opt_maxes = []
    for val in events:
        md.add(val, val) # Use val as timestamp
        md.remove_older_than(val - 1000)
        opt_maxes.append(md.get_max())
    end_opt = time.perf_counter()
    opt_duration = end_opt - start_opt
    
    assert naive_maxes == opt_maxes
    print(f"\nNaive sliding max: {naive_duration:.6f}s")
    print(f"Monotonic Deque sliding max: {opt_duration:.6f}s")
    
    # Opt should be significantly faster for larger windows.
    # At N=10000, W=1000, naive does O(N*W) ~ 10M ops. Opt does O(N) ~ 10K ops.
    assert opt_duration < naive_duration
