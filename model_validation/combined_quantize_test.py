# -*- coding: utf-8 -*-
"""TIBOK — Model Quantization & Testing (Section G, EXTENSION), MIT-BIH + INCART

**This is NOT the protocol described in RIM-01_Pre-Oral_9.pdf** — see
mitbih_quantize_test.py for the script that matches the plan, and
README.md for how the two relate.

Post-training INT8 full-integer quantization of the FP32 network trained by
`combined_train.py`, evaluated FP32-vs-INT8 on the same held-out test set.

Requires `combined_train.py` to have been run first (needs
`<RUN_TAG>_model.keras` and `<RUN_TAG>_train_summary.json` in OUTPUT_DIR).
Re-derives the validation/test arrays via `combined_data.load_all()` — this
is deterministic (fixed seed=42), so it reproduces byte-for-byte the same
splits and RR normalization the training stage used; a saved-vs-recomputed
rr_mean/rr_std check below guards against silent drift.

Known environment-specific issue: on some TF builds, full-integer
calibration of this exact two-input (ECG window + RR features) graph fails
inside the TFLite calibrator once the model has *trained* weights. If it
fails here, this falls back automatically to dynamic-range (weight-only
INT8) quantization, which still shrinks the model ~4x and runs correctly on
the nRF52840's Cortex-M4 FPU.
"""

import os, json
import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    average_precision_score, roc_auc_score, confusion_matrix,
    accuracy_score, precision_score, recall_score, f1_score,
)

import combined_data as data

np.random.seed(42)
tf.random.set_seed(42)

