"""Aggregate KPIs across all deals in the workspace."""

from __future__ import annotations

import pandas as pd

from . import excel
from .deal import load_deal
from .paths import deal_model_path, deals_dir


def rollup() -> pd.DataFrame:
    """Return a DataFrame with one row per deal and the live values of each
    output cell as columns (where the deal exposes them)."""
    rows: list[dict] = []
    for d in sorted(deals_dir().iterdir()):
        if not (d / "deal.yaml").exists():
            continue
        try:
            deal = load_deal(d.name)
            values = excel.read_cells(deal_model_path(deal.id), deal.outputs)
        except Exception as e:
            rows.append({"deal": d.name, "error": str(e)})
            continue
        row = {
            "deal": deal.id,
            "borrower": deal.borrower,
            "sector": deal.sector,
            "currency": deal.currency,
            "commitment": deal.commitment,
        }
        row.update(values)
        rows.append(row)
    return pd.DataFrame(rows)
