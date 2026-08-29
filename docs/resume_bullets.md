# Resume Bullets: NetRaptor-X

These bullets are grounded in the actual metrics from `docs/ablation-study.md` and `docs/benchmarks/results.md`.

## General Software Engineering / Backend
* **Architected an end-to-end event-driven Threat Detection Platform** using FastAPI, Kafka, and PostgreSQL, processing simulated high-volume network telemetry into actionable SOC incidents.
* **Engineered a scalable data pipeline** capable of handling over 3,000 events/second on CPU, maintaining median processing latencies of ~20ms and sub-30ms p99 latency under load.
* **Built a zero-trust network containment simulator** integrating role-based access control (RBAC) and audit logging, enabling automated and manual quarantine actions on isolated endpoints.
* **Developed a full-stack real-time SOC dashboard** using React, TypeScript, and Vite, featuring WebSockets for live threat streaming and D3/Force-Graph for dynamic network topology visualization.

## Machine Learning / AI / General
* **Designed a hybrid GNN + Transformer Fusion architecture** for network anomaly detection, improving F1-score to 0.89 (up from 0.56 baseline) by jointly capturing spatial propagation and temporal behavioral sequences.
* **Implemented an ablation-driven ML pipeline**, demonstrating that spatial-temporal fusion yields a 92% PR-AUC for highly imbalanced threat datasets, significantly outperforming standalone temporal models (62% PR-AUC).
* **Integrated a Retrieval-Augmented Generation (RAG) SOC Analyst LLM** to automatically synthesize unstructured MITRE ATT&CK knowledge and graph attack paths into structured, evidence-grounded incident reports.
* **Optimized inference performance** with batched processing, achieving throughput of >3,100 predictions/sec on commodity hardware (CPU) while utilizing less than 200MB memory footprint.

## Security Engineering / SOC / Applied AI
* **Built an Explainable Risk Engine** mapping network anomalies and GNN embeddings to MITRE ATT&CK frameworks, generating actionable attack-path reconstructions via Dijkstra and multi-source BFS algorithms.
* **Developed an automated incident response pipeline** that triggers simulated VLAN isolations upon crossing critical risk thresholds (e.g., Score > 80), reducing hypothetical time-to-containment from minutes to milliseconds.
* **Secured platform APIs** via strict JWT authentication, role-based authorization (Analyst vs. Viewer), and immutable audit logs, ensuring compliance-ready tracking of all network containment actions.
* **Operationalized a mock Knowledge Base** of security runbooks, enabling a simulated LLM agent to map complex lateral movement paths to specific adversarial techniques (e.g., T1021 Remote Services).
