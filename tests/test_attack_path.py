"""
Unit Tests for Attack Path Reconstruction Engine.

Verifies:
1. Deterministic Attack Chain: Host A -> Host B -> Host C -> Critical Asset
2. Temporal causal ordering along multi-hop lateral movement
3. Disconnected graph handling
4. Cyclic graph robustness (preventing infinite loops)
5. Multiple competing paths (choosing optimal risk path)
6. Compromised root node (source == target)
7. Unreachable target handling
8. Multi-source blast radius calculation
9. Articulation points / critical chokepoints
"""

import pytest
import datetime
from backend.app.graph.attack_path import AttackPathBuilder


@pytest.fixture
def deterministic_attack_topology():
    """
    Deterministic linear infection chain:
    Host A (10.0.0.10)
      -> Host B (10.0.0.20) [t=10:00:00, risk=0.7]
      -> Host C (10.0.0.30) [t=10:05:00, risk=0.85]
      -> Critical Asset (10.0.0.100) [t=10:12:00, risk=0.95]
    """
    t0 = datetime.datetime(2026, 10, 12, 10, 0, 0)
    t1 = datetime.datetime(2026, 10, 12, 10, 5, 0)
    t2 = datetime.datetime(2026, 10, 12, 10, 12, 0)

    links = [
        {
            "source": "10.0.0.10",
            "target": "10.0.0.20",
            "weight": 0.70,
            "timestamp": t0.isoformat(),
            "protocol": "TCP",
            "dst_port": 3389,
        },
        {
            "source": "10.0.0.20",
            "target": "10.0.0.30",
            "weight": 0.85,
            "timestamp": t1.isoformat(),
            "protocol": "TCP",
            "dst_port": 445,
        },
        {
            "source": "10.0.0.30",
            "target": "10.0.0.100",
            "weight": 0.95,
            "timestamp": t2.isoformat(),
            "protocol": "TCP",
            "dst_port": 1433,
        },
    ]
    return {"links": links}


def test_deterministic_attack_chain(deterministic_attack_topology):
    builder = AttackPathBuilder()
    builder.build_from_topology(deterministic_attack_topology)

    result = builder.compute_temporal_attack_path("10.0.0.10", "10.0.0.100")
    assert result["success"] is True
    assert result["path"] == ["10.0.0.10", "10.0.0.20", "10.0.0.30", "10.0.0.100"]

    # Validate timestamps are monotonic
    hops = result["hops"]
    assert len(hops) == 3
    t_hops = [datetime.datetime.fromisoformat(h["timestamp"]) for h in hops]
    assert t_hops[0] <= t_hops[1] <= t_hops[2]

    # Validate ports & protocols along lateral movement
    assert hops[0]["dst_port"] == 3389
    assert hops[1]["dst_port"] == 445
    assert hops[2]["dst_port"] == 1433


def test_temporal_ordering_violation_rejection():
    """
    If edge B -> C happened BEFORE edge A -> B, strict causal ordering must
    reject that temporal sequence or report fallback.
    """
    t_late = datetime.datetime(2026, 10, 12, 12, 0, 0).isoformat()
    t_early = datetime.datetime(2026, 10, 12, 8, 0, 0).isoformat()

    topology = {
        "links": [
            {"source": "HostA", "target": "HostB", "weight": 0.8, "timestamp": t_late},
            {"source": "HostB", "target": "HostC", "weight": 0.9, "timestamp": t_early},
        ]
    }
    builder = AttackPathBuilder()
    builder.build_from_topology(topology)

    # In strict mode, causal traversal from A to C cannot use a backwards-in-time hop
    res = builder.compute_temporal_attack_path("HostA", "HostC", strict_order=True)
    # The result falls back or flags non-strict
    assert res["success"] is True  # fallback path available
    assert "Fallback" in res["reason"]


def test_disconnected_graph():
    topology = {
        "links": [
            {"source": "10.0.0.1", "target": "10.0.0.2", "weight": 0.8},
            {"source": "10.0.0.3", "target": "10.0.0.4", "weight": 0.9},
        ]
    }
    builder = AttackPathBuilder()
    builder.build_from_topology(topology)

    path = builder.compute_shortest_path("10.0.0.1", "10.0.0.4")
    assert path == []

    res = builder.compute_temporal_attack_path("10.0.0.1", "10.0.0.4")
    assert res["success"] is False
    assert res["path"] == []


def test_graph_with_cycles():
    """
    Graph with cycle: A -> B -> C -> A, and C -> D.
    Pathfinder must reach D without getting trapped in infinite loop.
    """
    topology = {
        "links": [
            {"source": "A", "target": "B", "weight": 0.8},
            {"source": "B", "target": "C", "weight": 0.8},
            {"source": "C", "target": "A", "weight": 0.8},
            {"source": "C", "target": "D", "weight": 0.95},
        ]
    }
    builder = AttackPathBuilder()
    builder.build_from_topology(topology)

    path = builder.compute_shortest_path("A", "D")
    assert path == ["A", "B", "C", "D"]

    res = builder.compute_temporal_attack_path("A", "D")
    assert res["success"] is True
    assert res["path"] == ["A", "B", "C", "D"]


def test_multiple_competing_paths():
    """
    Two paths from A to D:
    Path 1: A -> B -> D (low risk weights: 0.1, 0.1 -> high cost)
    Path 2: A -> C -> D (high risk weights: 0.9, 0.9 -> low cost)
    Dijkstra with inverted risk must select the high-risk Path 2.
    """
    topology = {
        "links": [
            {"source": "A", "target": "B", "weight": 0.1},
            {"source": "B", "target": "D", "weight": 0.1},
            {"source": "A", "target": "C", "weight": 0.9},
            {"source": "C", "target": "D", "weight": 0.9},
        ]
    }
    builder = AttackPathBuilder()
    builder.build_from_topology(topology)

    path = builder.compute_shortest_path("A", "D")
    assert path == ["A", "C", "D"]


def test_compromised_root_node_is_target():
    builder = AttackPathBuilder()
    builder.build_from_topology({"links": [{"source": "A", "target": "B", "weight": 0.5}]})

    path = builder.compute_shortest_path("A", "A")
    assert path == ["A"]

    res = builder.compute_temporal_attack_path("A", "A")
    assert res["success"] is True
    assert res["path"] == ["A"]


def test_unreachable_target():
    builder = AttackPathBuilder()
    builder.build_from_topology({"links": [{"source": "A", "target": "B", "weight": 0.5}]})

    # Target not in graph at all
    path = builder.compute_shortest_path("A", "GhostHost")
    assert path == []


def test_blast_radius_multi_source():
    topology = {
        "links": [
            {"source": "Attacker", "target": "Host1"},
            {"source": "Host1", "target": "Host2"},
            {"source": "Host2", "target": "Host3"},
            {"source": "IsolatedHost", "target": "HostX"},
        ]
    }
    builder = AttackPathBuilder()
    builder.build_from_topology(topology)

    blast = builder.compute_blast_radius(["Attacker"])
    assert blast == {"Attacker", "Host1", "Host2", "Host3"}
    assert "IsolatedHost" not in blast


def test_articulation_points():
    """
    Graph: (A - B) and (B - C), B is an articulation point.
    """
    topology = {
        "links": [
            {"source": "A", "target": "B"},
            {"source": "B", "target": "A"},
            {"source": "B", "target": "C"},
            {"source": "C", "target": "B"},
        ]
    }
    builder = AttackPathBuilder()
    builder.build_from_topology(topology)

    chokepoints = builder.find_articulation_points()
    assert "B" in chokepoints
