# 🛡️ ThreatGraph: Spatial-Temporal Threat Detection Engine

> **Spatial-temporal threat detection using graph neural networks and Transformers, with attack-path reconstruction, MITRE ATT&CK retrieval, and simulated containment.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![PyTorch Geometric](https://img.shields.io/badge/PyTorch%20Geometric-2.4%2B-EE4C2C.svg?logo=pytorch)](https://pytorch-geometric.readthedocs.io/)
[![FAISS](https://img.shields.io/badge/FAISS-CPU%20Vector%20Search-blueviolet.svg)](https://github.com/facebookresearch/faiss)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-threatgraph.duckdns.org-brightgreen.svg)](http://threatgraph.duckdns.org/)

---

### ⚠️ Scientific Evaluation & Scope Notice
> **Evaluation is performed on synthetic/simulated network telemetry and is not a production SOC benchmark.**
> 
> All empirical metrics (PR-AUC, F1-score, and event processing throughput) reported in this repository are measured on synthetic network security telemetry generated under controlled adversary simulation scenarios (`traffic/generator.py`). Containment actions operate against an in-memory software policy engine rather than production firewall/EDR hardware. For the complete scientific audit and reproducible commands, see [EVALUATION.md](EVALUATION.md).

---

## 📌 Repository Topics
`pytorch-geometric` · `graph-neural-networks` · `transformers` · `cybersecurity` · `anomaly-detection` · `faiss` · `mitre-attack` · `fastapi`

---

## 🚀 Core Capabilities

1. **Dual-Tower Spatial-Temporal Fusion Engine**: Couples a 2-layer Graph Attention Network (`GATv2Conv`) + `GRUCell` with a 2-layer sequence `TransformerEncoder` to detect stealthy multi-hop intrusions across synthetic network flows.
2. **Automated Attack-Path Reconstruction**: Traces causal lateral movement corridors using risk-weighted Dijkstra shortest-path algorithms ($w = \frac{1}{\text{risk} + \epsilon}$) with strict monotonic temporal causal ordering ($t_i \le t_{i+1}$) and multi-source BFS blast-radius mapping.
3. **Graph-Aware RAG SOC Copilot**: Extracts graph entities, lateral hop sequences, and protocol contexts to formulate grounded queries over a FAISS vector index (`IndexFlatIP`) indexing 13 MITRE ATT&CK techniques and incident response runbooks.
4. **Simulated Zero-Trust Containment**: An in-memory micro-segmentation policy engine that dynamically evaluates risk scores ($\tau \ge 80.0$) to isolate compromised hosts and enforce ACL blocks with complete rollback capabilities.
5. **Event-Driven Streaming Ingestion**: Kafka-compatible pipeline abstraction capable of streaming high-volume telemetry through monotonic deques and Fenwick trees into batched tensor representations.

---

## 🧠 Spatial-Temporal Architecture

ThreatGraph models enterprise network traffic along two complementary axes: **structural topology** (spatial graph interactions) and **event sequence dynamics** (temporal flow behaviors).

```mermaid
flowchart TD
    subgraph Ingestion ["1. Event Ingestion & Feature Tensorization"]
        Raw["Raw Synthetic Telemetry Flows<br>(src_ip, dst_ip, port, proto, bytes, pkts)"]
        State["Sliding Window State Engine<br>(Monotonic Deque + Fenwick Tree)"]
        Raw --> State
        State -->|Graph Snapshot G=(V,E)| Topo["Host Graph Topology<br>N=50 Hosts, Node Feats d=16, Edge Feats d=4"]
        State -->|Sequence History T=10| Seq["Temporal Sequence Tensor<br>Batch x T x 16"]
    end

    subgraph SpatialStream ["2. Spatial Stream (GATv2 + GRU)"]
        GAT1["GATv2Conv Layer 1<br>(16 -> 32, Dynamic Edge Attention)"]
        GRU["GRUCell Temporal Memory<br>(32 -> 32 Host State Tracking)"]
        GAT2["GATv2Conv Layer 2<br>(32 -> 32 2-Hop Message Passing)"]
        Pool["Global Mean Pooling"]
        Topo --> GAT1 --> GRU --> GAT2 --> Pool
        Pool --> SpatialVec["Spatial Embedding<br>h_spatial in R^32"]
    end

    subgraph TemporalStream ["3. Temporal Stream (Transformer)"]
        Proj["Input Projection + Sinusoidal Positional Encoding"]
        Trans["2-Layer TransformerEncoder<br>(d_model=16, 4 Heads, hidden=32, dropout=0.1)"]
        TransPool["Sequence Mean Pooling"]
        Seq --> Proj --> Trans --> TransPool
        TransPool --> TempVec["Temporal Embedding<br>h_temporal in R^32"]
    end

    subgraph FusionLayer ["4. Cross-Modal Fusion & Prediction Heads"]
        Concat["Concatenation<br>[h_spatial || h_temporal] in R^64"]
        Bottleneck["Linear(64 -> 32) + ReLU + Dropout(0.2)"]
        SpatialVec --> Concat
        TempVec --> Concat
        Concat --> Bottleneck
        
        HeadThreat["Threat Probability<br>Linear(32 -> 1) + Sigmoid"]
        HeadAnom["Anomaly Score<br>Linear(32 -> 1)"]
        HeadClass["Threat Classification<br>Linear(32 -> 3) Softmax"]
        
        Bottleneck --> HeadThreat
        Bottleneck --> HeadAnom
        Bottleneck --> HeadClass
    end

    subgraph Downstream ["5. Graph-Aware Triage & Containment"]
        RiskScore["Risk Engine (0-100)<br>0.4*Threat + 0.3*Anom + 0.2*Class + 0.1*Hist"]
        HeadThreat --> RiskScore
        HeadAnom --> RiskScore
        HeadClass --> RiskScore

        PathEngine["Attack-Path Engine<br>Risk-Weighted Dijkstra & BFS"]
        FAISS["FAISS Vector Retrieval<br>MITRE ATT&CK T1021 / T1059 / T1071"]
        Firewall["Simulated Zero-Trust Firewall<br>Policy Isolation (Risk >= 80.0)"]

        RiskScore -->|Risk >= 50| PathEngine
        PathEngine -->|Graph Context + Hops| FAISS
        RiskScore -->|Risk >= 80| Firewall
    end
```

### Architectural Specifications
- **Graph Formulation**: Directed multigraph where nodes represent network endpoints (hosts/servers) and directed edges represent aggregated NetFlow communications.
- **Node Features ($d=16$)**: Outbound flow velocity, inbound flow velocity, failed authentication frequency, unique destination ports ratio, byte volume entropy, protocol distribution entropy, and historical risk EMA.
- **Edge Features ($d=4$)\**: Port classification (Web, Remote Admin/SSH/RDP, Database, Other), byte volume (log10), packet volume (log10), and connection duration.
- **GNN Layers**: Two `GATv2Conv` layers with dynamic multi-head attention (`heads=1`, `edge_dim=4`) interleaved with a `GRUCell` maintaining persistent hidden state vectors across sliding time slices.
- **Transformer Encoder**: 2 layers with `d_model=16`, `nhead=4`, `dim_feedforward=32`, and sinusoidal positional encodings processing sliding sequences of length $T=10$.
- **Loss Function**: Multi-task joint objective:
  $$\mathcal{L} = \mathcal{L}_{\text{BCE}}(\hat{y}_{\text{threat}}, y_{\text{threat}}) + 0.5 \cdot \mathcal{L}_{\text{MSE}}(\hat{s}_{\text{anom}}, s_{\text{anom}}) + 0.5 \cdot \mathcal{L}_{\text{CE}}(\hat{c}_{\text{class}}, c_{\text{class}})$$

---

## 📊 Verified Benchmarks & Ablation Study

All metrics below originate from reproducible test runs and are stored in machine-readable JSON artifacts:
- Detection Metrics: [`results/detection_metrics.json`](results/detection_metrics.json)
- Ablation Metrics: [`results/ablation_metrics.json`](results/ablation_metrics.json)
- Throughput Metrics: [`results/throughput_benchmark.json`](results/throughput_benchmark.json)

### 1. Model Detection Benchmark (Imbalanced Synthetic Telemetry)
Evaluated on **1,001 test events** (80/20 temporal split of 5,006 synthetic events) with an **8.29% positive attack ratio** (83 attack events):

| Architecture Variant | Precision | Recall | F1-Score | PR-AUC | ROC-AUC | Configuration Notes |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Temporal-GNN-Only** | 0.9259 | 0.3012 | 0.4545 | 0.6983 | 0.9238 | Captures structural port scans; misses subtle low-and-slow beacons. |
| **Transformer-Only** | 0.9342 | 0.8554 | 0.8931 | 0.8972 | 0.9394 | Strong temporal cadence modeling; misses multi-hop lateral propagation. |
| **GNN + Transformer** | 0.9467 | 0.8554 | **0.8987** | **0.9431** | **0.9796** | Fuses spatial propagation with temporal bursts; highest PR-AUC. |
| **Full-Fusion (Multi-Head)** | **1.0000** | 0.8554 | **0.9221** | **0.8913** | **0.9366** | Joint multi-task optimization eliminates false positives ($\text{FP}=0$). |

*Reproduce the detection benchmark:*
```bash
python evaluation/run_detection_benchmark.py --config configs/eval.yaml
```

---

### 2. Throughput & Processing Latency by Scope
Measured across **100,000 synthetic events** on commodity CPU (Intel 12-core, 16 GB RAM, no GPU):

| Latency Scope | Measured Metric | Value | Measurement Details |
| :--- | :--- | :---: | :--- |
| **Scope A: Model Inference** | Throughput | **3,193.80 events/sec** | Batched FusionModel inference (batch size 64) |
| | Median Latency (P50) | **14.28 ms** | Per batch (64 events) |
| | 95th Percentile (P95) | **67.99 ms** | Per batch (64 events) |
| | 99th Percentile (P99) | **97.23 ms** | Per batch (64 events) |
| | Per-Event Inference | **412.39 $\mu$s** | Single event inference cost |
| **Scope B: Feature Updates** | State Update Rate | **19,045.36 events/sec** | Monotonic deque + Fenwick tree windowing |
| | Per-Event Feature Cost | **52.51 $\mu$s** | Per-event state ingestion latency |
| **Scope C: Attack-Path Search** | Mean Query Latency | **0.098 ms** | Dijkstra risk-weighted shortest path on 50 hosts |
| | P95 Path Latency | **0.143 ms** | Causal path reconstruction + multi-source BFS |
| **Scope D: Containment Engine** | Mean Decision Latency | **19.19 $\mu$s** | Risk threshold evaluation & zone ACL lookup |
| | P95 Decision Latency | **20.91 $\mu$s** | Simulated quarantine execution |
| **Scope E: Composite Pipeline** | End-to-End Throughput | **2,065.75 events/sec** | Features + Model Inference + Policy Check |
| | End-to-End Latency | **0.484 ms/event** | Complete in-process processing time |

*Reproduce the throughput benchmark:*
```bash
python benchmarks/throughput.py --events 100000 --batch-size 64 --runs 3
```

---

## 🔀 Streaming Pipeline & Kafka Distinction

- **Pipeline Compatibility**: The system implements an asynchronous event consumer interface (`backend/worker_detection.py`) compatible with Apache Kafka brokers (`aiokafka`).
- **Benchmark Backend**: Local throughput benchmarks and unit tests execute against the in-process sliding window queue backend to eliminate external broker container dependencies.
- **Specification**: *Kafka-compatible architecture; reported local throughput benchmark uses the in-process queue backend.*

---

## 🔍 Attack-Path Reconstruction & Graph Algorithms

ThreatGraph's `AttackPathEngine` (`backend/app/graph/attack_path.py`) reconstructs lateral movement chains from dynamic network graphs:

1. **Risk-Weighted Shortest Path**: Employs Dijkstra's algorithm where edge traversal weight is inversely proportional to node risk score:
   $$\text{weight}(u, v) = \frac{1.0}{\max(\text{risk}(v), 0.01) + 10^{-9}}$$
   High-risk compromised hosts create low-resistance paths, ensuring the algorithm pinpoints the adversary's primary pivot path.
2. **Causal Monotonic Temporal Constraints**: Hops along candidate attack paths are validated for monotonic timestamp progression ($t_{(u \to v)} \le t_{(v \to w)}$). Traversal events occurring before ingress breach are deterministically rejected.
3. **Multi-Source BFS Blast Radius**: Computes the reachable blast radius from all compromised seeds up to depth $k=3$.
4. **Critical Asset Cut-Set Detection**: Uses Tarjan's bridge-finding algorithm to highlight articulation points—network bottlenecks that, if isolated, sever attacker access to critical database tiers.

All edge cases (cycles, disconnected components, unreachable targets, competing risk paths) are validated in [`tests/test_attack_path.py`](tests/test_attack_path.py).

---

## 📚 Graph-Aware RAG SOC Copilot

Rather than treating RAG as unstructured text search or claiming formal hierarchical GraphRAG:
- **Graph-Aware Query Formulation**: The copilot extracts structured context from the attack graph (pivot hosts, targeted destination, observed port, protocol, and reconstructed multi-hop path).
- **FAISS Vector Index**: Embeds text using term-weighted projection vectors into a FAISS `IndexFlatIP` index (exact cosine similarity).
- **Curated MITRE ATT&CK Corpus**: Indexes 13 enterprise techniques and mitigation runbooks:
  - `T1021.001`: Remote Desktop Protocol lateral movement
  - `T1021.002`: SMB / Windows Admin Shares lateral movement
  - `T1021.004`: SSH Remote Services lateral movement
  - `T1059`: Command & Scripting Interpreter execution
  - `T1071.001`: Web Protocol C2 beaconing
  - `T1071.004`: DNS Tunneling & Exfiltration
  - `T1046`: Network Service Discovery / Port Scans
  - `T1078`: Valid Accounts Privilege Abuse
  - `T1048`: Exfiltration over Alternative Protocols
  - `T1486`: Data Encrypted for Impact (Ransomware)
  - `RB-001`, `RB-002`, `RB-003`: Incident triage runbooks for RDP, SMB, and DNS isolation
- **Grounded Triage Generation**: Retrieves top-$k=3$ relevant techniques and runbooks, synthesizing an incident report with recommended containment steps.

---

## 🛡️ Simulated Zero-Trust Containment

The containment subsystem (`backend/simulation/policies.py`) simulates a software-defined micro-segmentation firewall:
- **Zero-Trust Zones**: Partitions the IP topology into `INTERNET`, `DMZ`, `INTERNAL`, and `DATABASE` enclaves.
- **Threshold Isolation**: Automatically isolates endpoints when risk scores meet or exceed threshold $\tau \ge 80.0$.
- **Benign Protection**: Benign endpoints (risk $< 80.0$) are strictly protected against false isolation (`tests/test_containment.py`).
- **Simulated Enforcement**: Drops network packets in software routing tables; does not alter production OS iptables, Windows Filtering Platform (WFP), or cloud network ACLs.
- **Full Rollback Support**: Every quarantine action generates an immutable audit record and supports programmatic release/rollback.

---

## 🧪 Testing & Verification

The test suite contains 30 passing tests across graph algorithms, vector search, containment, and feature extraction:

```bash
# Run complete test suite
pytest -v

# Run individual subsystems
pytest tests/test_attack_path.py    # 9 tests: Dijkstra, cycles, temporal constraints
pytest tests/test_rag.py            # 5 tests: FAISS index, cosine retrieval, MITRE match
pytest tests/test_containment.py    # 4 tests: Isolation thresholds, zone blocking, rollback
pytest tests/test_backend.py        # 4 tests: FastAPI endpoints and policy routes
pytest traffic/tests/               # 8 tests: Sliding windows, Fenwick tree, synthetic generator
```

---

## ⚙️ Quickstart & Local Setup

### Prerequisites
- Python 3.12+
- Node.js 18+ (for frontend dashboard)

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/khushalmidha/ThreatGraph.git
cd ThreatGraph

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1       # Windows PowerShell
# source venv/bin/activate        # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Benchmarks
```bash
# 1. Run detection & ablation benchmark
python evaluation/run_detection_benchmark.py --config configs/eval.yaml

# 2. Run throughput & latency benchmark
python benchmarks/throughput.py --events 100000 --batch-size 64
```

### 3. Launch Backend & SOC Dashboard
```bash
# Start backend API (from project root)
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# In a separate terminal, launch frontend
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## ⚠️ Scientific Limitations & Boundaries

To preserve strict scientific integrity, the following limitations are explicitly noted:
1. **Synthetic Telemetry Scope**: Telemetry is generated via stochastic simulation (`traffic/generator.py`). Real-world enterprise traffic features encrypted payloads, asynchronous packet drops, and vendor-specific NetFlow quirks not simulated here.
2. **No Production SOC Deployment**: This platform is an engineering and algorithmic prototype. It has not been deployed to an active enterprise SOC or evaluated against live enterprise intrusion datasets.
3. **Software-Simulated Quarantine**: Containment modifies an internal state table within the demo application. It does not interface with physical network switches, hypervisors, or EDR agents.
4. **Offline Batch Evaluation**: ML detection metrics are evaluated over offline dataset splits and do not account for concept drift or evolving adversary TTPs over months of operational runtime.
5. **Embedding Model**: RAG vector retrieval utilizes a deterministic term-projection model for local, reproducible FAISS execution without requiring commercial LLM API dependencies.
6. **No Adversarial Robustness Testing**: The GNN and Transformer models have not been evaluated against adversarial graph perturbation attacks (e.g., evasion via flow splitting).

---

## 📄 License & Attribution
Distributed under the MIT License. Developed as part of the ThreatGraph research platform.
