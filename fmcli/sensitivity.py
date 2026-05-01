"""Run a one-at-a-time (OAT) sensitivity analysis on a deal model.

Given a list of (input_cell_name, [shock1, shock2, ...]), apply each shock
in turn, recalc the workbook via LibreOffice, read the named outputs, and
roll back. Returns a tidy DataFrame.

The agent orchestrates higher-level analyses (multi-factor, scenarios) on
top of this primitive.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from . import backup, compute, excel
from .deal import Deal
from .excel import CellWrite
from .paths import deal_model_path


@dataclass
class Shock:
    input_name: str   # key in deal.input_map
    label: str        # human-readable, e.g. "+10% revenue"
    multiplier: float | None = None   # set base * multiplier
    delta: float | None = None        # base + delta
    absolute: float | None = None     # set to absolute value


def _apply(base, shock: Shock):
    if shock.absolute is not None:
        return shock.absolute
    if shock.multiplier is not None:
        return (base or 0) * shock.multiplier
    if shock.delta is not None:
        return (base or 0) + shock.delta
    return base


def run(deal: Deal, shocks: list[Shock], outputs: list[str] | None = None) -> pd.DataFrame:
    """Run each shock independently. Always restores the model to baseline."""
    output_names = outputs or list(deal.outputs)
    output_refs = {n: deal.outputs[n] for n in output_names}
    model = deal_model_path(deal.id)

    snap = backup.snapshot(deal.id, reason="pre-sensitivity")

    base_values = excel.read_cells(model, output_refs)
    rows: list[dict] = [{"scenario": "base", **base_values}]

    try:
        for shock in shocks:
            ref = deal.input_map.get(shock.input_name)
            if ref is None:
                rows.append({
                    "scenario": shock.label,
                    "error": f"unknown input {shock.input_name!r}",
                })
                continue

            current = excel.read_cell(model, ref)
            new_value = _apply(current, shock)

            excel.write_cells(model, [CellWrite(ref=ref, value=new_value, label=shock.label)])
            try:
                compute.recompute(deal)
            except Exception as e:
                rows.append({"scenario": shock.label, "error": f"recompute: {e}"})
            else:
                rows.append({
                    "scenario": shock.label,
                    "input": shock.input_name,
                    "from": current,
                    "to": new_value,
                    **excel.read_cells(model, output_refs),
                })
            # Roll back to baseline before the next shock.
            backup.restore(deal.id, snap.name)
    finally:
        # Final safety: ensure baseline is restored.
        try:
            backup.restore(deal.id, snap.name)
        except Exception:
            pass

    return pd.DataFrame(rows)
