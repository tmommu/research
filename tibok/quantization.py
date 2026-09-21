"""
TIBOK — INT8 post-training quantization + verification for the RR-fused 1D-CNN.

Companion to `eto_na_tlga_guys_final_na.py`. That notebook trains the model; this
module takes the trained Keras model plus the held-out arrays and answers the
deployment questions the pre-oral commits to:

  RQ2.1 / RQ2.3  Does INT8 quantization change F1 / specificity on held-out patients?
                 -> `compare_fp32_int8` runs a *paired* comparison (McNemar's exact
                    test + bootstrap CIs on the deltas), not two unrelated metric
                    dumps, because both models score the identical test beats.

  Fit on nRF52840 (1 MB flash / 256 KB RAM)
                 -> `estimate_tflm_arena` walks the operator schedule and reports the
                    peak simultaneously-live activation set, which is what the
                    TFLite-Micro arena actually has to hold.

Why this exists as its own module rather than one more notebook cell: the original
cell silently fell back to dynamic-range (weight-only) quantization when full-integer
conversion failed. That fallback is not deployable here -- TFLite-Micro has no
dynamic-range kernels for Conv1D/FullyConnected, so a dynamic-range .tflite will fail
at `AllocateTensors()` on the nRF52840 even though it loads fine on desktop. Falling
back quietly turns a conversion bug into a firmware bug found weeks later. This module
tries several full-integer conversion strategies in order and only ever reports
dynamic-range as an explicit, loudly-flagged failure state.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from dataclasses import dataclass, field, asdict

import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score, average_precision_score, confusion_matrix, f1_score,
    precision_score, recall_score, roc_auc_score,
)

__all__ = [
    "QuantizationResult", "quantize_int8", "evaluate_at_threshold", "recalibrate_int8",
    "compare_fp32_int8", "estimate_tflm_arena", "run_tflite",
    "benchmark_latency", "export_c_header", "quantize_and_test",
]

NRF52840_FLASH_KB = 1024
NRF52840_RAM_KB = 256


class _quiet:
    """Silence the SavedModel-export chatter the converter prints on every call.

    TFLite conversion internally exports a SavedModel and dumps its full signature and
    every captured resource tensor to stdout. With three conversion strategies plus a
    probe that is several hundred lines of noise per run, which buries the numbers this
    module exists to report. Redirect at the file-descriptor level, since the output
    comes from C++ rather than Python's `sys.stdout`.
    """

    def __enter__(self):
        import sys
        sys.stdout.flush()
        self._saved = os.dup(1)
        self._null = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self._null, 1)
        return self

    def __exit__(self, *exc):
        import sys
        sys.stdout.flush()
        os.dup2(self._saved, 1)
        os.close(self._null)
        os.close(self._saved)
        return False


# ---------------------------------------------------------------------------
# Input identification
# ---------------------------------------------------------------------------

def _classify_inputs(input_details, window_size, n_rr_features=4):
    """Return (ecg_index, rr_index) into `input_details`.

    The original notebook guessed with `shape[-1] != 4`, which silently breaks if the
    ECG window ever ends in a 4-sized axis. Match on name first (the Keras layers are
    named `ecg_window` / `rr_features`), then fall back to rank/shape, which is
    unambiguous here: the ECG tensor is rank 3 (N, window, 1), RR is rank 2 (N, 4).
    """
    ecg = rr = None
    for i, d in enumerate(input_details):
        name = d["name"].lower()
        if "ecg" in name or "window" in name:
            ecg = i
        elif "rr" in name:
            rr = i
    if ecg is not None and rr is not None and ecg != rr:
        return ecg, rr

    ecg = rr = None
    for i, d in enumerate(input_details):
        shape = [int(s) for s in d["shape"]]
        if len(shape) == 3 and window_size in shape:
            ecg = i
        elif len(shape) == 2 and shape[-1] == n_rr_features:
            rr = i
    if ecg is None or rr is None or ecg == rr:
        raise RuntimeError(
            f"Could not identify ECG vs RR inputs from {[(d['name'], d['shape']) for d in input_details]}"
        )
    return ecg, rr


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------

@dataclass
class QuantizationResult:
    tflite_bytes: bytes = b""
    full_int8: bool = False
    strategy: str = ""
    attempts: list = field(default_factory=list)
    size_kb: float = 0.0
    ecg_scale: float = None
    ecg_zero_point: int = None
    rr_scale: float = None
    rr_zero_point: int = None
    output_scale: float = None
    output_zero_point: int = None

    def summary(self):
        d = asdict(self)
        d.pop("tflite_bytes")
        return d


def _representative_factory(X_val, RR_val_n, order, n_samples=800, seed=42):
    """Yield calibration samples in the order the *converter* expects them.

    This is the fix for the `input->dims->size != 4 (3 != 4)` calibrator crash. With
    Keras 3 (TF >= 2.16) the concrete function traced out of a multi-input functional
    model does not necessarily order its flat input list the same way `model.inputs`
    does. When the order is flipped, the calibrator pushes the rank-2 RR tensor into
    the Conv1D branch, whose kernel expects rank 4 after the implicit ExpandDims --
    hence `3 != 4`. An untrained model converts fine only because the failure needs a
    calibration pass to happen at all, which is why the bug looked weight-dependent.

    `order` is derived by inspecting a throwaway float conversion of the same graph,
    so we feed the tensors in whatever order that specific TF build actually produced.
    """
    rng = np.random.default_rng(seed)
    n = min(n_samples, len(X_val))
    idx = rng.choice(len(X_val), n, replace=False)

    def representative_dataset():
        for i in idx:
            sample = {
                "ecg": X_val[i:i + 1].astype(np.float32),
                "rr": RR_val_n[i:i + 1].astype(np.float32),
            }
            yield [sample[k] for k in order]

    return representative_dataset


def _input_order_from_float_model(model, window_size):
    """Convert once without quantization to learn this TF build's input ordering."""
    with _quiet():
        conv = tf.lite.TFLiteConverter.from_keras_model(model)
        float_model = conv.convert()
    interp = tf.lite.Interpreter(model_content=float_model)
    interp.allocate_tensors()
    details = interp.get_input_details()
    ecg_i, rr_i = _classify_inputs(details, window_size)
    order = [None, None]
    order[ecg_i] = "ecg"
    order[rr_i] = "rr"
    return order, len(float_model)


