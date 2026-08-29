import ipaddress
import random
from typing import List

class HostNode:
    def __init__(self, ip: str, role: str, vlan: int):
        self.ip = ip
        self.role = role
        self.vlan = vlan

class EnterpriseNetwork:
    def __init__(self, num_hosts=200, seed=42):
        self.rng = random.Random(seed)
        self.hosts: List[HostNode] = []
        self._generate_topology(num_hosts)
        
    def _generate_topology(self, num_hosts: int):
        roles = [
            ("workstation", 10, 0.7), 
            ("app_server", 20, 0.15),
            ("db_server", 30, 0.05),
            ("dns", 40, 0.02),
            ("auth", 50, 0.03),
            ("monitoring", 60, 0.05)
        ]
        base_ip = ipaddress.IPv4Address('10.0.0.0')
        for i in range(num_hosts):
            role, vlan = self._pick_role(roles)
            ip = str(base_ip + i + 1)
            self.hosts.append(HostNode(ip, role, vlan))
            
    def _pick_role(self, roles):
        val = self.rng.random()
        cumulative = 0.0
        for r, v, w in roles:
            cumulative += w
            if val <= cumulative:
                return r, v
        return roles[0][0], roles[0][1]
        
    def get_random_host(self, role=None):
        if role:
            candidates = [h for h in self.hosts if h.role == role]
            return self.rng.choice(candidates) if candidates else None
        return self.rng.choice(self.hosts)
