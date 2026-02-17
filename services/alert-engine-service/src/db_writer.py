"""Database writer for persisting alerts to Postgres."""
from __future__ import annotations

import json
import logging
import os
import uuid

import psycopg2

logger = logging.getLogger(__name__)


class DBWriter:
    """Persist alerts and predictions to Postgres."""

    def __init__(self):
        # Use sync psycopg2 for simplicity in the service
        db_url = os.environ.get(
            "DATABASE_URL",
            "postgresql+asyncpg://ecg_admin:ecg_secret_2024@postgres:5432/ecg_cdss"
        )
        # Convert asyncpg URL to psycopg2 format
        conn_str = db_url.replace("postgresql+asyncpg://", "postgresql://")
        try:
            self.conn = psycopg2.connect(conn_str)
            self.conn.autocommit = True
            logger.info("Database connection established.")
        except Exception as e:
            logger.warning(f"Database connection failed (will retry on write): {e}")
            self.conn = None

    def _ensure_conn(self):
        if self.conn is None or self.conn.closed:
            db_url = os.environ.get(
                "DATABASE_URL",
                "postgresql://ecg_admin:ecg_secret_2024@postgres:5432/ecg_cdss"
            )
            conn_str = db_url.replace("postgresql+asyncpg://", "postgresql://")
            self.conn = psycopg2.connect(conn_str)
            self.conn.autocommit = True

    def insert_alert(self, session_id: str, alert: dict, model_version_id: str = "c0000000-0000-0000-0000-000000000001"):
        """Insert an alert record into the database."""
        try:
            self._ensure_conn()
            cur = self.conn.cursor()
            cur.execute(
                """
                INSERT INTO alert (alert_id, session_id, model_version_id, start_time, last_update, alert_type, status, severity, evidence_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    alert["alert_id"],
                    session_id,
                    model_version_id,
                    alert["start_time"],
                    alert["last_update"],
                    alert["alert_type"],
                    alert["status"],
                    alert["severity"],
                    json.dumps(alert.get("evidence", {})),
                ),
            )
            cur.close()
            logger.info(f"Alert {alert['alert_id']} persisted to DB.")
        except Exception as e:
            logger.error(f"Failed to insert alert: {e}")

    def insert_prediction(self, session_id: str, pred: dict, model_version_id: str = "c0000000-0000-0000-0000-000000000001"):
        """Insert a prediction record."""
        try:
            self._ensure_conn()
            cur = self.conn.cursor()
            cur.execute(
                """
                INSERT INTO prediction_beat (pred_id, session_id, model_version_id, beat_ts_sec, pred_class, confidence, p_a, probs_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    session_id,
                    model_version_id,
                    pred.get("beat_ts_sec", 0),
                    pred.get("pred_class", "N"),
                    pred.get("confidence", 0),
                    pred.get("pA", 0),
                    json.dumps(pred.get("probs", {})),
                ),
            )
            cur.close()
        except Exception as e:
            logger.error(f"Failed to insert prediction: {e}")

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()
