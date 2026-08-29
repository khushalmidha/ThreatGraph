import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import os
import datetime
import uuid
import sys
import torch

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.app.database import SessionLocal
from backend.app.models import Incident, Alert

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DetectionWorker:
    def __init__(self):
        # We would load the fusion model here. For Phase 8 we simulate the score.
        self.active_incidents = {}

    async def run(self):
        consumer = AIOKafkaConsumer(
            "features", # Consuming features
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id="detection_worker_group",
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

        while True:
            try:
                await consumer.start()
                await producer.start()
                break
            except Exception as e:
                logger.warning(f"Waiting for Kafka: {e}")
                await asyncio.sleep(5)

        logger.info("Detection worker running...")
        try:
            from backend.app.risk.engine import RiskEngine
            from backend.app.models import RiskScore
            risk_engine = RiskEngine()
            db = SessionLocal()
            
            async for msg in consumer:
                event = msg.value
                host_ip = event.get('host_id', 'unknown')
                
                # Mock fusion model predictions
                graph_prob = 0.8
                transformer_prob = 0.9
                anomaly = 8.5
                
                # Calculate real risk using the engine
                risk_result = risk_engine.calculate_risk(
                    host_id=host_ip,
                    graph_prob=graph_prob,
                    transformer_prob=transformer_prob,
                    anomaly_score=anomaly,
                    historical_risk=0.5
                )
                
                risk_score = risk_result['score']
                
                # Persist risk score
                new_risk = RiskScore(
                    host_id=host_ip,
                    score=risk_score,
                    severity_band=risk_result['severity_band'],
                    evidence=risk_result['evidence']
                )
                db.add(new_risk)
                db.commit()
                
                if risk_score > 74.99: # HIGH or CRITICAL
                    self.handle_high_risk(db, host_ip, risk_score, event)
                    # Stream over Kafka to be consumed by SSE/WebSockets in FastAPI
                    await producer.send_and_wait("alerts", {
                        "host_ip": host_ip,
                        "risk_score": risk_score,
                        "severity_band": risk_result['severity_band'],
                        "timestamp": event.get('timestamp')
                    })
                
        except asyncio.CancelledError:
            pass
        finally:
            db.close()
            await consumer.stop()
            await producer.stop()

    def handle_high_risk(self, db, host_ip, risk_score, event):
        try:
            # Check for active incident for this host
            active = db.query(Incident).filter(
                Incident.target_host == host_ip, 
                Incident.status == "OPEN"
            ).first()
            
            if not active:
                new_incident = Incident(
                    incident_id=str(uuid.uuid4()),
                    created_at=datetime.datetime.utcnow(),
                    updated_at=datetime.datetime.utcnow(),
                    title=f"High Risk Behavior Detected on {host_ip}",
                    status="OPEN",
                    severity="CRITICAL" if risk_score > 90 else "HIGH",
                    target_host=host_ip,
                    risk_score=risk_score
                )
                db.add(new_incident)
                db.commit()
                logger.info(f"Created new incident for {host_ip}")
                active = new_incident
            else:
                active.updated_at = datetime.datetime.utcnow()
                active.risk_score = max(active.risk_score, risk_score)
                db.commit()
                
            # Create alert linked to incident
            new_alert = Alert(
                alert_id=str(uuid.uuid4()),
                incident_id=active.incident_id,
                timestamp=datetime.datetime.utcnow(),
                rule_name="FusionModel_Anomaly",
                severity="HIGH",
                description=f"Model predicted risk {risk_score:.2f}",
                evidence={"event": event}
            )
            db.add(new_alert)
            db.commit()
            
        except Exception as e:
            logger.error(f"Error handling high risk: {e}")
            db.rollback()
        finally:
            db.close()

if __name__ == "__main__":
    worker = DetectionWorker()
    asyncio.run(worker.run())
