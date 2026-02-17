"""Kafka consumer service — runs in background thread, feeds WS broadcaster."""
from __future__ import annotations

import asyncio
import json
import logging
import threading
from typing import Optional

from confluent_kafka import Consumer, KafkaError

from app.core.config import settings
from app.services.ws_broadcaster import ws_broadcaster

logger = logging.getLogger(__name__)

TOPICS = ["ecg_waveform", "ecg_pred_beat", "ecg_alert"]


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
        try:
            consumer = Consumer({
                "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                "group.id": "backend-ws-group",
                "auto.offset.reset": "latest",
                "enable.auto.commit": True,
            })
            consumer.subscribe(TOPICS)
            logger.info(f"Kafka consumer subscribed to: {TOPICS}")

            while self._running:
                msg = consumer.poll(timeout=0.5)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    logger.error(f"Kafka error: {msg.error()}")
                    continue

                topic = msg.topic()
                try:
                    value = json.loads(msg.value().decode("utf-8"))
                except Exception as e:
                    logger.error(f"Failed to parse: {e}")
                    continue

                session_id = value.get("session_id", "")

                # Map topic to WS message type
                if topic == "ecg_waveform":
                    msg_type = "waveform"
                elif topic == "ecg_pred_beat":
                    msg_type = "prediction"
                elif topic == "ecg_alert":
                    msg_type = "alert"
                else:
                    continue

                # Schedule broadcast on the event loop
                if self._loop and self._loop.is_running():
                    asyncio.run_coroutine_threadsafe(
                        ws_broadcaster.broadcast(session_id, msg_type, value),
                        self._loop,
                    )

            consumer.close()
        except Exception as e:
            logger.error(f"Kafka consumer error: {e}", exc_info=True)
