"""Repeat the whole train -> quantize -> evaluate experiment R times.

Why this is not just `N_CANDIDATES = 10`
----------------------------------------

Those two settings answer different questions, and only one of them answers RQ2.1/RQ2.3.

`N_CANDIDATES` is a *best-of-N search*. It trains N models, keeps whichever scores highest
on validation PR-AUC, and throws the rest away. Raising it does not give you more evidence
-- it gives you one model chosen from a larger pool, and it makes the winner's validation
PR-AUC *more* optimistically biased, because you are selecting the maximum of N noisy
draws and then reporting that maximum from the same set you selected on. The observed
spread in one run of this study (candidate 1 at 0.8865, candidate 2 at 0.7418) is a
0.14 PR-AUC gap from nothing but the seed, so with N=3 the "winner" is substantially luck.

A *trial* here is an independent replication: one seed, one model, its own
validation-chosen thresholds, its own INT8 conversion, its own test metrics. Running R of
them gives a distribution, so you can report "quantization costs F1 0.040 +/- 0.006 across
10 runs" instead of "quantization cost F1 0.040 in the one run we did". That is the
defensible form of the claim, and it is what an examiner asking "would you get this again"
is asking for.

The two compose: a trial may itself run a best-of-N search internally
(`candidates_per_trial > 1`), which is the honest way to keep the deployment-selection
procedure while still measuring its variability. Cost multiplies, so the default is 1.

What this does and does not measure
-----------------------------------

The patient split is FIXED across trials, deliberately -- it is the split the methodology
commits to, and re-drawing it per trial would change the study population and make trials
non-comparable. So the variance reported here is *training* variance: weight init,
augmentation draws, batch shuffling. It is not an estimate of how the result would move on
a different set of patients, which is a larger and separate question. Say which one you are
reporting.

Statistics
----------

Per-trial FP32-vs-INT8 deltas are paired by construction (same trial, same test beats), so
the summary runs a Wilcoxon signed-rank test over the R deltas. Do not instead pool every
beat from every trial into one big McNemar table: beats repeat across trials and the models
are correlated, so that inflates n and understates the p-value.
"""

from __future__ import annotations

import json
import os
import time

import numpy as np

from .quantization import (
    evaluate_at_threshold, quantize_int8, run_tflite, estimate_tflm_arena,
)
from .thresholds import select_thresholds

__all__ = ["run_trials", "summarize_trials", "print_trial_summary"]


def _metrics_row(y_test, probs, thresholds, prefix):
    out = {}
    for name, thr in thresholds.items():
        m = evaluate_at_threshold(y_test, probs, thr, verbose=False)
        for k in ("f1_score", "specificity", "sensitivity", "precision", "accuracy"):
            out[f"{prefix}_{name}_{k}"] = m[k]
        out[f"{prefix}_{name}_threshold"] = float(thr)
    out[f"{prefix}_roc_auc"] = float(
        evaluate_at_threshold(y_test, probs, list(thresholds.values())[0], verbose=False)["roc_auc"]
    )
    out[f"{prefix}_pr_auc"] = float(
        evaluate_at_threshold(y_test, probs, list(thresholds.values())[0], verbose=False)["pr_auc"]
    )
    return out


def run_trials(build_model, fit_model, X_train, RR_train, y_train,
               X_val, RR_val, y_val, X_test, RR_test, y_test,
               window_size, n_trials=10, base_seed=4000, candidates_per_trial=1,
               out_dir=".", run_tag="tibok", resume=True, batch_one=False,
               n_calib=800):
    """Run `n_trials` independent replications, checkpointing after each one.

    `build_model(seed)` must return a compiled model; `fit_model(model, seed)` trains it.
    Both are passed in rather than hard-coded so this module never has to import the
    notebook's architecture.

    Checkpointing matters here: 10 trials is over an hour of GPU time, and a Colab runtime
    that disconnects at trial 8 would otherwise lose everything. Results are appended to a
    JSON file after every trial and `resume=True` picks up where it stopped.
    """
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{run_tag}_trials.json")

    rows = []
    if resume and os.path.exists(path):
        rows = json.load(open(path))["trials"]
        print(f"Resuming: {len(rows)} trial(s) already recorded in {path}")

    done = {r["trial"] for r in rows}

    for t in range(n_trials):
        if t in done:
            continue
        seed = base_seed + t
        t0 = time.time()
        print(f"\n{'='*72}\nTRIAL {t + 1}/{n_trials}  (seed={seed})\n{'='*72}")

        best, best_val = None, -1.0
        for c in range(candidates_per_trial):
            cand_seed = seed * 100 + c
            model = build_model(cand_seed)
            fit_model(model, cand_seed)
            vp = model.predict([X_val, RR_val], batch_size=256, verbose=0).flatten()
            from sklearn.metrics import average_precision_score
            score = average_precision_score(y_val, vp)
            if candidates_per_trial > 1:
                print(f"  candidate {c + 1}/{candidates_per_trial}: val PR-AUC {score:.4f}")
            if score > best_val:
                best_val, best, best_vp = score, model, vp

        model, val_probs = best, best_vp
        thresholds = select_thresholds(y_val, val_probs)

        probs_fp32 = model.predict([X_test, RR_test], batch_size=256, verbose=0).flatten()
        qr = quantize_int8(model, X_val, RR_val, window_size, n_calib=n_calib, seed=seed)
        probs_int8, _ = run_tflite(qr, X_test, RR_test, window_size, batch_one=batch_one)

        row = {"trial": t, "seed": seed, "val_pr_auc_selected": float(best_val),
               "full_int8": bool(qr.full_int8), "strategy": qr.strategy,
               "size_kb": float(qr.size_kb),
               "arena_kb": float(estimate_tflm_arena(qr, window_size).get("peak_arena_kb", 0.0)),
               "wall_s": round(time.time() - t0, 1)}
        row.update(_metrics_row(y_test, probs_fp32, thresholds, "fp32"))
        row.update(_metrics_row(y_test, probs_int8, thresholds, "int8"))

        rows.append(row)
        json.dump({"run_tag": run_tag, "n_trials": n_trials, "trials": rows},
                  open(path, "w"), indent=2)
        f32 = row["fp32_precision_floor_90_f1_score"]
        i8 = row["int8_precision_floor_90_f1_score"]
        print(f"  trial {t + 1} done in {row['wall_s']:.0f}s | "
              f"FP32 F1 {f32:.4f} -> INT8 F1 {i8:.4f} ({i8 - f32:+.4f})")

    print(f"\nAll trials recorded in {path}")
    return rows


