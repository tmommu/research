# -*- coding: utf-8 -*-
"""TIBOK — Model Architecture Training (Section C, EXTENSION), MIT-BIH + INCART

**This is NOT the protocol described in RIM-01_Pre-Oral_9.pdf.** See
mitbih_train.py for the script that matches the plan, and README.md for how
the two relate. This is the source notebook's MIT-BIH+INCART pooled
protocol, kept as a labeled ablation/extension.

Trains the FP32 desktop model, picks validation-selected thresholds, and
evaluates the FP32 model on the held-out test set. Saves the trained model
and a summary JSON that `combined_quantize_test.py` (Section G) picks up
for INT8 quantization and FP32-vs-INT8 testing.

**Architecture**: ECG window (1250x1) -> 3xConv1D(16/32/64, k7, BN+ReLU+SpatialDropout) ->
GlobalAveragePooling1D(64) (+) RR features (4) -> Dense(16) -> Concat(80) -> Dense(32) -> Dropout ->
Output(1, sigmoid).
"""

import os, json, time
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.keras import Model
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import (
    average_precision_score, roc_auc_score, precision_recall_curve,
    confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
)
from sklearn.utils.class_weight import compute_class_weight

import combined_data as data

np.random.seed(42)
tf.random.set_seed(42)
os.environ['PYTHONHASHSEED'] = '42'
os.environ['TF_DETERMINISTIC_OPS'] = '1'
os.environ['TF_CUDNN_DETERMINISTIC'] = '1'
tf.config.experimental.enable_op_determinism()

RUN_TAG = "tibok_combined_rr_cnn"
OUTPUT_DIR = os.environ.get("TIBOK_OUTPUT_DIR", os.path.dirname(os.path.abspath(__file__)))
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"RUN_TAG = {RUN_TAG}")
gpus = tf.config.list_physical_devices('GPU')
print(f"GPUs available: {len(gpus)}")
for gpu in gpus:
    print(f"  {gpu}")
if not gpus:
    print("No GPU detected — training will run on CPU and will be substantially slower.")

# ---------------------------------------------------------------------------
# Load data (see combined_data.py)
# ---------------------------------------------------------------------------

d = data.load_all()
X_train, y_train, RR_train_n = d["X_train"], d["y_train"], d["RR_train_n"]
X_val, y_val, RR_val_n = d["X_val"], d["y_val"], d["RR_val_n"]
X_test, y_test, RR_test_n = d["X_test"], d["y_test"], d["RR_test_n"]
y_test_symbols, rr_mean, rr_std = d["y_test_symbols"], d["rr_mean"], d["rr_std"]

print("Train class balance:", pd.Series(y_train).value_counts(normalize=True).to_dict())
print("Test  class balance:", pd.Series(y_test).value_counts(normalize=True).to_dict())

# ---------------------------------------------------------------------------
# Minority-class augmentation (time shift, baseline wander, powerline hum,
# Gaussian noise, amplitude scaling), applied 2x to arrhythmia-class windows
# only. RR features are carried over unchanged for augmented copies since
# the augmentation only perturbs the signal, not beat timing.
# ---------------------------------------------------------------------------

aug_rng = np.random.default_rng(42)
X_train_aug, RR_train_aug, y_train_aug = data.augment_dataset(X_train, RR_train_n, y_train, aug_rng)
shuffle_idx = np.random.RandomState(42).permutation(len(y_train_aug))
X_train_aug = X_train_aug[shuffle_idx]; RR_train_aug = RR_train_aug[shuffle_idx]; y_train_aug = y_train_aug[shuffle_idx]
print(f"After augmentation: X_train {X_train_aug.shape}, class balance:",
      pd.Series(y_train_aug).value_counts(normalize=True).to_dict())

# ---------------------------------------------------------------------------
# Model: CNN branch (morphology) + RR branch (rhythm timing), fused before
# the classifier head. Uses the source notebook's focal loss as-is
# (alpha=0.3 for the positive/arrhythmia term) — see README.md for why this
# is arguably backwards for a screening device, kept here for fidelity to
# the original notebook rather than silently changed.
# ---------------------------------------------------------------------------