RUN_TAG = "tibok_combined_rr_cnn"
OUTPUT_DIR = os.environ.get("TIBOK_OUTPUT_DIR", os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(OUTPUT_DIR, f'{RUN_TAG}_model.keras')
TRAIN_SUMMARY_PATH = os.path.join(OUTPUT_DIR, f'{RUN_TAG}_train_summary.json')

if not os.path.exists(MODEL_PATH) or not os.path.exists(TRAIN_SUMMARY_PATH):
    raise FileNotFoundError(
        f"Missing {MODEL_PATH} or {TRAIN_SUMMARY_PATH}. Run combined_train.py "
        "(Section C, extension) first — this script picks up where it left off."
    )

with open(TRAIN_SUMMARY_PATH) as f:
    train_summary = json.load(f)

print(f"Loading trained model from {MODEL_PATH} ...")
model = tf.keras.models.load_model(MODEL_PATH, compile=False)

# ---------------------------------------------------------------------------
# Re-derive validation/test data (deterministic — see combined_data.py)
# ---------------------------------------------------------------------------

d = data.load_all()
X_val, RR_val_n = d["X_val"], d["RR_val_n"]
X_test, y_test, RR_test_n = d["X_test"], d["y_test"], d["RR_test_n"]
y_test_symbols, rr_mean, rr_std = d["y_test_symbols"], d["rr_mean"], d["rr_std"]

saved_mean = np.array(train_summary["rr_feature_norm"]["mean"])
saved_std = np.array(train_summary["rr_feature_norm"]["std"])
if not (np.allclose(rr_mean, saved_mean) and np.allclose(rr_std, saved_std)):
    raise RuntimeError(
        "RR-feature normalization recomputed here does not match "
        f"{TRAIN_SUMMARY_PATH}. The data pipeline or PhysioNet mirror may "
        "have changed since training — do not trust the quantized model "
        "until this is resolved (re-run combined_train.py to retrain, or "
        "investigate the data source discrepancy)."
    )

thresholds = train_summary["thresholds"]

# ---------------------------------------------------------------------------
# INT8 post-training quantization
# ---------------------------------------------------------------------------

def representative_dataset():
    rng = np.random.default_rng(42)
    n = min(800, len(X_val))
    idx = rng.choice(len(X_val), n, replace=False)
    for i in idx:
        yield [X_val[i:i+1].astype(np.float32), RR_val_n[i:i+1].astype(np.float32)]


FULL_INT8_OK = True
try:
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = representative_dataset
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8
    tflite_model = converter.convert()
    print("Full-integer (INT8 activations + I/O) quantization succeeded.")
except Exception as e:
    print(f"Full-integer quantization failed in this environment ({e!r}); falling back to dynamic-range INT8.")
    FULL_INT8_OK = False
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

with open(os.path.join(OUTPUT_DIR, f'{RUN_TAG}_model.tflite'), 'wb') as f:
    f.write(tflite_model)
print(f"Quantized model size: {len(tflite_model) / 1024:.2f} KB  (full_int8={FULL_INT8_OK})")

interpreter = tf.lite.Interpreter(model_content=tflite_model)
interpreter.allocate_tensors()
in_details = interpreter.get_input_details()
out_details = interpreter.get_output_details()

tensor_details = interpreter.get_tensor_details()
def dtype_size(dt):
    return {np.int8: 1, np.uint8: 1, np.int16: 2, np.uint16: 2, np.int32: 4, np.uint32: 4, np.float32: 4}.get(dt, 0)
total_ram_bytes = sum((np.prod(t['shape']) if t['shape'].size > 0 else 1) * dtype_size(t['dtype']) for t in tensor_details)

nrf52840_flash_kb, nrf52840_ram_kb = 1024, 256
print(f"Estimated tensor RAM: {total_ram_bytes/1024:.2f} KB")
print(f"Flash headroom: {nrf52840_flash_kb - len(tflite_model)/1024:.2f} KB")
print(f"RAM headroom:   {nrf52840_ram_kb - total_ram_bytes/1024:.2f} KB")

ecg_idx = 0 if in_details[0]['shape'][-1] != 4 else 1
rr_idx = 1 - ecg_idx

if FULL_INT8_OK:
    ecg_scale, ecg_zp = in_details[ecg_idx]['quantization']
    rr_scale, rr_zp = in_details[rr_idx]['quantization']
    out_scale, out_zp = out_details[0]['quantization']
    X_test_q = np.clip(np.round(X_test / ecg_scale + ecg_zp), -128, 127).astype(np.int8)
    RR_test_q = np.clip(np.round(RR_test_n / rr_scale + rr_zp), -128, 127).astype(np.int8)
    interpreter.resize_tensor_input(in_details[ecg_idx]['index'], [len(X_test_q), data.WINDOW_SIZE, 1])
    interpreter.resize_tensor_input(in_details[rr_idx]['index'], [len(RR_test_q), 4])
    interpreter.allocate_tensors()
    interpreter.set_tensor(in_details[ecg_idx]['index'], X_test_q)
    interpreter.set_tensor(in_details[rr_idx]['index'], RR_test_q)
    interpreter.invoke()
    out = interpreter.get_tensor(out_details[0]['index'])
    y_test_probs_int8 = ((out.astype(np.float32) - out_zp) * out_scale).flatten()
else:
    interpreter.resize_tensor_input(in_details[ecg_idx]['index'], [len(X_test), data.WINDOW_SIZE, 1])
    interpreter.resize_tensor_input(in_details[rr_idx]['index'], [len(RR_test_n), 4])
    interpreter.allocate_tensors()
    interpreter.set_tensor(in_details[ecg_idx]['index'], X_test.astype(np.float32))
    interpreter.set_tensor(in_details[rr_idx]['index'], RR_test_n.astype(np.float32))
    interpreter.invoke()
    y_test_probs_int8 = interpreter.get_tensor(out_details[0]['index']).flatten()

print(f"\nINT8 test ROC-AUC: {roc_auc_score(y_test, y_test_probs_int8):.4f}")
print(f"(FP32 test ROC-AUC from training run: see {RUN_TAG}_train_summary.json)")


def evaluate(y_true, probs, threshold, label):
    pred = (probs > threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred).ravel()
    metrics = dict(
        threshold=float(threshold), accuracy=accuracy_score(y_true, pred),
        precision=precision_score(y_true, pred, zero_division=0),
        sensitivity=recall_score(y_true, pred, zero_division=0),
        specificity=tn / (tn + fp) if (tn + fp) > 0 else 0,
        f1_score=f1_score(y_true, pred, zero_division=0),
        roc_auc=roc_auc_score(y_true, probs), pr_auc=average_precision_score(y_true, probs),
        tp=int(tp), fp=int(fp), tn=int(tn), fn=int(fn),
    )
    print(f"\n--- {label} (threshold={threshold:.4f}) ---")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
    return metrics


int8_test_results = {}
for name, thr in thresholds.items():
    int8_test_results[name] = evaluate(y_test, y_test_probs_int8, thr, f"INT8 TEST — {name}")

deploy_threshold = thresholds[train_summary["deploy_threshold_recommended"]]
y_test_pred_int8 = (y_test_probs_int8 > deploy_threshold).astype(int)
int8_symbol_breakdown = {}
for sym in sorted(set(y_test_symbols[y_test == 1])):
    mask = (y_test_symbols == sym) & (y_test == 1)
    n = int(mask.sum())
    if n == 0:
        continue
    caught = int((y_test_pred_int8[mask] == 1).sum())
    int8_symbol_breakdown[sym] = {"n": n, "caught": caught, "sensitivity": caught / n}

print(f"Per-AAMI-symbol sensitivity (deploy threshold, INT8):")
for sym, d_ in int8_symbol_breakdown.items():
    print(f"  {sym}: {d_['caught']}/{d_['n']} ({d_['sensitivity']:.4f})")

# ---------------------------------------------------------------------------
# C header export for TensorFlow Lite Micro
# ---------------------------------------------------------------------------

def convert_to_c_array(tflite_path, header_path, array_name="tibok_model"):
    with open(tflite_path, 'rb') as f:
        content = f.read()
    with open(header_path, 'w') as f:
        f.write(f"#ifndef {array_name.upper()}_H\n#define {array_name.upper()}_H\n\n")
        f.write("#include <stddef.h>\n#ifndef __cplusplus\n#include <stdalign.h>\n#endif\n\n")
        f.write("#ifdef __cplusplus\nextern \"C\" {\n#endif\n\n")
        f.write(f"alignas(16) const unsigned char {array_name}[] = {{\n")
        for i, byte in enumerate(content):
            f.write(f"0x{byte:02x}, ")
            if (i + 1) % 12 == 0:
                f.write("\n")
        f.write(f"\n}};\n\nconst size_t {array_name}_len = {len(content)};\n\n")
        f.write("#ifdef __cplusplus\n}\n#endif\n\n#endif\n")
    print(f"Header written: {header_path} ({len(content)/1024:.2f} KB)")


convert_to_c_array(
    os.path.join(OUTPUT_DIR, f'{RUN_TAG}_model.tflite'),
    os.path.join(OUTPUT_DIR, f'{RUN_TAG}_model.h'),
    'tibok_model',
)
print(f"\nFirmware constants:")

firmware_constants = {}
if FULL_INT8_OK:
    firmware_constants = {
        "ECG_SCALE": float(ecg_scale), "ECG_ZERO_POINT": int(ecg_zp),
        "RR_SCALE": float(rr_scale), "RR_ZERO_POINT": int(rr_zp),
        "OUTPUT_SCALE": float(out_scale), "OUTPUT_ZERO_POINT": int(out_zp),
    }
    print(f"ECG_SCALE={ecg_scale}, ECG_ZERO_POINT={ecg_zp}")
    print(f"RR_SCALE={rr_scale}, RR_ZERO_POINT={rr_zp}")
    print(f"OUTPUT_SCALE={out_scale}, OUTPUT_ZERO_POINT={out_zp}")
else:
    print("Full-integer quantization fell back to dynamic-range (weight-only INT8) in this")
    print("environment — the .tflite model takes FLOAT32 input/output directly, not int8,")
    print("so there is no ECG_SCALE/RR_SCALE/OUTPUT_SCALE to bake into firmware here.")
    print("Feed the model raw float32 ECG samples and RR features (normalized exactly as")
    print("below), not quantized int8 codes.")

print(f"RR_FEATURE_MEAN={rr_mean.tolist()}")
print(f"RR_FEATURE_STD={rr_std.tolist()}")
print(f"DEPLOY_THRESHOLD ({train_summary['deploy_threshold_recommended']}) = {deploy_threshold:.4f}")

summary = {
    "run_tag": RUN_TAG,
    "full_int8_ok": FULL_INT8_OK,
    "tflite_size_kb": len(tflite_model) / 1024,
    "estimated_tensor_ram_kb": float(total_ram_bytes / 1024),
    "nrf52840_flash_headroom_kb": nrf52840_flash_kb - len(tflite_model) / 1024,
    "nrf52840_ram_headroom_kb": nrf52840_ram_kb - float(total_ram_bytes / 1024),
    "thresholds": thresholds,
    "deploy_threshold_recommended": train_summary["deploy_threshold_recommended"],
    "int8_test_results": int8_test_results,
    "int8_symbol_breakdown": int8_symbol_breakdown,
    "fp32_test_results_for_comparison": train_summary["fp32_test_results"],
    "fp32_symbol_breakdown_for_comparison": train_summary["fp32_symbol_breakdown"],
    "firmware_constants": firmware_constants,
    "rr_feature_norm": {"mean": rr_mean.tolist(), "std": rr_std.tolist()},
}
with open(os.path.join(OUTPUT_DIR, f'{RUN_TAG}_quantize_test_summary.json'), 'w') as f:
    json.dump(summary, f, indent=2)

print(f"\nSaved {RUN_TAG}_model.tflite, {RUN_TAG}_model.h, and "
      f"{RUN_TAG}_quantize_test_summary.json to {OUTPUT_DIR}")
