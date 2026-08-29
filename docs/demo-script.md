# NetRaptor-X Demo Script

## 12-Phase Demonstration Sequence

1. **Baseline Traffic (Normal)**: System ingests benign synthetic background traffic. Dashboard shows low risk, no incidents.
2. **Behavior Change**: Inject an initial suspicious behavior (e.g., unusual port scan).
3. **Destination Increase**: Host begins connecting to more unique internal destinations (simulating enumeration/lateral movement).
4. **Topology Change**: Graph updates show new edges forming a distinct pattern compared to historical baselines.
5. **GNN + Transformer Detect**: The fused model flags the behavior, assigning high threat probabilities to the sequence.
6. **Risk Engine Escalation**: Host risk score crosses the HIGH/CRITICAL threshold due to the sustained model predictions.
7. **Incident Creation**: The Incident Service automatically aggregates the alerts into a single tracked Incident.
8. **Attack Path Generation**: Shortest-path analysis reconstructs the propagation path, showing the source and potential blast radius.
9. **LLM SOC Investigation**: RAG-powered LLM analyzes the structured evidence and outputs a labeled report.
10. **MITRE Mapping**: LLM provides probable ATT&CK tactics/techniques based on the generated evidence.
11. **Containment Recommendation**: LLM recommends specific isolation policies.
12. **Simulated Isolation**: Analyst approves containment. Policy is applied, and subsequent synthetic traffic from the host is visibly blocked, bringing the risk score down.
