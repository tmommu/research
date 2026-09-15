# Model Validation Testing

This directory implements the "Model Validation Testing" step of TIBOK's
methodology, from `RIM-01_Pre-Oral_9.pdf`:

- **Section C** ("Software: Model Architecture Training") — patient-level
  70/15/15 train/val/test split, Adam optimizer, early stopping on
  validation loss.
- **Section G** ("Software: Model Quantization & Testing") — post-training
  INT8 full-integer quantization of the trained FP32 network.
- **Section XI** ("Data Collection") — data sourced from PhysioNet,
  partitioned at the patient level to prevent leakage.
- **Section XII** ("Data Analysis") — confusion-matrix-derived accuracy,
  sensitivity/specificity, F1, latency/resource metrics.
- **Scopes and Limitations** — "Model validation is conducted in-silico by
  benchmarking the quantized embedded network against a standard 32-bit
  floating-point (FP32) baseline using annotated recordings from the
  open-access MIT-BIH Arrhythmia Database."

## Two scripts, two different scopes

### `mitbih_only_validation.py` — matches the plan

Trains and validates on **MIT-BIH only**, with a patient-level 70/15/15
split, exactly as Sections C/XI/XII and Scopes & Limitations describe. **This
is the script to run and cite for the plan's "Model Validation Testing"
step.**

### `combined_mitbih_incart_validation.py` — extension, not in the plan

The original notebook this repo's pipeline was built from
(`eto_na_tlga_guys_final_na.py`, a Google Colab export) pools MIT-BIH with
the St. Petersburg INCART Arrhythmia Database, on the reasoning that
MIT-BIH-only training leaves the network under-exposed to cross-hospital
morphology variation (Qi et al., 2023).

**This protocol is not described anywhere in `RIM-01_Pre-Oral_9.pdf`** —
Section C, Section XI, Section XII, and Scopes & Limitations all name
MIT-BIH exclusively; INCART / St. Petersburg is not mentioned once. The
script is kept here, clearly labeled, in case the combined-database result
is something you want to present *in addition to* the plan's baseline — but
if so, the pre-oral document needs a corresponding update (citing INCART,
its 257 Hz native rate and lead-II resampling, and the resulting
patient-record split) before the defense, since a panelist reading the
current document has no way to know this database was used.

## Setup

```bash
pip install -r model_validation/requirements.txt
python model_validation/mitbih_only_validation.py
```

Both scripts download their source database(s) directly from PhysioNet on
first run (no Google Drive mount needed — that was a Colab-only step in the
original notebook) and cache them under `model_validation/data/`. Override
the cache location with `TIBOK_DATA_ROOT`, the number of best-of-N training
candidates with `TIBOK_N_CANDIDATES` (default 3), and the max epochs per
candidate with `TIBOK_EPOCHS` (default 50). Training is CPU-feasible for
MIT-BIH-only but slow without a GPU; INCART pooling roughly doubles the
dataset size.

Each run writes `<RUN_TAG>_model.keras`, `<RUN_TAG>_model.tflite`,
`<RUN_TAG>_model.h` (TFLite Micro C header), and `<RUN_TAG>_summary.json`
(all four threshold operating points, FP32-vs-INT8 test metrics, and the
per-AAMI-symbol sensitivity breakdown) into `model_validation/` by default.

## Known issue carried over from the source notebook

The source notebook's focal loss uses `alpha=0.3` — the coefficient on the
*positive* (arrhythmia) loss term. Since TIBOK is a screening device where a
missed arrhythmia is explicitly meant to cost more than a false alarm
(the whole reason for `class_weight_dict[1] *= 1.3` and for preferring the
Youden/high-sensitivity threshold over F1-optimal), `alpha` needs to exceed
0.5 to actually up-weight the minority positive class in the loss — 0.3 does
the opposite. `mitbih_only_validation.py` fixes this (`alpha=0.7`);
`combined_mitbih_incart_validation.py` keeps the original `alpha=0.3` to stay
a faithful port of the uploaded notebook. If you re-run the combined script,
consider applying the same fix there.
