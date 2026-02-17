"""CNN_RR4_Morph8 model architecture — must match training code exactly."""
from __future__ import annotations

import torch
import torch.nn as nn


class CNN_RR4_Morph8(nn.Module):
    """1D CNN + RR4 interval features + M8 morphology features.

    Architecture (matches checkpoint state_dict):
    - self.cnn: nn.Sequential with 3 conv blocks
      [Conv1d → BN → ReLU → MaxPool] × 3
    - Concatenate CNN flatten + rr4 (4) + m8 (8)
    - self.head: 140 → 192 → n_classes
    """

    def __init__(self, in_ch: int = 2, n_classes: int = 3):
        super().__init__()
        self.in_ch = in_ch
        self.n_classes = n_classes

        # CNN backbone — single Sequential so keys are cnn.0, cnn.1, ...
        self.cnn = nn.Sequential(
            # Block 1: cnn.0 (Conv), cnn.1 (BN), cnn.2 (ReLU), cnn.3 (Pool)
            nn.Conv1d(in_ch, 32, kernel_size=5, padding=2),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(2),
            # Block 2: cnn.4 (Conv), cnn.5 (BN), cnn.6 (ReLU), cnn.7 (Pool)
            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2),
            # Block 3: cnn.8 (Conv), cnn.9 (BN), cnn.10 (ReLU), cnn.11 (AdaptivePool)
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
        )

        # Head: CNN output (128) + rr4 (4) + m8 (8) = 140 → 192 → n_classes
        self.head = nn.Sequential(
            nn.Linear(128 + 4 + 8, 192),
            nn.ReLU(),
            nn.Dropout(0.3),
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
        h = self.cnn(x)
        h = h.squeeze(-1)  # (B, 128)

        # Concatenate
        combined = torch.cat([h, rr4, m8], dim=1)  # (B, 140)

        # FC head
        logits = self.head(combined)
        return logits
