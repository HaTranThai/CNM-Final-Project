"""Alert Engine Service — consumes predictions, applies alert rules, produces alerts."""
from __future__ import annotations

import json
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "common", "src"))

from confluent_kafka import KafkaError
from config import TOPIC_ECG_PRED_BEAT, TOPIC_ECG_ALERT
from kafka import wait_for_kafka

from .config import AlertConfig
from .state import StateManager
from .rules import check_v_alert, check_a_alert
from .kafka_io import create_consumer, create_producer, produce
from .db_writer import DBWriter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
logger = logging.getLogger("alert-engine")


def main():
    bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    config = AlertConfig()

    logger.info(f"Starting alert engine: {config}")

    # Wait for Kafka
    wait_for_kafka(bootstrap)

    # Initialize
    consumer = create_consumer(
        group_id="alert-engine-group",
        topics=[TOPIC_ECG_PRED_BEAT],
    )
    producer = create_producer()
    state_mgr = StateManager()
    db_writer = DBWriter()

    alert_count = 0
    beat_count = 0

    logger.info("Alert engine started. Waiting for predictions...")

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

            try:
                value = json.loads(msg.value().decode("utf-8"))
            except Exception as e:
                logger.error(f"Failed to parse: {e}")
                continue

            session_id = value.get("session_id", "")
            beat_ts = value.get("beat_ts_sec", 0)
            pred_class = value.get("pred_class", "N")
            pA = value.get("pA", 0)
            confidence = value.get("confidence", 0)

            # Add beat to session state
            session_state = state_mgr.get_session(session_id)
            session_state.add_beat(beat_ts, pred_class, pA, confidence)
            beat_count += 1

            # Optionally persist prediction
            db_writer.insert_prediction(session_id, value)

            # Check V alert
            v_alert = check_v_alert(session_state, beat_ts, config)
            if v_alert:
                v_alert["session_id"] = session_id
                v_alert["model_version"] = value.get("model_version", "mitbih_v25")
                produce(producer, TOPIC_ECG_ALERT, v_alert, key=session_id)
                db_writer.insert_alert(session_id, v_alert)
                alert_count += 1
                logger.warning(f"🚨 V ALERT: session={session_id[:8]}... count={v_alert['evidence']['count']}")

            # Check A alert
            a_alert = check_a_alert(session_state, beat_ts, config)
            if a_alert:
                a_alert["session_id"] = session_id
                a_alert["model_version"] = value.get("model_version", "mitbih_v25")
                produce(producer, TOPIC_ECG_ALERT, a_alert, key=session_id)
                db_writer.insert_alert(session_id, a_alert)
                alert_count += 1
                logger.warning(f"🚨 A ALERT: session={session_id[:8]}... count={a_alert['evidence']['count']}")

            if beat_count % 100 == 0:
                logger.info(f"Processed {beat_count} beats, {alert_count} alerts")

            producer.flush()

    except KeyboardInterrupt:
        logger.info("Shutting down.")
    finally:
        consumer.close()
        producer.flush()
        db_writer.close()


if __name__ == "__main__":
    main()