def focal_loss(gamma=3.0, alpha=0.3):
    def focal_loss_fixed(y_true, y_pred):
        y_true = tf.cast(y_true, tf.float32)
        epsilon = tf.keras.backend.epsilon()
        y_pred = tf.clip_by_value(y_pred, epsilon, 1.0 - epsilon)
        pos_term = -alpha * y_true * tf.pow(1.0 - y_pred, gamma) * tf.math.log(y_pred)
        neg_term = -(1.0 - alpha) * (1.0 - y_true) * tf.pow(y_pred, gamma) * tf.math.log(1.0 - y_pred)
        return tf.reduce_mean(tf.reduce_sum(pos_term + neg_term, axis=-1))
    return focal_loss_fixed


def build_model(window_size, n_rr_features=4):
    sig_in = layers.Input(shape=(window_size, 1), name="ecg_window")
    x = sig_in
    for filters, kernel, stride in [(16, 7, 4), (32, 7, 4), (64, 7, 2)]:
        x = layers.Conv1D(filters, kernel_size=kernel, strides=stride, padding='same',
                           kernel_regularizer=tf.keras.regularizers.l2(1e-4))(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation('relu')(x)
        x = layers.SpatialDropout1D(0.15)(x)
    x = layers.GlobalAveragePooling1D()(x)

    rr_in = layers.Input(shape=(n_rr_features,), name="rr_features")
    r = layers.Dense(16, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(1e-4))(rr_in)

    merged = layers.Concatenate()([x, r])
    merged = layers.Dropout(0.5)(merged)
    merged = layers.Dense(32, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(1e-4))(merged)
    merged = layers.Dropout(0.4)(merged)
    out = layers.Dense(1, activation='sigmoid')(merged)

    model = Model(inputs=[sig_in, rr_in], outputs=out)
    model.compile(
        optimizer=Adam(learning_rate=3e-4),
        loss=focal_loss(gamma=3.0, alpha=0.3),
        metrics=['accuracy', tf.keras.metrics.Precision(name='precision'),
                 tf.keras.metrics.Recall(name='recall')]
    )
    return model


build_model(data.WINDOW_SIZE).summary()

# ---------------------------------------------------------------------------
# Training — best-of-N candidate search, model selected by validation PR-AUC
# ---------------------------------------------------------------------------

early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=6, restore_best_weights=True)
reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6)

class_weights = compute_class_weight(class_weight='balanced', classes=np.unique(y_train_aug), y=y_train_aug)
class_weight_dict = {i: w for i, w in enumerate(class_weights)}
class_weight_dict[1] *= 1.3  # extra recall bias — a missed arrhythmia is costlier than a false alarm
print(f"Class weights: {class_weight_dict}")

N_CANDIDATES = int(os.environ.get("TIBOK_N_CANDIDATES", "3"))
EPOCHS = int(os.environ.get("TIBOK_EPOCHS", "50"))
BATCH_SIZE = 128

best_val_pr_auc = -1
best_model = None
all_candidates, candidate_val_pr_aucs = [], []

t0 = time.time()
for i in range(N_CANDIDATES):
    print(f"\n=== Candidate {i+1}/{N_CANDIDATES} ===")
    tf.keras.utils.set_random_seed(4000 + i)
    candidate = build_model(data.WINDOW_SIZE)
    candidate.fit(
        [X_train_aug, RR_train_aug], y_train_aug,
        validation_data=([X_val, RR_val_n], y_val),
        epochs=EPOCHS, batch_size=BATCH_SIZE,
        callbacks=[early_stop, reduce_lr],
        class_weight=class_weight_dict, verbose=2,
    )
    val_probs = candidate.predict([X_val, RR_val_n], batch_size=256, verbose=0).flatten()
    val_pr_auc = average_precision_score(y_val, val_probs)
    print(f"Candidate {i+1} val PR-AUC: {val_pr_auc:.4f}")
    all_candidates.append(candidate)
    candidate_val_pr_aucs.append(val_pr_auc)
    if val_pr_auc > best_val_pr_auc:
        best_val_pr_auc = val_pr_auc
        best_model = candidate

print(f"\nTraining wall time: {(time.time()-t0)/60:.1f} min")
print(f"Best candidate val PR-AUC: {best_val_pr_auc:.4f}  (per-candidate: {candidate_val_pr_aucs})")
model = best_model
model.save(os.path.join(OUTPUT_DIR, f'{RUN_TAG}_model.keras'))

# ---------------------------------------------------------------------------
# Threshold selection on validation, FP32 evaluation on the held-out test set
# ---------------------------------------------------------------------------

