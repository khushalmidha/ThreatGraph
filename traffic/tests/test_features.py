import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from traffic.feature_extractor.algorithms import MonotonicDeque, FenwickTree, CountMinSketch
from traffic.feature_extractor.extractor import HostFeatureState
from traffic.generator.scenarios import generate_base_event

def test_monotonic_deque():
    md = MonotonicDeque()
    md.add(100, 1.0)
    md.add(200, 2.0)
    assert md.get_max() == 200
    md.add(50, 3.0)
    assert md.get_max() == 200
    md.remove_older_than(2.5)
    assert md.get_max() == 50

def test_fenwick_tree():
    ft = FenwickTree(10)
    ft.add(0, 5)
    ft.add(2, 10)
    assert ft.query(0) == 5
    assert ft.query(2) == 15
    assert ft.range_query(1, 2) == 10

def test_feature_extraction_shape():
    state = HostFeatureState("10.0.0.1")
    event1 = generate_base_event("10.0.0.1", "10.0.0.2", 12345, 80, "TCP", 10, "INTERNAL", 1000, 10.0)
    state.add_event(event1, 100.0)
    
    event2 = generate_base_event("10.0.0.1", "10.0.0.3", 12345, 443, "TCP", 10, "INTERNAL", 2000, 10.0)
    state.add_event(event2, 105.0)
    
    features = state.extract_features(110.0)
    assert features["10s_bytes"] == 2000 # Only event2 is within 10s of 110.0 (event1 was at 100.0)
    assert features["30s_bytes"] == 3000
    assert features["current_burst_max"] == 2000
