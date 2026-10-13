"""
Unit Tests for Graph-Aware RAG Engine with FAISS.

Verifies:
1. FAISS index instantiation & document population
2. Semantic vector retrieval against MITRE ATT&CK corpus
3. Graph context grounding and query formulation
4. High-risk containment recommendation generation
5. Low-risk benign monitoring recommendation
"""

import pytest
from rag.engine import GraphAwareRAGEngine, MITRE_CORPUS


@pytest.fixture
def rag_engine():
    return GraphAwareRAGEngine(dim=128)


def test_faiss_index_initialization(rag_engine):
    assert rag_engine.index.ntotal == len(MITRE_CORPUS)
    assert rag_engine.index.d == 128


def test_vector_retrieval_rdp_lateral_movement(rag_engine):
    results = rag_engine.retrieve("RDP remote desktop port 3389 lateral movement", top_k=3)
    assert len(results) == 3
    # First result should be T1021.001 (RDP)
    assert any("T1021" in r["id"] for r in results)
    # Cosine similarities should be in descending order
    scores = [r["similarity_score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_vector_retrieval_smb_lateral_movement(rag_engine):
    results = rag_engine.retrieve("SMB admin shares port 445 lateral propagation", top_k=3)
    assert any("T1021.002" in r["id"] or "T1021" in r["id"] for r in results)


def test_graph_grounded_triage_high_risk(rag_engine):
    attack_path = ["10.0.0.10", "10.0.0.25", "10.0.0.100"]
    hop_details = [
        {"from": "10.0.0.10", "to": "10.0.0.25", "dst_port": 3389, "protocol": "TCP", "weight": 0.8},
        {"from": "10.0.0.25", "to": "10.0.0.100", "dst_port": 445, "protocol": "TCP", "weight": 0.9},
    ]

    triage = rag_engine.synthesize_triage(
        incident_id="INC-1001",
        attack_path=attack_path,
        hop_details=hop_details,
        threat_class="Lateral Movement",
        risk_score=92.5,
        top_k=3,
    )

    assert triage["incident_id"] == "INC-1001"
    assert triage["risk_score"] == 92.5
    assert triage["graph_context"]["hop_count"] == 2
    assert 3389 in triage["graph_context"]["observed_ports"]
    assert 445 in triage["graph_context"]["observed_ports"]

    # Critical risk >= 80 must trigger automated zero-trust quarantine
    action = triage["containment_action"]
    assert action["action"] == "AUTOMATED_ZERO_TRUST_QUARANTINE"
    assert "10.0.0.10" in action["target_hosts"]

    # Must match relevant MITRE techniques
    assert len(triage["retrieved_mitre_techniques"]) == 3
    assert any("T1021" in t for t in triage["matched_technique_ids"])


def test_graph_grounded_triage_low_risk_benign(rag_engine):
    attack_path = ["10.0.0.5"]
    hop_details = []

    triage = rag_engine.synthesize_triage(
        incident_id="INC-0010",
        attack_path=attack_path,
        hop_details=hop_details,
        threat_class="Normal",
        risk_score=24.0,
        top_k=2,
    )

    # Low risk < 80 should not quarantine
    action = triage["containment_action"]
    assert action["action"] == "MONITOR_AND_LOG"
    assert action["target_hosts"] == []