y_val_probs = model.predict([X_val, RR_val_n], batch_size=256, verbose=0).flatten()
precisions_val, recalls_val, thresholds_val = precision_recall_curve(y_val, y_val_probs)
f1_scores_val = 2 * (precisions_val * recalls_val) / (precisions_val + recalls_val + 1e-8)
f1_optimal_threshold = thresholds_val[np.argmax(f1_scores_val[:-1])]

specs, sens = [], []
for t in thresholds_val:
    preds = (y_val_probs > t).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_val, preds).ravel()
    specs.append(tn / (tn + fp) if (tn + fp) > 0 else 0)
    sens.append(tp / (tp + fn) if (tp + fn) > 0 else 0)
specs, sens = np.array(specs), np.array(sens)
youden_threshold = thresholds_val[np.argmax(sens + specs - 1)]

TARGET_SENSITIVITY = 0.90
valid_mask = sens >= TARGET_SENSITIVITY
if valid_mask.any():
    valid_specs = np.where(valid_mask, specs, -1)
    high_sens_threshold = thresholds_val[np.argmax(valid_specs)]
else:
    high_sens_threshold = thresholds_val[np.argmax(sens)]

PRECISION_FLOOR_TARGET = 0.90
valid_prec_idx = np.where(precisions_val[:-1] >= PRECISION_FLOOR_TARGET)[0]
if len(valid_prec_idx) > 0:
    precision_floor_90_threshold = thresholds_val[valid_prec_idx[0]]
else:
    precision_floor_90_threshold = thresholds_val[np.argmax(precisions_val[:-1])]

print(f"F1-optimal threshold (val): {f1_optimal_threshold:.4f}")
print(f"Youden's-J threshold (val): {youden_threshold:.4f}")
print(f"High-sensitivity threshold (val, target>=90%): {high_sens_threshold:.4f}")
print(f"Precision-floor threshold (val, target>=90% precision): {precision_floor_90_threshold:.4f}")


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


y_test_probs = model.predict([X_test, RR_test_n], batch_size=256, verbose=0).flatten()

fp32_test_results = {
    "f1_optimal": evaluate(y_test, y_test_probs, f1_optimal_threshold, "FP32 TEST — F1-optimal"),
    "youden": evaluate(y_test, y_test_probs, youden_threshold, "FP32 TEST — Youden-balanced"),
    "high_sensitivity": evaluate(y_test, y_test_probs, high_sens_threshold, "FP32 TEST — High-sensitivity (>=90% target)"),
    "precision_floor_90": evaluate(y_test, y_test_probs, precision_floor_90_threshold, "FP32 TEST — Precision-floor (>=90% val precision) [recommended deploy threshold]"),
}

y_test_pred = (y_test_probs > precision_floor_90_threshold).astype(int)
symbol_breakdown = {}
for sym in sorted(set(y_test_symbols[y_test == 1])):
    mask = (y_test_symbols == sym) & (y_test == 1)
    n = int(mask.sum())
    if n == 0:
        continue
    caught = int((y_test_pred[mask] == 1).sum())
    symbol_breakdown[sym] = {"n": n, "caught": caught, "sensitivity": caught / n}

print("Per-AAMI-symbol sensitivity (precision-floor threshold, FP32):")
for sym, d_ in symbol_breakdown.items():
    print(f"  {sym}: {d_['caught']}/{d_['n']} ({d_['sensitivity']:.4f})")

summary = {
    "run_tag": RUN_TAG,
    "candidate_val_pr_aucs": [float(v) for v in candidate_val_pr_aucs],
    "best_val_pr_auc": float(best_val_pr_auc),
    "thresholds": {"f1_optimal": float(f1_optimal_threshold), "youden": float(youden_threshold),
                    "high_sensitivity": float(high_sens_threshold),
                    "precision_floor_90": float(precision_floor_90_threshold)},
    "deploy_threshold_recommended": "precision_floor_90",
    "fp32_test_results": fp32_test_results,
    "fp32_symbol_breakdown": symbol_breakdown,
    "rr_feature_norm": {"mean": rr_mean.tolist(), "std": rr_std.tolist()},
}
with open(os.path.join(OUTPUT_DIR, f'{RUN_TAG}_train_summary.json'), 'w') as f:
    json.dump(summary, f, indent=2)

print(f"\nSaved {RUN_TAG}_model.keras and {RUN_TAG}_train_summary.json to {OUTPUT_DIR}")
print("Next: run combined_quantize_test.py for INT8 quantization and FP32-vs-INT8 testing (Section G).")
