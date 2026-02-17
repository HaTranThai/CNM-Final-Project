"""Kafka consumer service — runs in background thread, feeds WS broadcaster."""
from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from typing import Optional

from confluent_kafka import Consumer, KafkaError, KafkaException

from app.core.config import settings
from app.services.ws_broadcaster import ws_broadcaster

logger = logging.getLogger(__name__)

TOPICS = ["ecg_waveform", "ecg_pred_beat", "ecg_alert"]

TOPIC_TO_WS_TYPE = {
    "ecg_waveform": "waveform",
    "ecg_pred_beat": "prediction",
    "ecg_alert": "alert",
}


class KafkaConsumerService:
    """Background Kafka consumer that feeds WebSocket broadcaster."""

    def __init__(self):
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def start(self):
        self._running = True
        self._loop = asyncio.get_event_loop()
        self._thread = threading.Thread(target=self._consume_loop, daemon=True)
        self._thread.start()
        logger.info("Kafka consumer service started.")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Kafka consumer service stopped.")

    def _consume_loop(self):
        msg_counts: dict[str, int] = {t: 0 for t in TOPICS}

        # Retry connection to Kafka
        consumer = None
        for attempt in range(30):
            if not self._running:
                return
            try:
                consumer = Consumer({
                    "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                    "group.id": "backend-ws-group",
                    "auto.offset.reset": "latest",
                    "enable.auto.commit": True,
                    "session.timeout.ms": 30000,
                })
                consumer.subscribe(TOPICS)
                logger.info(f"Kafka consumer subscribed to: {TOPICS}")
                break
            except Exception as e:
                logger.warning(f"Kafka connect attempt {attempt+1}/30 failed: {e}")
                time.sleep(2)

        if consumer is None:
            logger.error("Failed to connect to Kafka after 30 attempts")
            return

        try:
            last_log_time = time.time()
            last_resubscribe_time = time.time()

            while self._running:
                msg = consumer.poll(timeout=0.5)

                # Periodically re-subscribe to discover newly created topics
                now = time.time()
                if now - last_resubscribe_time > 15:
                    consumer.subscribe(TOPICS)
                    last_resubscribe_time = now

                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    logger.error(f"Kafka error: {msg.error()}")
                    continue

                topic = msg.topic()
                msg_type = TOPIC_TO_WS_TYPE.get(topic)
                if msg_type is None:
                    continue

                try:
                    value = json.loads(msg.value().decode("utf-8"))
                except Exception as e:
                    logger.error(f"Failed to parse message from {topic}: {e}")
                    continue

                session_id = value.get("session_id", "")
                msg_counts[topic] = msg_counts.get(topic, 0) + 1

                # Periodic logging (every 30 seconds)
                if now - last_log_time > 30:
                    logger.info(
                        f"Kafka msg counts: {msg_counts} | "
                        f"Active WS sessions: {ws_broadcaster.active_sessions}"
                    )
                    last_log_time = now

                # Schedule broadcast on the event loop
                if self._loop and self._loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        ws_broadcaster.broadcast(session_id, msg_type, value),
                        self._loop,
                    )

            consumer.close()
        except Exception as e:
            logger.error(f"Kafka consumer error: {e}", exc_info=True)
