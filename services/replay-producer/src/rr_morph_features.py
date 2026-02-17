"""RR interval and morphology feature extraction — matches training pipeline."""
from __future__ import annotations

import numpy as np


def compute_rr4(
    beat_samples: list[int],
    beat_idx: int,
    fs: int,
) -> list[float]:
    """Compute RR4 features for a beat.
    
    Returns: [rr_prev, rr_next, rr_ratio, drr]
    """
    if beat_idx <= 0 or beat_idx >= len(beat_samples) - 1:
        return [0.0, 0.0, 1.0, 0.0]

    rr_prev = (beat_samples[beat_idx] - beat_samples[beat_idx - 1]) / fs
    rr_next = (beat_samples[beat_idx + 1] - beat_samples[beat_idx]) / fs

    rr_ratio = rr_prev / rr_next if rr_next > 0 else 1.0
    drr = rr_prev - rr_next

    return [float(rr_prev), float(rr_next), float(rr_ratio), float(drr)]


def morphology_features(seg: np.ndarray) -> list[float]:
    """Compute 8 morphology features from a beat segment.
    
    Args:
        seg: Segment array of shape (n_channels, seg_len) or (seg_len,)
        
    Returns: List of 8 float features
    """
    if seg.ndim == 2:
        # Use first channel for morphology
        s = seg[0]
    else:
        s = seg

    n = len(s)
    if n == 0:
        return [0.0] * 8

    # Basic statistics
    feat = []
    feat.append(float(np.max(s)))               # max amplitude
    feat.append(float(np.min(s)))               # min amplitude
    feat.append(float(np.max(s) - np.min(s)))   # peak-to-peak
    feat.append(float(np.mean(s)))              # mean
    feat.append(float(np.std(s)))               # std

    # R-peak relative position
    peak_pos = np.argmax(s) / n if n > 0 else 0.5
    feat.append(float(peak_pos))

    # Energy (RMS)
    rms = float(np.sqrt(np.mean(s ** 2)))
    feat.append(rms)

    # Zero crossing rate
    zero_crosses = np.sum(np.diff(np.sign(s)) != 0) / n if n > 1 else 0.0
    feat.append(float(zero_crosses))

    return feat[:8]
