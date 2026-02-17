"""Per-session state management for alert engine."""
from __future__ import annotations

import collections
import time
from typing import NamedTuple


class BeatRecord(NamedTuple):
    ts_sec: float
    pred_class: str
    pA: float
    confidence: float


class SessionState:
    """State for a single monitoring session."""

    def __init__(self):
        self.beats: collections.deque[BeatRecord] = collections.deque(maxlen=5000)
        self.last_v_alert_time: float = 0.0
        self.last_a_alert_time: float = 0.0

    def add_beat(self, ts_sec: float, pred_class: str, pA: float, confidence: float):
        self.beats.append(BeatRecord(ts_sec, pred_class, pA, confidence))

    def get_recent_beats(self, current_ts: float, window_sec: float) -> list[BeatRecord]:
        """Get beats within the time window."""
        cutoff = current_ts - window_sec
        return [b for b in self.beats if b.ts_sec >= cutoff]


class StateManager:
    """Manage per-session state."""

    def __init__(self):
        self._sessions: dict[str, SessionState] = {}

    def get_session(self, session_id: str) -> SessionState:
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState()
        return self._sessions[session_id]

    def remove_session(self, session_id: str):
        self._sessions.pop(session_id, None)
