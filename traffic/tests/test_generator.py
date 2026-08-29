import sys
import os
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from traffic.generator.network import EnterpriseNetwork
from traffic.generator.scenarios import ScenarioGenerator
from backend.app.schemas.event import NetworkEvent

def test_deterministic_generation():
    net1 = EnterpriseNetwork(num_hosts=100, seed=123)
    sg1 = ScenarioGenerator(net1, seed=123)
    ev1 = sg1.generate_normal_traffic(count=50)
    
    net2 = EnterpriseNetwork(num_hosts=100, seed=123)
    sg2 = ScenarioGenerator(net2, seed=123)
    ev2 = sg2.generate_normal_traffic(count=50)
    
    assert len(ev1) == len(ev2)
    for i in range(len(ev1)):
        assert ev1[i]['src_ip'] == ev2[i]['src_ip']
        assert ev1[i]['dst_ip'] == ev2[i]['dst_ip']
        assert ev1[i]['bytes'] == ev2[i]['bytes']

def test_event_schema_validation():
    net = EnterpriseNetwork(num_hosts=50, seed=42)
    sg = ScenarioGenerator(net, seed=42)
    events = sg.generate_normal_traffic(count=5)
    
    for ev in events:
        validated = NetworkEvent(**ev)
        assert validated.event_id == ev['event_id']

def test_scenario_isolation():
    net = EnterpriseNetwork(num_hosts=50, seed=42)
    sg = ScenarioGenerator(net, seed=42)
    
    attacker = net.get_random_host("workstation")
    targets = [h.ip for h in net.hosts if h.role == "app_server"]
    
    events = sg.generate_horizontal_scanning(attacker.ip, targets, port=80)
    assert len(events) == len(targets)
    assert all(e['src_ip'] == attacker.ip for e in events)
    assert all(e['dst_port'] == 80 for e in events)
