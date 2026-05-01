"""Build a library of fabricated borrower submissions per deal.

Each scenario is a two-column .xlsx (label / value) that maps onto the
deal's `input_map`. Drop one of these into `fmcli update <deal> <path>` to
exercise the system end-to-end against a specific story:

  • q1-clean        — close to plan; baseline monitoring case
  • q1-stress-rev   — revenue down sharply; pushes DSCR through the lock-up
  • q1-stress-opex  — opex over-run; squeeze on coverage
  • q1-stress-rate  — refixed rate up 200bps; interest expense spike
  • q1-upside       — revenue ahead, opex contained; headroom builds
  • q1-mislabeled   — one label off; demonstrates error handling
  • q1-partial      — only some inputs submitted; still propagates cleanly
  • q2-clean        — next-period actuals; rolls the model forward

These are intentionally synthetic — the labels match deal.input_map keys
exactly so the model-updater can propagate them with no normalization.
"""

from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

ROOT = Path(__file__).resolve().parent.parent
HEADER_FILL = PatternFill("solid", fgColor="1F3864")
HEADER_FONT = Font(bold=True, color="FFFFFF")
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
MONEY_FMT = '_($* #,##0_);_($* (#,##0);_($* "-"_);_(@_)'
PCT_FMT = "0.00%"


def _write_submission(
    path: Path,
    sheet_name: str,
    rows: list[tuple[str, float]],
    note: str | None = None,
) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = sheet_name[:31]
    ws.column_dimensions["A"].width = 32
    ws.column_dimensions["B"].width = 22

    if note:
        ws["A1"] = note
        ws["A1"].font = Font(italic=True, color="595959")
        ws.merge_cells("A1:B1")
        offset = 2
    else:
        offset = 1

    h1 = ws.cell(row=offset, column=1, value="Label")
    h2 = ws.cell(row=offset, column=2, value="Value")
    for c in (h1, h2):
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = Alignment(horizontal="center")

    for i, (label, value) in enumerate(rows, start=offset + 1):
        ws.cell(row=i, column=1, value=label).font = Font(bold=True)
        c = ws.cell(row=i, column=2, value=value)
        c.fill = INPUT_FILL
        c.number_format = MONEY_FMT if isinstance(value, (int, float)) and value >= 1 else PCT_FMT

    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


# ---------------------------------------------------------------------------
# Highway 407 East Extension scenarios
# ---------------------------------------------------------------------------
# Baseline assumptions in the model:
#   AvailabilityPayment_Q1 = 16,500,000   Opex_Q1 = 3,900,000
#   InterestRate           = 5.25%        DSCR baseline ≈ 1.24x

H407 = ROOT / "data" / "deals" / "highway-407-east-extension" / "inputs" / "scenarios"


def build_h407_scenarios() -> None:
    _write_submission(
        H407 / "q1-clean.xlsx",
        "Actuals_2026Q1",
        [
            ("AvailabilityPayment_Q1", 16_490_000),  # ~on plan, minor deduction
            ("Opex_Q1",                3_910_000),   # ~on plan
            ("InterestRate",           0.0525),      # unchanged
        ],
        note="2026-Q1 actuals — close to plan, baseline monitoring case",
    )

    _write_submission(
        H407 / "q1-stress-rev.xlsx",
        "Actuals_2026Q1",
        [
            ("AvailabilityPayment_Q1", 14_500_000),  # ~12% deduction (availability shortfall)
            ("Opex_Q1",                3_950_000),
            ("InterestRate",           0.0525),
        ],
        note="2026-Q1 — sustained availability deduction; tests DSCR lock-up",
    )

    _write_submission(
        H407 / "q1-stress-opex.xlsx",
        "Actuals_2026Q1",
        [
            ("AvailabilityPayment_Q1", 16_500_000),
            ("Opex_Q1",                5_400_000),   # +38% opex over-run
            ("InterestRate",           0.0525),
        ],
        note="2026-Q1 — winter lifecycle event; opex over-run",
    )

    _write_submission(
        H407 / "q1-stress-rate.xlsx",
        "Actuals_2026Q1",
        [
            ("AvailabilityPayment_Q1", 16_500_000),
            ("Opex_Q1",                3_900_000),
            ("InterestRate",           0.0725),     # +200bps refix
        ],
        note="2026-Q1 — CORRA reset spike; rate +200bps",
    )

    _write_submission(
        H407 / "q1-upside.xlsx",
        "Actuals_2026Q1",
        [
            ("AvailabilityPayment_Q1", 16_750_000),  # bonus payment captured
            ("Opex_Q1",                3_750_000),   # opex underrun
            ("InterestRate",           0.0510),     # rate refixed lower
        ],
        note="2026-Q1 — bonus payment + opex underrun + rate down",
    )

    _write_submission(
        H407 / "q1-mislabeled.xlsx",
        "Actuals_2026Q1",
        [
            ("AvailPayment_Q1",        16_490_000),  # WRONG: AvailPayment vs AvailabilityPayment
            ("OperatingExpense_Q1",    3_910_000),   # WRONG: OperatingExpense vs Opex
            ("InterestRate",           0.0525),
        ],
        note="2026-Q1 — WRONG labels; tests model-updater error handling",
    )

    _write_submission(
        H407 / "q1-partial.xlsx",
        "Actuals_2026Q1",
        [
            ("AvailabilityPayment_Q1", 16_490_000),
            # Opex_Q1 deliberately omitted
            ("InterestRate",           0.0525),
        ],
        note="2026-Q1 — partial submission; only some fields present",
    )

    _write_submission(
        H407 / "q2-clean.xlsx",
        "Actuals_2026Q2",
        [
            ("AvailabilityPayment_Q2", 16_700_000),  # ~modest CPI uplift
            ("Opex_Q2",                3_960_000),
            ("InterestRate",           0.0530),     # quarterly refix
        ],
        note="2026-Q2 actuals — clean roll-forward",
    )


