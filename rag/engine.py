"""
Graph-Aware RAG Engine for ThreatGraph.

Architecture:
1. Graph Context Ingestion:
   Extracts compromised path topology, protocol/port signatures, and anomaly scores from AttackPathBuilder.
2. Query Construction:
   Synthesizes graph entities and network flow characteristics into a semantic query.
3. Vector Retrieval (FAISS):
   Queries a curated MITRE ATT&CK Enterprise corpus indexed via faiss.IndexFlatIP (Cosine Similarity).
4. Evidence-Grounded Synthesis:
   Maps multi-hop attack paths to MITRE ATT&CK tactics, techniques, and SOC containment runbooks.
"""

import os
import re
import math
from typing import List, Dict, Any, Optional
import numpy as np
import faiss

# ==============================================================================
# Curated MITRE ATT&CK Enterprise & SOC Incident Response Knowledge Base
# Source: MITRE ATT&CK Enterprise Framework (Static Curated Corpus v14.1)
# ==============================================================================
MITRE_CORPUS: List[Dict[str, Any]] = [
    {
        "id": "T1059",
        "name": "Command and Scripting Interpreter",
        "tactic": "Execution",
        "content": "MITRE ATT&CK T1059: Command and Scripting Interpreter. Adversaries may abuse command and script interpreters (PowerShell, Bash, cmd, Python) to execute arbitrary commands, payloads, or interactive binaries across victim environments.",
        "tags": ["execution", "powershell", "bash", "cli", "scripting"],
    },
    {
        "id": "T1021.001",
        "name": "Remote Desktop Protocol (RDP)",
        "tactic": "Lateral Movement",
        "content": "MITRE ATT&CK T1021.001: Remote Services - Remote Desktop Protocol. Adversaries may log into an interactive desktop session over port 3389 using compromised credentials to move laterally across enterprise workstations and servers.",
        "tags": ["lateral_movement", "rdp", "port_3389", "remote_services", "credentials"],
    },
    {
        "id": "T1021.002",
        "name": "SMB/Windows Admin Shares",
        "tactic": "Lateral Movement",
        "content": "MITRE ATT&CK T1021.002: Remote Services - SMB/Windows Admin Shares. Adversaries may use Valid Accounts to interact with remote SMB shares over port 445 to transfer binaries, execute commands via RPC/WMI, and propagate across internal subnets.",
        "tags": ["lateral_movement", "smb", "port_445", "admin_shares", "rpc"],
    },
    {
        "id": "T1021.004",
        "name": "SSH",
        "tactic": "Lateral Movement",
        "content": "MITRE ATT&CK T1021.004: Remote Services - SSH. Adversaries may use compromised SSH keys or credentials over port 22 to establish remote shell access across enterprise servers and jump boxes.",
        "tags": ["lateral_movement", "ssh", "port_22", "linux", "remote_access"],
    },
    {
        "id": "T1071.001",
        "name": "Web Protocols (HTTP/HTTPS C2)",
        "tactic": "Command and Control",
        "content": "MITRE ATT&CK T1071.001: Application Layer Protocol - Web Protocols. Adversaries may communicate using standard HTTP/HTTPS over port 80/443 to blend command and control beaconing traffic with normal enterprise web browsing.",
        "tags": ["c2", "beaconing", "port_443", "https", "outbound"],
    },
    {
        "id": "T1071.004",
        "name": "DNS C2 & Tunneling",
        "tactic": "Command and Control",
        "content": "MITRE ATT&CK T1071.004: Application Layer Protocol - DNS. Adversaries may establish command and control communications or exfiltrate data embedded within DNS queries and responses over port 53 to evade perimeter firewalls.",
        "tags": ["c2", "dns", "port_53", "tunneling", "covert_channel"],
    },
    {
        "id": "T1046",
        "name": "Network Service Discovery",
        "tactic": "Discovery",
        "content": "MITRE ATT&CK T1046: Network Service Discovery. Adversaries may systematically scan IP ranges and port numbers (horizontal scanning, vertical sweeps) to map vulnerable listening services across internal enterprise subnets.",
        "tags": ["discovery", "scanning", "reconnaissance", "ports", "internal_sweep"],
    },
    {
        "id": "T1078",
        "name": "Valid Accounts",
        "tactic": "Defense Evasion / Initial Access",
        "content": "MITRE ATT&CK T1078: Valid Accounts. Adversaries may obtain and abuse legitimate user, service, or domain credentials to bypass access controls and evade heuristic anomaly detection rules.",
        "tags": ["defense_evasion", "credentials", "authentication", "privilege"],
    },
    {
        "id": "T1048",
        "name": "Exfiltration Over Alternative Protocol",
        "tactic": "Exfiltration",
        "content": "MITRE ATT&CK T1048: Exfiltration Over Alternative Protocol. Adversaries may steal sensitive enterprise datasets by transmitting them out-of-band using unmonitored network protocols or direct external socket connections.",
        "tags": ["exfiltration", "data_theft", "outbound_burst", "high_volume"],
    },
    {
        "id": "T1486",
        "name": "Data Encrypted for Impact (Ransomware)",
        "tactic": "Impact",
        "content": "MITRE ATT&CK T1486: Data Encrypted for Impact. Adversaries may encrypt target data and file shares over SMB/NFS to disrupt operational availability and extort victims for decryption keys.",
        "tags": ["ransomware", "encryption", "impact", "fileserver", "smb_burst"],
    },
    {
        "id": "RB-001",
        "name": "Runbook: High-Risk Lateral Movement Containment",
        "tactic": "Response Runbook",
        "content": "SOC Runbook RB-001: High-Risk Lateral Movement Containment. Immediate Action: Isolate compromised source host via zero-trust firewall policy. Revoke active Kerberos/NTLM/SSH tokens. Reconstruct attack path to identify downstream target assets and enforce VLAN boundary isolation.",
        "tags": ["runbook", "containment", "lateral_movement", "isolation", "vlan"],
    },
    {
        "id": "RB-002",
        "name": "Runbook: Outbound C2 Beaconing Mitigation",
        "tactic": "Response Runbook",
        "content": "SOC Runbook RB-002: Outbound C2 Mitigation. Immediate Action: Sinkhole destination C2 external IP at perimeter egress firewall. Quarantine source host from external gateway. Inspect host memory for injected beacon payloads.",
        "tags": ["runbook", "containment", "c2", "beaconing", "sinkhole"],
    },
    {
        "id": "RB-003",
        "name": "Runbook: Critical Data Exfiltration Containment",
        "tactic": "Response Runbook",
        "content": "SOC Runbook RB-003: Critical Data Exfiltration Containment. Immediate Action: Sever outbound session immediately. Apply zero-trust network quarantine to host. Freeze associated cloud / database credentials and audit egress volume bytes.",
        "tags": ["runbook", "containment", "exfiltration", "data_loss", "isolation"],
    },
]


