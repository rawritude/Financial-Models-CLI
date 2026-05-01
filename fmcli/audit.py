"""Append-only audit trail for every model mutation."""

from __future__ import annotations

import getpass
import json
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import deal_audit_path


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _user() -> str:
    try:
        return f"{getpass.getuser()}@{socket.gethostname()}"
    except Exception:
        return "unknown"


def append(deal_id: str, event: str, payload: dict[str, Any]) -> None:
    """Append a JSON Lines record to the deal's audit log."""
    path = deal_audit_path(deal_id)
    record = {
        "ts": _now(),
        "user": _user(),
        "event": event,
        "deal": deal_id,
        **payload,
    }
    with path.open("a") as f:
        f.write(json.dumps(record, default=str) + "\n")


def read(deal_id: str) -> list[dict[str, Any]]:
    path = deal_audit_path(deal_id)
    if not path.exists():
        return []
    out: list[dict[str, Any]] = []
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out
