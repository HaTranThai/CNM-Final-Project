"""Kafka producer for ECG data."""
from __future__ import annotations

import json
import logging

from confluent_kafka import Producer

logger = logging.getLogger(__name__)


class ECGKafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self.producer = Producer({
            "bootstrap.servers": bootstrap_servers,
            "client.id": "replay-producer",
            "acks": "1",
        })

    def produce(self, topic: str, value: dict, key: str | None = None):
        """Send a JSON message to a Kafka topic."""
        try:
            self.producer.produce(
                topic=topic,
                value=json.dumps(value).encode("utf-8"),
                key=key.encode("utf-8") if key else None,
            )
            self.producer.poll(0)
        except Exception as e:
            logger.error(f"Produce error on {topic}: {e}")

    def flush(self):
        self.producer.flush()
