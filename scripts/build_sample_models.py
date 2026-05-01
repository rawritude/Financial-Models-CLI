"""Build the two sample project-finance workbooks shipped with this repo.

This is a one-shot generator. Run it any time you want to rebuild the demo
models:

    python3 scripts/build_sample_models.py

It writes:
    data/deals/highway-407-east-extension/model.xlsx
    data/deals/oneida-energy-storage/model.xlsx
    data/inputs/h407-2026-q1-actuals.xlsx
    data/inputs/oneida-2026-q1-actuals.xlsx

The structure is deliberately simplified compared to a real project-finance
model — eight quarterly columns of operations, single-tranche senior debt,
no swap/inflation overlays — but the named output cells and input map are
representative enough to demo the agent workflow end-to-end.
"""

from __future__ import annotations

import sys
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook import Workbook

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fmcli import compute  # noqa: E402
from fmcli.deal import load_deal  # noqa: E402


# ---------------------------------------------------------------------------
# styling helpers
# ---------------------------------------------------------------------------

HEADER_FILL = PatternFill("solid", fgColor="1F3864")  # dark blue
HEADER_FONT = Font(bold=True, color="FFFFFF")
SECTION_FILL = PatternFill("solid", fgColor="D9E1F2")
SECTION_FONT = Font(bold=True, color="1F3864")
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")  # pale yellow = input
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
MONEY_FMT = '_($* #,##0_);_($* (#,##0);_($* "-"_);_(@_)'
RATIO_FMT = '0.00"x"'
PCT_FMT = '0.00%'


def header_row(ws, row, values, start_col=1):
    for i, v in enumerate(values):
        c = ws.cell(row=row, column=start_col + i, value=v)
        c.fill = HEADER_FILL
        c.font = HEADER_FONT
        c.alignment = Alignment(horizontal="center", vertical="center")


def section(ws, row, label, span=10):
    c = ws.cell(row=row, column=1, value=label)
    c.fill = SECTION_FILL
    c.font = SECTION_FONT
    for col in range(2, 2 + span):
        ws.cell(row=row, column=col).fill = SECTION_FILL


