"""Ring buffer for maintaining recent waveform data."""
from __future__ import annotations

import collections
from typing import Optional

import numpy as np


class WaveformRingBuffer:
    """Circular buffer storing last N seconds of waveform data per session."""

    def __init__(self, max_seconds: float = 10.0, fs: int = 360, n_channels: int = 2):
        self.max_samples = int(max_seconds * fs)
        self.fs = fs
        self.n_channels = n_channels
        self._buffers: dict[str, collections.deque] = {}

    def append(self, session_id: str, samples: list[list[float]]):
        """Append waveform samples to session buffer.
        
        Args:
            session_id: Session identifier
            samples: (n_channels, chunk_len) waveform data
        """
        if session_id not in self._buffers:
            self._buffers[session_id] = collections.deque(maxlen=self.max_samples)

        buf = self._buffers[session_id]
        # samples is (channels, chunk_len) — store as list of per-sample channel values
        n_samples = len(samples[0]) if samples else 0
        for i in range(n_samples):
            point = [ch[i] if i < len(ch) else 0.0 for ch in samples]
            buf.append(point)

    def get_last(self, session_id: str, seconds: float = 10.0) -> Optional[list[list[float]]]:
        """Get last N seconds of data as (channels, samples)."""
        if session_id not in self._buffers:
            return None

        buf = self._buffers[session_id]
        n = min(int(seconds * self.fs), len(buf))
        if n == 0:
            return None

        data = list(buf)[-n:]
        # Transpose: list of [ch0, ch1, ...] → [[ch0_samples], [ch1_samples], ...]
        n_ch = len(data[0]) if data else self.n_channels
        result = [[] for _ in range(n_ch)]
        for point in data:
            for ch in range(n_ch):
                result[ch].append(point[ch] if ch < len(point) else 0.0)

        return result

    def remove_session(self, session_id: str):
        self._buffers.pop(session_id, None)
