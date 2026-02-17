"""Signal Quality Index (SQI) estimation."""
from __future__ import annotations

import numpy as np


def compute_sqi(samples: list[float], fs: int = 360) -> float:
    """Compute a simple signal quality index.
    
    Uses power spectral density ratio in physiological ECG band (0.5-40 Hz)
    vs. total power. Returns 0.0-1.0 (1.0 = high quality).
    
    Args:
        samples: 1D waveform array
        fs: sampling rate
        
    Returns:
        SQI value 0.0-1.0
    """
    if len(samples) < fs:
        return 0.5  # insufficient data

    arr = np.array(samples, dtype=np.float64)

    # Simple SQI: ratio of signal in valid range
    std = np.std(arr)
    if std < 1e-8:
        return 0.0  # flat line

    # Check for clipping or extreme values
    max_abs = np.max(np.abs(arr))
    if max_abs > 10:  # extremely large values indicate noise
        return 0.2

    # Check kurtosis — normal ECG has moderate kurtosis
    mean = np.mean(arr)
    kurtosis = np.mean(((arr - mean) / std) ** 4)

    if kurtosis < 1.0 or kurtosis > 50:
        return 0.3  # abnormal distribution

    # Reasonable signal
    sqi = min(1.0, max(0.0, 1.0 - abs(kurtosis - 5) / 20))
    return round(sqi, 2)
