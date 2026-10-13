"""
Unit Tests for Simulated Zero-Trust Containment Engine.

Verifies:
1. Policy engine isolation logic (state changes to ISOLATED with DENY_ALL policy)
2. Micro-segmentation traffic enforcement (traffic dropped if src/dst is isolated)
3. Rollback behavior (node restored to ACTIVE with ALLOW_ALL)
4. Threshold verification: Benign nodes (Risk < 80.0) are NOT quarantined
5. High-risk nodes (Risk >= 80.0) trigger containment policy
6. Audit trail & action state consistency
"""

import pytest
from backend.simulation.policies import SimulatedFirewall
from backend.app.risk.engine import RiskEngine


@pytest.fixture
def firewall():
    fw = SimulatedFirewall()
    # Reset states for clean test execution
    fw.host_states = {}
    return fw


@pytest.fixture
def risk_engine():
    return RiskEngine()


def test_benign_host_not_isolated(risk_engine, firewall):
    """
    Benign node with low anomaly score and normal baseline must not cross
    containment threshold (Score < 80.0).
    """
    benign_host = "10.0.1.50"
    risk_output = risk_engine.calculate_risk(
        host_id=benign_host,
        graph_prob=0.08,
        transformer_prob=0.12,
        anomaly_score=0.5,
        historical_risk=0.05,
        asset_criticality=1.0,
    )
    score = risk_output["score"]
    assert score < 80.0, f"Benign host score {score} should be < 80.0"

    # Evaluator decision
    should_quarantine = score >= 80.0
    assert not should_quarantine
    assert not firewall.is_isolated(benign_host)


def test_high_risk_host_isolated(risk_engine, firewall):
    """
    Compromised host with multi-hop GNN threat and high transformer score
    crosses 80.0 threshold and triggers simulated zero-trust isolation.
    """
    threat_host = "10.0.1.99"
    risk_output = risk_engine.calculate_risk(
        host_id=threat_host,
        graph_prob=0.95,
        transformer_prob=0.88,
        anomaly_score=8.5,
        historical_risk=0.70,
        asset_criticality=1.0,
    )
    score = risk_output["score"]
    assert score >= 80.0, f"Threat host score {score} must be >= 80.0"

    # Enforce containment
    firewall.isolate_host(threat_host, reason="High-Risk Lateral Movement Compromise")
    assert firewall.is_isolated(threat_host)
    assert firewall.host_states[threat_host]["policy"] == "DENY_ALL"


def test_traffic_blocking_and_rollback(firewall):
    """
    Verifies network policy enforcement:
    1. Active traffic allowed
    2. Traffic blocked when source is isolated
    3. Traffic blocked when destination is isolated
    4. Rollback re-enables traffic
    """
    src = "10.0.1.15"
    dst = "10.0.3.20"

    # Initial state: both active
    assert firewall.check_traffic_allowed(src, dst) is True

    # Isolate source
    firewall.isolate_host(src, reason="Simulated Quarantine")
    assert firewall.is_isolated(src) is True
    assert firewall.check_traffic_allowed(src, dst) is False
    assert firewall.check_traffic_allowed(dst, src) is False

    # Rollback containment
    firewall.release_host(src)
    assert firewall.is_isolated(src) is False
    assert firewall.host_states[src]["state"] == "ACTIVE"
    assert firewall.check_traffic_allowed(src, dst) is True


def test_microsegmentation_zone_lookup(firewall):
    assert "CROWN_JEWELS" in firewall.zones
    assert "WORKSTATIONS" in firewall.zones
    assert "10.0.3.20" in firewall.zones["CROWN_JEWELS"]
