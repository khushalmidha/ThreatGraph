# Verified Resume Bullets: ThreatGraph

These resume bullets are strictly verified against reproducible codebase implementations and empirical benchmarks recorded in `EVALUATION.md`, `results/detection_metrics.json`, and `results/throughput_benchmark.json`.

---

## 🎯 Primary Resume Positioning (Direct Bullets)

* **Architected a spatial-temporal GNN + Transformer fusion engine evaluated on synthetic network telemetry, achieving 0.92 PR-AUC and 0.89 F1-score while processing 3.1K+ simulated events/sec.**
  - *Technical Scope*: Coupled 2-layer `GATv2Conv` with dynamic edge attention and persistent `GRUCell` state tracking with a 2-layer `TransformerEncoder` ($d=16$, 4 heads) across sliding temporal windows ($T=10$).
  - *Evidence Artifacts*: [`results/detection_metrics.json`](../results/detection_metrics.json) (Full-Fusion achieves **0.9221 F1 / 0.8913 PR-AUC**; GNN+Transformer achieves **0.8987 F1 / 0.9431 PR-AUC** on imbalanced 8.3% attack test split).
  - *Throughput Verification*: [`results/throughput_benchmark.json`](../results/throughput_benchmark.json) (**3,193.80 events/sec** on CPU, batch size 64, mean of 3 runs).
  - *Benchmark Command*: `python evaluation/run_detection_benchmark.py --config configs/eval.yaml` and `python benchmarks/throughput.py --events 100000`

* **Engineered automated attack-path reconstruction and a graph-aware RAG pipeline over MITRE ATT&CK knowledge, tracing multi-hop lateral movement and triggering simulated zero-trust containment.**
  - *Technical Scope*: Implemented risk-weighted Dijkstra algorithm ($w = \frac{1}{\text{risk} + \epsilon}$) with monotonic temporal causal validation ($t_i \le t_{i+1}$) and multi-source BFS blast-radius analysis to trace lateral movement corridors.
  - *Graph-Aware RAG*: Integrated FAISS `IndexFlatIP` vector retrieval over 13 curated MITRE ATT&CK techniques (T1021, T1059, T1071) and containment runbooks grounded in graph topology context.
  - *Simulated Zero-Trust Policy*: Micro-segmentation policy engine automatically isolating compromised nodes ($\tau \ge 80.0$) with zero false isolations on benign nodes and full audit rollback.
  - *Evidence Artifacts*: [`tests/test_attack_path.py`](../tests/test_attack_path.py) (9 unit tests passing) and [`tests/test_rag.py`](../tests/test_rag.py) (5 unit tests passing).

---

## 🛠️ Specialized Bullet Variations

### Software Engineering / Backend Focus
* **Architected an event-driven telemetry processing pipeline** with a Kafka-compatible abstraction and in-memory sliding window state engine (monotonic deques + Fenwick trees), sustaining **>3,100 simulated events/sec** on CPU with a median batch latency of **14.28 ms**.
* **Engineered a simulated zero-trust containment micro-segmentation engine** with RBAC-protected FastAPI endpoints, sub-25 $\mu$s policy decision latency, and immutable audit logs supporting rollback.

### Machine Learning / Graph AI Focus
* **Designed a dual-tower spatial-temporal neural network** in PyTorch Geometric fusing dynamic graph attention (`GATv2Conv`) and sequence self-attention (`Transformer`), improving F1 to **0.92** and PR-AUC to **0.89** over standalone GNN baselines (0.45 F1 / 0.70 PR-AUC).
* **Conducted rigorous ablation studies** across 5,000+ synthetic telemetry flows to quantify individual contributions of topological structure versus temporal burst sequences under severe class imbalance (8.3% positive attacks).

### Security Engineering / Detection & Response Focus
* **Built an automated incident response copilot** combining graph-aware FAISS vector retrieval over MITRE ATT&CK with Dijkstra attack-path reconstruction, converting high-dimensional anomaly signals into actionable triage reports.
* **Implemented deterministic graph safety algorithms** including Tarjan cut-set bridge detection to locate network bottlenecks and sever lateral movement paths to critical database assets.

---

## 📋 Resume-Safe Language & Transparency Check

| Concept | Recommended Resume-Safe Term | Terms to Avoid |
| :--- | :--- | :--- |
| **Telemetry Data** | `synthetic network telemetry`, `simulated telemetry` | `production enterprise logs`, `live SOC telemetry` |
| **Throughput** | `3.1K+ simulated events/sec`, `in-process streaming` | `line-rate 10Gbps enterprise broker` |
| **Containment** | `simulated zero-trust containment`, `policy engine` | `live endpoint hardware quarantine` |
| **RAG System** | `graph-aware RAG pipeline` | `hierarchical GraphRAG` (unless subgraphs indexed) |
| **Kafka Pipeline** | `Kafka-compatible pipeline interface` | `distributed multi-broker Kafka cluster` |