class TextFeatureProjector:
    """
    Deterministic TF-IDF + hashing text projector into R^d
    with L2-normalization for exact FAISS cosine similarity search.
    """

    def __init__(self, dim: int = 128):
        self.dim = dim
        # Common vocabulary indices
        self.vocab: Dict[str, int] = {}
        self._build_vocab()

    def _build_vocab(self):
        words = set()
        for doc in MITRE_CORPUS:
            tokens = re.findall(r"\w+", (doc["content"] + " " + " ".join(doc["tags"])).lower())
            words.update(tokens)
        self.vocab = {w: i % self.dim for i, w in enumerate(sorted(words))}

    def embed(self, text: str) -> np.ndarray:
        tokens = re.findall(r"\w+", text.lower())
        vec = np.zeros(self.dim, dtype=np.float32)
        if not tokens:
            return vec

        for t in tokens:
            # Word hashing into embedding space
            idx = self.vocab.get(t, hash(t) % self.dim)
            vec[idx] += 1.0

        # Sublinear term frequency scaling
        vec = np.log1p(vec)

        # L2 Normalize
        norm = np.linalg.norm(vec)
        if norm > 1e-8:
            vec /= norm
        return vec


class GraphAwareRAGEngine:
    """
    Graph-Aware Retrieval-Augmented Generation (RAG) Engine.
    Leverages attack-path topology, compromised entities, and flow signatures
    to retrieve grounded MITRE ATT&CK knowledge and formulate SOC triages.
    """

    def __init__(self, dim: int = 128):
        self.dim = dim
        self.projector = TextFeatureProjector(dim=dim)
        self.corpus = MITRE_CORPUS
        self.index = faiss.IndexFlatIP(dim)
        self._build_faiss_index()

    def _build_faiss_index(self):
        """Indexes the static MITRE ATT&CK corpus into FAISS IndexFlatIP."""
        embeddings = []
        for doc in self.corpus:
            combined_text = f"{doc['name']} {doc['tactic']} {doc['content']} {' '.join(doc['tags'])}"
            embeddings.append(self.projector.embed(combined_text))
        embeddings_matrix = np.vstack(embeddings).astype(np.float32)
        self.index.add(embeddings_matrix)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves top-k MITRE ATT&CK techniques/runbooks using FAISS cosine similarity.
        """
        query_vec = self.projector.embed(query).reshape(1, -1).astype(np.float32)
        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.corpus):
                item = dict(self.corpus[idx])
                item["similarity_score"] = round(float(score), 4)
                results.append(item)
        return results

    def synthesize_triage(
        self,
        incident_id: str,
        attack_path: List[str],
        hop_details: List[Dict[str, Any]],
        threat_class: str,
        risk_score: float,
        top_k: int = 3,
    ) -> Dict[str, Any]:
        """
        Synthesizes a graph-grounded SOC incident triage report.
        Query is dynamically constructed from graph path entities and flow metadata.
        """
        # 1. Graph Context Extraction
        source_host = attack_path[0] if attack_path else "unknown"
        target_host = attack_path[-1] if attack_path else "unknown"
        hop_count = max(0, len(attack_path) - 1)

        ports = [h.get("dst_port") for h in hop_details if h.get("dst_port")]
        protocols = [h.get("protocol", "TCP") for h in hop_details]

        port_str = f"ports {', '.join(map(str, set(ports)))}" if ports else ""
        proto_str = f"protocols {', '.join(set(protocols))}" if protocols else ""

        # 2. Graph-Aware Query Construction
        query_tokens = [threat_class, "lateral movement" if hop_count > 1 else "anomalous access"]
        if ports:
            if 3389 in ports:
                query_tokens.append("rdp 3389 remote desktop")
            if 445 in ports:
                query_tokens.append("smb 445 admin shares")
            if 22 in ports:
                query_tokens.append("ssh 22 remote access")
            if 443 in ports:
                query_tokens.append("c2 443 beaconing exfiltration")
        query_tokens.append(f"risk {risk_score}")
        graph_query = " ".join(query_tokens)

        # 3. FAISS Retrieval
        retrieved_docs = self.retrieve(graph_query, top_k=top_k)

        # 4. Formulate Actionable Containment Recommendation
        matched_techniques = [d["id"] for d in retrieved_docs if d["id"].startswith("T")]
        recommended_runbook = next(
            (d for d in retrieved_docs if d["id"].startswith("RB")),
            self.corpus[-1],
        )

        should_quarantine = risk_score >= 80.0

        return {
            "incident_id": incident_id,
            "threat_class": threat_class,
            "risk_score": risk_score,
            "graph_context": {
                "source_host": source_host,
                "target_host": target_host,
                "hop_count": hop_count,
                "attack_chain": attack_path,
                "observed_ports": list(set(ports)),
                "observed_protocols": list(set(protocols)),
            },
            "graph_grounded_query": graph_query,
            "retrieved_mitre_techniques": retrieved_docs,
            "matched_technique_ids": matched_techniques,
            "recommended_runbook_id": recommended_runbook.get("id"),
            "containment_action": {
                "action": "AUTOMATED_ZERO_TRUST_QUARANTINE" if should_quarantine else "MONITOR_AND_LOG",
                "target_hosts": [source_host] if should_quarantine else [],
                "justification": f"Risk score {risk_score} crossed critical threshold 80.0 with {hop_count}-hop lateral propagation.",
            },
            "grounding_source": "Static Curated MITRE ATT&CK Enterprise v14.1 Corpus via FAISS IndexFlatIP",
        }


# Backwards compatibility alias
SimpleRAGEngine = GraphAwareRAGEngine
