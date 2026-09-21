"""Locate the MIT-BIH / INCART record folders on a Colab Drive mount, and fail loudly.

The plain `os.walk(base_path)` indexing this replaces has one bad failure mode: `os.walk`
on a nonexistent path -- or on a `https://drive.google.com/...` sharing URL pasted in
where a filesystem path belongs -- does not raise. It yields nothing. The index comes
back empty, the "expect 75" warning scrolls past, and the run continues until it dies
much later inside `load_and_segment`, far from the actual mistake.

A Drive *sharing link* is a browser URL. Drive is mounted as a filesystem at
/content/drive, so the path is always /content/drive/MyDrive/... -- a URL can never be
one. If the folder was shared with you rather than owned by you, it does not appear under
MyDrive at all until you add a shortcut to it (Drive UI -> right-click the folder ->
"Organise" -> "Add shortcut to Drive"); only then does it show up as a normal directory.

So `resolve_db_path` rejects URLs outright, searches the mount for the records when the
configured path is wrong, and raises with the candidates it did find.
"""

from __future__ import annotations

import os
import re

__all__ = ["is_url", "index_records", "find_records_root", "resolve_db_path", "preflight"]

_URL_RE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.I)

DEFAULT_SEARCH_ROOTS = ("/content/drive/MyDrive", "/content/drive/Shareddrives", "/content")


def is_url(s):
    return bool(_URL_RE.match(str(s).strip()))


def index_records(base_path):
    """Map record id -> extensionless path for every .hea under `base_path`."""
    index = {}
    for root, _dirs, files in os.walk(base_path):
        for f in files:
            if f.endswith(".hea"):
                index[f[:-4]] = os.path.join(root, f[:-4])
    return index


def find_records_root(probe_records, search_roots=DEFAULT_SEARCH_ROOTS, max_depth=6):
    """Find directories containing any of `probe_records` (e.g. ['I01', 'I75']).

    Returns [(directory, n_probe_records_found)] best first. Depth-capped because a full
    walk of a large Drive is slow and we only ever need the folder itself.
    """
    wanted = {f"{r}.hea" for r in probe_records}
    hits = {}
    for root in search_roots:
        if not os.path.isdir(root):
            continue
        base_depth = root.rstrip("/").count("/")
        for dirpath, dirnames, files in os.walk(root):
            if dirpath.count("/") - base_depth >= max_depth:
                dirnames[:] = []
                continue
            found = wanted.intersection(files)
            if found:
                hits[dirpath] = max(hits.get(dirpath, 0), len(found))
    return sorted(hits.items(), key=lambda kv: -kv[1])


def resolve_db_path(configured, probe_records, label, search_roots=DEFAULT_SEARCH_ROOTS,
                    autodetect=True):
    """Return a usable directory for `label`, or raise with what was actually found."""
    configured = str(configured).strip()

    if is_url(configured):
        msg = (
            f"{label}: {configured!r} is a URL, not a filesystem path.\n"
            f"  Google Drive is MOUNTED as a filesystem, so the path always looks like\n"
            f"  /content/drive/MyDrive/<folder>. A browser sharing link is never a path --\n"
            f"  os.walk() on it silently returns nothing, which is why 0 records were found.\n"
            f"  If the folder was shared with you rather than owned by you, it will not be\n"
            f"  under MyDrive until you add a shortcut: in Drive, right-click the folder ->\n"
            f"  Organise -> 'Add shortcut to Drive'. Then use that shortcut's path here."
        )
        if autodetect:
            found = find_records_root(probe_records, search_roots)
            if found:
                best = found[0][0]
                print(f"{label}: configured path is a URL; auto-detected records at {best!r} instead.")
                for d, n in found[:5]:
                    print(f"    {d}  ({n}/{len(probe_records)} probe records)")
                return best
            msg += f"\n  Searched {list(search_roots)} for {probe_records} and found nothing."
        raise ValueError(msg)

    if os.path.isdir(configured):
        idx = index_records(configured)
        if any(r in idx for r in probe_records):
            return configured
        extra = ""
        if autodetect:
            found = find_records_root(probe_records, search_roots)
            if found:
                best = found[0][0]
                print(f"{label}: {configured!r} exists but holds none of {probe_records}; "
                      f"auto-detected {best!r} instead.")
                return best
            extra = f"\n  Searched {list(search_roots)} and found none of {probe_records}."
        raise FileNotFoundError(
            f"{label}: {configured!r} exists but contains none of {probe_records} "
            f"({len(idx)} .hea files found there).{extra}"
        )

    if autodetect:
        found = find_records_root(probe_records, search_roots)
        if found:
            best = found[0][0]
            print(f"{label}: {configured!r} does not exist; auto-detected {best!r} instead.")
            for d, n in found[:5]:
                print(f"    {d}  ({n}/{len(probe_records)} probe records)")
            return best

    raise FileNotFoundError(
        f"{label}: {configured!r} does not exist, and no folder containing "
        f"{probe_records} was found under {list(search_roots)}.\n"
        f"  Check the mount ran (drive.mount('/content/drive')) and that the folder is "
        f"under MyDrive -- a folder merely shared with you needs a shortcut first."
    )


def preflight(index, required, label, expected_total=None):
    """Verify every required record is present BEFORE loading starts.

    The old code printed a warning and carried on, so a missing database surfaced as a
    FileNotFoundError deep inside the loading loop, long after the real mistake. Checking
    up front means the error names the problem.
    """
    missing = [r for r in required if r not in index]
    print(f"{label}: {len(index)} .hea files indexed, {len(required) - len(missing)}/{len(required)} required records present")

    if expected_total is not None and len(index) != expected_total:
        print(
            f"  NOTE: expected about {expected_total} .hea files here but found {len(index)}. "
            f"That is not fatal -- only the {len(required)} required records are read -- but "
            f"an unexpected count usually means another database, a duplicate copy, or a "
            f"nested extraction is sharing this folder. Worth confirming it is what you think."
        )

    if missing:
        raise FileNotFoundError(
            f"{label}: {len(missing)} required records are missing: {missing}\n"
            f"  Indexed {len(index)} .hea files. Fix the path or the folder contents before "
            f"training -- continuing would change the study population."
        )
    return True
