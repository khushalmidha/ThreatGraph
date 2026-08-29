from collections import deque
import math
from typing import Dict, List, Any
from .algorithms import MonotonicDeque, CountMinSketch
from .config import WINDOWS

class HostFeatureState:
    def __init__(self, host_ip: str):
        self.host_ip = host_ip
        
        # Keep raw events within the max window (300s)
        self.events_window = deque()
        
        # O(1) structures
        self.burst_deque = MonotonicDeque()
        self.destination_sketch = CountMinSketch(width=1000, depth=5)
        self.port_sketch = CountMinSketch(width=1000, depth=5)
        
    def add_event(self, event: Dict[str, Any], timestamp_s: float):
        self.events_window.append((timestamp_s, event))
        self.burst_deque.add(event.get('bytes', 0), timestamp_s)
        self.destination_sketch.add(event.get('dst_ip'))
        self.port_sketch.add(event.get('dst_port'))
        
        # Cleanup older than 5m
        max_win = WINDOWS["5m"]
        while self.events_window and self.events_window[0][0] <= timestamp_s - max_win:
            self.events_window.popleft()
        self.burst_deque.remove_older_than(timestamp_s - max_win)

    def extract_features(self, current_time_s: float) -> Dict[str, Any]:
        features = {}
        for win_name, win_sec in WINDOWS.items():
            win_events = [e for ts, e in self.events_window if ts > current_time_s - win_sec]
            
            traffic_volume = sum(e.get('bytes', 0) for e in win_events)
            packet_count = sum(e.get('packets', 0) for e in win_events)
            flow_count = len(win_events)
            
            # Use exact counts for smaller windows
            unique_dsts = len(set(e.get('dst_ip') for e in win_events))
            unique_ports = len(set(e.get('dst_port') for e in win_events))
            
            internal = sum(1 for e in win_events if e.get('direction') == 'INTERNAL')
            outbound = sum(1 for e in win_events if e.get('direction') == 'OUTBOUND')
            
            features[f"{win_name}_bytes"] = traffic_volume
            features[f"{win_name}_packets"] = packet_count
            features[f"{win_name}_flows"] = flow_count
            features[f"{win_name}_unique_dsts"] = unique_dsts
            features[f"{win_name}_unique_ports"] = unique_ports
            
            features[f"{win_name}_byte_rate"] = traffic_volume / win_sec if win_sec > 0 else 0
            
            if flow_count > 0:
                features[f"{win_name}_internal_ratio"] = internal / flow_count
                features[f"{win_name}_outbound_ratio"] = outbound / flow_count
            else:
                features[f"{win_name}_internal_ratio"] = 0.0
                features[f"{win_name}_outbound_ratio"] = 0.0

        features["current_burst_max"] = self.burst_deque.get_max()
        return features
