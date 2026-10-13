# Verified Resume Bullets: ThreatGraph

These resume bullets are strictly verified against reproducible codebase implementations and empirical benchmarks recorded in [`EVALUATION.md`](../EVALUATION.md), [`results/detection_metrics.json`](../results/detection_metrics.json), and [`results/throughput_benchmark.json`](../results/throughput_benchmark.json).

---

## 🎯 Final Resume Section (LaTeX Format)

```latex
% Project 3 - ThreatGraph
\resumeSubheading
{\href{https://github.com/khushalmidha/ThreatGraph}{ThreatGraph \faGithub}}{\textit{Jan 2026 - May 2026}}
{\textbf{Python}, \textbf{PyTorch Geometric}, \textbf{Transformers}, \textbf{GNNs}, \textbf{FAISS}, \textbf{FastAPI}}{}
\begin{enumerate}
\item Architected a spatial-temporal \textbf{GNN + Transformer} fusion engine evaluated on \textbf{synthetic network telemetry}, achieving \textbf{0.943 PR-AUC} and \textbf{0.899 F1-score} with \textbf{3.1K+ events/sec} batched CPU inference.
\item Engineered automated \textbf{attack-path reconstruction} and a \textbf{graph-aware RAG} pipeline over MITRE ATT\&CK knowledge, tracing multi-hop lateral movement and triggering simulated zero-trust containment.
\end{enumerate}
\vspace{-17pt}
```

---

## 🔬 Evidence & Metric Traceability

### Bullet 1: Spatial-Temporal GNN + Transformer Fusion Engine
* **Bullet Text**:
  > *Architected a spatial-temporal GNN + Transformer fusion engine evaluated on synthetic network telemetry, achieving 0.943 PR-AUC and 0.899 F1-score with 3.1K+ events/sec batched CPU inference.*
* **Architecture Verification**:
  - GNN: 2-layer `GATv2Conv(16 -> 32, edge_dim=4)` with dynamic edge attention + `GRUCell(32, 32)` for persistent temporal node states ([`ml/models/gnn.py`](../ml/models/gnn.py)).
  - Transformer: 2-layer `TransformerEncoder` ($d_{\text{model}}=16$, 4 heads, $d_{\text{ff}}=32$) processing temporal sliding sequences of length $T=10$ with sinusoidal positional encoding ([`ml/models/transformer.py`](../ml/models/transformer.py)).
  - Fusion: Concatenation $[h_{\text{spatial}} \,\|\, h_{\text{temporal}}] \in \mathbb{R}^{64}$ through dense projection `Linear(64 -> 32) + ReLU + Dropout(0.2)` ([`ml/models/fusion.py`](../ml/models/fusion.py)).
* **Metric Verification (Model-Specific)**:
  - Source: [`results/ablation_metrics.json`](../results/ablation_metrics.json) (`GNN + Transformer` row).
  - Measured PR-AUC: **0.9431** (reported as **0.943**).
  - Measured F1-Score: **0.8987** (reported as **0.899**), Precision: 0.9467, Recall: 0.8554 on imbalanced test set (8.29% attack events).
  - Multi-head Full-Fusion comparison: **0.9221 F1-score** and **0.8913 PR-AUC** with zero false positives ($\text{FP}=0$).
* **Throughput Verification (Scope A)**:
  - Source: [`results/throughput_benchmark.json`](../results/throughput_benchmark.json) (`scope_A_model_inference`).
  - Measured Inference Rate: **3,193.80 events/sec** (batch size 64 on CPU, Intel 12-core, mean of 3 runs).
  - Batch Latencies: P50 = 14.28 ms, P95 = 67.99 ms, P99 = 97.23 ms (412.39 $\mu$s/event).
  - Composite Detection Pipeline (Scope E): **2,065.75 events/sec** (feature engineering + model inference + policy check).

### Bullet 2: Attack-Path Reconstruction & Graph-Aware RAG
* **Bullet Text**:
  > *Engineered automated attack-path reconstruction and a graph-aware RAG pipeline over MITRE ATT&CK knowledge, tracing multi-hop lateral movement and triggering simulated zero-trust containment.*
* **Attack-Path Algorithm Verification**:
  - Implementation: [`backend/app/graph/attack_path.py`](../backend/app/graph/attack_path.py) (`AttackPathEngine`).
  - Algorithm: Risk-weighted Dijkstra shortest path where weight inversely mirrors node threat risk ($w = \frac{1}{\max(\text{risk}, 0.01) + 10^{-9}}$).
  - Causal Constraints: Monotonic temporal progression validation ($t_i \le t_{i+1}$) ensures historical flows preceding ingress are rejected.
  - Collateral Analysis: Multi-source BFS blast-radius expansion ($k=3$) and Tarjan cut-set bridge analysis to locate structural bottlenecks.
  - Test Suite: 9 passing unit tests in [`tests/test_attack_path.py`](../tests/test_attack_path.py) validating deterministic chains (`Host A -> B -> C -> DB`), cycles, disconnected graphs, and temporal ordering.
* **Graph-Aware RAG Verification**:
  - Implementation: [`rag/engine.py`](../rag/engine.py) (`GraphAwareRAGEngine`).
  - Index: FAISS `IndexFlatIP` (exact cosine similarity over L2-normalized 128-d term projection vectors).
  - Indexed Knowledge Base: Exactly **10 MITRE ATT&CK Enterprise techniques** plus **3 SOC incident response runbooks** (13 total documents indexed):
    - Techniques: `T1059` (Execution), `T1021.001` (RDP), `T1021.002` (SMB), `T1021.004` (SSH), `T1071.001` (Web C2), `T1071.004` (DNS C2), `T1046` (Discovery), `T1078` (Valid Accounts), `T1048` (Exfiltration), `T1486` (Ransomware).
    - Runbooks: `RB-001` (Lateral Movement Containment), `RB-002` (Outbound C2 Mitigation), `RB-003` (Exfiltration Mitigation).
  - Query Formulation: Synthesizes graph entities, pivot IPs, protocol/port signatures, and path hops into grounded vector queries.
  - Test Suite: 5 passing unit tests in [`tests/test_rag.py`](../tests/test_rag.py).
* **Simulated Zero-Trust Containment Verification**:
  - Implementation: [`backend/simulation/policies.py`](../backend/simulation/policies.py) (`SimulatedFirewall`).
  - Policy Engine: Isolates compromised endpoints when risk score $\ge 80.0$, protecting benign nodes ($< 80.0$) with default-deny intra-zone routing.
  - Test Suite: 4 passing unit tests in [`tests/test_containment.py`](../tests/test_containment.py).

---

## 📋 Resume-Safe Terminology Checklist

| Concept | Recommended Resume-Safe Term | Terms to Avoid |
| :--- | :--- | :--- |
| **Telemetry Data** | `synthetic network telemetry`, `simulated telemetry` | `production enterprise logs`, `live SOC telemetry` |
| **Throughput** | `3.1K+ events/sec batched CPU inference`, `sustaining 2K+ events/sec across composite pipeline` | `processing 3.1K+ events/sec end-to-end` |
| **Containment** | `simulated zero-trust containment`, `policy engine` | `live endpoint hardware quarantine`, `kernel iptables` |
| **RAG System** | `graph-aware RAG pipeline` | `hierarchical GraphRAG` |
| **Knowledge Base** | `10 MITRE ATT&CK techniques plus 3 SOC runbooks` | `13 MITRE techniques` |
| **Kafka Pipeline** | `Kafka-compatible pipeline interface; local in-process queue backend` | `distributed production Kafka cluster` |