def _apply_int8_settings(converter, rep_ds):
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = rep_ds
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8
    return converter


def quantize_int8(model, X_val, RR_val_n, window_size, n_calib=800, seed=42,
                  allow_dynamic_range_fallback=False):
    """Convert `model` to a full-integer INT8 .tflite, trying strategies in order.

    Set `allow_dynamic_range_fallback=True` only to unblock desktop experimentation.
    The resulting model will NOT run under TFLite-Micro on the nRF52840.
    """
    result = QuantizationResult()

    try:
        order, float_size = _input_order_from_float_model(model, window_size)
        result.attempts.append(f"probe: float conversion OK ({float_size/1024:.1f} KB), input order = {order}")
    except Exception as e:
        order = ["ecg", "rr"]
        result.attempts.append(f"probe: float conversion failed ({e!r}); assuming order {order}")

    rep_ds = _representative_factory(X_val, RR_val_n, order, n_calib, seed)

    # Strategy A -- direct from the Keras model, with calibration fed in probe order.
    def _strategy_keras():
        with _quiet():
            return _apply_int8_settings(tf.lite.TFLiteConverter.from_keras_model(model), rep_ds).convert()

    # Strategy B -- go through a SavedModel with an explicit batch-1 signature. This
    # pins the input spec instead of relying on whatever the Keras tracer emits, and
    # is the path TF documents for TF >= 2.16.
    def _strategy_savedmodel():
        with tempfile.TemporaryDirectory() as tmp, _quiet():
            path = os.path.join(tmp, "saved_model")
            if hasattr(model, "export"):
                model.export(path)
            else:
                tf.saved_model.save(model, path)
            conv = tf.lite.TFLiteConverter.from_saved_model(path)
            return _apply_int8_settings(conv, rep_ds).convert()

    # Strategy C -- build our own concrete function with a fixed, explicitly ordered
    # batch-1 signature. Batch 1 also matches how the firmware will actually invoke it.
    def _strategy_concrete():
        @tf.function(input_signature=[
            tf.TensorSpec([1, window_size, 1], tf.float32, name="ecg_window"),
            tf.TensorSpec([1, 4], tf.float32, name="rr_features"),
        ])
        def serve(ecg, rr):
            return model([ecg, rr], training=False)

        with _quiet():
            cf = serve.get_concrete_function()
            conv = tf.lite.TFLiteConverter.from_concrete_functions([cf], model)
            return _apply_int8_settings(conv, rep_ds).convert()

    strategies = [
        ("keras_direct", _strategy_keras),
        ("saved_model", _strategy_savedmodel),
        ("concrete_function_batch1", _strategy_concrete),
    ]

    for name, fn in strategies:
        try:
            blob = fn()
            result.tflite_bytes = blob
            result.full_int8 = True
            result.strategy = name
            result.attempts.append(f"{name}: SUCCESS (full integer)")
            break
        except Exception as e:
            result.attempts.append(f"{name}: failed -- {type(e).__name__}: {e}")

    if not result.full_int8:
        if not allow_dynamic_range_fallback:
            raise RuntimeError(
                "All full-integer quantization strategies failed:\n  - "
                + "\n  - ".join(result.attempts)
                + "\n\nNot falling back to dynamic-range: TFLite-Micro has no dynamic-range "
                  "kernels for this graph, so such a model cannot run on the nRF52840. "
                  "Pass allow_dynamic_range_fallback=True only for desktop experiments."
            )
        with _quiet():
            conv = tf.lite.TFLiteConverter.from_keras_model(model)
            conv.optimizations = [tf.lite.Optimize.DEFAULT]
            result.tflite_bytes = conv.convert()
        result.strategy = "dynamic_range_NOT_DEPLOYABLE"
        result.attempts.append("dynamic_range: used as explicit fallback -- NOT deployable on nRF52840")

    result.size_kb = len(result.tflite_bytes) / 1024

    interp = tf.lite.Interpreter(model_content=result.tflite_bytes)
    interp.allocate_tensors()
    in_det, out_det = interp.get_input_details(), interp.get_output_details()
    if result.full_int8:
        ecg_i, rr_i = _classify_inputs(in_det, window_size)
        result.ecg_scale, result.ecg_zero_point = (float(in_det[ecg_i]["quantization"][0]),
                                                   int(in_det[ecg_i]["quantization"][1]))
        result.rr_scale, result.rr_zero_point = (float(in_det[rr_i]["quantization"][0]),
                                                 int(in_det[rr_i]["quantization"][1]))
        result.output_scale, result.output_zero_point = (float(out_det[0]["quantization"][0]),
                                                         int(out_det[0]["quantization"][1]))
    return result


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------

