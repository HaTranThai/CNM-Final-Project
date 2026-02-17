"""Preprocess Buffer Service — consumes raw ECG, produces waveform + beat_ready."""
from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "common", "src"))

from confluent_kafka import KafkaError
from config import (
    TOPIC_ECG_RAW,
    TOPIC_ECG_BEAT_EVENT,
    TOPIC_ECG_WAVEFORM,
    TOPIC_ECG_BEAT_READY,
)
from kafka import wait_for_kafka

from .buffer import WaveformRingBuffer
from .preprocess import downsample, normalize_for_display
from .sqi import compute_sqi
from .kafka_io import create_consumer, create_producer, produce

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("preprocess-buffer")


def main():
    bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    wait_for_kafka(bootstrap)

    consumer = create_consumer(
        group_id="preprocess-buffer-group",
        topics=[TOPIC_ECG_RAW, TOPIC_ECG_BEAT_EVENT],
    )
    producer = create_producer()
    ring_buffer = WaveformRingBuffer(max_seconds=10.0)

    logger.info("Preprocess buffer service started.")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
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
                logger.error(f"Failed to parse message: {e}")
                continue

            if topic == TOPIC_ECG_RAW:
                handle_ecg_raw(value, ring_buffer, producer)
            elif topic == TOPIC_ECG_BEAT_EVENT:
                handle_beat_event(value, producer)

    except KeyboardInterrupt:
        logger.info("Shutting down.")
    finally:
        consumer.close()
        producer.flush()


def handle_ecg_raw(msg: dict, ring_buffer: WaveformRingBuffer, producer):
    """Process raw ECG: buffer + produce waveform for UI."""
    session_id = msg.get("session_id", "")
    samples = msg.get("samples", [])

    # Append to ring buffer
    ring_buffer.append(session_id, samples)

    # Compute SQI on first channel
    sqi = 0.5
    if samples and len(samples[0]) > 0:
        sqi = compute_sqi(samples[0], msg.get("fs", 360))

    # Produce waveform for UI (downsample for performance)
    ds_samples = downsample(samples, factor=2)

    waveform_msg = {
        "session_id": session_id,
        "ts_start": msg.get("ts_start", datetime.now(timezone.utc).isoformat()),
        "fs": msg.get("fs", 360) // 2,  # downsampled fs
        "lead": msg.get("lead", ["MLII", "V1"]),
        "samples": ds_samples,
        "sqi": sqi,
    }
    produce(producer, TOPIC_ECG_WAVEFORM, waveform_msg, key=session_id)


def handle_beat_event(msg: dict, producer):
    """Pass-through beat events as ecg_beat_ready."""
    produce(producer, TOPIC_ECG_BEAT_READY, msg, key=msg.get("session_id", ""))


if __name__ == "__main__":
    main()
