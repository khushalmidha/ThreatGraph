# Performance Benchmarks: ThreatGraph

> ⚠️ **Benchmark Environment Disclosure**:
> - Evaluated on **synthetic network telemetry** on local commodity hardware (Intel64 Family 6 Model 154 Stepping 4, GenuineIntel).
> - **Kafka Architecture Note**: The architecture is Apache Kafka compatible (`aiokafka` producer/consumer interfaces). The local throughput benchmarks reported below execute against the **in-process streaming queue backend**.

## 1. Latency Breakdown by Operational Scope

| Operational Scope | Evaluated Target | P50 Latency | P95 Latency | P99 Latency | Metric Unit |
|---|---|---|---|---|---|
| **Scope A: Model Inference** | `FusionModel` CPU Batched Forward (B=64) | 14.277 | 67.985 | 97.228 | ms / batch |
| **Scope B: Feature Updates** | `HostFeatureState` Window & Sketch Ingestion | 52.506 | 63.01 | 78.76 | $\mu$s / event |
| **Scope C: Attack Reconstruction** | Dijkstra Shortest Path + BFS Blast Radius | 0.075 | 0.143 | 0.365 | ms / query |
| **Scope D: Containment Decision** | `RiskEngine` + `SimulatedFirewall` Policy | 15.5 | 20.91 | 112.32 | $\mu$s / eval |
| **Scope E: Composite Pipeline** | End-to-End In-Process Detection Pipeline | 0.484 | 0.629 | 0.775 | ms / event |

## 2. Ingestion & Inference Throughput Summary

| Component | Tested Scale | Measured Throughput | Standard Deviation | Hardware |
|---|---|---|---|---|
| **Model Batched Inference** | 99,968 simulated events | **3,193.80 events/sec** | $\pm$1552.15 eps | CPU (10 physical cores) |
| **Feature Extraction Engine** | 50,000 simulated events | **19,045.36 events/sec** | - | In-memory O(1) structures |
| **Composite In-Process Pipeline** | Streaming ingestion buffer | **2,065.75 events/sec** | - | In-process queue backend |

*Artifact Reference: `results/throughput_benchmark.json`.*