def run_tflite(qr: QuantizationResult, X, RR_n, window_size, batch_one=True):
    """Run the .tflite model over (X, RR_n) and return float probabilities.

    `batch_one=True` invokes one window at a time, which is exactly how the firmware
    will call it. Batched inference can differ slightly because it changes nothing
    numerically here but does exercise a different kernel path; keeping batch 1 means
    the numbers reported are the numbers the device will produce.
    """
    interp = tf.lite.Interpreter(model_content=qr.tflite_bytes)
    in_det = interp.get_input_details()
    out_det = interp.get_output_details()
    ecg_i, rr_i = _classify_inputs(in_det, window_size)

    n = len(X)
    if batch_one:
        interp.resize_tensor_input(in_det[ecg_i]["index"], [1, window_size, 1])
        interp.resize_tensor_input(in_det[rr_i]["index"], [1, RR_n.shape[1]])
    else:
        interp.resize_tensor_input(in_det[ecg_i]["index"], [n, window_size, 1])
        interp.resize_tensor_input(in_det[rr_i]["index"], [n, RR_n.shape[1]])
    interp.allocate_tensors()
    in_det, out_det = interp.get_input_details(), interp.get_output_details()

    def _prep(arr, det):
        if det["dtype"] == np.int8:
            s, z = det["quantization"]
            return np.clip(np.round(arr / s + z), -128, 127).astype(np.int8)
        return arr.astype(np.float32)

    Xq = _prep(X.reshape(n, window_size, 1), in_det[ecg_i])
    RRq = _prep(RR_n, in_det[rr_i])

    raw_codes = np.empty(n, dtype=np.float64)
    if batch_one:
        for i in range(n):
            interp.set_tensor(in_det[ecg_i]["index"], Xq[i:i + 1])
            interp.set_tensor(in_det[rr_i]["index"], RRq[i:i + 1])
            interp.invoke()
            raw_codes[i] = interp.get_tensor(out_det[0]["index"]).flatten()[0]
    else:
        interp.set_tensor(in_det[ecg_i]["index"], Xq)
        interp.set_tensor(in_det[rr_i]["index"], RRq)
        interp.invoke()
        raw_codes = interp.get_tensor(out_det[0]["index"]).flatten().astype(np.float64)

    if out_det[0]["dtype"] == np.int8:
        s, z = out_det[0]["quantization"]
        return (raw_codes - z) * s, raw_codes
    return raw_codes, raw_codes


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def evaluate_at_threshold(y_true, probs, threshold, label=None, verbose=True):
    pred = (probs > threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    m = dict(
        threshold=float(threshold),
        accuracy=float(accuracy_score(y_true, pred)),
        precision=float(precision_score(y_true, pred, zero_division=0)),
        sensitivity=float(recall_score(y_true, pred, zero_division=0)),
        specificity=float(tn / (tn + fp)) if (tn + fp) else 0.0,
        f1_score=float(f1_score(y_true, pred, zero_division=0)),
        roc_auc=float(roc_auc_score(y_true, probs)),
        pr_auc=float(average_precision_score(y_true, probs)),
        tp=int(tp), fp=int(fp), tn=int(tn), fn=int(fn),
    )
    if verbose and label:
        print(f"\n--- {label} (threshold={threshold:.4f}) ---")
        for k, v in m.items():
            print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
    return m


def _mcnemar_exact(b, c):
    """Two-sided exact McNemar p-value for discordant counts (b, c).

    b = FP32 correct & INT8 wrong, c = FP32 wrong & INT8 correct. Under H0 (quantization
    changes nothing systematic) each discordant beat is a fair coin flip, so the exact
    binomial tail is the right test -- and it is the *paired* test, which matters because
    both models are scored on the identical beats. Comparing two independent-sample
    confidence intervals here would be needlessly conservative.
    """
    from math import comb
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(comb(n, i) for i in range(k + 1)) / (2 ** n)
    return float(min(1.0, 2 * tail))


def _bootstrap_delta(y_true, probs_a, probs_b, threshold, metric, n_boot=2000, seed=42):
    """Percentile CI for (metric_b - metric_a), resampling beats in paired fashion."""
    rng = np.random.default_rng(seed)
    n = len(y_true)
    pred_a = (probs_a > threshold).astype(int)
    pred_b = (probs_b > threshold).astype(int)

    def _m(yt, pa):
        tn, fp, fn, tp = confusion_matrix(yt, pa, labels=[0, 1]).ravel()
        if metric == "f1":
            return 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) else 0.0
        if metric == "specificity":
            return tn / (tn + fp) if (tn + fp) else 0.0
        if metric == "sensitivity":
            return tp / (tp + fn) if (tp + fn) else 0.0
        raise ValueError(metric)

    deltas = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        deltas[i] = _m(y_true[idx], pred_b[idx]) - _m(y_true[idx], pred_a[idx])
    return dict(
        observed=float(_m(y_true, pred_b) - _m(y_true, pred_a)),
        ci_lo=float(np.percentile(deltas, 2.5)),
        ci_hi=float(np.percentile(deltas, 97.5)),
    )


