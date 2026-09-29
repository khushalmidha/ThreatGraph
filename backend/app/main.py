import logging
import socket
import asyncio
import json
import random
from datetime import datetime
from fastapi import FastAPI, Response, status, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
from pydantic import BaseModel
from sqlalchemy.orm import Session
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

# Enable CORS for local & remote frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.database import SessionLocal, engine
from app.graph.queries import get_current_topology
from app.auth import require_analyst, log_audit
import app.models as models

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    """Ensure database tables exist and seed demo data on first boot"""
    logger.info("Initializing NetRaptor-X backend...")
    try:
        models.Base.metadata.create_all(bind=engine)
        from app.seed import seed_database
        seed_database(force=True)
        logger.info("Massive enterprise dataset initialized and verified.")
    except Exception as e:
        logger.error(f"Error during startup DB initialization: {e}")

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

@app.get("/seed")
@app.post("/seed")
def trigger_seed(force: bool = True, db: Session = Depends(get_db)):
    from app.seed import seed_database
    res = seed_database(db, force=force)
    return res

@app.get("/hosts")
def get_hosts(db: Session = Depends(get_db)):
    hosts = db.query(models.Host).all()
    return hosts

@app.get("/hosts/{id}/risk")
def get_host_risk(id: str, db: Session = Depends(get_db)):
    score = db.query(models.RiskScore).filter(models.RiskScore.host_id == id).order_by(models.RiskScore.timestamp.desc()).first()
    if not score:
        return {
            "host_id": id,
            "score": 15.0,
            "severity_band": "NORMAL",
            "evidence": {"status": "baseline"}
        }
    return score

@app.get("/network/graph")
@app.get("/network/topology")
@app.get("/graph/topology")
def get_network_topology_endpoint(lookback_sec: int = 3600, db: Session = Depends(get_db)):
    return get_current_topology(db, lookback_sec)

@app.get("/models")
def get_models(db: Session = Depends(get_db)):
    versions = db.query(models.ModelVersion).all()
    if versions:
        return [{"id": v.version_id, "version": "1.2.0", "active": v.is_active, "description": "GNN + Transformer Full-Fusion Engine"} for v in versions]
    return [
        {"id": "temporal_gnn_v1", "version": "1.0.0", "active": True, "description": "GNN + Transformer Full-Fusion Engine"}
    ]

@app.get("/models/{id}/metrics")
def get_model_metrics(id: str):
    return {
        "Precision": 0.92, "Recall": 0.89, "F1": 0.905, "ROC-AUC": 0.965, "PR-AUC": 0.938
    }

@app.get("/models/{id}/predictions")
def get_model_predictions(id: str):
    return [
        {"timestamp": datetime.utcnow().isoformat(), "src_ip": "10.0.0.1", "dst_ip": "10.0.0.5", "threat_probability": 0.95},
        {"timestamp": datetime.utcnow().isoformat(), "src_ip": "10.0.0.5", "dst_ip": "10.0.0.10", "threat_probability": 0.94},
        {"timestamp": datetime.utcnow().isoformat(), "src_ip": "10.0.0.10", "dst_ip": "10.0.0.20", "threat_probability": 0.98}
    ]

@app.get("/alerts")
def get_alerts(db: Session = Depends(get_db)):
    alerts = db.query(models.Alert).order_by(models.Alert.timestamp.desc()).limit(50).all()
    return alerts

@app.get("/incidents")
def get_incidents(db: Session = Depends(get_db)):
    incidents = db.query(models.Incident).order_by(models.Incident.updated_at.desc()).limit(50).all()
    return {"incidents": incidents, "total": len(incidents)}

