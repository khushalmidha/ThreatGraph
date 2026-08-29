import json
import asyncio
import logging
from aiokafka import AIOKafkaProducer
import os
import sys

# Add parent directory to path to import generator modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from traffic.generator.network import EnterpriseNetwork
from traffic.generator.scenarios import ScenarioGenerator

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    # Wait for Kafka to be ready
    while True:
        try:
            await producer.start()
            break
        except Exception as e:
            logger.warning(f"Waiting for Kafka: {e}")
            await asyncio.sleep(5)
            
    network = EnterpriseNetwork(num_hosts=200)
    scenarios = ScenarioGenerator(network)

    try:
        logger.info("Starting Flow Collector...")
        while True:
            # Generate baseline
            events = scenarios.generate_normal_traffic(count=10)
            
            # Send to Kafka
            for event in events:
                await producer.send_and_wait("network_events", event)
                
            logger.info(f"Sent {len(events)} normal events")
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        logger.info("Collector stopped")
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(main())
