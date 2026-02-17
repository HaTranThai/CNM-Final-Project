"""Shared configuration reader from environment variables."""
import os


def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def get_env_float(key: str, default: float = 0.0) -> float:
    return float(os.environ.get(key, str(default)))


def get_env_int(key: str, default: int = 0) -> int:
    return int(os.environ.get(key, str(default)))


# Common config
KAFKA_BOOTSTRAP_SERVERS = get_env("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
DATABASE_URL = get_env("DATABASE_URL", "postgresql+asyncpg://ecg_admin:ecg_secret_2024@localhost:5432/ecg_cdss")

# Topics
TOPIC_ECG_RAW = "ecg_raw"
TOPIC_ECG_BEAT_EVENT = "ecg_beat_event"
TOPIC_ECG_WAVEFORM = "ecg_waveform"
TOPIC_ECG_BEAT_READY = "ecg_beat_ready"
TOPIC_ECG_PRED_BEAT = "ecg_pred_beat"
TOPIC_ECG_ALERT = "ecg_alert"