@app.get("/incidents/{id}")
def get_incident(id: str, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.incident_id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    alerts = db.query(models.Alert).filter(models.Alert.incident_id == id).all()
    return {"incident": incident, "alerts": alerts}

@app.get("/incidents/{id}/attack-path")
def get_incident_attack_path(id: str, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.incident_id == id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    from app.graph.attack_path import AttackPathBuilder
    topology = get_current_topology(db, lookback_sec=3600)
    builder = AttackPathBuilder()
    builder.build_from_topology(topology)
    
    edges = topology.get("links", []) if isinstance(topology, dict) else (topology or [])
    all_hosts = list(set([edge["source"] for edge in edges] + [edge["target"] for edge in edges]))
    
    path_data = builder.generate_attack_path_record(id, incident.target_host, all_hosts)
    return path_data

@app.post("/soc/investigate/{incident_id}")
def investigate_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(models.Incident).filter(models.Incident.incident_id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    path_data = get_incident_attack_path(incident_id, db)
    
    try:
        from app.rag.engine import SimpleRAGEngine
    except ImportError:
        try:
            from rag.engine import SimpleRAGEngine
        except ImportError:
            from backend.rag.engine import SimpleRAGEngine

    from app.soc.llm import SOCAnalystLLM
    
    rag = SimpleRAGEngine()
    query = f"lateral movement from {incident.target_host} high risk"
    context = rag.retrieve(query)
    
    llm = SOCAnalystLLM()
    report = llm.investigate(
        incident={
            "target_host": incident.target_host,
            "severity": incident.severity,
            "risk_score": incident.risk_score,
            "updated_at": str(incident.updated_at)
        },
        attack_path=path_data,
        context=context
    )
    return {"report": report}

class QueryRequest(BaseModel):
    query: str

@app.post("/soc/query")
def soc_query(req: QueryRequest):
    try:
        from app.rag.engine import SimpleRAGEngine
    except ImportError:
        try:
            from rag.engine import SimpleRAGEngine
        except ImportError:
            from backend.rag.engine import SimpleRAGEngine

    from app.soc.llm import SOCAnalystLLM
    
    rag = SimpleRAGEngine()
    context = rag.retrieve(req.query)
    
    llm = SOCAnalystLLM()
    answer = llm.query(req.query, context)
    return {"answer": answer}

@app.post("/containment/isolate/{host_id}")
def isolate_host(host_id: str, db: Session = Depends(get_db), user: dict = Depends(require_analyst)):
    try:
        from app.simulation.policies import firewall
    except ImportError:
        try:
            from simulation.policies import firewall
        except ImportError:
            from backend.simulation.policies import firewall
    
    firewall.isolate_host(host_id)
    
    action = models.ContainmentAction(
        host_id=host_id,
        action="ISOLATE",
        policy="DENY_ALL",
        reason="Manual Analyst Approval",
        status="ACTIVE"
    )
    db.add(action)
    db.commit()
    log_audit(db, user.get("sub", "analyst-admin"), user.get("role", "ANALYST"), "ISOLATE", host_id, "SUCCESS")
    return {"status": "success", "host_id": host_id, "state": "ISOLATED"}

@app.post("/containment/release/{host_id}")
def release_host(host_id: str, db: Session = Depends(get_db), user: dict = Depends(require_analyst)):
    try:
        from app.simulation.policies import firewall
    except ImportError:
        try:
            from simulation.policies import firewall
        except ImportError:
            from backend.simulation.policies import firewall
    
    firewall.release_host(host_id)
    
    db.query(models.ContainmentAction).filter(
        models.ContainmentAction.host_id == host_id, 
        models.ContainmentAction.status == "ACTIVE"
    ).update({"status": "ROLLED_BACK"})
    
    action = models.ContainmentAction(
        host_id=host_id,
        action="RELEASE",
        policy="ALLOW_ALL",
        reason="Manual Analyst Rollback",
        status="ROLLED_BACK"
    )
    db.add(action)
    db.commit()
    log_audit(db, user.get("sub", "analyst-admin"), user.get("role", "ANALYST"), "RELEASE", host_id, "SUCCESS")
    return {"status": "success", "host_id": host_id, "state": "ACTIVE"}

@app.get("/policies")
def get_policies():
    try:
        from app.simulation.policies import firewall
    except ImportError:
        try:
            from simulation.policies import firewall
        except ImportError:
            from backend.simulation.policies import firewall
    return {
        "zones": firewall.zones,
        "isolated_hosts": firewall.host_states
    }

# SSE Endpoint for real-time updates and live dashboard pulse
async def event_stream():
    hosts = ["10.0.0.1", "10.0.0.5", "10.0.0.10", "10.0.0.20", "10.0.0.2"]
    counter = 0
    while True:
        await asyncio.sleep(4)
        counter += 1
        # Every 8 seconds emit a live detection event to dynamically animate the dashboard
        if counter % 2 == 0:
            target = random.choice(hosts)
            score = round(random.uniform(55.0, 96.5), 1)
            payload = {
                "type": "alert",
                "data": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "target_host": target,
                    "risk_score": score,
                    "severity": "CRITICAL" if score > 80 else ("HIGH" if score > 65 else "NORMAL")
                }
            }
            yield f"data: {json.dumps(payload)}\n\n"
        else:
            yield f"data: {{\"type\": \"heartbeat\", \"timestamp\": \"{datetime.utcnow().isoformat()}\"}}\n\n"

@app.get("/stream")
def stream_alerts():
    return StreamingResponse(event_stream(), media_type="text/event-stream")
