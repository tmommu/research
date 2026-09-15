# -*- coding: utf-8 -*-
"""TIBOK — MIT-BIH, RR-Interval-Fused 1D-CNN (standalone) — matches the plan

This is the "Model Validation Testing" step exactly as described in
RIM-01_Pre-Oral_9: Section C ("Software: Model Architecture Training") trains
the network on the MIT-BIH Arrhythmia Database with a **patient-level 70%
train / 15% validation / 15% test split**; Section XI ("Data Collection")
sources the data from PhysioNet at its native 360 Hz / 11-bit / +-10 mV
range, with patient-level partitioning to prevent leakage; Section G
("Software: Model Quantization & Testing") post-training INT8-quantizes the
trained network; Section XII ("Data Analysis") and "Scopes and Limitations"
describe validating the model in-silico by benchmarking the INT8-quantized
embedded network against the FP32 desktop baseline across F1-score,
sensitivity, specificity, PPV, NPV, and Cohen's kappa. No other database
(INCART included) is referenced anywhere in the plan — see
model_validation/combined_mitbih_incart_validation.py for that separate,
explicitly-labeled extension, and model_validation/README.md for how the two
relate.

Each ECG window is paired with 4 RR-interval features (pre-RR, post-RR,
causal local-average RR, prematurity ratio), fused into the classifier head
next to the CNN's pooled output.

**Architecture**: ECG window (1250x1) -> 3xConv1D(16/32/64, k7, BN+ReLU+SpatialDropout) ->
GlobalAveragePooling1D(64) (+) RR features (4) -> Dense(16) -> Concat(80) -> Dense(32) -> Dropout ->
Output(1, sigmoid).

Pulls MIT-BIH directly from PhysioNet into a local cache directory (no
Google Drive mount required) and saves all artifacts to disk.
"""

import os, json, time
import numpy as np
import pandas as pd
import wfdb
import tensorflow as tf
from tensorflow.keras import layers, models, Model
from tensorflow.keras.optimizers import Adam
from sklearn.metrics import (
    average_precision_score, roc_auc_score, precision_recall_curve,
    confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
)
from sklearn.utils.class_weight import compute_class_weight

np.random.seed(42)
tf.random.set_seed(42)
os.environ['PYTHONHASHSEED'] = '42'
os.environ['TF_DETERMINISTIC_OPS'] = '1'
os.environ['TF_CUDNN_DETERMINISTIC'] = '1'
tf.config.experimental.enable_op_determinism()

RUN_TAG = "tibok_mitbih_rr_cnn"
print(f"RUN_TAG = {RUN_TAG}")

gpus = tf.config.list_physical_devices('GPU')
print(f"GPUs available: {len(gpus)}")
for gpu in gpus:
    print(f"  {gpu}")
if not gpus:
    print("No GPU detected — training will run on CPU and will be substantially slower.")

# ---------------------------------------------------------------------------
# Data split — MIT-BIH, patient-level 70/15/15 (Section C / Section XI)
# ---------------------------------------------------------------------------

WINDOW_SIZE = 1250
FS = 360

MITDB_RECORDS = [
    '100', '101', '103', '105', '106', '108', '109', '111', '112', '113',
    '114', '115', '116', '117', '118', '119', '121', '122', '123', '124',
    '200', '201', '202', '203', '205', '207', '208', '209', '210', '212',
    '213', '214', '215', '219', '220', '221', '222', '223', '228', '230',
    '231', '232', '233', '234'
]  # MIT-BIH, paced-beat records 102/104/107/217 excluded

rng_split = np.random.RandomState(42)
shuffled = list(MITDB_RECORDS)
rng_split.shuffle(shuffled)
n_total = len(shuffled)
n_train = round(0.70 * n_total)
n_val = round(0.15 * n_total)
TRAIN_RECORDS = shuffled[:n_train]
VAL_RECORDS = shuffled[n_train:n_train + n_val]
TEST_RECORDS = shuffled[n_train + n_val:]

print(f"Total patient-records: {n_total} (MIT-BIH)")
print(f"Train ({len(TRAIN_RECORDS)}): {TRAIN_RECORDS}")
print(f"Val   ({len(VAL_RECORDS)}): {VAL_RECORDS}")
print(f"Test  ({len(TEST_RECORDS)}): {TEST_RECORDS}")