def compare_fp32_int8(y_true, probs_fp32, probs_int8, threshold, label="", n_boot=2000):
    """Paired FP32-vs-INT8 comparison at one operating point. Answers RQ2.1 / RQ2.3."""
    pred_a = (probs_fp32 > threshold).astype(int)
    pred_b = (probs_int8 > threshold).astype(int)
    correct_a, correct_b = (pred_a == y_true), (pred_b == y_true)
    b = int(np.sum(correct_a & ~correct_b))
    c = int(np.sum(~correct_a & correct_b))
    p = _mcnemar_exact(b, c)

    out = dict(
        label=label, threshold=float(threshold),
        fp32=evaluate_at_threshold(y_true, probs_fp32, threshold, verbose=False),
        int8=evaluate_at_threshold(y_true, probs_int8, threshold, verbose=False),
        mcnemar=dict(
            fp32_right_int8_wrong=b, fp32_wrong_int8_right=c,
            n_discordant=b + c, p_value=p,
            significant_at_0p05=bool(p < 0.05),
        ),
        label_agreement=float(np.mean(pred_a == pred_b)),
        prob_delta=dict(
            mean_abs=float(np.mean(np.abs(probs_int8 - probs_fp32))),
            max_abs=float(np.max(np.abs(probs_int8 - probs_fp32))),
        ),
        delta_f1=_bootstrap_delta(y_true, probs_fp32, probs_int8, threshold, "f1", n_boot),
        delta_specificity=_bootstrap_delta(y_true, probs_fp32, probs_int8, threshold, "specificity", n_boot),
        delta_sensitivity=_bootstrap_delta(y_true, probs_fp32, probs_int8, threshold, "sensitivity", n_boot),
    )
    return out


def print_comparison(cmp):
    f, q = cmp["fp32"], cmp["int8"]
    print(f"\n=== FP32 vs INT8 @ {cmp['label']} (threshold={cmp['threshold']:.4f}) ===")
    print(f"{'metric':<14}{'FP32':>10}{'INT8':>10}{'delta':>10}")
    for k in ("f1_score", "specificity", "sensitivity", "precision", "accuracy", "roc_auc", "pr_auc"):
        print(f"{k:<14}{f[k]:>10.4f}{q[k]:>10.4f}{q[k]-f[k]:>+10.4f}")
    m = cmp["mcnemar"]
    print(f"\nLabel agreement: {cmp['label_agreement']*100:.3f}%   "
          f"mean|dp|={cmp['prob_delta']['mean_abs']:.5f}  max|dp|={cmp['prob_delta']['max_abs']:.5f}")
    print(f"McNemar: FP32-right/INT8-wrong={m['fp32_right_int8_wrong']}, "
          f"FP32-wrong/INT8-right={m['fp32_wrong_int8_right']}, p={m['p_value']:.4f} "
          f"-> {'SIGNIFICANT difference' if m['significant_at_0p05'] else 'no significant difference'}")
    for name in ("delta_f1", "delta_specificity", "delta_sensitivity"):
        d = cmp[name]
        print(f"  {name:<18} {d['observed']:+.4f}  95% CI [{d['ci_lo']:+.4f}, {d['ci_hi']:+.4f}]")


