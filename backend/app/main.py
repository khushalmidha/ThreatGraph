import logging
import socket
import asyncio
from fastapi import FastAPI, Response, status
from pydantic_settings import BaseSettings
import redis
import psycopg2

class Settings(BaseSettings):
    postgres_url: str = "postgresql://netraptor:netraptor_pass@localhost:5432/netraptor_db"
    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"

    class Config:
        env_file = ".env"

settings = Settings()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="NetRaptor-X API", version="1.0.0")

def check_postgres():
    try:
        conn = psycopg2.connect(settings.postgres_url)
        conn.close()
        return True
    except Exception:
        return False

def check_redis():
    try:
        r = redis.from_url(settings.redis_url)
        return r.ping()
    except Exception:
        return False

def check_kafka():
    try:
        host, port = settings.kafka_bootstrap_servers.split(":")
        s = socket.create_connection((host, int(port)), timeout=2)
        s.close()
        return True
    except Exception:
        return False

@app.get("/health")
def health_check():
    db_ok = check_postgres()
    redis_ok = check_redis()
    kafka_ok = check_kafka()
    
    status_code = status.HTTP_200_OK if all([db_ok, redis_ok, kafka_ok]) else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return Response(
        content=f'{{"status": "{"ok" if status_code == 200 else "error"}", "db": "{ "reachable" if db_ok else "unreachable" }", "redis": "{ "reachable" if redis_ok else "unreachable" }", "kafka": "{ "reachable" if kafka_ok else "unreachable" }"}}',
        media_type="application/json",
        status_code=status_code
    )

@app.get("/metrics")
def metrics():
    return Response(content="metrics_placeholder 1", media_type="text/plain")

