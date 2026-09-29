from typing import List, Dict, Any

class SimulatedFirewall:
    def __init__(self):
        # Default policies mapping host -> state (ACTIVE/ISOLATED)
        self.host_states = {
            "10.0.1.10": {
                "state": "ISOLATED",
                "reason": "Automated Lateral Movement Containment (Patient Zero)",
                "policy": "DENY_ALL"
            },
            "10.0.2.5": {
                "state": "ISOLATED",
                "reason": "Analyst Containment: Compromised Jumpbox Bastion",
                "policy": "DENY_ALL"
            }
        }
        # Multi-tier enterprise micro-segmentation zones
        self.zones = {
            "DMZ_PERIMETER": ["10.0.0.30", "10.0.0.31", "10.0.0.32", "10.0.0.33"],
            "IDENTITY_CORE": ["10.0.0.10", "10.0.0.11", "10.0.0.12", "10.0.0.13", "10.0.0.14"],
            "APP_SERVICES":  ["10.0.2.5", "10.0.2.6", "10.0.2.7", "10.0.2.8", "10.0.2.9", "10.0.2.15", "10.0.2.16"],
            "CROWN_JEWELS":  ["10.0.3.20", "10.0.3.21", "10.0.3.22", "10.0.3.23", "10.0.3.24"],
            "WORKSTATIONS":  ["10.0.1.10", "10.0.1.11", "10.0.1.12", "10.0.1.13", "10.0.1.14", "10.0.1.15", "10.0.1.16", "10.0.1.17", "10.0.1.18", "10.0.1.19", "10.0.1.20"]
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
