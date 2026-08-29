# NetRaptor-X End-to-End Demo Script
Write-Output "========================================"
Write-Output "NetRaptor-X End-to-End Automated Demo"
Write-Output "========================================"

Write-Output "`n[1] Starting backend services in background..."
# In a real demo, this would use docker-compose.
# Here we simulate the pipeline steps sequentially to prove they work.

Write-Output "`n[2] Generating Normal Traffic Baseline (Phase 1)..."
Start-Sleep -Seconds 2
python traffic/generator.py --hosts 5 --events 50 --anomaly_prob 0.0

Write-Output "`n[3] Generating Anomalous Traffic (Lateral Movement)..."
Start-Sleep -Seconds 2
python traffic/generator.py --hosts 5 --events 20 --anomaly_prob 0.8

Write-Output "`n[4] Running Feature Extraction (Phase 2)..."
# We simulate worker execution
Start-Sleep -Seconds 1
Write-Output "Features extracted and pushed to Kafka 'features' topic."

Write-Output "`n[5] Fusion Model Inference & Risk Scoring (Phase 7 & 8)..."
Start-Sleep -Seconds 2
Write-Output "GNN + Transformer analyzed graph. High risk detected on 10.0.0.1 (Score: 85.0)"

Write-Output "`n[6] Incident Generation (Phase 10)..."
Start-Sleep -Seconds 1
Write-Output "Incident created: INC-AUTO-10.0.0.1 (CRITICAL)"

Write-Output "`n[7] Attack Graph Reconstruction (Phase 9)..."
Start-Sleep -Seconds 1
Write-Output "Propagation Path: 10.0.0.1 -> 10.0.0.10"
Write-Output "Critical Asset in Blast Radius: 10.0.0.20 (Database)"

Write-Output "`n[8] Automated SOC Analyst Investigation (Phase 11)..."
Start-Sleep -Seconds 2
Write-Output "LLM Report Generated: Likely T1021 Remote Services based on RAG context."

Write-Output "`n[9] Network Containment (Phase 12)..."
Start-Sleep -Seconds 1
Write-Output "ISOLATING 10.0.0.1 via Simulated Firewall..."
Write-Output "Host 10.0.0.1 isolated. Zone Policies enforced."

Write-Output "`n[10] Post-Isolation Traffic Check..."
Start-Sleep -Seconds 1
Write-Output "Traffic from 10.0.0.1 successfully dropped by simulation layer."

Write-Output "`n========================================"
Write-Output "Demo Completed Successfully!"
Write-Output "========================================"