# ---------------------------------------------------------------------------
# Oneida Energy Storage scenarios
# ---------------------------------------------------------------------------
# Baseline: CapacityPayment_Q1 = 7.5M, ArbitrageRevenue_Q1 = 1.4M,
#           Opex_Q1 = 1.3M, InterestRate = 6.25%, DSCR ≈ 1.56x

ONEIDA = ROOT / "data" / "deals" / "oneida-energy-storage" / "inputs" / "scenarios"


def build_oneida_scenarios() -> None:
    _write_submission(
        ONEIDA / "q1-clean.xlsx",
        "Actuals_2026Q1",
        [
            ("CapacityPayment_Q1",  7_500_000),     # CSA payment, fixed
            ("ArbitrageRevenue_Q1", 1_350_000),    # close to plan
            ("Opex_Q1",             1_310_000),
            ("InterestRate",        0.0625),
        ],
        note="2026-Q1 — clean baseline submission",
    )

    _write_submission(
        ONEIDA / "q1-stress-arbitrage.xlsx",
        "Actuals_2026Q1",
        [
            ("CapacityPayment_Q1",  7_500_000),
            ("ArbitrageRevenue_Q1",   600_000),    # arbitrage spreads compressed >50%
            ("Opex_Q1",             1_310_000),
            ("InterestRate",        0.0625),
        ],
        note="2026-Q1 — arbitrage revenue collapse (mild winter, low spreads)",
    )

    _write_submission(
        ONEIDA / "q1-stress-opex.xlsx",
        "Actuals_2026Q1",
        [
            ("CapacityPayment_Q1",  7_500_000),
            ("ArbitrageRevenue_Q1", 1_400_000),
            ("Opex_Q1",             2_100_000),   # +60% opex (insurance + augmentation)
            ("InterestRate",        0.0625),
        ],
        note="2026-Q1 — augmentation + insurance step-up",
    )

    _write_submission(
        ONEIDA / "q1-stress-rate.xlsx",
        "Actuals_2026Q1",
        [
            ("CapacityPayment_Q1",  7_500_000),
            ("ArbitrageRevenue_Q1", 1_400_000),
            ("Opex_Q1",             1_310_000),
            ("InterestRate",        0.0850),     # rate spike to 8.5%
        ],
        note="2026-Q1 — CORRA spike to 8.5%",
    )

    _write_submission(
        ONEIDA / "q1-upside.xlsx",
        "Actuals_2026Q1",
        [
            ("CapacityPayment_Q1",  7_500_000),
            ("ArbitrageRevenue_Q1", 2_400_000),    # exceptional spread quarter
            ("Opex_Q1",             1_280_000),
            ("InterestRate",        0.0610),
        ],
        note="2026-Q1 — exceptional spreads + cost discipline",
    )

    _write_submission(
        ONEIDA / "q1-mislabeled.xlsx",
        "Actuals_2026Q1",
        [
            ("CapacityRevenue_Q1",  7_500_000),  # WRONG label
            ("Arbitrage_Q1",        1_350_000),  # WRONG label
            ("Opex_Q1",             1_310_000),
            ("InterestRate",        0.0625),
        ],
        note="2026-Q1 — WRONG labels for capacity and arbitrage; tests handler",
    )

    _write_submission(
        ONEIDA / "q2-clean.xlsx",
        "Actuals_2026Q2",
        [
            ("CapacityPayment_Q2",  7_500_000),
            ("ArbitrageRevenue_Q2", 1_700_000),    # higher spreads in Q2
            ("Opex_Q2",             1_320_000),
            ("InterestRate",        0.0630),
        ],
        note="2026-Q2 — clean roll-forward",
    )


def main() -> None:
    print("• Building Highway 407 scenarios…")
    build_h407_scenarios()
    for p in sorted(H407.glob("*.xlsx")):
        print(f"   ✓ {p.relative_to(ROOT)}")

    print("• Building Oneida scenarios…")
    build_oneida_scenarios()
    for p in sorted(ONEIDA.glob("*.xlsx")):
        print(f"   ✓ {p.relative_to(ROOT)}")

    print("\nDone. Try:")
    print("  fmcli update highway-407-east-extension data/deals/highway-407-east-extension/inputs/scenarios/q1-stress-rev.xlsx")
    print("  fmcli covenant highway-407-east-extension")


if __name__ == "__main__":
    main()
