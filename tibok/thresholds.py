"""Operating-point selection on the validation set.

Lifted out of the notebook so the trial harness can reuse it. Every threshold here is
chosen on VALIDATION and only ever applied to test -- that separation is the whole point,
and inlining this in the notebook made it easy to accidentally break when repeating a run.
"""

from __future__ import annotations

import numpy as np
from sklearn.metrics import confusion_matrix, precision_recall_curve

__all__ = ["select_thresholds"]


def select_thresholds(y_val, val_probs, precision_floor=0.90, target_sensitivity=0.90):
    """Return the four operating points the study reports, all chosen on validation."""
    y_val = np.asarray(y_val)
    precisions, recalls, thresholds = precision_recall_curve(y_val, val_probs)

    f1 = 2 * (precisions * recalls) / (precisions + recalls + 1e-8)
    f1_optimal = thresholds[np.argmax(f1[:-1])]

    specs, sens = [], []
    for t in thresholds:
        tn, fp, fn, tp = confusion_matrix(y_val, (val_probs > t).astype(int), labels=[0, 1]).ravel()
        specs.append(tn / (tn + fp) if (tn + fp) else 0.0)
        sens.append(tp / (tp + fn) if (tp + fn) else 0.0)
    specs, sens = np.array(specs), np.array(sens)

    youden = thresholds[np.argmax(sens + specs - 1)]

    mask = sens >= target_sensitivity
    high_sens = thresholds[np.argmax(np.where(mask, specs, -1))] if mask.any() else thresholds[np.argmax(sens)]

    # Lowest threshold still meeting the precision floor -- lowest keeps recall as high as
    # the floor allows.
    idx = np.where(precisions[:-1] >= precision_floor)[0]
    prec_floor = thresholds[idx[0]] if len(idx) else thresholds[np.argmax(precisions[:-1])]

    return {
        "f1_optimal": float(f1_optimal),
        "youden": float(youden),
        "high_sensitivity": float(high_sens),
        "precision_floor_90": float(prec_floor),
    }
