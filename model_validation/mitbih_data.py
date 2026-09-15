# -*- coding: utf-8 -*-
"""Shared MIT-BIH data pipeline for mitbih_train.py and mitbih_quantize_test.py.

Deterministic (fixed seed=42 throughout): re-running load_all() reproduces
the exact same train/val/test split, arrays, and RR-feature normalization
every time, so the quantization/testing stage can independently regenerate
the same validation and test sets the training stage used, without needing
to serialize the raw arrays to disk.
"""

import os
import numpy as np
import wfdb
from sklearn.utils.class_weight import compute_class_weight  # re-exported for convenience

WINDOW_SIZE = 1250
FS = 360

MITDB_RECORDS = [
    '100', '101', '103', '105', '106', '108', '109', '111', '112', '113',
    '114', '115', '116', '117', '118', '119', '121', '122', '123', '124',
    '200', '201', '202', '203', '205', '207', '208', '209', '210', '212',
    '213', '214', '215', '219', '220', '221', '222', '223', '228', '230',
    '231', '232', '233', '234'
]  # MIT-BIH, paced-beat records 102/104/107/217 excluded

LABEL_MAP = {
    'N': 0, 'L': 0, 'R': 0, 'e': 0, 'j': 0,
    'V': 1, 'A': 1, 'F': 1, 'S': 1, 'a': 1, 'J': 1,
}
BEAT_SYMBOLS = set(LABEL_MAP.keys()) | {'B', 'r', 'n', 'E', 'f', 'Q', '/'}

DATA_ROOT = os.environ.get(
    "TIBOK_DATA_ROOT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
)
MITDB_PATH = os.path.join(DATA_ROOT, "mitdb")


def get_splits():
    """Patient-level 70/15/15 split (Section C / Section XI). Fixed seed=42."""
    rng_split = np.random.RandomState(42)
    shuffled = list(MITDB_RECORDS)
    rng_split.shuffle(shuffled)
    n_total = len(shuffled)
    n_train = round(0.70 * n_total)
    n_val = round(0.15 * n_total)
    train_records = shuffled[:n_train]
    val_records = shuffled[n_train:n_train + n_val]
    test_records = shuffled[n_train + n_val:]
    assert not any(r in train_records for r in val_records)
    assert not any(r in train_records for r in test_records)
    assert not any(r in val_records for r in test_records)
    return train_records, val_records, test_records


def _ensure_database(pn_dir, local_path):
    if os.path.isdir(local_path) and any(f.endswith('.hea') for f in os.listdir(local_path)):
        return
    os.makedirs(local_path, exist_ok=True)
    print(f"Downloading PhysioNet database '{pn_dir}' into {local_path} ...")
    wfdb.dl_database(pn_dir, dl_dir=local_path)


def _index_records(base_path):
    index = {}
    for root, dirs, files in os.walk(base_path):
        for f in files:
            if f.endswith('.hea'):
                index[f[:-4]] = os.path.join(root, f[:-4])
    return index


def load_and_segment(record_id, window_size, mitdb_index):
    if record_id not in mitdb_index:
        raise FileNotFoundError(f"{record_id}.hea not found anywhere under {MITDB_PATH}")
    path = mitdb_index[record_id]
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


def build_dataset(record_list, mitdb_index):
    all_segments, all_labels, all_symbols, all_rr = [], [], [], []
    for rid in record_list:
        segs, labs, syms, rrf = load_and_segment(rid, WINDOW_SIZE, mitdb_index)
        all_segments.extend(segs); all_labels.extend(labs)
        all_symbols.extend(syms); all_rr.extend(rrf)
        print(f"  mitdb/{rid}: {len(segs)} beats loaded")
    return all_segments, all_labels, all_symbols, all_rr


def normalize_batch(segments):
    arr = np.stack(segments).astype(np.float32)
    mean = arr.mean(axis=1, keepdims=True)
    std = arr.std(axis=1, keepdims=True) + 1e-8
    return (arr - mean) / std


def load_all():
    """Downloads (if needed), loads, and preprocesses MIT-BIH into arrays.

    Returns a dict with X_train/y_train/RR_train_n, X_val/y_val/RR_val_n,
    X_test/y_test/RR_test_n/y_test_symbols, and rr_mean/rr_std (computed on
    the training split only). Deterministic given the fixed seed=42 split.
    """
    _ensure_database('mitdb', MITDB_PATH)
    mitdb_index = _index_records(MITDB_PATH)
    print(f"MIT-BIH: found {len(mitdb_index)} records under {MITDB_PATH}  (expect {len(MITDB_RECORDS)})")
    missing = [r for r in MITDB_RECORDS if r not in mitdb_index]
    if missing:
        print(f"WARNING: {len(missing)} MIT-BIH records not found anywhere under {MITDB_PATH}: {missing}")

    train_records, val_records, test_records = get_splits()
    print(f"Total patient-records: {len(MITDB_RECORDS)} (MIT-BIH)")
    print(f"Train ({len(train_records)}): {train_records}")
    print(f"Val   ({len(val_records)}): {val_records}")
    print(f"Test  ({len(test_records)}): {test_records}")

    print("Loading training records...")
    train_segments, train_labels, train_symbols, train_rr = build_dataset(train_records, mitdb_index)
    print("\nLoading validation records...")
    val_segments, val_labels, val_symbols, val_rr = build_dataset(val_records, mitdb_index)
    print("\nLoading held-out test records...")
    test_segments, test_labels, test_symbols, test_rr = build_dataset(test_records, mitdb_index)
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

    rr_mean = RR_train.mean(axis=0)
    rr_std = RR_train.std(axis=0) + 1e-8

    return dict(
        X_train=X_train, y_train=y_train, RR_train_n=(RR_train - rr_mean) / rr_std,
        X_val=X_val, y_val=y_val, RR_val_n=(RR_val - rr_mean) / rr_std,
        X_test=X_test, y_test=y_test, RR_test_n=(RR_test - rr_mean) / rr_std,
        y_test_symbols=y_test_symbols, rr_mean=rr_mean, rr_std=rr_std,
    )


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
