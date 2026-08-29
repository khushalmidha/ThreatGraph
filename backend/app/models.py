from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Host(Base):
    __tablename__ = "hosts"
    host_id = Column(String, primary_key=True, index=True)
    ip_address = Column(String, index=True)
    hostname = Column(String)
    host_type = Column(String)
    criticality = Column(String)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)

class NetworkFlow(Base):
    __tablename__ = "network_flows"
    event_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    src_ip = Column(String, index=True)
    dst_ip = Column(String, index=True)
    src_port = Column(Integer)
    dst_port = Column(Integer)
    protocol = Column(String)
    packets = Column(Integer)
    bytes = Column(Integer)
    duration_ms = Column(Float)
    vlan = Column(Integer)
    direction = Column(String)
    event_version = Column(String)

class GraphEvent(Base):
    __tablename__ = "graph_events"
    event_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    node_a = Column(String, index=True)
    node_b = Column(String, index=True)
    edge_type = Column(String)
    edge_features = Column(JSON)

class Feature(Base):
    __tablename__ = "features"
    feature_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    host_id = Column(String, index=True)
    window_size = Column(String)
    feature_vector = Column(JSON)

class ModelPrediction(Base):
    __tablename__ = "model_predictions"
    prediction_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    host_id = Column(String, index=True)
    model_version = Column(String)
    threat_probability = Column(Float)
    threat_class = Column(String)
    anomaly_score = Column(Float)

class Anomaly(Base):
    __tablename__ = "anomalies"
    anomaly_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    host_id = Column(String, index=True)
    score = Column(Float)
    description = Column(String)

class Alert(Base):
    __tablename__ = "alerts"
    alert_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    host_id = Column(String, index=True)
    severity = Column(String)
    evidence = Column(JSON)

class Incident(Base):
    __tablename__ = "incidents"
    incident_id = Column(String, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    title = Column(String)
    status = Column(String) # OPEN, INVESTIGATING, RESOLVED
    severity = Column(String)
    target_host = Column(String)
    risk_score = Column(Float)

class RiskScore(Base):
    __tablename__ = "risk_scores"
    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    score = Column(Float)
    severity_band = Column(String)
    evidence = Column(JSON)

class AttackPath(Base):
    __tablename__ = "attack_paths"
    path_id = Column(String, primary_key=True, index=True)
    incident_id = Column(String, ForeignKey("incidents.incident_id"), index=True)
    source_host = Column(String)
    dest_host = Column(String)
    risk_contribution = Column(Float)
    evidence = Column(JSON)

class RiskScore(Base):
    __tablename__ = "risk_scores"
    risk_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    host_id = Column(String, index=True)
    score = Column(Float)
    severity_band = Column(String)
    evidence = Column(JSON)

class ContainmentAction(Base):
    __tablename__ = "containment_actions"
    action_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    host_id = Column(String, index=True)
    policy_applied = Column(String)
    reason = Column(String)
    status = Column(String)

class NetworkPolicy(Base):
    __tablename__ = "network_policies"
    policy_id = Column(String, primary_key=True, index=True)
    zone_source = Column(String)
    zone_dest = Column(String)
    action = Column(String)
    port = Column(Integer)
    protocol = Column(String)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    log_id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True)
    user_id = Column(String)
    action = Column(String)
    target = Column(String)
    result = Column(String)

class ModelVersion(Base):
    __tablename__ = "model_versions"
    version_id = Column(String, primary_key=True, index=True)
    trained_at = Column(DateTime)
    dataset_ref = Column(String)
    metrics = Column(JSON)
    is_active = Column(Boolean, default=False)

class ContainmentAction(Base):
    __tablename__ = "containment_actions"
    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(String, index=True)
    action = Column(String)
    policy = Column(String)
    reason = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    role = Column(String)
    action = Column(String)
    resource = Column(String)
    status = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