def recalibrate_int8(qr, model, X_val, RR_val_n, y_val, window_size, batch_one=False,
                     precision_floor=0.90, target_sensitivity=0.90):
    """Re-select operating points on the INT8 model's OWN validation probabilities.

    The pipeline otherwise chooses thresholds from FP32 validation probabilities and then
    applies those same numbers to INT8 test scores. For answering "did quantization change
    the predictions" that is exactly right -- holding the threshold fixed is what makes it
    a controlled comparison.

    For deciding what to ship it is wrong, and pessimistically so. INT8 shifts the score
    distribution (here: systematically more positive), so an FP32-derived cutoff sits in
    the wrong place on the INT8 curve and throws away precision that the model has not
    actually lost. The giveaway is ROC-AUC: if it barely moves under quantization while F1
    drops sharply, the ranking survived and only the calibration moved -- and calibration
    is free to fix, because on-device you would tune the threshold against the INT8 model
    anyway.

    Returns thresholds chosen on INT8 validation scores, to be applied to INT8 test scores.
    Report both: the fixed-threshold comparison answers the research question, the
    recalibrated one describes the deployed device.
    """
    from .thresholds import select_thresholds
    val_probs_int8, _ = run_tflite(qr, X_val, RR_val_n, window_size, batch_one=batch_one)
    return select_thresholds(y_val, val_probs_int8,
                             precision_floor=precision_floor,
                             target_sensitivity=target_sensitivity)


# ---------------------------------------------------------------------------
# Memory footprint
# ---------------------------------------------------------------------------

_DTYPE_BYTES = {np.int8: 1, np.uint8: 1, np.int16: 2, np.uint16: 2,
                np.int32: 4, np.uint32: 4, np.int64: 8, np.float32: 4, np.float16: 2}


def _tensor_bytes(t):
    shape = t["shape"]
    n = int(np.prod(shape)) if getattr(shape, "size", len(shape)) > 0 else 1
    return n * _DTYPE_BYTES.get(t["dtype"], 4)


def estimate_tflm_arena(qr: QuantizationResult, window_size):
    """Estimate the TFLite-Micro tensor arena: peak *simultaneously live* activations.

    The original notebook summed every tensor in the model and called that RAM. That
    overstates the requirement twice over:

      1. It counts weight tensors, which TFLite-Micro reads straight out of the flash
         image (the model is a `const` array) and never copies into the arena.
      2. It ignores lifetime reuse. An activation is dead once its last consumer has
         run, and the arena planner reuses that space, so the requirement is the peak
         of the live set across the op schedule, not the total ever allocated.

    Walking the schedule instead gives a number in the right ballpark for sizing
    `kTensorArenaSize`. It is still an estimate -- the real planner adds per-tensor
    bookkeeping, 16-byte alignment padding, and scratch buffers some kernels request --
    so budget headroom and confirm against what `AllocateTensors()` actually reports on
    hardware before treating it as final.
    """
    interp = tf.lite.Interpreter(model_content=qr.tflite_bytes)
    interp.resize_tensor_input(interp.get_input_details()[0]["index"],
                               interp.get_input_details()[0]["shape"])
    interp.allocate_tensors()
    tensors = interp.get_tensor_details()
    by_index = {t["index"]: t for t in tensors}

    # Constant (weight) tensors live in flash. A tensor is constant if the interpreter
    # can hand us its contents without an invoke and no operator produces it.
    try:
        ops = interp._get_ops_details()
    except Exception as e:
        total = sum(_tensor_bytes(t) for t in tensors)
        return dict(method="fallback_sum_all_tensors", note=f"op schedule unavailable ({e!r})",
                    peak_arena_bytes=total, peak_arena_kb=total / 1024,
                    naive_sum_kb=total / 1024, flash_kb=qr.size_kb)

    produced_at, last_used_at = {}, {}
    for step, op in enumerate(ops):
        for ti in op["inputs"]:
            if ti >= 0:
                last_used_at[ti] = step
        for ti in op["outputs"]:
            if ti >= 0:
                produced_at.setdefault(ti, step)

    graph_inputs = {d["index"] for d in interp.get_input_details()}
    graph_outputs = {d["index"] for d in interp.get_output_details()}
    for ti in graph_inputs:
        produced_at.setdefault(ti, -1)
    for ti in graph_outputs:
        last_used_at[ti] = len(ops)

    # Anything never produced by an op and not a graph input is a constant -> flash.
    activation_indices = set(produced_at)
    weight_bytes = sum(_tensor_bytes(by_index[i]) for i in by_index
                       if i not in activation_indices)

    peak, peak_step = 0, -1
    for step in range(len(ops)):
        live = 0
        for ti in activation_indices:
            if produced_at.get(ti, 1 << 30) <= step <= last_used_at.get(ti, -1):
                live += _tensor_bytes(by_index[ti])
        if live > peak:
            peak, peak_step = live, step

    naive = sum(_tensor_bytes(t) for t in tensors)
    return dict(
        method="peak_live_activation_set",
        n_ops=len(ops),
        peak_arena_bytes=int(peak),
        peak_arena_kb=peak / 1024,
        peak_at_op=int(peak_step),
        peak_op_name=ops[peak_step]["op_name"] if peak_step >= 0 else None,
        weights_in_flash_kb=weight_bytes / 1024,
        naive_sum_all_tensors_kb=naive / 1024,
        flash_kb=qr.size_kb,
        flash_headroom_kb=NRF52840_FLASH_KB - qr.size_kb,
        ram_headroom_kb=NRF52840_RAM_KB - peak / 1024,
        fits_nrf52840=bool(qr.size_kb < NRF52840_FLASH_KB and peak / 1024 < NRF52840_RAM_KB),
    )


