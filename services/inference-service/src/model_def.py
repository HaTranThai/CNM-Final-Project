"""CNN_RR4_Morph8 model architecture — copied from mitbih_end2end_v25.py training code."""
from __future__ import annotations

import torch
import torch.nn as nn


class CNN_RR4_Morph8(nn.Module):
    """1D CNN + RR4 interval features + M8 morphology features.

    Architecture must match training checkpoint exactly:
    - 3 conv blocks with kernels 9→7→5
    - AdaptiveAvgPool1d(1) at the end
    - Head: 140 → 192 → n_classes
    """

    def __init__(self, in_ch: int = 2, n_classes: int = 3):
        super().__init__()
        self.cnn = nn.Sequential(
            nn.Conv1d(in_ch, 32, 9, padding=4),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(32, 64, 7, padding=3),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(64, 128, 5, padding=2),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
        )
        self.head = nn.Sequential(
            nn.Linear(128 + 4 + 8, 192),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(192, n_classes),
        )

    def forward(self, x: torch.Tensor, rr4: torch.Tensor, m8: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (B, in_ch, L) ECG segment
            rr4: (B, 4) RR interval features
            m8: (B, 8) morphology features

        Returns:
            logits: (B, n_classes)
        """
        z = self.cnn(x).squeeze(-1)  # (B, 128)
        z = torch.cat([z, rr4, m8], dim=1)  # (B, 140)
        return self.head(z)