def summarize_trials(rows, threshold_name="precision_floor_90"):
    """Mean / SD / CI per metric, plus a Wilcoxon signed-rank on the per-trial deltas."""
    if not rows:
        raise ValueError("no trials to summarize")
    n = len(rows)
    summary = {"n_trials": n, "threshold": threshold_name, "metrics": {}}

    for metric in ("f1_score", "specificity", "sensitivity", "precision", "accuracy"):
        a = np.array([r[f"fp32_{threshold_name}_{metric}"] for r in rows])
        b = np.array([r[f"int8_{threshold_name}_{metric}"] for r in rows])
        d = b - a
        entry = {
            "fp32_mean": float(a.mean()), "fp32_sd": float(a.std(ddof=1)) if n > 1 else 0.0,
            "int8_mean": float(b.mean()), "int8_sd": float(b.std(ddof=1)) if n > 1 else 0.0,
            "delta_mean": float(d.mean()), "delta_sd": float(d.std(ddof=1)) if n > 1 else 0.0,
        }
        if n > 1:
            se = d.std(ddof=1) / np.sqrt(n)
            entry["delta_ci95"] = [float(d.mean() - 1.96 * se), float(d.mean() + 1.96 * se)]
            try:
                from scipy.stats import wilcoxon
                if np.any(d != 0):
                    entry["wilcoxon_p"] = float(wilcoxon(a, b).pvalue)
            except Exception:
                pass
        summary["metrics"][metric] = entry

    for k in ("val_pr_auc_selected", "size_kb", "arena_kb"):
        v = np.array([r[k] for r in rows], dtype=float)
        summary[k] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)) if n > 1 else 0.0,
                      "min": float(v.min()), "max": float(v.max())}
    summary["all_full_int8"] = bool(all(r["full_int8"] for r in rows))
    return summary


def print_trial_summary(summary):
    print(f"\n{'='*72}")
    print(f"TRIAL SUMMARY  (n={summary['n_trials']}, threshold={summary['threshold']})")
    print("=" * 72)
    print(f"{'metric':<14}{'FP32 mean±sd':>20}{'INT8 mean±sd':>20}{'delta mean±sd':>20}")
    for k, m in summary["metrics"].items():
        print(f"{k:<14}"
              f"{m['fp32_mean']:>12.4f}±{m['fp32_sd']:<7.4f}"
              f"{m['int8_mean']:>12.4f}±{m['int8_sd']:<7.4f}"
              f"{m['delta_mean']:>+12.4f}±{m['delta_sd']:<7.4f}")
    print()
    for k, m in summary["metrics"].items():
        if "delta_ci95" in m:
            p = m.get("wilcoxon_p")
            ptxt = f"  Wilcoxon p={p:.4f}" if p is not None else ""
            print(f"  {k:<14} delta 95% CI [{m['delta_ci95'][0]:+.4f}, {m['delta_ci95'][1]:+.4f}]{ptxt}")
    v = summary["val_pr_auc_selected"]
    print(f"\n  val PR-AUC across trials: {v['mean']:.4f} ± {v['sd']:.4f} "
          f"(min {v['min']:.4f}, max {v['max']:.4f})")
    print(f"  model size: {summary['size_kb']['mean']:.2f} KB  |  "
          f"arena: {summary['arena_kb']['mean']:.2f} KB  |  "
          f"all full-INT8: {summary['all_full_int8']}")
