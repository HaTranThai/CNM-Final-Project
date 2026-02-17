"""Tests for alert rules engine."""
import sys
import os

# Add alert engine to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "services", "alert-engine-service"))

from src.config import AlertConfig
from src.state import SessionState
from src.rules import check_v_alert, check_a_alert


def test_v_alert_triggers():
    """V alert triggers when >= V_THRESH V-beats in V_WINDOW."""
    config = AlertConfig()
    config.V_WINDOW = 10
    config.V_THRESH = 5
    config.COOLDOWN_V = 20

    state = SessionState()

    # Add 5 V beats within 10 seconds
    for i in range(5):
        state.add_beat(ts_sec=100.0 + i, pred_class="V", pA=0.0, confidence=0.9)

    result = check_v_alert(state, current_ts=104.0, config=config)
    assert result is not None
    assert result["alert_type"] == "V"
    assert result["status"] == "NEW"


def test_v_alert_not_triggered_below_threshold():
    """V alert does NOT trigger when < V_THRESH."""
    config = AlertConfig()
    config.V_WINDOW = 10
    config.V_THRESH = 5

    state = SessionState()

    # Add only 3 V beats
    for i in range(3):
        state.add_beat(ts_sec=100.0 + i, pred_class="V", pA=0.0, confidence=0.9)

    result = check_v_alert(state, current_ts=102.0, config=config)
    assert result is None


def test_v_alert_cooldown():
    """V alert respects cooldown period."""
    config = AlertConfig()
    config.V_WINDOW = 10
    config.V_THRESH = 5
    config.COOLDOWN_V = 20

    state = SessionState()

    # Trigger first alert
    for i in range(5):
        state.add_beat(ts_sec=100.0 + i, pred_class="V", pA=0.0, confidence=0.9)
    result1 = check_v_alert(state, current_ts=104.0, config=config)
    assert result1 is not None

    # Try again within cooldown — should not trigger
    for i in range(5):
        state.add_beat(ts_sec=110.0 + i, pred_class="V", pA=0.0, confidence=0.9)
    result2 = check_v_alert(state, current_ts=114.0, config=config)
    assert result2 is None


def test_a_alert_triggers():
    """A alert triggers with pA >= thr_A."""
    config = AlertConfig()
    config.A_WINDOW = 30
    config.A_THRESH = 4
    config.COOLDOWN_A = 45
    config.THR_A = 0.65

    state = SessionState()

    # Add 4 A beats with high pA
    for i in range(4):
        state.add_beat(ts_sec=200.0 + i, pred_class="A", pA=0.80, confidence=0.85)

    result = check_a_alert(state, current_ts=203.0, config=config)
    assert result is not None
    assert result["alert_type"] == "A"


def test_a_alert_low_pa_not_counted():
    """A beats with pA < thr_A should not count toward alert."""
    config = AlertConfig()
    config.A_WINDOW = 30
    config.A_THRESH = 4
    config.THR_A = 0.65

    state = SessionState()

    # Add A beats with LOW pA — should not trigger
    for i in range(4):
        state.add_beat(ts_sec=200.0 + i, pred_class="A", pA=0.50, confidence=0.6)

    result = check_a_alert(state, current_ts=203.0, config=config)
    assert result is None


if __name__ == "__main__":
    test_v_alert_triggers()
    test_v_alert_not_triggered_below_threshold()
    test_v_alert_cooldown()
    test_a_alert_triggers()
    test_a_alert_low_pa_not_counted()
    print("All alert rule tests passed! ✅")
