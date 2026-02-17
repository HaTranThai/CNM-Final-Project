"""Shared message schemas for Kafka topics."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


def new_uuid() -> str:
    return str(uuid.uuid4())


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


# ── ecg_raw ──
class ECGRawMessage(BaseModel):
    session_id: str
    patient_id: str
    ts_start: str
    fs: int = 360
    lead: list[str] = ["MLII", "V1"]
    samples: list[list[float]]  # (C, chunk_len)


# ── ecg_beat_event ──
class ECGBeatEventMessage(BaseModel):
    session_id: str
    record_name: str
    beat_ts_sec: float
    true_sym: str
    fs: int = 360
    seg: list[list[float]]  # (C, seg_len)
    rr4: list[float]  # (4,)
    m8: list[float]  # (8,)
    channels_used: list[int] = [0, 1]
    seg_len: int


# ── ecg_waveform (for UI) ──
class ECGWaveformMessage(BaseModel):
    session_id: str
    ts_start: str
    fs: int = 360
    lead: list[str] = ["MLII", "V1"]
    samples: list[list[float]]
    sqi: float = 1.0  # signal quality index 0-1


# ── ecg_beat_ready (normalized for inference) ──
class ECGBeatReadyMessage(BaseModel):
    session_id: str
    record_name: str
    beat_ts_sec: float
    true_sym: str
    fs: int = 360
    seg: list[list[float]]
    rr4: list[float]
    m8: list[float]
    channels_used: list[int]
    seg_len: int


# ── ecg_pred_beat ──
class ECGPredBeatMessage(BaseModel):
    session_id: str
    beat_ts_sec: float
    pred_class: str
    confidence: float
    pA: float
    model_version: str = "mitbih_v25"
    probs: dict[str, float]
    gated_A: bool = False


# ── ecg_alert ──
class ECGAlertMessage(BaseModel):
    alert_id: str = Field(default_factory=new_uuid)
    session_id: str
    start_time: str = Field(default_factory=now_iso)
    last_update: str = Field(default_factory=now_iso)
    alert_type: str  # "A" or "V"
    status: str = "NEW"
    severity: float = 0.0
    model_version: str = "mitbih_v25"
    evidence: dict = Field(default_factory=dict)
