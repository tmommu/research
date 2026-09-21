"""Write the study's results as a CSV, one row per (model, operating point).

Column layout is fixed to match the format already in use:

    Model,Threshold Type,Threshold Value,Accuracy,Sensitivity,Specificity,Precision,F1,ROC-AUC,PR-AUC

Every candidate is reported, not just the selected one. That is the point: on one observed
run the eight candidates scored 0.8865 / 0.7418 / 0.7516 / 0.7305 / 0.7352 / 0.6813 /
0.6938 / 0.7420 on validation PR-AUC — the winner sat six standard deviations above the
other seven, which cluster at 0.725 +/- 0.027. A table showing only the winner presents a
lucky draw as the model's performance. Showing all eight, plus mean and SD, lets a reader
see how much of the headline number is selection.

**Selection still happens on validation.** These rows put every candidate's *test* metrics
in one table for transparency, which is only honest while the deployed model stays the
validation winner. Picking a different row because it scores better on test converts the
test set into a second validation set and the headline number stops estimating held-out
performance. The `Selected` marker in the Model column records which one selection actually
chose.
"""

from __future__ import annotations

import csv
import os

import numpy as np

from .quantization import evaluate_at_threshold

__all__ = ["RESULT_COLUMNS", "THRESHOLD_LABELS", "result_rows", "summary_rows",
           "write_results_csv", "build_results_table"]

RESULT_COLUMNS = ["Model", "Threshold Type", "Threshold Value", "Accuracy", "Sensitivity",
                  "Specificity", "Precision", "F1", "ROC-AUC", "PR-AUC"]

THRESHOLD_LABELS = {
    "f1_optimal": "F1-optimal",
    "youden": "Youden",
    "high_sensitivity": "High-sensitivity",
    "precision_floor_90": "Precision-floor",
}

_METRIC_KEYS = [("Accuracy", "accuracy"), ("Sensitivity", "sensitivity"),
                ("Specificity", "specificity"), ("Precision", "precision"),
                ("F1", "f1_score"), ("ROC-AUC", "roc_auc"), ("PR-AUC", "pr_auc")]


def result_rows(model_label, y_true, probs, thresholds, nd=4):
    """One row per operating point for a single model's probabilities."""
    out = []
    for name, thr in thresholds.items():
        m = evaluate_at_threshold(y_true, probs, thr, verbose=False)
        row = {"Model": model_label,
               "Threshold Type": THRESHOLD_LABELS.get(name, name),
               "Threshold Value": round(float(thr), nd)}
        for col, key in _METRIC_KEYS:
            row[col] = round(float(m[key]), nd)
        out.append(row)
    return out


def summary_rows(rows, group_prefixes=("FP32", "INT8"), nd=4):
    """Mean and SD across candidates, per precision and operating point.

    Grouped by whether the Model label starts with FP32 or INT8, so it works whether the
    labels are "C1 FP32" or plain "FP32".
    """
    out = []
    for prefix in group_prefixes:
        sel = [r for r in rows if str(r["Model"]).startswith(prefix)
               and "mean" not in str(r["Model"]) and "SD" not in str(r["Model"])]
        if not sel:
            continue
        for label in dict.fromkeys(r["Threshold Type"] for r in sel):
            grp = [r for r in sel if r["Threshold Type"] == label]
            if not grp:
                continue
            n = len(grp)
            for stat in ("mean", "SD"):
                if stat == "SD" and n < 2:
                    continue
                row = {"Model": f"{prefix} {stat}", "Threshold Type": label}
                vals = np.array([r["Threshold Value"] for r in grp], dtype=float)
                row["Threshold Value"] = round(float(vals.mean() if stat == "mean"
                                                     else vals.std(ddof=1)), nd)
                for col, _ in _METRIC_KEYS:
                    v = np.array([r[col] for r in grp], dtype=float)
                    row[col] = round(float(v.mean() if stat == "mean" else v.std(ddof=1)), nd)
                out.append(row)
    return out


def write_results_csv(path, rows, nd=4):
    """Write the CSV with LF line endings, matching the reference file exactly.

    `csv.writer` defaults to CRLF (`\r\n`) per RFC 4180, which does not match the
    reference file's bare LF. Excel and pandas read either, but "byte-identical format"
    means the terminator too, so it is set explicitly.
    """
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=RESULT_COLUMNS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in RESULT_COLUMNS})
    print(f"Wrote {path}  ({len(rows)} rows)")
    return path


def build_results_table(candidates, val_pr_aucs, selected_index, thresholds,
                        X_test, RR_test_n, y_test, X_val, RR_val_n, window_size,
                        quantize=True, n_calib=800, batch_one=False, nd=4,
                        include_summary=True):
    """FP32 and INT8 rows for every candidate, plus mean/SD summary rows.

    Thresholds are the ones selected on validation from the *chosen* model, applied to
    every candidate, so the columns are comparable across rows. Per-candidate thresholds
    would make each row internally optimal but mutually incomparable, which defeats the
    purpose of putting them in one table.
    """
    from .quantization import quantize_int8, run_tflite

    rows = []
    single = len(candidates) == 1
    for i, model in enumerate(candidates):
        # Model labels stay in the reference file's style: the bare precision when there is
        # one model, and a trailing index only when several need telling apart. Which model
        # selection chose is printed below rather than marked in the CSV, so the column
        # keeps the same shape as the reference.
        fp32_label = "FP32" if single else f"FP32 {i + 1}"
        int8_label = "INT8" if single else f"INT8 {i + 1}"

        probs = model.predict([X_test, RR_test_n], batch_size=256, verbose=0).flatten()
        rows += result_rows(fp32_label, y_test, probs, thresholds, nd=nd)

        if quantize:
            try:
                qr = quantize_int8(model, X_val, RR_val_n, window_size, n_calib=n_calib)
                q_probs, _ = run_tflite(qr, X_test, RR_test_n, window_size, batch_one=batch_one)
                rows += result_rows(int8_label, y_test, q_probs, thresholds, nd=nd)
            except Exception as e:
                print(f"  {int8_label}: INT8 conversion failed, FP32 row only -- "
                      f"{type(e).__name__}: {e}")

        pa = val_pr_aucs[i] if i < len(val_pr_aucs) else float("nan")
        mark = "  <- selected on validation" if i == selected_index else ""
        print(f"  model {i + 1}: val PR-AUC {pa:.4f}{mark}")

    if include_summary:
        rows += summary_rows(rows, nd=nd)
    return rows
