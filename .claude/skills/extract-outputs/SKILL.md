---
name: extract-outputs
description: Pull live values from a deal model's named output cells (DSCR, LLCR, debt balance, DSRA, available commitment, etc.) with units. Use whenever a workflow needs "the current numbers from the model", or to feed values into a notice/template.
---

# Extract outputs

## When to use

- Before drafting a notice (so figures are fresh).
- Before testing covenants.
- For ad-hoc "what's our current DSCR?" queries.
- As input to a portfolio rollup or comparison.

## Steps

1. **All declared outputs:**
   ```
   fmcli extract <deal_id>
   ```

2. **A subset, by name:**
   ```
   fmcli extract <deal_id> --outputs DSCR,LLCR,DebtBalance,DSRA
   ```

3. **JSON for downstream piping:**
   ```
   fmcli extract <deal_id> --json
   ```

## Reading the result

Each row is `name · cell · value`. The CLI does not re-derive — it reads the
cached value of the cell. If the workbook hasn't been recalculated since the
last input write (LibreOffice failed, or the file was edited externally),
the value will be stale.

To force a recalc:
```
fmcli backup <deal_id> --reason force-recalc
# open the file once in Excel/Calc, then close — or
# re-run the last update with no actual change to trigger recalc
```

## Conventions

- Name outputs in `deal.yaml` so analysts work with names, not coordinates.
  `DSCR` not `Outputs!B14`.
- Standard names this repo expects (where applicable):
  - `DSCR` — Debt Service Coverage Ratio (period)
  - `LLCR` — Loan Life Coverage Ratio (cumulative)
  - `DebtBalance` — outstanding senior debt
  - `DSRA` — Debt Service Reserve Account balance
  - `AvailableCommitment` — undrawn senior commitment
  - `MinDSCRForecast` — minimum forecast DSCR over remaining tenor
- Add deal-specific outputs as needed; document them in `deal.yaml > notes`.
