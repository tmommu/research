# TIBOK — INT8 quantization & deployment verification

`quantization.py` takes the trained RR-fused 1D-CNN from
`eto_na_tlga_guys_final_na.py` and produces the artifact that actually ships on the
nRF52840, plus the evidence needed to defend it.

## Running it in Colab

Open **`TIBOK_Quantization_and_Testing.ipynb`** — that is the deliverable, and it is
self-contained. A `%%writefile` cell drops this module onto the runtime's disk before it
is imported, so there is no clone, no upload and no GitHub auth. That is deliberate: the
repo is private, so `git clone` from a Colab runtime prompts for credentials and fails,
and `files.upload()` would mean re-uploading the module every time the runtime recycles.

The notebook is **generated**, not hand-maintained:

```
python3 tools/build_notebook.py           # regenerate after editing the sources
python3 tools/build_notebook.py --check   # non-zero exit if the notebook is stale
```

Sources of truth are `eto_na_tlga_guys_final_na.py` (the Colab .py export) and
`tibok/quantization.py`. **Never hand-edit the module inside the .ipynb** — the next
rebuild overwrites it. Edit the repo file and re-run the builder.

```python
from tibok.quantization import quantize_and_test

report = quantize_and_test(
    model=model, X_val=X_val, RR_val_n=RR_val_n,
    X_test=X_test, RR_test_n=RR_test_n, y_test=y_test,
    thresholds={"precision_floor_90": 0.61, ...},
    window_size=1250, run_tag="tibok_combined_rr_cnn",
    test_symbols=y_test_symbols, rr_mean=rr_mean, rr_std=rr_std,
)
```

Outputs `<run_tag>_model_int8.tflite`, `<run_tag>_model_int8.h` and
`<run_tag>_quantization_report.json`.

## Database paths (`data_paths.py`)

`MITDB_PATH` / `INCART_PATH` must be **filesystem paths**, not Drive sharing links. Drive
is mounted at `/content/drive`, so a folder's path is always
`/content/drive/MyDrive/<folder>`. A `https://drive.google.com/drive/folders/...` URL is a
browser link, and `os.walk()` on one does not raise — it yields nothing, so the index comes
back empty and the run dies much later, far from the real mistake.

If a folder was *shared with you* rather than owned by you, it will not appear under
`MyDrive` until you add a shortcut: in Drive, right-click the folder → Organise → **Add
shortcut to Drive**.

- `resolve_db_path(configured, probe_records, label)` rejects URLs, and when the configured
  path is wrong it searches the mount for the probe records and reports where it found
  them. Records commonly land in a nested subfolder after a ZIP is extracted without
  flattening, under a name that doesn't match PhysioNet's.
- `resolve_db_source(...)` wraps that and adds a **PhysioNet fallback**: when the Drive
  folder is missing or incomplete it streams records over HTTPS via `wfdb`'s `pn_dir`
  instead. Pass `prefer="physionet"` to skip Drive entirely. Both databases are
  open-access and `wfdb` fetches one record at a time, so there is no bulk download.

  This matters for a *shared* folder. View-only access is enough to read files, and "Add
  shortcut to Drive" works at view-only — but if the owner ticked **"Viewers cannot
  download, print, or copy"**, the mount cannot read the bytes at all, and Drive enforces
  per-file download quotas on widely-shared files that a 75-record run can trip partway
  through. PhysioNet depends on none of that.
- `pick_lead(record, preferred)` selects the input channel **by name**. MIT-BIH is mostly
  ordered `[MLII, V5]`, but record 114 is `[V5, MLII]` — so the previous
  `p_signal[:, 0]` fed V5 into the model for that record while every other record
  contributed MLII. It raises rather than guessing when no preferred lead is present.
- `preflight(index, required, label, expected_total=)` verifies every required record is
  present *before* loading starts, and raises listing what is missing. The old code printed
  a warning and carried on. It also notes — without failing — when the folder holds an
  unexpected number of `.hea` files, which usually means a second database, a duplicate
  copy, or a nested extraction is sharing the folder.

## Replication trials (`trials.py`)

One training run supports "quantization cost F1 0.040 *in this run*" and nothing stronger.
`run_trials` repeats the whole train → quantize → evaluate experiment R times with
different seeds so the claim becomes "F1 0.040 ± sd across R runs", with CIs and a Wilcoxon
signed-rank test over the per-trial deltas.

**A trial is not a candidate.** `N_CANDIDATES` is a best-of-N *search* — it trains N models,
keeps the best on validation PR-AUC, discards the rest. Raising it yields one model picked
from a larger pool and makes the winner's validation PR-AUC *more* optimistically biased
(you report the maximum of N noisy draws from the set you selected on). It adds no evidence
about reproducibility. A trial is an independent replication and does. The two compose via
`candidates_per_trial`, at multiplied cost.

The patient split is fixed across trials by design, so what is measured is **training
variance** (init, augmentation, shuffling) — not variance across patient populations. Say
which one you report.

Deltas are paired within a trial, so the summary runs Wilcoxon over the R per-trial deltas.
Do not pool every beat from every trial into one McNemar table: beats repeat and models are
correlated, which inflates n and understates p.

Results checkpoint to `<run_tag>_trials.json` after each trial; `resume=True` continues
where a disconnected runtime stopped.

## The conversion failure, and what it actually was

The previous notebook cell carried this note:

> on one local TF 2.20 pip build (macOS/arm64), full-integer calibration of this exact
> two-input graph fails inside the TFLite calibrator once the model has *trained*
> weights (`input->dims->size != 4 (3 != 4)` — a freshly-initialized model of the
> identical architecture converts fine, so this is not an architecture problem).

