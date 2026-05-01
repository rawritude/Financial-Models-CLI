"""Load and represent a deal's metadata (deal.yaml)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import yaml

from .paths import deal_yaml_path


@dataclass
class Covenant:
    name: str
    description: str
    output: str            # name of the output cell to test (e.g. "DSCR")
    operator: str          # ">=", ">", "<=", "<"
    threshold: float
    severity: str = "default"   # "info" | "default" | "breach"
    tested_periods: str = "current"  # "current" | "ltm" | "all"


@dataclass
class Deal:
    id: str
    borrower: str
    project: str
    sector: str
    facility: str
    currency: str
    commitment: float
    closing_date: str
    maturity_date: str
    inputs_sheet: str
    outputs: dict[str, str]              # name -> "Sheet!Cell"
    input_map: dict[str, str]            # borrower-submission column -> "Sheet!Cell"
    covenants: list[Covenant] = field(default_factory=list)
    parties: dict[str, dict[str, str]] = field(default_factory=dict)
    notes: str = ""

    @property
    def commitment_fmt(self) -> str:
        return f"{self.currency} {self.commitment:,.0f}"


def load_deal(deal_id: str) -> Deal:
    path = deal_yaml_path(deal_id)
    with path.open() as f:
        raw: dict[str, Any] = yaml.safe_load(f)

    covenants = [Covenant(**c) for c in raw.get("covenants", [])]
    return Deal(
        id=deal_id,
        borrower=raw["borrower"],
        project=raw["project"],
        sector=raw["sector"],
        facility=raw["facility"],
        currency=raw.get("currency", "CAD"),
        commitment=float(raw["commitment"]),
        closing_date=str(raw["closing_date"]),
        maturity_date=str(raw["maturity_date"]),
        inputs_sheet=raw.get("inputs_sheet", "Inputs"),
        outputs=raw["outputs"],
        input_map=raw.get("input_map", {}),
        covenants=covenants,
        parties=raw.get("parties", {}),
        notes=raw.get("notes", ""),
    )
