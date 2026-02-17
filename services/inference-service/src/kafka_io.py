"""Kafka I/O for inference service."""
from __future__ import annotations

import json
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "common", "src"))

from confluent_kafka import Consumer, Producer
from config import KAFKA_BOOTSTRAP_SERVERS

logger = logging.getLogger(__name__)


def create_consumer(group_id: str, topics: list[str]) -> Consumer:
    bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", KAFKA_BOOTSTRAP_SERVERS)
    conf = {
        "bootstrap.servers": bootstrap,
        "group.id": group_id,
        "auto.offset.reset": "latest",
        "enable.auto.commit": True,
    }
    consumer = Consumer(conf)
    consumer.subscribe(topics)
    return consumer


def create_producer() -> Producer:
    bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", KAFKA_BOOTSTRAP_SERVERS)
    return Producer({
        "bootstrap.servers": bootstrap,
        "client.id": "inference-service",
    })


def produce(producer: Producer, topic: str, value: dict, key: str | None = None):
    producer.produce(
        topic=topic,
        value=json.dumps(value).encode("utf-8"),
        key=key.encode("utf-8") if key else None,
    )
    producer.poll(0)
