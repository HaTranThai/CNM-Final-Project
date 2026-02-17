"""Model loader — loads .pt checkpoint with model_state and idx_to_label."""
from __future__ import annotations

import logging
from pathlib import Path

import torch

from .model_def import CNN_RR4_Morph8

logger = logging.getLogger(__name__)


def load_model(
    checkpoint_path: str,
    device: str = "cpu",
) -> tuple[CNN_RR4_Morph8, dict[int, str], int]:
    """Load trained model from checkpoint.
    
    The checkpoint contains:
    - model_state: state dict
    - idx_to_label: {0: "N", 1: "A", 2: "V"} (example)
    
    Returns:
        model: loaded model in eval mode
        idx_to_label: index to label mapping
        a_idx: index of "A" class
    """
    path = Path(checkpoint_path)
    if not path.exists():
        raise FileNotFoundError(f"Model checkpoint not found: {checkpoint_path}")

    logger.info(f"Loading model from {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)

    # Extract idx_to_label
    idx_to_label = checkpoint.get("idx_to_label", {0: "N", 1: "A", 2: "V"})
    n_classes = len(idx_to_label)

    # Determine in_ch from state dict
    first_conv_weight = checkpoint["model_state"].get("conv1.0.weight")
    in_ch = first_conv_weight.shape[1] if first_conv_weight is not None else 2

    # Build model
    model = CNN_RR4_Morph8(in_ch=in_ch, n_classes=n_classes)
    model.load_state_dict(checkpoint["model_state"])
    model.to(device)
    model.eval()

    # Find A index
    a_idx = -1
    for idx, lab in idx_to_label.items():
        if lab == "A":
            a_idx = int(idx)
            break

    logger.info(f"Model loaded: in_ch={in_ch}, n_classes={n_classes}, idx_to_label={idx_to_label}, a_idx={a_idx}")
    return model, idx_to_label, a_idx
