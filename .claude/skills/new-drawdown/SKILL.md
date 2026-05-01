---
name: new-drawdown
description: Process a borrower drawdown request end-to-end — verify availability, snapshot the model, record the drawdown, recompute outputs, and draft a drawdown confirmation notice. Use when a borrower has submitted a drawdown notice or the team is approving a scheduled advance.
---

# Process a new drawdown

## When to use

- Borrower has issued a drawdown notice (typical 3-5 business day lead time).
- Scheduled drawdown per the drawdown schedule comes due.

## Pre-flight

1. **Confirm availability.**
   ```
   fmcli extract <deal_id> --outputs AvailableCommitment,DebtBalance
   ```
   The requested amount must be ≤ AvailableCommitment.

2. **Confirm conditions precedent are satisfied.** This repo doesn't track CPs
   line-by-line; the deal team confirms. Note CP confirmation in the audit:
   ```bash
   python3 -c "from fmcli import audit; audit.append('<deal>', 'cp.confirmed', {'note': 'all CPs satisfied for drawdown'})"
   ```

3. **Snapshot the model with a meaningful tag.**
   ```
   fmcli backup <deal_id> --reason pre-drawdown
   ```

## Apply the drawdown

If the drawdown is recorded as a single input cell (e.g. `Drawdown_Q2_2026`),
construct a small `.xlsx` with that label/value and run `update-model`:

```
fmcli update <deal_id> data/deals/<deal_id>/inputs/<filename>.xlsx
```

If the drawdown is recorded by directly setting a balance, prefer a structured
input file rather than ad-hoc cell writes — this keeps the audit trail clean.

## Post-flight

1. **Re-extract.**
   ```
   fmcli extract <deal_id> --outputs AvailableCommitment,DebtBalance,DSCR,LLCR
   ```

2. **Run covenants.** A drawdown can change DSCR forecasts.
   ```
   fmcli covenant <deal_id>
   ```

3. **Draft confirmation notice.**
   ```
   fmcli notice <deal_id> drawdown-confirmation --amount <amount>
   ```
   Review the draft in `data/deals/<deal_id>/outputs/`. The notice references
   live figures: advance amount, updated balance, undrawn commitment, next
   payment date.

## What you don't do

- Don't approve the drawdown — that's a credit decision.
- Don't send the confirmation — that's a borrower-relations decision.
- Don't bypass the snapshot. If you skip `pre-drawdown`, an erroneous
  drawdown can't be cleanly rolled back.
