"""Balance the positive class BY SYMBOL, not just positive-vs-negative.

The problem
-----------

Two mechanisms in this study balance classes, and both are blind to which *kind* of
arrhythmia a beat is:

  - `augment_dataset(..., n_aug_positive=2)` copies every positive beat twice. V beats and
    F beats are boosted by the same factor, so the ratio between them is exactly preserved.
  - `class_weight` only ever sees the binary label, so it cannot tell a V from an F either.

The positive class is 97% V beats. So "balanced" training is, in practice, training a
V-beat detector, and the pooled sensitivity is a V-beat number wearing a label that says
"arrhythmia". One observed test split:

    V  6030 beats -> 0.974 sensitivity
    A   163 beats -> 0.859
    F    23 beats -> 0.087
    S     1 beat  -> 0.000

Sensitivity tracks sample count monotonically. Nothing about thresholds, quantization or
the loss function fixes that: the model was never given enough F beats to learn fusion
morphology, and the RR features actively mislead there, because a fusion beat is a sinus
beat and an ectopic beat arriving together and so is not especially premature.

Two levers
----------

`symbol_augmentation_plan` + `augment_by_symbol` oversample rare symbols more than common
ones. `symbol_sample_weights` instead reweights the loss per beat, which costs no memory
and creates no near-duplicates.

**The weights lever only works because `focal_loss` now returns one value per sample.**
While it reduced to a scalar, `sample_weight` had nothing per-sample to scale and was as
inert as `class_weight` was.

Strategies
----------

`"equal"` brings every positive symbol to the largest one's count. Honest in intent but
brutal in practice: with 700 F beats against 24k V beats it means ~34 copies of each F
beat, and the model can memorise those 700 rather than learn fusion.

`"sqrt"` (default) targets counts proportional to sqrt(n), the usual middle ground: rare
symbols gain a lot of weight without the common ones being drowned or the rare ones being
reduced to a few memorised examples.

`cap` bounds the multiplier regardless of strategy. Oversampling cannot create information
that is not in the data -- 23 F beats augmented 30x is still 23 F beats. If F sensitivity
matters for the claim, the real fix is more F beats, not more copies of these ones.
"""

from __future__ import annotations

import numpy as np

__all__ = ["symbol_counts", "symbol_augmentation_plan", "augment_by_symbol",
           "symbol_sample_weights"]


def symbol_counts(symbols, y):
    """Count positive beats per annotation symbol."""
    symbols = np.asarray(symbols)
    y = np.asarray(y)
    pos = symbols[y == 1]
    return {s: int((pos == s).sum()) for s in sorted(set(pos.tolist()))}


def symbol_augmentation_plan(symbols, y, strategy="sqrt", cap=10, min_count=0):
    """Return {symbol: extra_copies_per_beat} for the positive class.

    `extra_copies` is how many augmented duplicates to add per original beat, so 0 means
    "leave as is". Negative targets are clamped: this never discards data.
    """
    counts = symbol_counts(symbols, y)
    if not counts:
        return {}
    biggest = max(counts.values())

    plan = {}
    for s, n in counts.items():
        if n <= 0:
            continue
        if strategy == "equal":
            target = biggest
        elif strategy == "sqrt":
            # target ∝ sqrt(n), scaled so the largest symbol keeps its own count
            target = biggest * float(np.sqrt(n / biggest))
        elif strategy == "none":
            target = n
        else:
            raise ValueError(f"unknown strategy {strategy!r}")
        target = max(target, min_count)
        extra = max(0, int(round(target / n)) - 1)
        plan[s] = min(extra, cap)
    return plan


def augment_by_symbol(X, rr, y, symbols, augment_fn, rng, plan=None,
                      strategy="sqrt", cap=10, verbose=True):
    """Oversample positive beats per symbol according to `plan`.

    `augment_fn(segment, rng)` is the notebook's existing `augment_segment`. RR features are
    carried over unchanged for copies, since the augmentation perturbs the waveform and not
    beat timing -- the same assumption the original uniform augmentation made.
    """
    X = np.asarray(X)
    rr = np.asarray(rr)
    y = np.asarray(y)
    symbols = np.asarray(symbols)

    if plan is None:
        plan = symbol_augmentation_plan(symbols, y, strategy=strategy, cap=cap)

    Xs, rrs, ys, syms = [X], [rr], [y], [symbols]
    counts = symbol_counts(symbols, y)
    if verbose:
        print(f"{'sym':<6}{'n':>8}{'extra copies':>14}{'after':>10}")
    for s, extra in sorted(plan.items(), key=lambda kv: -counts.get(kv[0], 0)):
        n = counts.get(s, 0)
        if verbose:
            print(f"{s:<6}{n:>8}{extra:>14}{n * (1 + extra):>10}")
        if extra <= 0 or n == 0:
            continue
        idx = np.where((y == 1) & (symbols == s))[0]
        for _ in range(extra):
            Xs.append(np.stack([augment_fn(X[i], rng) for i in idx]).astype(np.float32))
            rrs.append(rr[idx])
            ys.append(np.ones(len(idx), dtype=y.dtype))
            syms.append(symbols[idx])

    return (np.concatenate(Xs), np.concatenate(rrs),
            np.concatenate(ys), np.concatenate(syms))


def symbol_sample_weights(symbols, y, strategy="sqrt", cap=10.0, negative_weight=1.0):
    """Per-beat loss weights that lift rare positive symbols.

    Pass the result as `sample_weight` to `model.fit`. Prefer this over oversampling when
    memory matters or when duplicating 23 beats 30 times feels like what it is.

    Requires a per-sample loss. With the old scalar-reducing focal loss these weights would
    be silently ignored, exactly as `class_weight` was.
    """
    symbols = np.asarray(symbols)
    y = np.asarray(y)
    counts = symbol_counts(symbols, y)
    if not counts:
        return np.full(len(y), negative_weight, dtype=np.float32)
    biggest = max(counts.values())

    w = np.full(len(y), float(negative_weight), dtype=np.float32)
    for s, n in counts.items():
        if strategy == "equal":
            wt = biggest / n
        elif strategy == "sqrt":
            wt = float(np.sqrt(biggest / n))
        elif strategy == "none":
            wt = 1.0
        else:
            raise ValueError(f"unknown strategy {strategy!r}")
        w[(y == 1) & (symbols == s)] = min(wt, cap)
    return w
