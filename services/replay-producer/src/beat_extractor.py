"""Beat segment extraction with bandpass filter and z-score normalization."""
from __future__ import annotations

import logging

import numpy as np
from scipy.signal import butter, filtfilt

logger = logging.getLogger(__name__)

# Segment parameters (match training pipeline)
PRE_SEC = 0.35
POST_SEC = 0.55


def bandpass_filter(signal: np.ndarray, fs: int, low: float = 0.5, high: float = 40.0, order: int = 4) -> np.ndarray:
    """Apply bandpass filter to signal."""
    nyq = fs / 2.0
    b, a = butter(order, [low / nyq, high / nyq], btype="band")
    return filtfilt(b, a, signal, axis=-1)


def zscore(signal: np.ndarray) -> np.ndarray:
    """Z-score normalize signal."""
    std = np.std(signal)
    if std < 1e-8:
        return signal - np.mean(signal)
    return (signal - np.mean(signal)) / std


def extract_beat_segment(
    p_signal: np.ndarray,
    beat_sample: int,
    fs: int,
    channels_used: list[int] = [0, 1],
) -> np.ndarray | None:
    """Extract a beat segment around an R-peak.
    
    Args:
        p_signal: Full signal array (samples, channels)
        beat_sample: Sample index of the R-peak
        fs: Sampling frequency
        channels_used: Channel indices to use
        
    Returns:
        Processed segment of shape (n_channels, seg_len) or None if out of bounds
    """
    pre_samples = int(PRE_SEC * fs)
    post_samples = int(POST_SEC * fs)
    seg_len = pre_samples + post_samples

    start = beat_sample - pre_samples
    end = beat_sample + post_samples

    if start < 0 or end > p_signal.shape[0]:
        return None

    segments = []
    for ch in channels_used:
        seg = p_signal[start:end, ch].astype(np.float64)
        seg = bandpass_filter(seg, fs)
        seg = zscore(seg)
        segments.append(seg)

    return np.array(segments)  # (n_channels, seg_len)