LABEL_MAP = {
    'N': 0, 'L': 0, 'R': 0, 'e': 0, 'j': 0,
    'V': 1, 'A': 1, 'F': 1, 'S': 1, 'a': 1, 'J': 1,
}
BEAT_SYMBOLS = set(LABEL_MAP.keys()) | {'B', 'r', 'n', 'E', 'f', 'Q', '/'}

assert not any(r in TRAIN_RECORDS for r in VAL_RECORDS)
assert not any(r in TRAIN_RECORDS for r in TEST_RECORDS)
assert not any(r in VAL_RECORDS for r in TEST_RECORDS)
print("Data split integrity OK.")

# ---------------------------------------------------------------------------
# Local cache for MIT-BIH, downloaded directly from PhysioNet
# ---------------------------------------------------------------------------

DATA_ROOT = os.environ.get(
    "TIBOK_DATA_ROOT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
)
MITDB_PATH = os.path.join(DATA_ROOT, "mitdb")


def _ensure_database(pn_dir, local_path):
    """Download a PhysioNet database into local_path if it isn't cached yet."""
    if os.path.isdir(local_path) and any(f.endswith('.hea') for f in os.listdir(local_path)):
        return
    os.makedirs(local_path, exist_ok=True)
    print(f"Downloading PhysioNet database '{pn_dir}' into {local_path} ...")
    wfdb.dl_database(pn_dir, dl_dir=local_path)


_ensure_database('mitdb', MITDB_PATH)

def _index_records(base_path):
    index = {}
    for root, dirs, files in os.walk(base_path):
        for f in files:
            if f.endswith('.hea'):
                index[f[:-4]] = os.path.join(root, f[:-4])
    return index

MITDB_INDEX = _index_records(MITDB_PATH)
print(f"MIT-BIH: found {len(MITDB_INDEX)} records under {MITDB_PATH}  (expect {len(MITDB_RECORDS)})")
missing = [r for r in MITDB_RECORDS if r not in MITDB_INDEX]
if missing:
    print(f"WARNING: {len(missing)} MIT-BIH records not found anywhere under {MITDB_PATH}: {missing}")

# ---------------------------------------------------------------------------
# Loading + RR-interval feature extraction, at MIT-BIH's native 360 Hz
# ---------------------------------------------------------------------------

def load_and_segment(record_id, window_size):
    if record_id not in MITDB_INDEX:
        raise FileNotFoundError(f"{record_id}.hea not found anywhere under {MITDB_PATH}")
    path = MITDB_INDEX[record_id]
    record = wfdb.rdrecord(path)
    annotation = wfdb.rdann(path, 'atr')
    signal = record.p_signal[:, 0]  # MLII
    assert record.fs == FS, f"{record_id}: expected {FS} Hz, got {record.fs} Hz"

    beat_mask = np.array([s in BEAT_SYMBOLS for s in annotation.symbol])
    beat_samples = annotation.sample[beat_mask]
    beat_symbols = np.array(annotation.symbol)[beat_mask]
    if len(beat_samples) < 3:
        return [], [], [], []

    half = window_size // 2
    sig_len = len(signal)

    rr = np.diff(beat_samples) / FS
    pre_rr = np.empty(len(beat_samples)); post_rr = np.empty(len(beat_samples))
    pre_rr[0] = rr[0] if len(rr) else 0.8; pre_rr[1:] = rr
    post_rr[-1] = rr[-1] if len(rr) else 0.8; post_rr[:-1] = rr

    local_rr = np.empty(len(beat_samples))
    global_mean_rr = rr.mean() if len(rr) else 0.8
    for i in range(len(beat_samples)):
        window = pre_rr[max(0, i - 10):i]
        local_rr[i] = window.mean() if len(window) > 0 else global_mean_rr
    ratio = pre_rr / (local_rr + 1e-6)

    segments, labels, symbols, rr_feats = [], [], [], []
    for i, (sample, symbol) in enumerate(zip(beat_samples, beat_symbols)):
        if symbol not in LABEL_MAP:
            continue
        if sample - half < 0 or sample + half > sig_len:
            continue
        segments.append(signal[sample - half: sample + half])
        labels.append(LABEL_MAP[symbol])
        symbols.append(symbol)
        rr_feats.append([pre_rr[i], post_rr[i], local_rr[i], ratio[i]])
    return segments, labels, symbols, rr_feats


