"""Alert rules engine — V and A alert logic with window/threshold/cooldown."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from .config import AlertConfig
from .state import SessionState

logger = logging.getLogger(__name__)


def check_v_alert(
    state: SessionState,
    current_ts: float,
    config: AlertConfig,
) -> Optional[dict]:
    """Check if V alert should be triggered.
    
    V alert: count of pred=="V" in last V_WINDOW seconds >= V_THRESH
    AND not in cooldown.
    """
    # Cooldown check
    if current_ts - state.last_v_alert_time < config.COOLDOWN_V:
        return None

    recent = state.get_recent_beats(current_ts, config.V_WINDOW)
    v_beats = [b for b in recent if b.pred_class == "V"]

    if len(v_beats) >= config.V_THRESH:
        state.last_v_alert_time = current_ts
        now = datetime.now(timezone.utc).isoformat()

        return {
            "alert_id": str(uuid.uuid4()),
            "alert_type": "V",
            "status": "NEW",
            "start_time": now,
            "last_update": now,
            "severity": min(1.0, len(v_beats) / (config.V_THRESH * 2)),
            "evidence": {
                "window_sec": config.V_WINDOW,
                "count": len(v_beats),
                "threshold": config.V_THRESH,
                "cooldown_sec": config.COOLDOWN_V,
                "recent_beats": [
                    {"t": b.ts_sec, "pred": b.pred_class, "confidence": b.confidence}
                    for b in v_beats[-10:]
                ],
            },
        }
    return None


def check_a_alert(
    state: SessionState,
    current_ts: float,
    config: AlertConfig,
) -> Optional[dict]:
    """Check if A alert should be triggered.
    
    A alert: count of (pred=="A" AND pA>=thr_A) in last A_WINDOW seconds >= A_THRESH
    AND not in cooldown.
    """
    # Cooldown check
    if current_ts - state.last_a_alert_time < config.COOLDOWN_A:
        return None

    recent = state.get_recent_beats(current_ts, config.A_WINDOW)
    a_beats = [b for b in recent if b.pred_class == "A" and b.pA >= config.THR_A]

    if len(a_beats) >= config.A_THRESH:
        state.last_a_alert_time = current_ts
        now = datetime.now(timezone.utc).isoformat()

        return {
            "alert_id": str(uuid.uuid4()),
            "alert_type": "A",
            "status": "NEW",
            "start_time": now,
            "last_update": now,
            "severity": min(1.0, max(b.pA for b in a_beats)),
            "evidence": {
                "window_sec": config.A_WINDOW,
                "count": len(a_beats),
                "threshold": config.A_THRESH,
                "cooldown_sec": config.COOLDOWN_A,
                "thr_A": config.THR_A,
                "recent_beats": [
                    {"t": b.ts_sec, "pred": b.pred_class, "pA": b.pA}
                    for b in a_beats[-10:]
                ],
            },
        }
    return None
