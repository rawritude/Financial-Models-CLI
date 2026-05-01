"""Covenant testing against current model outputs."""

from __future__ import annotations

from dataclasses import dataclass

from .deal import Covenant, Deal
from .excel import read_cells
from .paths import deal_model_path


@dataclass
class CovenantResult:
    name: str
    description: str
    output: str
    operator: str
    threshold: float
    actual: float | None
    passed: bool
    severity: str  # "ok" | "watch" | "breach"
    note: str = ""


_OPS = {
    ">=": lambda a, b: a >= b,
    ">":  lambda a, b: a > b,
    "<=": lambda a, b: a <= b,
    "<":  lambda a, b: a < b,
    "==": lambda a, b: a == b,
}


def _coerce_float(v) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _classify(c: Covenant, passed: bool, actual: float | None) -> str:
    if actual is None:
        return "watch"
    if passed:
        # Within 10% of the threshold? Flag as watch.
        margin = abs(actual - c.threshold) / max(abs(c.threshold), 1e-9)
        return "watch" if margin < 0.10 else "ok"
    return c.severity if c.severity in {"watch", "breach"} else "breach"


def test_one(deal: Deal, c: Covenant) -> CovenantResult:
    if c.output not in deal.outputs:
        return CovenantResult(
            name=c.name,
            description=c.description,
            output=c.output,
            operator=c.operator,
            threshold=c.threshold,
            actual=None,
            passed=False,
            severity="watch",
            note=f"Output '{c.output}' not declared in deal.yaml outputs map.",
        )

    refs = {c.output: deal.outputs[c.output]}
    actual = _coerce_float(read_cells(deal_model_path(deal.id), refs)[c.output])
    if actual is None:
        return CovenantResult(
            name=c.name,
            description=c.description,
            output=c.output,
            operator=c.operator,
            threshold=c.threshold,
            actual=None,
            passed=False,
            severity="watch",
            note="No numeric value at the output cell — recalc may not have run.",
        )

    op = _OPS.get(c.operator)
    if op is None:
        return CovenantResult(
            name=c.name,
            description=c.description,
            output=c.output,
            operator=c.operator,
            threshold=c.threshold,
            actual=actual,
            passed=False,
            severity="watch",
            note=f"Unknown operator {c.operator!r}.",
        )
    passed = bool(op(actual, c.threshold))
    return CovenantResult(
        name=c.name,
        description=c.description,
        output=c.output,
        operator=c.operator,
        threshold=c.threshold,
        actual=actual,
        passed=passed,
        severity=_classify(c, passed, actual),
    )


def test_all(deal: Deal) -> list[CovenantResult]:
    return [test_one(deal, c) for c in deal.covenants]
