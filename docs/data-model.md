# NetRaptor-X Data Model

## Event Schema
The fundamental unit of network activity.

### Pydantic Model
```python
from pydantic import BaseModel, Field, IPvAnyAddress
from datetime import datetime

class NetworkEvent(BaseModel):
    event_id: str = Field(..., description="Unique identifier for the event")
    timestamp: datetime = Field(..., description="Event timestamp")
    src_ip: IPvAnyAddress = Field(..., description="Source IP address")
    dst_ip: IPvAnyAddress = Field(..., description="Destination IP address")
    src_port: int = Field(..., ge=0, le=65535, description="Source port")
    dst_port: int = Field(..., ge=0, le=65535, description="Destination port")
    protocol: str = Field(..., description="Transport protocol (e.g., TCP, UDP)")
    packets: int = Field(..., ge=0, description="Number of packets")
    bytes: int = Field(..., ge=0, description="Total bytes transferred")
    duration_ms: float = Field(..., ge=0.0, description="Duration in milliseconds")
    vlan: int = Field(..., description="VLAN identifier")
    direction: str = Field(..., description="Traffic direction (e.g., INBOUND, OUTBOUND, INTERNAL)")
    event_version: str = Field(..., description="Version of the event schema")
```

## PostgreSQL Schema
Tables needed for persistence.

- **hosts**: host_id, ip_address, hostname, host_type, criticality, first_seen, last_seen
- **network_flows**: (Matches Event Schema) + Indexes on timestamp, src_ip, dst_ip.
- **graph_events**: event_id, timestamp, node_a, node_b, edge_type, edge_features
- **features**: feature_id, timestamp, host_id, window_size, feature_vector
- **model_predictions**: prediction_id, timestamp, host_id, model_version, threat_probability, threat_class, anomaly_score
- **anomalies**: anomaly_id, timestamp, host_id, score, description
- **alerts**: alert_id, timestamp, host_id, severity, evidence
- **incidents**: incident_id, timestamp, primary_host_id, status, severity, created_at, updated_at
- **attack_paths**: path_id, incident_id, source_host, dest_host, risk_contribution, evidence
- **risk_scores**: risk_id, timestamp, host_id, score (0-100), severity_band, evidence
- **containment_actions**: action_id, timestamp, host_id, policy_applied, reason, status
- **network_policies**: policy_id, zone_source, zone_dest, action, port, protocol
- **audit_logs**: log_id, timestamp, user_id, action, target, result
- **model_versions**: version_id, trained_at, dataset_ref, metrics, is_active

*Indexes*: timestamp, source/destination IP, host ID, severity, incident status.

## Graph Representation
**Update Strategy**: Event-based temporal graph updates.
*Rationale*: A stream-based event approach allows more granular tracking of temporal dynamics and avoids the overhead and loss of precision inherent in discrete periodic snapshots. Memory features (like in TGN) naturally align with an event-driven edge ingestion process.

**Node Types**: workstation, server, database, identity_service, security_infrastructure, external_endpoint
**Node Features**: host statistics, historical behavior baselines.
**Edge Types**: communication (with protocol/direction)
**Edge Features**: duration, bytes, packets, ports.
