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

__all__ = ["is_url", "index_records", "find_records_root", "resolve_db_path", "preflight",
           "DbSource", "resolve_db_source", "pick_lead"]

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


# ---------------------------------------------------------------------------
# Record sources: a local Drive folder, or PhysioNet streamed over HTTP
# ---------------------------------------------------------------------------

class DbSource:
    """Where a database's records are read from, and how to read one.

    Two kinds:

      local     -- records sit in a mounted directory (a Drive folder).
      physionet -- records are streamed per-record over HTTPS via wfdb's `pn_dir`.

    The PhysioNet kind exists because depending on a *shared* Drive folder is fragile in
    ways that have nothing to do with the code. View-only access is enough to read files,
    and "Add shortcut to Drive" works at view-only too, so permissions alone are usually
    not the blocker. But two things can still stop it:

      - If the owner ticked "Viewers cannot download, print, or copy", the FUSE mount
        cannot read the bytes at all, and no path fix helps.
      - Drive enforces per-file download quotas on widely-shared files. A run that reads
        75 multi-megabyte records can trip "download quota exceeded", which then blocks
        the folder for hours -- and it fails partway through a run, not at the start.

    Streaming from PhysioNet sidesteps both: INCART and MIT-BIH are open-access there, so
    the run depends on nothing anyone else controls. `wfdb.rdrecord(rec, pn_dir=...)`
    fetches one record at a time rather than mirroring the whole database, so there is no
    multi-hundred-megabyte download step.
    """

    def __init__(self, kind, label, path=None, index=None, pn_dir=None):
        self.kind = kind
        self.label = label
        self.path = path
        self.index = index or {}
        self.pn_dir = pn_dir

    def __repr__(self):
        where = self.path if self.kind == "local" else f"physionet:{self.pn_dir}"
        return f"<DbSource {self.label} {self.kind} {where!r}>"

    def read(self, record_id, ann_ext="atr"):
        """Return (record, annotation) for one record, from whichever source applies."""
        import wfdb
        if self.kind == "local":
            if record_id not in self.index:
                raise FileNotFoundError(
                    f"{self.label}: {record_id}.hea not found under {self.path!r}"
                )
            p = self.index[record_id]
            return wfdb.rdrecord(p), wfdb.rdann(p, ann_ext)
        return (wfdb.rdrecord(record_id, pn_dir=self.pn_dir),
                wfdb.rdann(record_id, ann_ext, pn_dir=self.pn_dir))


def resolve_db_source(configured, probe_records, label, pn_dir, required=None,
                      expected_total=None, search_roots=DEFAULT_SEARCH_ROOTS,
                      prefer="local"):
    """Resolve a database to a local folder, falling back to PhysioNet streaming.

    `prefer="physionet"` skips the local lookup entirely, which is the reproducible
    choice: it does not depend on anyone's Drive sharing settings.
    """
    if prefer == "physionet":
        print(f"{label}: using PhysioNet (pn_dir={pn_dir!r}) by request.")
        return DbSource("physionet", label, pn_dir=pn_dir)

    try:
        path = resolve_db_path(configured, probe_records, label, search_roots=search_roots)
    except (ValueError, FileNotFoundError) as e:
        print(f"{label}: local lookup failed, falling back to PhysioNet streaming.")
        print(f"    reason: {str(e).splitlines()[0]}")
        print(f"    reading from PhysioNet pn_dir={pn_dir!r} instead -- no Drive access needed.")
        return DbSource("physionet", label, pn_dir=pn_dir)

    index = index_records(path)
    if required is not None:
        try:
            preflight(index, required, label, expected_total=expected_total)
        except FileNotFoundError as e:
            print(f"{label}: local folder is incomplete, falling back to PhysioNet streaming.")
            print(f"    reason: {str(e).splitlines()[0]}")
            return DbSource("physionet", label, pn_dir=pn_dir)
    return DbSource("local", label, path=path, index=index)


def pick_lead(record, preferred, label="", record_id=""):
    """Index of the first `preferred` lead present in `record.sig_name`.

    Reading channel 0 and assuming it is MLII is wrong for MIT-BIH. Most records are
    ordered [MLII, V5], but not all -- record 114 is [V5, MLII], so channel 0 there is a
    completely different lead from every other record in the study. Selecting by name
    instead keeps the input channel consistent, which is the whole point of specifying a
    lead in the methodology.
    """
    names = [str(n).strip() for n in (record.sig_name or [])]
    for want in preferred:
        if want in names:
            return names.index(want)
    raise ValueError(
        f"{label} {record_id}: none of {list(preferred)} in sig_name={names}. "
        f"Refusing to guess a channel -- that would silently feed a different lead "
        f"into the model for this record."
    )
