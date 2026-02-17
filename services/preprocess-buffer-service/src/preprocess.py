"""Waveform preprocessing: downsample and normalize for UI stream."""
from __future__ import annotations

import numpy as np


def downsample(samples: list[list[float]], factor: int = 2) -> list[list[float]]:
    """Downsample waveform by factor for UI rendering.
    
    Args:
        samples: (channels, length) waveform
        factor: downsample factor
        
    Returns:
        Downsampled (channels, new_length) waveform
    """
    result = []
    for ch_data in samples:
        arr = np.array(ch_data)
        downsampled = arr[::factor]
        result.append(downsampled.tolist())
    return result


def normalize_for_display(samples: list[list[float]]) -> list[list[float]]:
    """Normalize waveform to [-1, 1] range for UI display."""
    result = []
    for ch_data in samples:
        arr = np.array(ch_data)
        max_val = np.max(np.abs(arr)) if len(arr) > 0 else 1.0
        if max_val < 1e-8:
            max_val = 1.0
        normalized = (arr / max_val).tolist()
        result.append(normalized)
    return result
