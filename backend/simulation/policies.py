from typing import List, Dict, Any

class SimulatedFirewall:
    def __init__(self):
        # Default policies mapping host -> state (ACTIVE/ISOLATED)
        self.host_states = {
            "10.0.0.1": {
                "state": "ISOLATED",
                "reason": "Automated Lateral Movement Containment",
                "policy": "DENY_ALL"
            }
        }
        # Simple zone mapping simulation
        self.zones = {
            "USER": ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4"],
            "SERVER": ["10.0.0.5", "10.0.0.10", "10.0.0.11"],
            "DATABASE": ["10.0.0.20"]
        }
        
    def isolate_host(self, host_id: str, reason: str = "Automated Containment"):
        self.host_states[host_id] = {
            "state": "ISOLATED",
            "reason": reason,
            "policy": "DENY_ALL"
        }
        
    def release_host(self, host_id: str):
        if host_id in self.host_states:
            self.host_states[host_id]["state"] = "ACTIVE"
            self.host_states[host_id]["policy"] = "ALLOW_ALL"
            
    def is_isolated(self, host_id: str) -> bool:
        return self.host_states.get(host_id, {}).get("state") == "ISOLATED"
        
    def check_traffic_allowed(self, src_ip: str, dst_ip: str) -> bool:
        if self.is_isolated(src_ip) or self.is_isolated(dst_ip):
            return False
        return True

# Singleton for the simulation
firewall = SimulatedFirewall()
