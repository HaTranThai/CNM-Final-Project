"""Pydantic schemas for sessions, alerts, predictions, settings, analytics, WS."""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


# ── Sessions ──
class SessionOut(BaseModel):
    session_id: str
    patient_id: str | None
    start_time: str | None
    end_time: str | None
    source_type: str | None
    status: str
    record_name: str | None
    class Config:
        from_attributes = True


# ── Predictions ──
class PredictionOut(BaseModel):
    pred_id: str
    session_id: str
    beat_ts_sec: float
    pred_class: str
    confidence: float | None
    p_a: float | None
    probs_json: dict | None
    created_at: str | None
    class Config:
        from_attributes = True


# ── Alerts ──
class AlertOut(BaseModel):
    alert_id: str
    session_id: str
    start_time: str | None
    last_update: str | None
    alert_type: str
    status: str
    severity: float | None
    evidence_json: dict | None
    class Config:
        from_attributes = True


class AlertActionRequest(BaseModel):
    reason: str | None = None
    note: str | None = None


class AlertActionOut(BaseModel):
    action_id: str
    alert_id: str
    user_id: str
    action_time: str | None
    action_type: str
    reason: str | None
    note: str | None
    class Config:
        from_attributes = True


class AlertDetailOut(AlertOut):
    actions: list[AlertActionOut] = []


# ── Settings ──
class SettingsUpdate(BaseModel):
    thr_A: Optional[float] = None
    V_WINDOW: Optional[int] = None
    V_THRESH: Optional[int] = None
    COOLDOWN_V: Optional[int] = None
    A_WINDOW: Optional[int] = None
    A_THRESH: Optional[int] = None
    COOLDOWN_A: Optional[int] = None
    STREAM_CHUNK_SEC: Optional[float] = None
    REALTIME_SPEED: Optional[float] = None


class SettingOut(BaseModel):
    key: str
    value: str | float | int | None


# ── Analytics ──
class AlertsHourly(BaseModel):
    hour: str
    count: int
    alert_type: str | None = None


class AnalyticsSummary(BaseModel):
    total_alerts: int
    ack_count: int
    dismiss_count: int
    new_count: int
    dismiss_rate: float
    avg_response_time_sec: float | None


# ── WebSocket ──
class WSMessage(BaseModel):
    type: str  # "waveform" | "prediction" | "alert"
    data: dict
