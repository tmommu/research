#!/usr/bin/env python3
"""Build the Colab notebook from the script + the quantization module.

    python3 tools/build_notebook.py

`eto_na_tlga_guys_final_na.py` (the Colab .py export) and `tibok/quantization.py` stay
the source of truth; the .ipynb is generated. Embedding the module as a `%%writefile`
cell keeps the notebook self-contained, which is required here because the repo is
private -- a `git clone` from a Colab runtime would prompt for credentials and fail, and
`files.upload()` makes the person re-upload the module on every fresh runtime.

The cost of embedding is that the module now exists in two places, so never hand-edit it
inside the .ipynb: edit `tibok/quantization.py` and re-run this script. `--check` fails
if the committed notebook has drifted from the sources, so CI or a pre-commit hook can
catch that.
"""

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "eto_na_tlga_guys_final_na.py")
# Every module the notebook needs on the runtime, written out before first use.
MODULES = ["quantization.py", "data_paths.py", "thresholds.py", "trials.py", "sweep.py"]
NOTEBOOK = os.path.join(ROOT, "TIBOK_Quantization_and_Testing.ipynb")

# The module-writing cells are injected immediately before the section whose markdown
# starts with this heading. It must sit ahead of the FIRST consumer of any embedded
# module -- `tibok.data_paths` is imported back in the data-loading section, long before
# quantization -- so this anchors near the top of the notebook rather than at the
# quantization step.
ANCHOR_HEADING = "## Data split"


def split_cells(source):
    """Split a Colab .py export into (kind, text) cells.

    Colab writes markdown cells as module-level triple-quoted strings and everything
    else as plain code, with no explicit code-cell delimiters -- the original code-cell
    boundaries are simply not recoverable from the export. So each run of code between
    two markdown blocks becomes one code cell, which reads naturally and keeps the
    notebook runnable top to bottom.
    """
    cells = []
    pattern = re.compile(r'^"""(.*?)"""$', re.S | re.M)
    pos = 0
    for m in pattern.finditer(source):
        code = source[pos:m.start()]
        if code.strip():
            cells.append(("code", code.strip("\n")))
        cells.append(("markdown", m.group(1).strip("\n")))
        pos = m.end()
    tail = source[pos:]
    if tail.strip():
        cells.append(("code", tail.strip("\n")))
    return cells


def strip_coding_header(code):
    lines = code.split("\n")
    while lines and (lines[0].startswith("# -*- coding") or not lines[0].strip()):
        lines.pop(0)
    return "\n".join(lines)


def nb_cell(kind, text):
    lines = text.split("\n")
    src = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    if kind == "markdown":
        return {"cell_type": "markdown", "metadata": {}, "source": src}
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": src}


def build():
    source = open(SCRIPT).read()
    module_srcs = {m: open(os.path.join(ROOT, "tibok", m)).read() for m in MODULES}

    raw = split_cells(source)
    cells = []
    injected = False

    for i, (kind, text) in enumerate(raw):
        if i == 0 and kind == "code":
            text = strip_coding_header(text)
            if not text.strip():
                continue
        if kind == "code":
            text = strip_coding_header(text)
            if not text.strip():
                continue

        if kind == "markdown" and text.lstrip().startswith(ANCHOR_HEADING):
            cells.append(nb_cell("markdown",
                "## Write the `tibok` modules onto the runtime\n\n"
                "This notebook is self-contained on purpose. The repository is private, so a\n"
                "`git clone` from a Colab runtime would prompt for credentials and fail, and\n"
                "`files.upload()` would mean re-uploading the modules every time the runtime is\n"
                "recycled. The cells below write them straight to disk instead.\n\n"
                "- `data_paths.py` — resolves the MIT-BIH / INCART folders and fails loudly on a\n"
                "  bad path. Used by the data-loading section immediately below.\n"
                "- `quantization.py` — INT8 conversion and FP32-vs-INT8 verification, used at the\n"
                "  end of the notebook.\n"
                "- `thresholds.py` / `trials.py` — operating-point selection and the optional\n"
                "  multi-trial replication study.\n\n"
                "**Do not edit the modules here.** They are generated from `tibok/` in the repo by\n"
                "`tools/build_notebook.py`; edits made in these cells are lost the next time the\n"
                "notebook is rebuilt. Change the repo file and re-run the builder."))
            cells.append(nb_cell("code",
                "import os, sys\n"
                "os.makedirs('tibok', exist_ok=True)\n"
                "# Lazy __init__: importing tibok.data_paths must not drag in TensorFlow.\n"
                "open('tibok/__init__.py', 'w').close()\n"
                "if '.' not in sys.path:\n    sys.path.insert(0, '.')"))
            for mod in MODULES:
                cells.append(nb_cell("code",
                    f"%%writefile tibok/{mod}\n" + module_srcs[mod].rstrip("\n")))
            injected = True

        cells.append(nb_cell(kind, text))

    if not injected:
        sys.exit(f"ERROR: anchor heading {ANCHOR_HEADING!r} not found in {SCRIPT}")

    return {
        "nbformat": 4,
        "nbformat_minor": 0,
        "metadata": {
            "colab": {"provenance": [], "toc_visible": True},
            "kernelspec": {"name": "python3", "display_name": "Python 3"},
            "language_info": {"name": "python"},
            "accelerator": "GPU",
        },
        "cells": cells,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if the committed notebook is stale")
    args = ap.parse_args()

    nb = build()
    text = json.dumps(nb, indent=1, ensure_ascii=False) + "\n"

    if args.check:
        if not os.path.exists(NOTEBOOK):
            sys.exit(f"STALE: {NOTEBOOK} does not exist")
        if open(NOTEBOOK).read() != text:
            sys.exit(f"STALE: {NOTEBOOK} differs from its sources -- re-run tools/build_notebook.py")
        print(f"OK: {os.path.basename(NOTEBOOK)} is up to date")
    else:
        open(NOTEBOOK, "w").write(text)
        n_code = sum(1 for c in nb["cells"] if c["cell_type"] == "code")
        n_md = len(nb["cells"]) - n_code
        print(f"Wrote {NOTEBOOK}\n  {len(nb['cells'])} cells ({n_code} code, {n_md} markdown), "
              f"{len(text)/1024:.1f} KB")