Both halves of that are wrong, and the difference matters because the stated diagnosis
("environment-specific, weight-dependent") is what justified the silent fallback.

Reproduced on TF 2.21.0 / Keras 3.15.1 with a trained model of this exact architecture:

| model | calibration fed in | result |
|---|---|---|
| untrained | Keras order `[ecg, rr]` | **FAILS** `3 != 4` at CONV_2D node 1 |
| untrained | probed order `[rr, ecg]` | succeeds, 31.6 KB |
| trained   | Keras order `[ecg, rr]` | **FAILS** `3 != 4` at CONV_2D node 1 |
| trained   | probed order `[rr, ecg]` | succeeds, 34.4 KB |

So it is not weight-dependent — an untrained model fails identically. (The earlier
"converts fine" observation was most likely a conversion without
`representative_dataset` set, which skips calibration entirely and so never reaches the
crash.) And it is not really environment-specific either; it is deterministic given the
converter's ordering behaviour.

**Root cause.** `TFLiteConverter` does not preserve `model.inputs` ordering for a
multi-input model. Here Keras reports:

```
position 0: 'ecg_window'   (None, 1250, 1)
position 1: 'rr_features'  (None, 4)
```

while the converted graph reports:

```
position 0: 'serving_default_rr_features:0'  [1, 4]
position 1: 'serving_default_ecg_window:0'   [1, 1250, 1]
```

The old `representative_dataset` yielded `[X_val[i:i+1], RR_val_n[i:i+1]]`
positionally. The calibrator therefore pushed the 4-element RR vector into the Conv1D
branch. Conv1D lowers to CONV_2D with an implicit ExpandDims, so the kernel wants rank
4 and got rank 3 — `input->dims->size != 4 (3 != 4)`.

**Fix.** Run one throwaway float conversion, read the resulting input order, and feed
calibration samples in *that* order. Inputs are then identified by name (falling back to
rank/shape) rather than the old `shape[-1] != 4` guess. Two further strategies
(SavedModel with a pinned signature, explicit batch-1 concrete function) are tried if the
direct path still fails.

## No more silent dynamic-range fallback

The old cell caught the conversion failure and fell back to dynamic-range (weight-only)
INT8, describing it as something that "still shrinks the model ~4x and runs correctly on
the nRF52840's Cortex-M4 FPU."

It does not. TFLite-Micro ships no dynamic-range kernels for this graph's
Conv1D/FullyConnected ops, so a dynamic-range `.tflite` loads fine under the desktop
interpreter and then fails at `AllocateTensors()` on device. That fallback turns a
conversion bug into a firmware bug discovered much later. `quantize_int8` now raises by
default; `allow_dynamic_range_fallback=True` is available for desktop experiments only,
and the artifact is tagged `dynamic_range_NOT_DEPLOYABLE`.

## RAM estimate

The old cell summed every tensor in the model and called that RAM. That overstates the
requirement twice: it counts weight tensors, which TFLite-Micro reads directly from the
flash image and never copies into the arena, and it ignores lifetime reuse — an
activation is dead once its last consumer runs, and the arena planner reuses that space.

`estimate_tflm_arena` walks the operator schedule and reports the peak simultaneously
live activation set. On the synthetic verification fixture that is **~13.6 KB estimated**
against the old method's **~50.6 KB** — a ~3.7x overestimate. Both figures are estimates
from a fixture, not measurements, and neither is a result: the real planner adds
per-tensor bookkeeping, 16-byte alignment padding and kernel scratch buffers. Keep
headroom and confirm against what `AllocateTensors()` actually reports on hardware
before sizing `kTensorArenaSize` off either number.

## Paired FP32-vs-INT8 testing (RQ2.1 / RQ2.3)

Both models score the identical test beats, so the comparison is paired and the report
uses paired statistics:

- **McNemar's exact test** on the discordant pairs — the correct test for two classifiers
  on the same samples. Comparing two independent-sample CIs here would be needlessly
  conservative.
- **Bootstrap 95% CIs** on ΔF1, Δspecificity and Δsensitivity (2000 paired resamples).
- Label agreement rate and mean/max |Δprobability|.
- Per-AAMI-symbol sensitivity, FP32 vs INT8, so a regression concentrated in rare F or J
  beats is not hidden by the V-beat-dominated pooled figure.

Inference runs at **batch 1** by default, matching how the firmware invokes the model.

## INT8 threshold snapping

The sigmoid output is INT8, so probabilities land on ~256 discrete levels
(`output_scale` ≈ 1/256). Firmware comparing a dequantized float against a float
threshold does the same comparison as an integer cutoff, only slower and with rounding
risk. `int8_threshold_grid` reports the integer cutoff code and the *effective* float
threshold it corresponds to — quote that effective value in the write-up, and bake the
integer rule into firmware:

```
classify as ARRHYTHMIA when raw int8 output >= <int8_cutoff_code>
```

## Verification status

The module was exercised end-to-end on a trained fixture of this exact architecture
(synthetic ECG-like data, since MIT-BIH/INCART are not available in this environment):
full-integer conversion succeeded, the arena walk ran over the 18-op schedule, the paired
statistics ran, and the emitted C header compiles under `gcc -std=c11` with the TFL3
flatbuffer magic intact and `tibok_model_len` matching the `.tflite` byte count exactly.

The numbers in that run are from synthetic data and are **not** results — they only show
the pipeline works. Re-run it on the real trained model to get reportable figures.