def benchmark_latency(qr: QuantizationResult, X, RR_n, window_size, n_runs=200, warmup=20):
    """Single-window inference latency on *this* machine.

    This is a desktop/Colab x86 number and says nothing directly about the nRF52840's
    Cortex-M4 -- it is here to catch pathological regressions and to give a relative
    FP32-vs-INT8 figure. Real timing has to be measured on hardware.
    """
    interp = tf.lite.Interpreter(model_content=qr.tflite_bytes)
    in_det = interp.get_input_details()
    ecg_i, rr_i = _classify_inputs(in_det, window_size)
    interp.resize_tensor_input(in_det[ecg_i]["index"], [1, window_size, 1])
    interp.resize_tensor_input(in_det[rr_i]["index"], [1, RR_n.shape[1]])
    interp.allocate_tensors()
    in_det = interp.get_input_details()

    def _prep(arr, det):
        if det["dtype"] == np.int8:
            s, z = det["quantization"]
            return np.clip(np.round(arr / s + z), -128, 127).astype(np.int8)
        return arr.astype(np.float32)

    x = _prep(X[:1].reshape(1, window_size, 1), in_det[ecg_i])
    r = _prep(RR_n[:1], in_det[rr_i])

    for _ in range(warmup):
        interp.set_tensor(in_det[ecg_i]["index"], x)
        interp.set_tensor(in_det[rr_i]["index"], r)
        interp.invoke()

    times = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        interp.set_tensor(in_det[ecg_i]["index"], x)
        interp.set_tensor(in_det[rr_i]["index"], r)
        interp.invoke()
        times.append((time.perf_counter() - t0) * 1000)
    times = np.array(times)
    return dict(n_runs=n_runs, mean_ms=float(times.mean()), p50_ms=float(np.percentile(times, 50)),
                p95_ms=float(np.percentile(times, 95)), min_ms=float(times.min()),
                note="host CPU, not nRF52840 -- measure on hardware for the real figure")


def int8_threshold_grid(qr: QuantizationResult, threshold):
    """Map a float threshold onto the INT8 output grid the device actually compares on.

    The sigmoid output is INT8, so probabilities land on ~256 discrete levels. Firmware
    that compares a dequantized float against a float threshold is doing the same
    comparison as `code > ceil(threshold/scale + zero_point) - 1`, only slower and with
    rounding risk. Bake the integer cutoff in instead, and report the *effective*
    threshold so the thesis quotes the operating point the device truly uses.
    """
    if not qr.full_int8:
        return dict(applicable=False, reason="model is not full-integer; output is float32")
    s, z = qr.output_scale, qr.output_zero_point
    code = int(np.floor(threshold / s + z))
    if (code - z) * s <= threshold:
        code += 1
    code = int(np.clip(code, -128, 127))
    return dict(applicable=True, float_threshold=float(threshold), output_scale=s,
                output_zero_point=z, int8_cutoff_code=code,
                effective_float_threshold=float((code - z) * s),
                n_distinct_levels=256,
                firmware_rule=f"classify as ARRHYTHMIA when raw int8 output >= {code}")


