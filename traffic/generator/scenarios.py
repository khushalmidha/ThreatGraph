import uuid
import time
import random
from datetime import datetime, timezone

def generate_base_event(src_ip, dst_ip, src_port, dst_port, protocol, vlan, direction, bytes_cnt, duration, timestamp=None):
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": timestamp or datetime.utcnow().isoformat(),
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "src_port": src_port,
        "dst_port": dst_port,
        "protocol": protocol,
        "packets": max(1, bytes_cnt // 1500),
        "bytes": bytes_cnt,
        "duration_ms": duration,
        "vlan": vlan,
        "direction": direction,
        "event_version": "1.0"
    }

class ScenarioGenerator:
    def __init__(self, network, seed=42):
        self.network = network
        self.rng = random.Random(seed)

    def generate_normal_traffic(self, count=1):
        events = []
        for _ in range(count):
            src = self.network.get_random_host("workstation")
            dst = self.network.get_random_host("app_server")
            if not src or not dst: continue
            events.append(generate_base_event(
                src.ip, dst.ip, self.rng.randint(1024, 65535), 443, "TCP", src.vlan, "INTERNAL", 
                self.rng.randint(500, 5000), self.rng.uniform(10, 100)
            ))
        return events

    def generate_horizontal_scanning(self, attacker_ip, target_subnet_ips, port=445):
        events = []
        for target_ip in target_subnet_ips:
            events.append(generate_base_event(
                attacker_ip, target_ip, self.rng.randint(1024, 65535), port, "TCP", 10, "INTERNAL", 
                60, 1.5
            ))
        return events
        
    def generate_vertical_scanning(self, attacker_ip, target_ip, ports):
        events = []
        for port in ports:
            events.append(generate_base_event(
                attacker_ip, target_ip, self.rng.randint(1024, 65535), port, "TCP", 10, "INTERNAL", 
                60, 1.0
            ))
        return events
        
    def generate_lateral_movement(self, source_ip, path_ips):
        events = []
        curr = source_ip
        for nxt in path_ips:
            events.append(generate_base_event(
                curr, nxt, self.rng.randint(1024, 65535), 3389, "TCP", 10, "INTERNAL", 
                1500, 500.0
            ))
            curr = nxt
        return events

    def generate_beaconing(self, infected_ip, c2_ip, interval_s, count):
        events = []
        base_time = time.time()
        for i in range(count):
            ts = datetime.fromtimestamp(base_time + i * interval_s, tz=timezone.utc).isoformat()
            events.append(generate_base_event(
                infected_ip, c2_ip, self.rng.randint(1024, 65535), 443, "TCP", 10, "OUTBOUND", 
                120, 5.0, timestamp=ts
            ))
        return events

    def generate_ransomware(self, infected_ip, fileserver_ip):
        events = []
        for _ in range(50):
            events.append(generate_base_event(
                infected_ip, fileserver_ip, self.rng.randint(1024, 65535), 445, "TCP", 10, "INTERNAL", 
                self.rng.randint(10000, 50000), self.rng.uniform(50, 200)
            ))
        return events

    def generate_abnormal_data_movement(self, internal_ip, external_ip):
        events = []
        events.append(generate_base_event(
            internal_ip, external_ip, self.rng.randint(1024, 65535), 443, "TCP", 10, "OUTBOUND", 
            1024 * 1024 * 500, 
            self.rng.uniform(5000, 20000)
        ))
        return events
