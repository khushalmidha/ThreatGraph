# 🛡️ ThreatGraph: AI-Driven Zero-Trust Threat Intelligence Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![React 18](https://img.shields.io/badge/react-18.0%2B-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg?logo=pytorch)](https://pytorch.org/)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-threatgraph.duckdns.org-brightgreen.svg)](http://threatgraph.duckdns.org/)

ThreatGraph is an end-to-end, event-driven network security platform. It simulates a modern Security Operations Center (SOC) pipeline by fusing real-time network telemetry with Spatial-Temporal Machine Learning and Retrieval-Augmented Generation (RAG) LLMs to detect, explain, and contain anomalous behaviors like lateral movement and data exfiltration.

---

## 🚀 Features

- **Event-Driven Pipeline**: Processes high-volume synthetic network flows using a Kafka-like event stream.
- **Hybrid AI Detection**: Fuses Graph Neural Networks (GNNs) for spatial topology and Transformers for time-series behavior, achieving **92% PR-AUC** on highly imbalanced threat data.
- **Automated Incident Response**: Reconstructs attack paths via graph algorithms (Dijkstra/BFS) and uses a local RAG LLM to synthesize MITRE ATT&CK incident reports automatically.
- **Zero-Trust Containment**: Features a software-defined firewall layer for simulated, millisecond-latency endpoint isolation based on Risk Engine thresholds.
- **Real-Time SOC Dashboard**: A dynamic React/Vite frontend equipped with D3 Force-Graphs for live topology tracking and Server-Sent Events (SSE) for instant alerts.

---

## 🧠 Why Graph + Transformer?

Traditional rule-based SIEMs (Security Information and Event Management) struggle to detect slow, sophisticated lateral movement (e.g., APTs) across complex network topologies, producing high false-positive rates that fatigue analysts. 

Detecting modern network threats requires understanding two critical dimensions:
1. **Spatial (Who talks to whom?)**: Graph Neural Networks (GNNs) map the network topology to identify anomalous structural edges.
2. **Temporal (How do they talk over time?)**: Transformers model behavioral shifts, identifying sudden spikes in payload sizes or connection frequencies.

**ThreatGraph** fuses both representations, yielding a highly accurate Risk Score that drastically outperforms standalone temporal or spatial models.

---

## 🏗️ Architecture

### 1. End-to-End System Architecture

```mermaid
graph TD
    %% Styling
    classDef generator fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#fff
    classDef messageBus fill:#1e293b,stroke:#f59e0b,stroke-width:2px,color:#fff
    classDef processing fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#fff
    classDef mlEngine fill:#1e293b,stroke:#8b5cf6,stroke-width:2px,color:#fff
    classDef datastore fill:#1e293b,stroke:#ef4444,stroke-width:2px,color:#fff
    classDef frontend fill:#1e293b,stroke:#0ea5e9,stroke-width:2px,color:#fff
    
    subgraph "1. Data Generation & Ingestion"
        TG[Traffic Generator <br> Python / Synthetic Flows]:::generator
        ZTA[Zero-Trust Zones <br> Web / App / DB Enclaves]:::generator
        Kafka[(Kafka Event Stream <br> 3,000+ Flows/sec)]:::messageBus
        
        TG -->|Simulated Network Traffic| ZTA
        ZTA -->|Telemetry Events| Kafka
    end

    subgraph "2. Stream Processing & Topology State"
        GraphWorker[Graph Worker <br> Real-time Edge Aggregator]:::processing
        FeatExtractor[Feature Extractor <br> Sliding Window Tensorizer]:::processing
        NX[(In-Memory Graph <br> NetworkX State)]:::datastore
        
        Kafka --> GraphWorker
        Kafka --> FeatExtractor
        GraphWorker --> NX
        FeatExtractor --> NX
    end

    subgraph "3. AI Threat Detection Engine"
        GNN[Temporal GNN <br> GATv2Conv + GRUCell]:::mlEngine
        Transformer[Time-Series Transformer <br> 4-Head Self-Attention]:::mlEngine
        Fusion[Cross-Modal Fusion Layer <br> MLP + Dropout]:::mlEngine
        RiskEngine[Explainable Risk Engine <br> 0 - 100 Severity Scorer]:::processing
        
        NX -->|Node Subgraphs| GNN
        NX -->|Sequential Telemetry| Transformer
        GNN -->|Spatial Embedding| Fusion
        Transformer -->|Temporal Embedding| Fusion
        Fusion -->|Fused Vector| RiskEngine
    end

    subgraph "4. Automated Incident Response & Copilot"
        IncidentDB[(Incident Database <br> PostgreSQL Store)]:::datastore
        AttackGraph[Attack Path Engine <br> Dijkstra / Multi-Source BFS]:::processing
        FAISS[(FAISS Vector DB <br> MITRE ATT&CK Embeddings)]:::datastore
        RAG[RAG SOC Copilot <br> MITRE Evidence Synthesizer]:::mlEngine
        Containment[Software-Defined Firewall <br> Zero-Trust Policy Engine]:::processing
        
        RiskEngine -->|Risk Score > 80| IncidentDB
        RiskEngine -->|Trigger Triage| AttackGraph
        NX --> AttackGraph
        AttackGraph -->|Lateral Hop Sequence| RAG
        FAISS -->|Technique Match: T1021 / T1059| RAG
        IncidentDB --> Containment
        Containment -.->|Quarantine / Drop Traffic| ZTA
    end

    subgraph "5. SOC Command Center"
        FastAPI[FastAPI Backend <br> REST API & SSE Streams]:::processing
        ReactUI[React + Vite Dashboard <br> D3 Force Graph Visualizer]:::frontend
        
        IncidentDB --> FastAPI
        RAG --> FastAPI
        Containment --> FastAPI
        FastAPI -->|Live Incident Feeds| ReactUI
    end
```

