"""Automatic backups for model files.

Every mutation of a deal's model.xlsx must call `snapshot()` first. Backups
land in `data/deals/<deal>/.backups/` with a UTC timestamp and a short reason
tag. `restore()` rolls a deal back to a named snapshot.

Design choices
--------------
- Plain file copies, not git: the .xlsx is binary and we want fast,
  isolation-free rollback per deal.
- Snapshots are append-only. We never overwrite a snapshot.
- Latest 50 snapshots per deal are kept; older ones are pruned on each
  snapshot. Tune via FMCLI_BACKUP_RETAIN env var.
"""

from __future__ import annotations

import hashlib
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .paths import deal_dir, deal_model_path


def _retain() -> int:
    try:
        return max(1, int(os.environ.get("FMCLI_BACKUP_RETAIN", "50")))
    except ValueError:
        return 50


def backups_dir(deal_id: str) -> Path:
    p = deal_dir(deal_id) / ".backups"
    p.mkdir(exist_ok=True)
    return p


def _hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:12]


@dataclass
class Snapshot:
    deal_id: str
    path: Path
    ts: str
    reason: str
    sha: str

    @property
    def name(self) -> str:
        return self.path.name


def snapshot(deal_id: str, reason: str = "pre-write") -> Snapshot:
    """Copy the deal's model.xlsx into .backups/. Returns the snapshot."""
    src = deal_model_path(deal_id)
    if not src.exists():
        raise FileNotFoundError(f"No model.xlsx for {deal_id}")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    sha = _hash(src)
    # Convert any underscores in the reason to hyphens so the filename parser
    # remains unambiguous: model_<ts>_<reason>_<sha>.xlsx
    safe_reason = "".join(c if c.isalnum() or c == "-" else "-" for c in reason)[:40]
    dst_name = f"model_{ts}_{safe_reason}_{sha}.xlsx"
    dst = backups_dir(deal_id) / dst_name
    shutil.copyfile(src, dst)

    _prune(deal_id, _retain())
    return Snapshot(deal_id=deal_id, path=dst, ts=ts, reason=reason, sha=sha)


def list_snapshots(deal_id: str) -> list[Snapshot]:
    out: list[Snapshot] = []
    for p in sorted(backups_dir(deal_id).glob("model_*.xlsx"), reverse=True):
        # filename: model_<ts>_<reason>_<sha>.xlsx
        stem = p.stem  # strip .xlsx
        parts = stem.split("_", 3)
        if len(parts) < 4:
            continue
        _, ts, reason, sha = parts
        out.append(Snapshot(deal_id=deal_id, path=p, ts=ts, reason=reason, sha=sha))
    return out


def restore(deal_id: str, snapshot_name: str) -> Snapshot:
    """Restore a named snapshot. Takes a 'pre-restore' snapshot first."""
    candidates = [s for s in list_snapshots(deal_id) if s.name == snapshot_name or snapshot_name in s.name]
    if not candidates:
        raise FileNotFoundError(f"No snapshot matching {snapshot_name!r} for {deal_id}.")
    if len(candidates) > 1:
        raise ValueError(
            f"Ambiguous snapshot match {snapshot_name!r} — {len(candidates)} candidates. "
            "Be more specific."
        )
    snap = candidates[0]
    # Always snapshot the current state before clobbering it.
    snapshot(deal_id, reason="pre-restore")
    shutil.copyfile(snap.path, deal_model_path(deal_id))
    return snap


def _prune(deal_id: str, keep: int) -> None:
    snaps = list_snapshots(deal_id)
    for old in snaps[keep:]:
        try:
            old.path.unlink()
        except FileNotFoundError:
            pass
