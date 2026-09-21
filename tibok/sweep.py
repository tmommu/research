"""Sweep the loss/class-weight knobs that trade precision against sensitivity.

The study's two settings currently pull in opposite directions: `focal_loss(alpha=0.3)`
down-weights positives (0.3 against 0.7 for negatives) while `class_weight[1] *= 1.3`
pushes them back up, on top of an already-balanced weighting. The net is a mild recall
bias, arrived at by accident rather than by choice. Since the model is over on sensitivity
and under on precision, that bias is being paid for in exactly the wrong currency -- this
sweep measures the trade instead of guessing at it.

Selection hygiene
-----------------

A sweep that picks its winner on the test set makes the reported test metrics meaningless:
you would be choosing the configuration that happens to suit those particular patients, and
the number you quote would no longer estimate held-out performance. So nothing here touches
test data. The flow is:

  1. Split VALIDATION in two. `val_thr` chooses the operating point; `val_sel` scores the
     configuration. Without that split the comparison is circular -- you would pick a
     threshold on the same beats you then use to judge the threshold, which flatters every
     configuration and flatters the overfitted ones most.
  2. Rank configurations on `val_sel`.
  3. Take the winner to test EXACTLY ONCE, via `finalize_on_test`.

Step 3 is the only time test data is read, and it is a report, not a decision. If you find
yourself re-running the sweep after seeing test numbers, the test set has become a second
validation set and the honest move is to say so in the write-up.

Cost
----

One training run per (config, seed). A 6-config grid at one seed is roughly six training
runs. Seed noise in this study is large (0.8865 vs 0.7418 val PR-AUC across seeds), so a
one-seed sweep ranks configurations noisily; `n_seeds=2` or 3 averages that down at
proportional cost. Results checkpoint after every run and `resume=True` continues an
interrupted session.
"""

from __future__ import annotations

import json
import os
import time

import numpy as np

from .quantization import evaluate_at_threshold
from .thresholds import select_thresholds

__all__ = ["make_grid", "run_sweep", "summarize_sweep", "print_sweep", "finalize_on_test"]

DEFAULT_TARGETS = {"f1_score": 0.90, "precision": 0.90, "sensitivity": 0.95, "specificity": 0.95}


def make_grid(pos_boosts=(1.0, 1.3), alphas=(0.15, 0.30, 0.45), gammas=(3.0,)):
    """Grid over the knobs that actually move the precision/recall balance.

    `alpha` weights the positive term of the focal loss: lower favours precision, higher
    favours recall. `pos_boost` is the manual multiplier applied on top of balanced class
    weights -- 1.0 removes it entirely, which is the cleanest precision lever available.
    """
    return [{"pos_boost": p, "alpha": a, "gamma": g}
            for p in pos_boosts for a in alphas for g in gammas]


def _key(cfg, seed):
    return f"pb{cfg['pos_boost']}_a{cfg['alpha']}_g{cfg['gamma']}_s{seed}"


def run_sweep(train_one, configs, X_val, RR_val, y_val, window_size,
              n_seeds=1, base_seed=9000, val_split=0.5, out_dir=".", run_tag="tibok",
              resume=True, threshold_name="precision_floor_90", rng_seed=42):
    """Train one model per (config, seed) and score it on held-out validation.

    `train_one(config, seed)` must build, compile and fit a model, then return it. It is
    passed in rather than imported so this module never needs the notebook's architecture.
    """
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{run_tag}_sweep.json")

    rows = []
    if resume and os.path.exists(path):
        rows = json.load(open(path))["rows"]
        print(f"Resuming: {len(rows)} run(s) already recorded in {path}")
    done = {r["key"] for r in rows}

    y_val = np.asarray(y_val)
    rng = np.random.default_rng(rng_seed)
    idx = rng.permutation(len(y_val))
    cut = int(len(idx) * val_split)
    i_thr, i_sel = idx[:cut], idx[cut:]
    print(f"Validation split: {len(i_thr)} beats to choose the threshold, "
          f"{len(i_sel)} to score the configuration")

    total = len(configs) * n_seeds
    n = 0
    for cfg in configs:
        for s in range(n_seeds):
            seed = base_seed + s
            k = _key(cfg, seed)
            n += 1
            if k in done:
                continue
            t0 = time.time()
            print(f"\n[{n}/{total}] {k}  pos_boost={cfg['pos_boost']} "
                  f"alpha={cfg['alpha']} gamma={cfg['gamma']}")

            model = train_one(cfg, seed)
            probs = model.predict([X_val, RR_val], batch_size=256, verbose=0).flatten()

            thr = select_thresholds(y_val[i_thr], probs[i_thr])[threshold_name]
            m = evaluate_at_threshold(y_val[i_sel], probs[i_sel], thr, verbose=False)

            row = {"key": k, "seed": seed, **cfg, "threshold": float(thr),
                   "wall_s": round(time.time() - t0, 1)}
            row.update({f"val_{x}": m[x] for x in
                        ("f1_score", "precision", "sensitivity", "specificity",
                         "accuracy", "roc_auc", "pr_auc")})
            rows.append(row)
            json.dump({"run_tag": run_tag, "rows": rows}, open(path, "w"), indent=2)
            print(f"      val F1 {m['f1_score']:.4f} | prec {m['precision']:.4f} | "
                  f"sens {m['sensitivity']:.4f} | spec {m['specificity']:.4f}  "
                  f"({row['wall_s']:.0f}s)")

    print(f"\nSweep recorded in {path}")
    return rows


