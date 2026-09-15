# Model Validation Testing

This directory implements two steps of TIBOK's software process (matching
the process flowchart and `RIM-01_Pre-Oral_9.pdf`), each split into a
**training** stage and a separate **quantization & testing** stage so each
checkpoint is its own runnable artifact:

| Flowchart step | Plan section | Script |
|---|---|---|
| Model Architecture Training | Section C | `mitbih_train.py` / `combined_train.py` |
| Model Quantization & Testing | Section G | `mitbih_quantize_test.py` / `combined_quantize_test.py` |

- **Section C** — patient-level 70/15/15 train/val/test split, Adam optimizer,
  categorical cross-entropy-style focal loss, early stopping on validation
  loss. Produces the FP32 desktop model plus validation-selected thresholds
  and FP32 test-set metrics.
- **Section G** — post-training INT8 full-integer quantization of the
  Section C model, exported as a TFLite Micro C header, with FP32-vs-INT8
  comparison on the same held-out test set.
- **Section XI** — data sourced from PhysioNet, partitioned at the patient
  level to prevent leakage.
- **Section XII** — confusion-matrix-derived accuracy, sensitivity/specificity,
  F1, latency/resource metrics.
- **Scopes and Limitations** — "Model validation is conducted in-silico by
  benchmarking the quantized embedded network against a standard 32-bit
  floating-point (FP32) baseline using annotated recordings from the
  open-access MIT-BIH [and St. Petersburg INCART] Arrhythmia Database[s]."

## Two protocols, two different scopes

### MIT-BIH only — `mitbih_data.py`, `mitbih_train.py`, `mitbih_quantize_test.py`

Matches the plan: patient-level 70/15/15 split of MIT-BIH alone. **Run
these two for the plan's "Model Validation Testing" step.**

```bash
pip install -r model_validation/requirements.txt
python model_validation/mitbih_train.py          # Section C — writes tibok_mitbih_rr_cnn_model.keras
python model_validation/mitbih_quantize_test.py  # Section G — reads that model, writes .tflite + .h
```

### MIT-BIH + INCART — `combined_data.py`, `combined_train.py`, `combined_quantize_test.py`

The pooled protocol from the original Colab notebook
(`eto_na_tlga_guys_final_na.py`), kept as a clearly labeled extension. The
paper (`RIM-01_Pre-Oral_9.pdf` / the shared Google Doc) has since been
updated to describe this combined MIT-BIH+INCART protocol throughout
(Abstract, Objectives, Section C, Section XI, Scopes & Limitations, and the
RRL, citing Qi et al., 2023) — see git history / conversation for the
specific edits made.

```bash
python model_validation/combined_train.py          # Section C — writes tibok_combined_rr_cnn_model.keras
python model_validation/combined_quantize_test.py  # Section G — reads that model, writes .tflite + .h
```

## How the two stages hand off

`*_train.py` saves `<RUN_TAG>_model.keras` (the trained FP32 model) and
`<RUN_TAG>_train_summary.json` (validation-selected thresholds, RR-feature
normalization stats, FP32 test-set metrics, per-AAMI-symbol breakdown).
`*_quantize_test.py` requires both of those to already exist — it loads the
model, **re-derives** the validation/test arrays from scratch via
`load_all()` in the matching `*_data.py` module (deterministic given the
fixed seed=42 split, so this reproduces the exact same arrays without
needing to serialize them to disk), and cross-checks the recomputed RR
normalization against what's saved in `train_summary.json` before trusting
the quantized model — this guards against silent drift if the data pipeline
or PhysioNet mirror ever changes between the two runs.

## Setup

Both `*_data.py` modules download their source database(s) directly from
PhysioNet on first run (no Google Drive mount needed — that was a Colab-only
step in the original notebook) and cache them under `model_validation/data/`.
Override the cache location with `TIBOK_DATA_ROOT`, the output directory
with `TIBOK_OUTPUT_DIR`, the number of best-of-N training candidates with
`TIBOK_N_CANDIDATES` (default 3), and the max epochs per candidate with
`TIBOK_EPOCHS` (default 50). Training is CPU-feasible for MIT-BIH-only but
slow without a GPU; INCART pooling roughly doubles the dataset size.

## Known issue carried over from the source notebook

The source notebook's focal loss uses `alpha=0.3` — the coefficient on the
*positive* (arrhythmia) loss term. Since TIBOK is a screening device where a
missed arrhythmia is explicitly meant to cost more than a false alarm
(the whole reason for `class_weight_dict[1] *= 1.3` and for preferring the
Youden/high-sensitivity threshold over F1-optimal), `alpha` needs to exceed
0.5 to actually up-weight the minority positive class in the loss — 0.3 does
the opposite. `mitbih_train.py` fixes this (`alpha=0.7`); `combined_train.py`
keeps the original `alpha=0.3` to stay a faithful port of the uploaded
notebook. If you re-run the combined script, consider applying the same fix
there.
