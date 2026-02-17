"""MIT-BIH WFDB record reader."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


def load_record(data_dir: str, record_name: str):
    """Load a WFDB record and its annotations.
    
    Returns:
        record: wfdb Record object
        annotation: wfdb Annotation object
    """
    import wfdb

    record_path = str(Path(data_dir) / record_name)
    logger.info(f"Loading WFDB record: {record_path}")

    record = wfdb.rdrecord(record_path)
    annotation = wfdb.rdann(record_path, "atr")

    logger.info(
        f"Record {record_name}: {record.sig_len} samples, "
        f"{record.fs} Hz, {len(record.sig_name)} channels: {record.sig_name}, "
        f"{len(annotation.sample)} annotations"
    )
    return record, annotation


def get_waveform_chunk(record, start_sample: int, chunk_samples: int) -> Optional[np.ndarray]:
    """Extract a chunk of waveform data.
    
    Returns:
        numpy array of shape (channels, chunk_samples) or None if past end
    """
    end_sample = min(start_sample + chunk_samples, record.sig_len)
    if start_sample >= record.sig_len:
        return None

    # record.p_signal is (samples, channels)
    chunk = record.p_signal[start_sample:end_sample, :]
    return chunk.T  # (channels, chunk_samples)
