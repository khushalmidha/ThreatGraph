import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer
import os
import datetime
import uuid
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from traffic.feature_extractor.extractor import HostFeatureState
from backend.app.database import SessionLocal
from backend.app.models import Feature

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureWorker:
    def __init__(self):
        self.hosts_state = {}

    async def consume(self):
        consumer = AIOKafkaConsumer(
            "network_events",
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            group_id="feature_worker_group",
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

        while True:
            try:
                await consumer.start()
                break
            except Exception as e:
                logger.warning(f"Waiting for Kafka: {e}")
                await asyncio.sleep(5)

        logger.info("Feature worker listening on network_events...")
        try:
            async for msg in consumer:
                event = msg.value
                src_ip = event.get('src_ip')
                
                if src_ip not in self.hosts_state:
                    self.hosts_state[src_ip] = HostFeatureState(src_ip)
                
                state = self.hosts_state[src_ip]
                try:
                    ts = datetime.datetime.fromisoformat(event['timestamp']).timestamp()
                except ValueError:
                    ts = datetime.datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00')).timestamp()
                
                state.add_event(event, ts)
                
                features = state.extract_features(ts)
                self.save_features(src_ip, event['timestamp'], features)
                
        except asyncio.CancelledError:
            pass
        except KeyboardInterrupt:
            logger.info("Worker stopped")
        finally:
            await consumer.stop()

    def save_features(self, host_ip, timestamp, features):
        db = SessionLocal()
        try:
            try:
                dt = datetime.datetime.fromisoformat(timestamp)
            except ValueError:
                dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            db_feature = Feature(
                feature_id=str(uuid.uuid4()),
                timestamp=dt,
                host_id=host_ip,
                window_size="all",
                feature_vector=features
            )
            db.add(db_feature)
            db.commit()
        except Exception as e:
            logger.error(f"Error saving feature: {e}")
            db.rollback()
        finally:
            db.close()

if __name__ == "__main__":
    worker = FeatureWorker()
    asyncio.run(worker.consume())