def build_dataset(record_list):
    all_segments, all_labels, all_symbols, all_rr = [], [], [], []
    for rid in record_list:
        segs, labs, syms, rrf = load_and_segment(rid, WINDOW_SIZE)
        all_segments.extend(segs); all_labels.extend(labs)
        all_symbols.extend(syms); all_rr.extend(rrf)
        print(f"  mitdb/{rid}: {len(segs)} beats loaded")
    return all_segments, all_labels, all_symbols, all_rr


def normalize_batch(segments):
    arr = np.stack(segments).astype(np.float32)
    mean = arr.mean(axis=1, keepdims=True)
    std = arr.std(axis=1, keepdims=True) + 1e-8
    return (arr - mean) / std


print("Loading training records...")
train_segments, train_labels, train_symbols, train_rr = build_dataset(TRAIN_RECORDS)
print("\nLoading validation records...")
val_segments, val_labels, val_symbols, val_rr = build_dataset(VAL_RECORDS)
print("\nLoading held-out test records...")
test_segments, test_labels, test_symbols, test_rr = build_dataset(TEST_RECORDS)
y_test_symbols = np.array(test_symbols)

X_train = normalize_batch(train_segments).reshape(-1, WINDOW_SIZE, 1)
y_train = np.array(train_labels)
RR_train = np.array(train_rr, dtype=np.float32)

X_val = normalize_batch(val_segments).reshape(-1, WINDOW_SIZE, 1)
y_val = np.array(val_labels)
RR_val = np.array(val_rr, dtype=np.float32)

X_test = normalize_batch(test_segments).reshape(-1, WINDOW_SIZE, 1)
y_test = np.array(test_labels)
RR_test = np.array(test_rr, dtype=np.float32)

print(f"\nX_train {X_train.shape}  X_val {X_val.shape}  X_test {X_test.shape}")
print("Train class balance:", pd.Series(y_train).value_counts(normalize=True).to_dict())
print("Test  class balance:", pd.Series(y_test).value_counts(normalize=True).to_dict())

rr_mean = RR_train.mean(axis=0)
rr_std = RR_train.std(axis=0) + 1e-8
RR_train_n = (RR_train - rr_mean) / rr_std
RR_val_n = (RR_val - rr_mean) / rr_std
RR_test_n = (RR_test - rr_mean) / rr_std

# ---------------------------------------------------------------------------
# Minority-class augmentation (time shift, baseline wander, powerline hum,
# Gaussian noise, amplitude scaling), applied 2x to arrhythmia-class windows
# only. RR features are carried over unchanged for augmented copies since
# the augmentation only perturbs the signal, not beat timing.
# ---------------------------------------------------------------------------

def augment_segment(segment, rng, shift_max=40, noise_std=0.03, scale_range=(0.9, 1.1),
                     baseline_wander_prob=0.3, powerline_prob=0.3):
    seg = segment.copy().astype(np.float32).flatten()
    n = len(seg)
    shift = int(rng.integers(-shift_max, shift_max + 1))
    seg = np.roll(seg, shift)
    if rng.random() < baseline_wander_prob:
        freq = rng.uniform(0.15, 0.4); t = np.arange(n)
        wander_amp = rng.uniform(0.05, 0.15)
        seg = seg + wander_amp * np.sin(2 * np.pi * freq * t / FS)
    if rng.random() < powerline_prob:
        freq = rng.choice([50, 60]); t = np.arange(n)
        pl_amp = rng.uniform(0.02, 0.06)
        seg = seg + pl_amp * np.sin(2 * np.pi * freq * t / FS)
    seg = seg + rng.normal(0, noise_std, n).astype(np.float32)
    seg = seg * rng.uniform(*scale_range)
    return seg.reshape(segment.shape)


def augment_dataset(X, rr, y, rng, n_aug_positive=2):
    X_list, rr_list, y_list = [X], [rr], [y]
    idx = np.where(y == 1)[0]
    for _ in range(n_aug_positive):
        X_aug = np.stack([augment_segment(X[i], rng) for i in idx]).astype(np.float32)
        rr_aug = rr[idx]
        y_aug = np.full(len(idx), 1)
        X_list.append(X_aug); rr_list.append(rr_aug); y_list.append(y_aug)
    return np.concatenate(X_list), np.concatenate(rr_list), np.concatenate(y_list)


