import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer
import os
import datetime
import uuid
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.app.database import SessionLocal
from backend.app.models import GraphEvent

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphWorker:
    async def consume(self):
        consumer = AIOKafkaConsumer(
            "network_events",
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id="graph_worker_group",
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

        while True:
            try:
                await consumer.start()
                break
            except Exception as e:
                logger.warning(f"Waiting for Kafka: {e}")
                await asyncio.sleep(5)

        logger.info("Graph worker listening on network_events...")
        try:
            async for msg in consumer:
                event = msg.value
                self.save_graph_event(event)
                
        except asyncio.CancelledError:
            pass
        except KeyboardInterrupt:
            logger.info("Worker stopped")
        finally:
            await consumer.stop()

    def save_graph_event(self, event):
        db = SessionLocal()
        try:
            timestamp = event['timestamp']
            try:
                dt = datetime.datetime.fromisoformat(timestamp)
            except ValueError:
                dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
            edge_features = {
                "protocol": event.get("protocol"),
                "ports": [event.get("src_port"), event.get("dst_port")],
                "bytes": event.get("bytes"),
                "duration": event.get("duration_ms"),
                "direction": event.get("direction")
            }
            
            db_event = GraphEvent(
                event_id=event['event_id'],
                timestamp=dt,
                node_a=event['src_ip'],
                node_b=event['dst_ip'],
                edge_type="communication",
                edge_features=edge_features
            )
            db.add(db_event)
            db.commit()
        except Exception as e:
            logger.error(f"Error saving graph event: {e}")
            db.rollback()
        finally:
            db.close()

if __name__ == "__main__":
    worker = GraphWorker()
    asyncio.run(worker.consume())