def summarize_sweep(rows, targets=None):
    """Average over seeds per config and mark which targets each configuration meets."""
    targets = targets or DEFAULT_TARGETS
    groups = {}
    for r in rows:
        k = (r["pos_boost"], r["alpha"], r["gamma"])
        groups.setdefault(k, []).append(r)

    out = []
    for (pb, a, g), rs in groups.items():
        e = {"pos_boost": pb, "alpha": a, "gamma": g, "n_seeds": len(rs)}
        for metric in ("f1_score", "precision", "sensitivity", "specificity", "pr_auc"):
            v = np.array([r[f"val_{metric}"] for r in rs])
            e[metric] = float(v.mean())
            e[f"{metric}_sd"] = float(v.std(ddof=1)) if len(v) > 1 else 0.0
        e["targets_met"] = sum(1 for m, t in targets.items() if e.get(m, 0) >= t)
        e["all_targets"] = e["targets_met"] == len(targets)
        # Shortfall against every target at once -- ranks by how far from passing, so a
        # config that misses one target narrowly beats one that misses two badly.
        e["shortfall"] = float(sum(max(0.0, t - e.get(m, 0)) for m, t in targets.items()))
        out.append(e)
    return sorted(out, key=lambda e: (e["shortfall"], -e["f1_score"]))


def print_sweep(summary, targets=None):
    targets = targets or DEFAULT_TARGETS
    print("\n" + "=" * 86)
    print("SWEEP  (validation only -- test set untouched)   ranked by distance to targets")
    print("=" * 86)
    print(f"{'pos_boost':>10}{'alpha':>7}{'gamma':>7}{'F1':>9}{'prec':>9}"
          f"{'sens':>9}{'spec':>9}{'met':>5}{'short':>8}")
    for e in summary:
        print(f"{e['pos_boost']:>10}{e['alpha']:>7}{e['gamma']:>7}"
              f"{e['f1_score']:>9.4f}{e['precision']:>9.4f}"
              f"{e['sensitivity']:>9.4f}{e['specificity']:>9.4f}"
              f"{e['targets_met']:>4}/{len(targets)}{e['shortfall']:>8.4f}")
    print(f"\n  targets: " + ", ".join(f"{m}>={t}" for m, t in targets.items()))
    best = summary[0]
    if best["all_targets"]:
        print(f"  -> {('pos_boost=%s alpha=%s' % (best['pos_boost'], best['alpha']))} "
              f"meets every target on validation.")
    else:
        miss = [m for m, t in targets.items() if best.get(m, 0) < t]
        print(f"  -> best config still misses: {', '.join(miss)}. "
              f"No threshold or loss setting fixes that -- it needs a better model.")


def finalize_on_test(model, X_test, RR_test, y_test, X_val, RR_val, y_val,
                     threshold_name="precision_floor_90", targets=None):
    """Score ONE chosen configuration on test. Call this once, after the sweep is settled.

    The threshold comes from the FULL validation set here (not the half-split used for
    ranking), because at this point there is nothing left to choose between -- the split
    existed only to keep the comparison honest.
    """
    targets = targets or DEFAULT_TARGETS
    val_probs = model.predict([X_val, RR_val], batch_size=256, verbose=0).flatten()
    thr = select_thresholds(y_val, val_probs)[threshold_name]
    probs = model.predict([X_test, RR_test], batch_size=256, verbose=0).flatten()
    m = evaluate_at_threshold(y_test, probs, thr, label=f"FINAL TEST ({threshold_name})")
    print("\n  target check:")
    for name, t in targets.items():
        v = m.get(name, 0.0)
        print(f"    {name:<14} {v:.4f}  vs  >={t:.2f}   {'PASS' if v >= t else 'FAIL'}")
    return m