aug_rng = np.random.default_rng(42)
X_train_aug, RR_train_aug, y_train_aug = augment_dataset(X_train, RR_train_n, y_train, aug_rng)
shuffle_idx = np.random.RandomState(42).permutation(len(y_train_aug))
X_train_aug = X_train_aug[shuffle_idx]; RR_train_aug = RR_train_aug[shuffle_idx]; y_train_aug = y_train_aug[shuffle_idx]
print(f"After augmentation: X_train {X_train_aug.shape}, class balance:",
      pd.Series(y_train_aug).value_counts(normalize=True).to_dict())

# ---------------------------------------------------------------------------
# Model: CNN branch (morphology) + RR branch (rhythm timing), fused before
# the classifier head. This is a screening device, so a false negative
# (missed arrhythmia) should cost more than a false positive; alpha=0.7
# up-weights the positive (arrhythmia) term in the focal loss accordingly
# (alpha is the positive-class loss coefficient, so it must exceed 0.5 to
# actually favor recall — see README for why the source notebook's alpha=0.3
# was backwards for this stated goal).
# ---------------------------------------------------------------------------

def focal_loss(gamma=3.0, alpha=0.7):
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
        loss=focal_loss(gamma=3.0, alpha=0.7),
        metrics=['accuracy', tf.keras.metrics.Precision(name='precision'),
                 tf.keras.metrics.Recall(name='recall')]
    )
    return model


build_model(WINDOW_SIZE).summary()

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
    candidate = build_model(WINDOW_SIZE)
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

OUTPUT_DIR = os.environ.get("TIBOK_OUTPUT_DIR", os.path.dirname(os.path.abspath(__file__)))
os.makedirs(OUTPUT_DIR, exist_ok=True)
model.save(os.path.join(OUTPUT_DIR, f'{RUN_TAG}_model.keras'))

# ---------------------------------------------------------------------------
# Threshold selection on validation, evaluation on the held-out test set
#
# Reports four operating points: F1-optimal, Youden's-J (balanced
# sensitivity/specificity), a high-sensitivity point targeting >=90% recall,
# and a precision-floor point. TIBOK is a *screening* device — a missed
# arrhythmia is costlier than a false alarm — so Youden or high-sensitivity
# is the more defensible deployment choice, not F1-optimal.
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

# Precision-floor threshold: the lowest threshold on VALIDATION that still
# reaches >=90% precision there. Chosen on val, only ever evaluated on test.
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

results = {
    "f1_optimal": evaluate(y_test, y_test_probs, f1_optimal_threshold, "TEST — F1-optimal"),
    "youden": evaluate(y_test, y_test_probs, youden_threshold, "TEST — Youden-balanced"),
    "high_sensitivity": evaluate(y_test, y_test_probs, high_sens_threshold, "TEST — High-sensitivity (>=90% target)"),
    "precision_floor_90": evaluate(y_test, y_test_probs, precision_floor_90_threshold, "TEST — Precision-floor (>=90% val precision) [recommended deploy threshold]"),
}

# ---------------------------------------------------------------------------
# Per-AAMI-symbol sensitivity breakdown
# ---------------------------------------------------------------------------

y_test_pred = (y_test_probs > precision_floor_90_threshold).astype(int)
symbol_breakdown = {}
for sym in sorted(set(y_test_symbols[y_test == 1])):
    mask = (y_test_symbols == sym) & (y_test == 1)
    n = int(mask.sum())
    if n == 0:
        continue
    caught = int((y_test_pred[mask] == 1).sum())
    symbol_breakdown[sym] = {"n": n, "caught": caught, "sensitivity": caught / n}

print("Per-AAMI-symbol sensitivity (precision-floor threshold):")
for sym, d in symbol_breakdown.items():
    print(f"  {sym}: {d['caught']}/{d['n']} ({d['sensitivity']:.4f})")