### 2. Spatial-Temporal Deep Learning Architecture

```mermaid
flowchart LR
    %% Subgraph 1: Inputs
    subgraph Inputs ["Input Telemetry Streams"]
        A1["Graph Topology<br>(Nodes: Hosts, Edges: Flows)"]
        A2["Host Sliding Windows<br>(Sequence Length T x Features)"]
    end

    %% Subgraph 2: Encoders
    subgraph Encoders ["Dual-Tower Encoders"]
        B1["GATv2Conv Layers<br>(Dynamic Edge Attention)"]
        B2["GRUCell<br>(Graph Temporal State)"]
        B3["Transformer Encoder<br>(2 Layers, 4 Attention Heads)"]
        
        A1 --> B1 --> B2
        A2 --> B3
    end

    %% Subgraph 3: Embeddings
    subgraph Repr ["Embeddings"]
        C1["Spatial Representation<br>e_gnn (Mean Pooled)"]
        C2["Temporal Representation<br>e_transformer (Last Step)"]
        B2 --> C1
        B3 --> C2
    end

    %% Subgraph 4: Fusion
    subgraph FusionBlock ["Cross-Modal Fusion"]
        D1["Concatenate: [e_gnn || e_transformer]"]
        D2["Linear(hidden*2 -> hidden) + ReLU + Dropout(0.2)"]
        C1 --> D1
        C2 --> D1
        D1 --> D2
    end

    %% Subgraph 5: Multi-Task Heads
    subgraph Heads ["Multi-Task Prediction Heads"]
        E1["Threat Probability<br>Sigmoid in [0, 1]"]
        E2["Anomaly Score<br>Continuous Regression"]
        E3["Threat Classification<br>Normal / Lateral / Exfil"]
        D2 --> E1
        D2 --> E2
        D2 --> E3
    end

    %% Subgraph 6: Downstream
    subgraph Downstream ["Risk Engine & Response"]
        F1["Weighted Risk Formula<br>(0.4 GNN + 0.3 Trans + 0.2 Anom + 0.1 Hist)"]
        F2["FAISS Vector Retrieval<br>(MITRE ATT&CK T1021 / T1059)"]
        F3["Automated Zero-Trust Quarantine<br>(sub-50ms isolation)"]
        
        E1 --> F1
        E2 --> F1
        F1 -->|Score > 80| F2
        F1 -->|Critical Alert| F3
    end
```

*(For detailed architectural specifications, see [docs/architecture.md](docs/architecture.md))*

---

## 📊 Benchmarks & ML Performance

### Machine Learning Ablation Study
The hybrid architecture significantly outperforms baseline models on synthetic threat data:
| Model | Precision | Recall | F1 Score | ROC-AUC | PR-AUC |
|-------|-----------|--------|----------|---------|--------|
| Transformer-Only | 0.65 | 0.50 | 0.56 | 0.70 | 0.55 |
| Temporal-GNN-Only | 0.70 | 0.65 | 0.67 | 0.78 | 0.62 |
| **Full-Fusion** | **0.90** | **0.88** | **0.89** | **0.95** | **0.92** |

### System Performance (CPU Inference)
- **Throughput**: ~3,113 events/sec (at 100k event scale)
- **Median Latency**: 20.59 ms
- **P99 Latency**: 25.20 ms
- **Memory Footprint**: ~195 MB

*(For full reports, see [docs/ablation-study.md](docs/ablation-study.md) and [docs/benchmarks/results.md](docs/benchmarks/results.md))*

---

## 🛠️ Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/khushalmidha/ThreatGraph.git
   cd ThreatGraph
   ```

2. **Backend Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Run the End-to-End Demo**
   The repository includes an automated script that simulates normal traffic, introduces a lateral movement anomaly, detects it via the ML fusion engine, and triggers the automated SOC response.
   ```bash
   # On Windows PowerShell
   .\demo.ps1
   
   # Or run tests to verify
   pytest tests/test_backend.py
   ```

---

## 🛡️ Security Considerations

All containment APIs handling live infrastructure isolations are protected via:
- **Strict JWT Authentication**
- **Role-Based Access Control (RBAC)**: Requires the `ANALYST` role to execute containment commands.
- **Immutable Audit Logging**: Every containment action (Isolate/Release) is durably recorded for compliance tracking.

---

## 🔮 Future Limitations & Roadmap

While this project is a functional end-to-end prototype, some components are mocked to run locally without cloud dependencies:
- **LLM Integration**: The SOC Analyst agent is currently simulated for rapid, cost-free execution. Connecting this to `gpt-4` or a local `Ollama` instance is a straightforward next step.
- **Message Broker**: Uses local Python queues in place of a full clustered `confluent-kafka` deployment.
- **Database**: Uses portable `SQLite` (JSON serialized strings). A production deployment would migrate this immediately to `PostgreSQL` with native `JSONB` columns.

---

### Developed as part of the ThreatGraph initiative.