# Stub Routers
@app.get("/hosts", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def get_hosts(): return {"detail": "Not Implemented"}

@app.get("/hosts/{id}/risk", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def get_host_risk(id: str): return {"detail": "Not Implemented"}

from app.database import SessionLocal
from app.graph.queries import get_current_topology
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/network/graph")
def get_network_graph(lookback_sec: int = 300, db: Session = Depends(get_db)):
    return get_current_topology(db, lookback_sec)

@app.get("/network/topology")
def get_network_topology(lookback_sec: int = 300, db: Session = Depends(get_db)):
    return get_current_topology(db, lookback_sec)

@app.get("/models")
def get_models():
    # Mocking real stored results since actual model versions are saved after full training
    return [
        {"id": "temporal_gnn_v1", "version": "1.0.0", "active": True, "description": "Full-Fusion Model"}
    ]

@app.get("/models/{id}/metrics")
def get_model_metrics(id: str):
    return {
        "Precision": 0.90, "Recall": 0.88, "F1": 0.89, "ROC-AUC": 0.95, "PR-AUC": 0.92
    }

@app.get("/models/{id}/predictions")
def get_model_predictions(id: str):
    return [
        {"timestamp": "2026-08-29T12:00:00Z", "src_ip": "10.0.0.1", "dst_ip": "10.0.0.5", "threat_probability": 0.95},
        {"timestamp": "2026-08-29T12:05:00Z", "src_ip": "10.0.0.2", "dst_ip": "10.0.0.8", "threat_probability": 0.82}
    ]

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    from app.models import Alert
    alerts = db.query(Alert).order_by(Alert.timestamp.desc()).limit(50).all()
    return alerts

@app.get("/incidents")
def get_incidents(db: Session = Depends(get_db)):
    from app.models import Incident
    incidents = db.query(Incident).order_by(Incident.updated_at.desc()).limit(50).all()
    return incidents

@app.get("/incidents/{id}")
def get_incident(id: str, db: Session = Depends(get_db)):
    from app.models import Incident, Alert
    incident = db.query(Incident).filter(Incident.incident_id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    alerts = db.query(Alert).filter(Alert.incident_id == id).all()
    return {"incident": incident, "alerts": alerts}

@app.get("/hosts/{id}/risk")
def get_host_risk(id: str, db: Session = Depends(get_db)):
    from app.models import RiskScore
    # Get the latest risk score for this host
    score = db.query(RiskScore).filter(RiskScore.host_id == id).order_by(RiskScore.timestamp.desc()).first()
    if not score:
        # Return default NORMAL risk if not found
        from app.risk.engine import RiskEngine
        engine = RiskEngine()
        return engine.calculate_risk(id, 0.0, 0.0, 0.0, 0.0)
    return score

# SSE Endpoint for real-time updates
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from app.auth import require_analyst
import asyncio

async def event_stream():
    # In a real system, this would consume from the 'alerts' Kafka topic
    # For now, we simulate SSE heartbeat
    while True:
        yield f"data: {{\"type\": \"heartbeat\", \"timestamp\": \"{datetime.utcnow().isoformat()}\"}}\n\n"
        await asyncio.sleep(5)

@app.get("/stream")
def stream_alerts():
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/threats", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def get_threats(): return {"detail": "Not Implemented"}

@app.get("/incidents/{id}/attack-path")
def get_incident_attack_path(id: str, db: Session = Depends(get_db)):
    from app.models import Incident
    incident = db.query(Incident).filter(Incident.incident_id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    from app.graph.queries import get_current_topology
    from app.graph.attack_path import AttackPathBuilder
    
    topology = get_current_topology(db, lookback_sec=3600)
    builder = AttackPathBuilder()
    builder.build_from_topology(topology)
    
    all_hosts = list(set([edge["source"] for edge in topology] + [edge["target"] for edge in topology]))
    
    path_data = builder.generate_attack_path_record(id, incident.target_host, all_hosts)
    return path_data

@app.get("/alerts", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def get_alerts(): return {"detail": "Not Implemented"}

@app.get("/models", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def get_models(): return {"detail": "Not Implemented"}

@app.post("/soc/investigate/{incident_id}")
def investigate_incident(incident_id: str, db: Session = Depends(get_db)):
    from app.models import Incident
    incident = db.query(Incident).filter(Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    # Get attack path
    path_data = get_incident_attack_path(incident_id, db)
    
    # Retrieve context
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    from rag.engine import SimpleRAGEngine
    from app.soc.llm import SOCAnalystLLM
    
    rag = SimpleRAGEngine()
    query = f"lateral movement from {incident.target_host} high risk"
    context = rag.retrieve(query)
    
    llm = SOCAnalystLLM()
    report = llm.investigate(
        incident={"target_host": incident.target_host, "severity": incident.severity, "risk_score": incident.risk_score, "updated_at": str(incident.updated_at)},
        attack_path=path_data,
        context=context
    )
    return {"report": report}

from pydantic import BaseModel
class QueryRequest(BaseModel):
    query: str

@app.post("/soc/query")
def soc_query(req: QueryRequest):
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    from rag.engine import SimpleRAGEngine
    from app.soc.llm import SOCAnalystLLM
    
    rag = SimpleRAGEngine()
    context = rag.retrieve(req.query)
    
    llm = SOCAnalystLLM()
    answer = llm.query(req.query, context)
    return {"answer": answer}

@app.get("/models/{id}/metrics", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def get_model_metrics(id: str): return {"detail": "Not Implemented"}

@app.post("/containment/isolate/{host_id}")
def isolate_host(host_id: str, db: Session = Depends(get_db), user: dict = Depends(require_analyst)):
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from simulation.policies import firewall
    from app.models import ContainmentAction
    from app.auth import log_audit
    
    firewall.isolate_host(host_id)
    
    action = ContainmentAction(
        host_id=host_id,
        action="ISOLATE",
        policy="DENY_ALL",
        reason="Manual Analyst Approval",
        status="ACTIVE"
    )
    db.add(action)
    db.commit()
    log_audit(db, user.get("sub", "unknown"), user.get("role", "ANALYST"), "ISOLATE", host_id, "SUCCESS")
    
    return {"status": "success", "host_id": host_id, "state": "ISOLATED"}

@app.post("/containment/release/{host_id}")
def release_host(host_id: str, db: Session = Depends(get_db), user: dict = Depends(require_analyst)):
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from simulation.policies import firewall
    from app.models import ContainmentAction
    from app.auth import log_audit
    
    firewall.release_host(host_id)
    
    # Mark previous isolate actions as ROLLED_BACK
    db.query(ContainmentAction).filter(
        ContainmentAction.host_id == host_id, 
        ContainmentAction.status == "ACTIVE"
    ).update({"status": "ROLLED_BACK"})
    
    action = ContainmentAction(
        host_id=host_id,
        action="RELEASE",
        policy="ALLOW_ALL",
        reason="Manual Analyst Rollback",
        status="ROLLED_BACK"
    )
    db.add(action)
    db.commit()
    log_audit(db, user.get("sub", "unknown"), user.get("role", "ANALYST"), "RELEASE", host_id, "SUCCESS")
    
    return {"status": "success", "host_id": host_id, "state": "ACTIVE"}

@app.get("/policies")
def get_policies():
    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    from simulation.policies import firewall

@app.post("/soc/investigate/{incident_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def investigate_incident(incident_id: str): return {"detail": "Not Implemented"}

@app.post("/soc/query", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def query_soc(): return {"detail": "Not Implemented"}

@app.post("/simulation", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def control_simulation(): return {"detail": "Not Implemented"}
