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
from backend.app.models import RiskScore

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
MODEL_PATH = os.path.dirname(__file__) + "/../exports/temporal_gnn.pt"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InferenceWorker:
    def __init__(self):
        self.model = None
        if os.path.exists(MODEL_PATH):
            self.model = torch.jit.load(MODEL_PATH)
            self.model.eval()
            logger.info("Loaded TorchScript model.")
        else:
            logger.warning(f"Model not found at {MODEL_PATH}. Running in dummy mode.")

    async def run(self):
        consumer = AIOKafkaConsumer(
            "network_events", # Real implementation would consume 'features' or 'graph_events' topic
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id="inference_worker_group",
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

        logger.info("Inference worker listening...")
        try:
            async for msg in consumer:
                event = msg.value
                src_ip = event.get('src_ip')
                dst_ip = event.get('dst_ip')
                
                # Mock feature construction - in reality we fetch from DB or memory store
                # using the features emitted by the FeatureWorker
                x = torch.randn(2, 16) # 2 nodes, 16 features
                edge_index = torch.tensor([[0], [1]])
                edge_attr = torch.randn(1, 4)
                
                risk_score_val = 0.1 # default low risk
                
                if self.model:
                    with torch.no_grad():
                        out, _ = self.model(x, edge_index, edge_attr)
                        # Anomaly score is reconstruction error
                        loss = torch.nn.functional.mse_loss(out, x)
                        risk_score_val = float(loss.item())
                        
                # Normalize risk to 0-1 (mock)
                risk_score_val = min(1.0, risk_score_val)
                
                self.save_risk_score(src_ip, dst_ip, risk_score_val, event['timestamp'])
                
                if risk_score_val > 0.8:
                    anomaly_event = {
                        "timestamp": event['timestamp'],
                        "src_ip": src_ip,
                        "dst_ip": dst_ip,
                        "risk_score": risk_score_val,
                        "evidence": "High reconstruction error from Temporal GNN"
                    }
                    await producer.send_and_wait("anomalies", anomaly_event)
                
        except asyncio.CancelledError:
            pass
        except KeyboardInterrupt:
            logger.info("Worker stopped")
        finally:
            await consumer.stop()
            await producer.stop()

    def save_risk_score(self, src_ip, dst_ip, score, timestamp):
        db = SessionLocal()
        try:
            try:
                dt = datetime.datetime.fromisoformat(timestamp)
            except ValueError:
                dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
            db_score = RiskScore(
                score_id=str(uuid.uuid4()),
                timestamp=dt,
                source_host=src_ip,
                dest_host=dst_ip,
                risk_contribution=score,
                evidence={"model": "temporal_gnn", "score": score}
            )
            db.add(db_score)
            db.commit()
        except Exception as e:
            logger.error(f"Error saving risk score: {e}")
            db.rollback()
        finally:
            db.close()

if __name__ == "__main__":
    worker = InferenceWorker()
    asyncio.run(worker.run())