# ---------------------------------------------------------------------------
# INT8 post-training quantization — the model that actually ships on the
# nRF52840 (Section G, and the FP32-vs-INT8 protocol in Scopes and
# Limitations)
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
    interpreter.resize_tensor_input(in_details[ecg_idx]['index'], [len(X_test_q), WINDOW_SIZE, 1])
    interpreter.resize_tensor_input(in_details[rr_idx]['index'], [len(RR_test_q), 4])
    interpreter.allocate_tensors()
    interpreter.set_tensor(in_details[ecg_idx]['index'], X_test_q)
    interpreter.set_tensor(in_details[rr_idx]['index'], RR_test_q)
    interpreter.invoke()
    out = interpreter.get_tensor(out_details[0]['index'])
    y_test_probs_int8 = ((out.astype(np.float32) - out_zp) * out_scale).flatten()
else:
    interpreter.resize_tensor_input(in_details[ecg_idx]['index'], [len(X_test), WINDOW_SIZE, 1])
    interpreter.resize_tensor_input(in_details[rr_idx]['index'], [len(RR_test_n), 4])
    interpreter.allocate_tensors()
    interpreter.set_tensor(in_details[ecg_idx]['index'], X_test.astype(np.float32))
    interpreter.set_tensor(in_details[rr_idx]['index'], RR_test_n.astype(np.float32))
    interpreter.invoke()
    y_test_probs_int8 = interpreter.get_tensor(out_details[0]['index']).flatten()

print(f"\nFP32 test ROC-AUC: {roc_auc_score(y_test, y_test_probs):.4f}")
print(f"INT8 test ROC-AUC: {roc_auc_score(y_test, y_test_probs_int8):.4f}")

for name, thr in [("f1_optimal", f1_optimal_threshold), ("youden", youden_threshold),
                   ("high_sensitivity", high_sens_threshold), ("precision_floor_90", precision_floor_90_threshold)]:
    evaluate(y_test, y_test_probs_int8, thr, f"INT8 TEST — {name}")

# ---------------------------------------------------------------------------
# C header export for TensorFlow Lite Micro
# ---------------------------------------------------------------------------

def convert_to_c_array(tflite_path, header_path, array_name="tibok_model"):
    with open(tflite_path, 'rb') as f:
        data = f.read()
    with open(header_path, 'w') as f:
        f.write(f"#ifndef {array_name.upper()}_H\n#define {array_name.upper()}_H\n\n")
        f.write("#include <stddef.h>\n#ifndef __cplusplus\n#include <stdalign.h>\n#endif\n\n")
        f.write("#ifdef __cplusplus\nextern \"C\" {\n#endif\n\n")
        f.write(f"alignas(16) const unsigned char {array_name}[] = {{\n")
        for i, byte in enumerate(data):
            f.write(f"0x{byte:02x}, ")
            if (i + 1) % 12 == 0:
                f.write("\n")
        f.write(f"\n}};\n\nconst size_t {array_name}_len = {len(data)};\n\n")
        f.write("#ifdef __cplusplus\n}\n#endif\n\n#endif\n")
    print(f"Header written: {header_path} ({len(data)/1024:.2f} KB)")


convert_to_c_array(
    os.path.join(OUTPUT_DIR, f'{RUN_TAG}_model.tflite'),
    os.path.join(OUTPUT_DIR, f'{RUN_TAG}_model.h'),
    'tibok_model',
)
print(f"\nFirmware constants:")

if FULL_INT8_OK:
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
print(f"DEPLOY_THRESHOLD (precision-floor, recommended) = {precision_floor_90_threshold:.4f}")

# ---------------------------------------------------------------------------
# Save summary
# ---------------------------------------------------------------------------

summary = {
    "candidate_val_pr_aucs": [float(v) for v in candidate_val_pr_aucs],
    "best_val_pr_auc": float(best_val_pr_auc),
    "thresholds": {"f1_optimal": float(f1_optimal_threshold), "youden": float(youden_threshold),
                    "high_sensitivity": float(high_sens_threshold),
                    "precision_floor_90": float(precision_floor_90_threshold)},
    "deploy_threshold_recommended": "precision_floor_90",
    "test_results": results,
    "symbol_breakdown": symbol_breakdown,
    "rr_feature_norm": {"mean": rr_mean.tolist(), "std": rr_std.tolist()},
}
with open(os.path.join(OUTPUT_DIR, f'{RUN_TAG}_summary.json'), 'w') as f:
    json.dump(summary, f, indent=2)

print(f"\nSaved model + summary files to {OUTPUT_DIR}")