def widen(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ---------------------------------------------------------------------------
# Highway 407 East Extension — Availability-payment P3
# ---------------------------------------------------------------------------

def build_highway_407(path: Path) -> None:
    """Build a simplified availability-payment P3 monitoring model.

    Eight quarterly columns of operations (2026-Q1 .. 2027-Q4).
    Senior debt: CAD 480M, 25y tenor, level annual amortization profile.
    Revenue: quarterly availability payment from the Province.
    Opex: lifecycle + routine.
    """
    wb = Workbook()

    # ------------------------------------------------------------------
    # Cover sheet
    # ------------------------------------------------------------------
    cover = wb.active
    cover.title = "Cover"
    widen(cover, [40, 30])
    cover["A1"] = "Highway 407 East Extension — Senior Debt Monitoring Model"
    cover["A1"].font = Font(bold=True, size=14, color="1F3864")
    cover.merge_cells("A1:D1")

    info = [
        ("Project", "Highway 407 East Extension"),
        ("Borrower", "407 East ProjectCo Ltd."),
        ("Sector", "Transportation — P3"),
        ("Facility", "Senior secured term loan, fully amortizing"),
        ("Currency", "CAD"),
        ("Commitment", 480_000_000),
        ("Closing date", "2024-12-15"),
        ("Maturity", "2049-12-15"),
        ("Reference rate", "3M CORRA + 185 bps"),
        ("Model period", "Quarterly, 2026-Q1 .. 2027-Q4 (operations)"),
        ("Concession structure", "Availability-payment from the Province of Ontario"),
    ]
    for i, (k, v) in enumerate(info, start=3):
        cover.cell(row=i, column=1, value=k).font = Font(bold=True)
        c = cover.cell(row=i, column=2, value=v)
        if isinstance(v, (int, float)):
            c.number_format = MONEY_FMT

    # ------------------------------------------------------------------
    # Inputs sheet
    # ------------------------------------------------------------------
    ip = wb.create_sheet("Inputs")
    widen(ip, [38, 16, 16, 16, 16, 16, 16, 16, 16])

    periods = ["2026-Q1", "2026-Q2", "2026-Q3", "2026-Q4",
               "2027-Q1", "2027-Q2", "2027-Q3", "2027-Q4"]
    header_row(ip, 1, ["Input", *periods])

    # Availability payment: ~CAD 70M annually, quarterly = 17.5M, slight CPI
    # Toll-credit / O&M deduction baked in: net AP ~16.5M/quarter rising 1%/q
    ap = [16_500_000, 16_665_000, 16_831_650, 17_000_000,
          17_170_000, 17_341_700, 17_515_000, 17_690_000]
    opex = [3_900_000, 3_950_000, 4_010_000, 4_080_000,
            4_120_000, 4_160_000, 4_210_000, 4_270_000]

    rows = [
        ("AvailabilityPayment_Q1", ap[0]),
        ("AvailabilityPayment_Q2", ap[1]),
        ("AvailabilityPayment_Q3", ap[2]),
        ("AvailabilityPayment_Q4", ap[3]),
        ("AvailabilityPayment_Q5", ap[4]),
        ("AvailabilityPayment_Q6", ap[5]),
        ("AvailabilityPayment_Q7", ap[6]),
        ("AvailabilityPayment_Q8", ap[7]),
        ("Opex_Q1", opex[0]),
        ("Opex_Q2", opex[1]),
        ("Opex_Q3", opex[2]),
        ("Opex_Q4", opex[3]),
        ("Opex_Q5", opex[4]),
        ("Opex_Q6", opex[5]),
        ("Opex_Q7", opex[6]),
        ("Opex_Q8", opex[7]),
        ("InterestRate", 0.0525),
        ("InflationIndex", 0.025),
        ("DSRA_Target", 18_400_000),
        ("DSRA_Balance", 18_400_000),
    ]
    for i, (label, value) in enumerate(rows, start=2):
        c1 = ip.cell(row=i, column=1, value=label)
        c1.font = Font(bold=True)
        c2 = ip.cell(row=i, column=2, value=value)
        c2.fill = INPUT_FILL
        c2.number_format = MONEY_FMT if isinstance(value, (int, float)) and value > 1 else PCT_FMT

    # ------------------------------------------------------------------
    # DebtSchedule sheet
    # ------------------------------------------------------------------
    ds = wb.create_sheet("DebtSchedule")
    widen(ds, [38, 16, 16, 16, 16, 16, 16, 16, 16])
    header_row(ds, 1, ["Item", *periods])

    # Opening balance Q1 = 432M (fully drawn 480M, two years of amortization
    # already paid down through closing -> 2026-Q1).
    opening_q1 = 432_000_000
    # Quarterly amortization: ~CAD 4.5M
    amort = 4_500_000

    def write_row(row, label, formula_fn, fmt=MONEY_FMT):
        ds.cell(row=row, column=1, value=label).font = Font(bold=True)
        for q in range(8):
            col = q + 2
            ds.cell(row=row, column=col, value=formula_fn(q)).number_format = fmt

    # Opening balance row
    write_row(2, "OpeningBalance",
              lambda q: opening_q1 if q == 0 else f"={get_column_letter(q+1)}5")

    # Scheduled amortization
    write_row(3, "Amortization", lambda q: amort)

    # Interest expense = OpeningBalance * Rate / 4
    write_row(4, "Interest",
              lambda q: f"={get_column_letter(q+2)}2*Inputs!$B$18/4")

    # Closing balance = Opening - Amortization
    write_row(5, "ClosingBalance",
              lambda q: f"={get_column_letter(q+2)}2-{get_column_letter(q+2)}3")

    # Debt service = Interest + Amortization
    write_row(6, "DebtService",
              lambda q: f"={get_column_letter(q+2)}3+{get_column_letter(q+2)}4")

    # ------------------------------------------------------------------
    # CashFlow sheet
    # ------------------------------------------------------------------
    cf = wb.create_sheet("CashFlow")
    widen(cf, [38, 16, 16, 16, 16, 16, 16, 16, 16])
    header_row(cf, 1, ["Item", *periods])

    write_row_cf = lambda r, l, fn, fmt=MONEY_FMT: (
        cf.cell(row=r, column=1, value=l).__setattr__("font", Font(bold=True)),
        [
            cf.cell(row=r, column=q + 2, value=fn(q)).__setattr__("number_format", fmt)
            for q in range(8)
        ],
    )
    # Revenue (=AvailabilityPayment from Inputs row 2..9)
    cf.cell(row=2, column=1, value="Revenue (AP)").font = Font(bold=True)
    for q in range(8):
        cf.cell(row=2, column=q + 2, value=f"=Inputs!{get_column_letter(q + 2)}2").number_format = MONEY_FMT

    # Opex (rows 10..17 in Inputs)
    cf.cell(row=3, column=1, value="Opex").font = Font(bold=True)
    for q in range(8):
        cf.cell(row=3, column=q + 2, value=f"=Inputs!{get_column_letter(q + 2)}10").number_format = MONEY_FMT

    # CFADS = Revenue - Opex
    cf.cell(row=4, column=1, value="CFADS").font = Font(bold=True)
    for q in range(8):
        cf.cell(row=4, column=q + 2, value=f"={get_column_letter(q + 2)}2-{get_column_letter(q + 2)}3").number_format = MONEY_FMT

    # Debt Service (from DebtSchedule!row 6)
    cf.cell(row=5, column=1, value="DebtService").font = Font(bold=True)
    for q in range(8):
        cf.cell(row=5, column=q + 2, value=f"=DebtSchedule!{get_column_letter(q + 2)}6").number_format = MONEY_FMT

    # DSCR = CFADS / DebtService
    cf.cell(row=6, column=1, value="DSCR").font = Font(bold=True)
    for q in range(8):
        cf.cell(row=6, column=q + 2, value=f"={get_column_letter(q + 2)}4/{get_column_letter(q + 2)}5").number_format = RATIO_FMT

    # ------------------------------------------------------------------
    # Outputs sheet
    # ------------------------------------------------------------------
    out = wb.create_sheet("Outputs")
    widen(out, [38, 22])
    header_row(out, 1, ["Output", "Value"])

    out.cell(row=2, column=1, value="Period under test").font = Font(bold=True)
    out.cell(row=2, column=2, value="2026-Q1")

    # Period DSCR (current quarter = column 2 in CashFlow row 6)
    rows_o = [
        ("DSCR (current period)", "=CashFlow!B6", RATIO_FMT),
        ("Min DSCR (forecast 8q)", "=MIN(CashFlow!B6:I6)", RATIO_FMT),
        ("LLCR (NPV CFADS / DebtBalance)",
         "=SUMPRODUCT(CashFlow!B4:I4,1/(1+Inputs!$B$18/4)^(ROW(INDIRECT(\"1:8\"))))/DebtSchedule!B2",
         RATIO_FMT),
        ("Outstanding senior debt", "=DebtSchedule!B5", MONEY_FMT),
        ("DSRA balance", "=Inputs!B21", MONEY_FMT),
        ("DSRA target", "=Inputs!B20", MONEY_FMT),
        ("Available commitment", 0, MONEY_FMT),
        ("Quarterly debt service (current)", "=DebtSchedule!B6", MONEY_FMT),
        ("Quarterly CFADS (current)", "=CashFlow!B4", MONEY_FMT),
    ]
    for i, (lbl, val, fmt) in enumerate(rows_o, start=3):
        out.cell(row=i, column=1, value=lbl).font = Font(bold=True)
        c = out.cell(row=i, column=2, value=val)
        c.number_format = fmt

    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


# ---------------------------------------------------------------------------
# Oneida Energy Storage — battery storage senior debt
# ---------------------------------------------------------------------------

def build_oneida(path: Path) -> None:
    """Build a simplified battery-storage senior-debt model.

    250 MW / 1000 MWh battery storage facility. Senior debt CAD 170M, fully
    drawn at close. Revenue from capacity payments + arbitrage.
    """
    wb = Workbook()

    cover = wb.active
    cover.title = "Cover"
    widen(cover, [40, 30])
    cover["A1"] = "Oneida Energy Storage — Senior Debt Monitoring Model"
    cover["A1"].font = Font(bold=True, size=14, color="1F3864")
    cover.merge_cells("A1:D1")
    info = [
        ("Project", "Oneida Energy Storage Facility"),
        ("Borrower", "Oneida Energy Storage LP"),
        ("Sector", "Clean power — battery storage"),
        ("Facility", "Senior secured term loan, project finance"),
        ("Currency", "CAD"),
        ("Commitment", 170_000_000),
        ("Closing date", "2024-03-28"),
        ("Maturity", "2042-03-28"),
        ("Reference rate", "3M CORRA + 215 bps"),
        ("Capacity / energy", "250 MW / 1000 MWh, 4-hr duration"),
        ("Revenue structure", "20-yr Capacity Services Agreement + arbitrage"),
    ]
    for i, (k, v) in enumerate(info, start=3):
        cover.cell(row=i, column=1, value=k).font = Font(bold=True)
        c = cover.cell(row=i, column=2, value=v)
        if isinstance(v, (int, float)):
            c.number_format = MONEY_FMT

    ip = wb.create_sheet("Inputs")
    widen(ip, [38, 16, 16, 16, 16, 16, 16, 16, 16])
    periods = ["2026-Q1", "2026-Q2", "2026-Q3", "2026-Q4",
               "2027-Q1", "2027-Q2", "2027-Q3", "2027-Q4"]
    header_row(ip, 1, ["Input", *periods])

    cap = [7_500_000, 7_500_000, 7_500_000, 7_500_000,
           7_650_000, 7_650_000, 7_650_000, 7_650_000]
    arb = [1_400_000, 1_650_000, 2_100_000, 1_900_000,
           1_500_000, 1_750_000, 2_200_000, 1_950_000]
    opex = [1_300_000, 1_300_000, 1_330_000, 1_330_000,
            1_360_000, 1_360_000, 1_390_000, 1_390_000]

    rows: list[tuple[str, float | int]] = []
    for i, p in enumerate(periods):
        rows.append((f"CapacityPayment_Q{i+1}", cap[i]))
    for i in range(8):
        rows.append((f"ArbitrageRevenue_Q{i+1}", arb[i]))
    for i in range(8):
        rows.append((f"Opex_Q{i+1}", opex[i]))
    rows += [
        ("InterestRate", 0.0625),
        ("DSRA_Target", 6_500_000),
        ("DSRA_Balance", 6_500_000),
    ]
    for i, (label, value) in enumerate(rows, start=2):
        c1 = ip.cell(row=i, column=1, value=label)
        c1.font = Font(bold=True)
        c2 = ip.cell(row=i, column=2, value=value)
        c2.fill = INPUT_FILL
        c2.number_format = MONEY_FMT if isinstance(value, (int, float)) and value > 1 else PCT_FMT

    ds = wb.create_sheet("DebtSchedule")
    widen(ds, [38, 16, 16, 16, 16, 16, 16, 16, 16])
    header_row(ds, 1, ["Item", *periods])
    opening_q1 = 162_000_000
    amort = 2_350_000

    ds.cell(row=2, column=1, value="OpeningBalance").font = Font(bold=True)
    for q in range(8):
        col = q + 2
        if q == 0:
            ds.cell(row=2, column=col, value=opening_q1).number_format = MONEY_FMT
        else:
            ds.cell(row=2, column=col, value=f"={get_column_letter(q+1)}5").number_format = MONEY_FMT

    ds.cell(row=3, column=1, value="Amortization").font = Font(bold=True)
    for q in range(8):
        ds.cell(row=3, column=q+2, value=amort).number_format = MONEY_FMT

    ds.cell(row=4, column=1, value="Interest").font = Font(bold=True)
    for q in range(8):
        ds.cell(row=4, column=q+2, value=f"={get_column_letter(q+2)}2*Inputs!$B$26/4").number_format = MONEY_FMT

    ds.cell(row=5, column=1, value="ClosingBalance").font = Font(bold=True)
    for q in range(8):
        ds.cell(row=5, column=q+2, value=f"={get_column_letter(q+2)}2-{get_column_letter(q+2)}3").number_format = MONEY_FMT

    ds.cell(row=6, column=1, value="DebtService").font = Font(bold=True)
    for q in range(8):
        ds.cell(row=6, column=q+2, value=f"={get_column_letter(q+2)}3+{get_column_letter(q+2)}4").number_format = MONEY_FMT

    cf = wb.create_sheet("CashFlow")
    widen(cf, [38, 16, 16, 16, 16, 16, 16, 16, 16])
    header_row(cf, 1, ["Item", *periods])

    cf.cell(row=2, column=1, value="Capacity revenue").font = Font(bold=True)
    for q in range(8):
        cf.cell(row=2, column=q+2, value=f"=Inputs!{get_column_letter(q+2)}2").number_format = MONEY_FMT

    cf.cell(row=3, column=1, value="Arbitrage revenue").font = Font(bold=True)
    for q in range(8):
        cf.cell(row=3, column=q+2, value=f"=Inputs!{get_column_letter(q+2)}10").number_format = MONEY_FMT

    cf.cell(row=4, column=1, value="Opex").font = Font(bold=True)
    for q in range(8):
        cf.cell(row=4, column=q+2, value=f"=Inputs!{get_column_letter(q+2)}18").number_format = MONEY_FMT

    cf.cell(row=5, column=1, value="CFADS").font = Font(bold=True)
    for q in range(8):
        cf.cell(row=5, column=q+2, value=f"={get_column_letter(q+2)}2+{get_column_letter(q+2)}3-{get_column_letter(q+2)}4").number_format = MONEY_FMT

    cf.cell(row=6, column=1, value="DebtService").font = Font(bold=True)
    for q in range(8):
        cf.cell(row=6, column=q+2, value=f"=DebtSchedule!{get_column_letter(q+2)}6").number_format = MONEY_FMT

    cf.cell(row=7, column=1, value="DSCR").font = Font(bold=True)
    for q in range(8):
        cf.cell(row=7, column=q+2, value=f"={get_column_letter(q+2)}5/{get_column_letter(q+2)}6").number_format = RATIO_FMT

    out = wb.create_sheet("Outputs")
    widen(out, [38, 22])
    header_row(out, 1, ["Output", "Value"])
    out.cell(row=2, column=1, value="Period under test").font = Font(bold=True)
    out.cell(row=2, column=2, value="2026-Q1")
    rows_o = [
        ("DSCR (current period)", "=CashFlow!B7", RATIO_FMT),
        ("Min DSCR (forecast 8q)", "=MIN(CashFlow!B7:I7)", RATIO_FMT),
        ("LLCR (NPV CFADS / DebtBalance)",
         "=SUMPRODUCT(CashFlow!B5:I5,1/(1+Inputs!$B$26/4)^(ROW(INDIRECT(\"1:8\"))))/DebtSchedule!B2",
         RATIO_FMT),
        ("Outstanding senior debt", "=DebtSchedule!B5", MONEY_FMT),
        ("DSRA balance", "=Inputs!B28", MONEY_FMT),
        ("DSRA target", "=Inputs!B27", MONEY_FMT),
        ("Available commitment", 0, MONEY_FMT),
        ("Quarterly debt service (current)", "=DebtSchedule!B6", MONEY_FMT),
        ("Quarterly CFADS (current)", "=CashFlow!B5", MONEY_FMT),
    ]
    for i, (lbl, val, fmt) in enumerate(rows_o, start=3):
        out.cell(row=i, column=1, value=lbl).font = Font(bold=True)
        c = out.cell(row=i, column=2, value=val)
        c.number_format = fmt

    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


# ---------------------------------------------------------------------------
# Borrower submissions (the "actuals" workbooks)
# ---------------------------------------------------------------------------

def build_h407_actuals(path: Path) -> None:
    """A two-column borrower submission for Highway 407, 2026-Q1.

    Schema: column A = label, column B = value. The labels match
    deal.input_map keys so `fmcli update` finds the right cells.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Actuals_2026Q1"
    widen(ws, [40, 22])
    header_row(ws, 1, ["Label", "Value"])

    rows = [
        ("AvailabilityPayment_Q1", 16_350_000),  # ~1% lower than forecast (deduction)
        ("Opex_Q1", 4_120_000),                  # opex came in a touch high
        ("InterestRate", 0.0540),                # +15bps reset
    ]
    for i, (label, value) in enumerate(rows, start=2):
        ws.cell(row=i, column=1, value=label).font = Font(bold=True)
        c = ws.cell(row=i, column=2, value=value)
        c.number_format = MONEY_FMT if value > 1 else PCT_FMT

    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def build_oneida_actuals(path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Actuals_2026Q1"
    widen(ws, [40, 22])
    header_row(ws, 1, ["Label", "Value"])

    rows = [
        ("CapacityPayment_Q1", 7_500_000),     # on plan
        ("ArbitrageRevenue_Q1", 1_180_000),    # softer than forecast
        ("Opex_Q1", 1_350_000),                # slightly elevated
        ("InterestRate", 0.0640),              # +15bps reset
    ]
    for i, (label, value) in enumerate(rows, start=2):
        ws.cell(row=i, column=1, value=label).font = Font(bold=True)
        c = ws.cell(row=i, column=2, value=value)
        c.number_format = MONEY_FMT if value > 1 else PCT_FMT

    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def main() -> None:
    h407 = ROOT / "data" / "deals" / "highway-407-east-extension" / "model.xlsx"
    oneida = ROOT / "data" / "deals" / "oneida-energy-storage" / "model.xlsx"
    h407_act = ROOT / "data" / "deals" / "highway-407-east-extension" / "inputs" / "h407-2026-q1-actuals.xlsx"
    oneida_act = ROOT / "data" / "deals" / "oneida-energy-storage" / "inputs" / "oneida-2026-q1-actuals.xlsx"

    print("• Building Highway 407 East Extension model …")
    build_highway_407(h407)

    print("• Building Oneida Energy Storage model …")
    build_oneida(oneida)

    print("• Building borrower submissions …")
    build_h407_actuals(h407_act)
    build_oneida_actuals(oneida_act)

    print("• Recomputing model outputs via fmcli.compute …")
    for deal_id in ("highway-407-east-extension", "oneida-energy-storage"):
        deal = load_deal(deal_id)
        report = compute.recompute(deal)
        print(f"   ✓ {deal_id}: method={report.method}, outputs="
              + ", ".join(f"{k}={v:,.4g}" for k, v in report.output_writes.items()))

    print("\nDone. Try:  fmcli list   then   fmcli show highway-407-east-extension")


if __name__ == "__main__":
    main()