def export_c_header(tflite_bytes, header_path, array_name="tibok_model"):
    with open(header_path, "w") as f:
        f.write(f"#ifndef {array_name.upper()}_H\n#define {array_name.upper()}_H\n\n")
        f.write("#include <stddef.h>\n#ifndef __cplusplus\n#include <stdalign.h>\n#endif\n\n")
        f.write("#ifdef __cplusplus\nextern \"C\" {\n#endif\n\n")
        f.write(f"alignas(16) const unsigned char {array_name}[] = {{\n")
        for i, byte in enumerate(tflite_bytes):
            f.write(f"0x{byte:02x}, ")
            if (i + 1) % 12 == 0:
                f.write("\n")
        f.write(f"\n}};\n\nconst size_t {array_name}_len = {len(tflite_bytes)};\n\n")
        f.write("#ifdef __cplusplus\n}\n#endif\n\n#endif\n")
    print(f"Header written: {header_path} ({len(tflite_bytes)/1024:.2f} KB)")
    return header_path


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def quantize_and_test(model, X_val, RR_val_n, X_test, RR_test_n, y_test,
                      thresholds, window_size, run_tag="tibok", y_val=None,
                      test_symbols=None, deploy_threshold_name="precision_floor_90",
                      rr_mean=None, rr_std=None, n_calib=800, n_boot=2000,
                      batch_one=True, out_dir=".", allow_dynamic_range_fallback=False):
    """Full quantization + verification pass. Returns a JSON-serializable report."""
    os.makedirs(out_dir, exist_ok=True)
    report = {"run_tag": run_tag, "window_size": window_size}

    print("=" * 72)
    print("STEP 1 -- INT8 conversion")
    print("=" * 72)
    qr = quantize_int8(model, X_val, RR_val_n, window_size, n_calib=n_calib,
                       allow_dynamic_range_fallback=allow_dynamic_range_fallback)
    for a in qr.attempts:
        print(f"  {a}")
    print(f"\nStrategy: {qr.strategy}   full_int8={qr.full_int8}   size={qr.size_kb:.2f} KB")
    if not qr.full_int8:
        print("  *** WARNING: dynamic-range model -- will NOT run under TFLite-Micro. ***")
    report["quantization"] = qr.summary()

    tflite_path = os.path.join(out_dir, f"{run_tag}_model_int8.tflite")
    with open(tflite_path, "wb") as f:
        f.write(qr.tflite_bytes)

    print("\n" + "=" * 72)
    print("STEP 2 -- memory footprint vs nRF52840 budget")
    print("=" * 72)
    mem = estimate_tflm_arena(qr, window_size)
    report["memory"] = mem
    for k, v in mem.items():
        print(f"  {k}: {v:.2f}" if isinstance(v, float) else f"  {k}: {v}")

    print("\n" + "=" * 72)
    print("STEP 3 -- inference (FP32 reference vs INT8), batch=1" if batch_one
          else "STEP 3 -- inference (FP32 reference vs INT8)")
    print("=" * 72)
    probs_fp32 = model.predict([X_test, RR_test_n], batch_size=256, verbose=0).flatten()
    t0 = time.time()
    probs_int8, raw_codes = run_tflite(qr, X_test, RR_test_n, window_size, batch_one=batch_one)
    print(f"  INT8 inference over {len(y_test)} test beats: {time.time()-t0:.1f}s")
    print(f"  FP32 ROC-AUC {roc_auc_score(y_test, probs_fp32):.4f} | "
          f"INT8 ROC-AUC {roc_auc_score(y_test, probs_int8):.4f}")
    if qr.full_int8:
        print(f"  Distinct INT8 output codes observed: {len(np.unique(raw_codes))} / 256")

    print("\n" + "=" * 72)
    print("STEP 4 -- paired FP32 vs INT8 comparison  (RQ2.1 / RQ2.3)")
    print("=" * 72)
    print("  Thresholds held fixed at their FP32 validation values -- the controlled")
    print("  comparison that answers the research question.")
    comparisons = {}
    for name, thr in thresholds.items():
        cmp = compare_fp32_int8(y_test, probs_fp32, probs_int8, thr, label=name, n_boot=n_boot)
        print_comparison(cmp)
        comparisons[name] = cmp
    report["comparisons"] = comparisons

    # --- Step 4b: what the device would actually do -------------------------------
    # Thresholds re-chosen on the INT8 model's own validation scores. See
    # `recalibrate_int8` for why the fixed-threshold numbers understate the shipped model.
    if y_val is not None:
        print("\n" + "=" * 72)
        print("STEP 4b -- INT8 with thresholds recalibrated on INT8 validation scores")
        print("=" * 72)
        int8_thr = recalibrate_int8(qr, model, X_val, RR_val_n, y_val, window_size,
                                    batch_one=batch_one)
        recal = {}
        print(f"{'operating point':<22}{'thr(FP32)':>11}{'thr(INT8)':>11}"
              f"{'F1':>9}{'prec':>9}{'sens':>9}{'spec':>9}")
        for name, thr in int8_thr.items():
            m = evaluate_at_threshold(y_test, probs_int8, thr, verbose=False)
            fixed = comparisons[name]["int8"]
            recal[name] = {"threshold_fp32": float(thresholds[name]),
                           "threshold_int8": float(thr), "metrics": m,
                           "delta_f1_vs_fixed": m["f1_score"] - fixed["f1_score"]}
            print(f"{name:<22}{thresholds[name]:>11.4f}{thr:>11.4f}"
                  f"{m['f1_score']:>9.4f}{m['precision']:>9.4f}"
                  f"{m['sensitivity']:>9.4f}{m['specificity']:>9.4f}")
        print("\n  recovery vs the fixed-threshold INT8 numbers above:")
        for name, d in recal.items():
            print(f"    {name:<22} F1 {d['delta_f1_vs_fixed']:+.4f}")
        report["int8_recalibrated"] = recal

    if test_symbols is not None:
        print("\n" + "=" * 72)
        print("STEP 5 -- per-AAMI-symbol sensitivity, FP32 vs INT8")
        print("=" * 72)
        thr = thresholds[deploy_threshold_name]
        sym = np.asarray(test_symbols)
        pf = (probs_fp32 > thr).astype(int)
        pq = (probs_int8 > thr).astype(int)
        breakdown = {}
        print(f"{'sym':<6}{'n':>7}{'FP32':>10}{'INT8':>10}{'delta':>9}")
        for s in sorted(set(sym[y_test == 1])):
            mask = (sym == s) & (y_test == 1)
            n = int(mask.sum())
            if not n:
                continue
            a, b = float(pf[mask].mean()), float(pq[mask].mean())
            breakdown[s] = dict(n=n, fp32_sensitivity=a, int8_sensitivity=b, delta=b - a)
            print(f"{s:<6}{n:>7}{a:>10.4f}{b:>10.4f}{b-a:>+9.4f}")
        report["symbol_breakdown"] = breakdown

    print("\n" + "=" * 72)
    print("STEP 6 -- latency + firmware constants")
    print("=" * 72)
    lat = benchmark_latency(qr, X_test, RR_test_n, window_size)
    report["latency"] = lat
    print(f"  mean {lat['mean_ms']:.3f} ms | p50 {lat['p50_ms']:.3f} | p95 {lat['p95_ms']:.3f}  ({lat['note']})")

    deploy_thr = thresholds[deploy_threshold_name]
    grid = int8_threshold_grid(qr, deploy_thr)
    report["int8_threshold"] = grid
    if grid.get("applicable"):
        print(f"\n  Deploy threshold {deploy_thr:.4f} -> int8 cutoff code {grid['int8_cutoff_code']} "
              f"(effective {grid['effective_float_threshold']:.4f})")
        print(f"  {grid['firmware_rule']}")

    header_path = os.path.join(out_dir, f"{run_tag}_model_int8.h")
    export_c_header(qr.tflite_bytes, header_path)

    fw = {
        "full_int8": qr.full_int8,
        "deployable_on_tflm": bool(qr.full_int8),
        "ecg_scale": qr.ecg_scale, "ecg_zero_point": qr.ecg_zero_point,
        "rr_scale": qr.rr_scale, "rr_zero_point": qr.rr_zero_point,
        "output_scale": qr.output_scale, "output_zero_point": qr.output_zero_point,
        "rr_feature_mean": list(map(float, rr_mean)) if rr_mean is not None else None,
        "rr_feature_std": list(map(float, rr_std)) if rr_std is not None else None,
        "deploy_threshold_name": deploy_threshold_name,
        "deploy_threshold_float": float(deploy_thr),
        "deploy_threshold_int8_code": grid.get("int8_cutoff_code"),
        "tensor_arena_bytes_estimate": mem.get("peak_arena_bytes"),
    }
    report["firmware"] = fw
    print("\n  Firmware constants:")
    for k, v in fw.items():
        print(f"    {k} = {v}")

    report_path = os.path.join(out_dir, f"{run_tag}_quantization_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nWrote: {tflite_path}\n       {header_path}\n       {report_path}")

    print("\n" + "=" * 72)
    print("VERDICT")
    print("=" * 72)
    d = comparisons[deploy_threshold_name]
    print(f"  Full-integer INT8: {'YES' if qr.full_int8 else 'NO -- NOT DEPLOYABLE'}")
    print(f"  Fits nRF52840:     {mem.get('fits_nrf52840')} "
          f"(flash {qr.size_kb:.1f}/{NRF52840_FLASH_KB} KB, "
          f"arena ~{mem.get('peak_arena_kb', 0):.1f}/{NRF52840_RAM_KB} KB)")
    print(f"  At {deploy_threshold_name}:  dF1 {d['delta_f1']['observed']:+.4f} "
          f"[{d['delta_f1']['ci_lo']:+.4f}, {d['delta_f1']['ci_hi']:+.4f}], "
          f"dSpec {d['delta_specificity']['observed']:+.4f} "
          f"[{d['delta_specificity']['ci_lo']:+.4f}, {d['delta_specificity']['ci_hi']:+.4f}]")
    print(f"  McNemar p={d['mcnemar']['p_value']:.4f} -> "
          f"{'quantization DID change predictions significantly' if d['mcnemar']['significant_at_0p05'] else 'no significant change from quantization'}")
    return report
