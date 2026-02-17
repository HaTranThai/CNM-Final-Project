"""Inference logic — softmax, prediction, A-threshold gating."""
from __future__ import annotations

import logging

import numpy as np
import torch

from .model_def import CNN_RR4_Morph8

logger = logging.getLogger(__name__)


def softmax_np(logits: np.ndarray) -> np.ndarray:
    """Numerically stable softmax."""
    exp = np.exp(logits - np.max(logits))
    return exp / exp.sum()


def predict_beat(
    model: CNN_RR4_Morph8,
    seg: list[list[float]],
    rr4: list[float],
    m8: list[float],
    idx_to_label: dict[int, str],
    a_idx: int,
    thr_a: float = 0.65,
    device: str = "cpu",
) -> dict:
    """Run inference on a single beat.
    
    Args:
        model: loaded CNN_RR4_Morph8 model
        seg: segment (C, L) as nested list
        rr4: RR4 features (4,)
        m8: morphology features (8,)
        idx_to_label: class index to label mapping
        a_idx: index of "A" class
        thr_a: threshold for A-class gating
        device: torch device
        
    Returns:
        dict with pred_class, confidence, pA, probs, gated_A
    """
    # Prepare tensors
    x = torch.tensor([seg], dtype=torch.float32, device=device)  # (1, C, L)
    rr4_t = torch.tensor([rr4], dtype=torch.float32, device=device)  # (1, 4)
    m8_t = torch.tensor([m8], dtype=torch.float32, device=device)  # (1, 8)

    # Forward pass
    with torch.no_grad():
        logits = model(x, rr4_t, m8_t)  # (1, n_classes)

    logits_np = logits.cpu().numpy()[0]
    probs = softmax_np(logits_np)

    # Get prediction
    pred_idx = int(np.argmax(probs))
    pred_lab = idx_to_label.get(pred_idx, "N")
    confidence = float(probs[pred_idx])

    # Get pA
    pA = float(probs[a_idx]) if a_idx >= 0 else 0.0

    # A-threshold gating
    gated_A = False
    if pred_lab == "A" and pA < thr_a:
        pred_lab = "N"
        gated_A = True

    # Build probs dict
    probs_dict = {}
    for idx, lab in idx_to_label.items():
        probs_dict[lab] = round(float(probs[int(idx)]), 4)

    return {
        "pred_class": pred_lab,
        "confidence": round(confidence, 4),
        "pA": round(pA, 4),
        "probs": probs_dict,
        "gated_A": gated_A,
    }
