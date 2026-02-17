"""Replay Producer — streams MIT-BIH ECG data in real-time to Kafka."""
from __future__ import annotations

import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone

import numpy as np

# Add common to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "common", "src"))

from config import (
    KAFKA_BOOTSTRAP_SERVERS,
    TOPIC_ECG_RAW,
    TOPIC_ECG_BEAT_EVENT,
)
from kafka import wait_for_kafka

from .mitbih_reader import load_record, get_waveform_chunk
from .beat_extractor import extract_beat_segment, PRE_SEC, POST_SEC
from .rr_morph_features import compute_rr4, morphology_features
from .kafka_producer import ECGKafkaProducer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("replay-producer")

# Symbol mapping for MIT-BIH
SYMBOL_MAP = {
    "N": "N", "L": "N", "R": "N", "e": "N", "j": "N",
    "A": "A", "a": "A", "S": "A", "J": "A",
    "V": "V", "E": "V",
}


def main():
    data_dir = os.environ.get("MITBIH_DATA_DIR", "/app/data")
    record_name = os.environ.get("MITBIH_RECORD", "223")
    chunk_sec = float(os.environ.get("STREAM_CHUNK_SEC", "1.0"))
    speed = float(os.environ.get("REALTIME_SPEED", "1.0"))
    bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", KAFKA_BOOTSTRAP_SERVERS)

    logger.info(f"Starting replay producer: record={record_name}, chunk={chunk_sec}s, speed={speed}x")

    # Wait for Kafka
    wait_for_kafka(bootstrap)

    # Load record
    record, annotation = load_record(data_dir, record_name)
    fs = record.fs
    p_signal = record.p_signal  # (samples, channels)
    channels_used = [0, 1] if p_signal.shape[1] >= 2 else [0]

    # Create session
    session_id = str(uuid.uuid4())
    patient_id = "d0000000-0000-0000-0000-000000000001"

    # Build beat list from annotations
    beat_samples = list(annotation.sample)
    beat_symbols = list(annotation.symbol)

    # Pre-compute beat events
    beat_events = []
    for i, (samp, sym) in enumerate(zip(beat_samples, beat_symbols)):
        mapped_sym = SYMBOL_MAP.get(sym, None)
        if mapped_sym is None:
            continue

        seg = extract_beat_segment(p_signal, samp, fs, channels_used)
        if seg is None:
            continue

        rr4 = compute_rr4(beat_samples, i, fs)
        m8 = morphology_features(seg)

        beat_events.append({
            "session_id": session_id,
            "record_name": record_name,
            "beat_ts_sec": float(samp / fs),
            "true_sym": mapped_sym,
            "fs": fs,
            "seg": seg.tolist(),
            "rr4": rr4,
            "m8": m8,
            "channels_used": channels_used,
            "seg_len": seg.shape[1],
        })

    logger.info(f"Prepared {len(beat_events)} beat events for session {session_id}")

    # Initialize Kafka producer
    producer = ECGKafkaProducer(bootstrap)

    # Stream waveform + beat events
    chunk_samples = int(chunk_sec * fs)
    total_samples = p_signal.shape[0]
    total_chunks = total_samples // chunk_samples
    beat_event_idx = 0

    logger.info(f"Streaming {total_chunks} chunks ({total_samples / fs:.1f}s total)")

    for chunk_i in range(total_chunks):
        start_sample = chunk_i * chunk_samples
        end_sample = start_sample + chunk_samples
        chunk_time_sec = start_sample / fs

        # Send waveform chunk
        waveform = get_waveform_chunk(record, start_sample, chunk_samples)
        if waveform is not None:
            ts_start = datetime.now(timezone.utc).isoformat()
            raw_msg = {
                "session_id": session_id,
                "patient_id": patient_id,
                "ts_start": ts_start,
                "fs": fs,
                "lead": record.sig_name[:len(channels_used)],
                "samples": waveform.tolist(),
            }
            producer.produce(TOPIC_ECG_RAW, raw_msg, key=session_id)

        # Send beat events that fall within this chunk
        while beat_event_idx < len(beat_events):
            evt = beat_events[beat_event_idx]
            if evt["beat_ts_sec"] < end_sample / fs:
                producer.produce(TOPIC_ECG_BEAT_EVENT, evt, key=session_id)
                beat_event_idx += 1
            else:
                break

        producer.flush()

        # Real-time pacing
        sleep_time = chunk_sec / speed
        time.sleep(sleep_time)

        if chunk_i % 10 == 0:
            logger.info(f"Chunk {chunk_i}/{total_chunks} | t={chunk_time_sec:.1f}s | beats sent: {beat_event_idx}")

    logger.info(f"Replay complete. Total beats sent: {beat_event_idx}")
    producer.flush()


if __name__ == "__main__":
    main()
