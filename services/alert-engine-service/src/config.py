"""Alert engine configuration."""
from __future__ import annotations

import os


class AlertConfig:
    """Alert rules configuration (loaded from env or defaults)."""

    def __init__(self):
        self.V_WINDOW = int(os.environ.get("V_WINDOW", "10"))
        self.V_THRESH = int(os.environ.get("V_THRESH", "5"))
        self.COOLDOWN_V = int(os.environ.get("COOLDOWN_V", "20"))
        self.A_WINDOW = int(os.environ.get("A_WINDOW", "30"))
        self.A_THRESH = int(os.environ.get("A_THRESH", "4"))
        self.COOLDOWN_A = int(os.environ.get("COOLDOWN_A", "45"))
        self.THR_A = float(os.environ.get("THR_A", "0.65"))

    def __repr__(self):
        return (
            f"AlertConfig(V_WINDOW={self.V_WINDOW}, V_THRESH={self.V_THRESH}, "
            f"COOLDOWN_V={self.COOLDOWN_V}, A_WINDOW={self.A_WINDOW}, "
            f"A_THRESH={self.A_THRESH}, COOLDOWN_A={self.COOLDOWN_A}, THR_A={self.THR_A})"
        )
