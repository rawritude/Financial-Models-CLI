---
name: rate-reset
description: Process a floating-rate reset — capture the new applicable rate (CDOR/CORRA + spread), update the model, recompute interest schedule and DSCR, and draft a rate reset notice to the borrower. Use at every interest period reset for floating-rate facilities.
---

# Rate reset

## When to use

- Floating-rate interest period is about to roll (e.g. quarterly reset).
- Reference rate has changed (CORRA replacing CDOR, etc.) and the deal
  requires a one-off reset.

## Pre-flight

1. Confirm the deal is floating-rate. `deal.yaml > notes` should mention
   the reference rate. If the deal is fixed-rate, this skill does not apply.

2. Capture the new rate. Components:
   - **Reference rate** (e.g. 3-month CORRA, term value).
   - **Spread** (per the facility agreement, fixed at close).
   - **Effective rate** = reference + spread.

## Steps

1. **Snapshot.**
   ```
   fmcli backup <deal_id> --reason rate-reset-<period>
   ```

2. **Update the rate input.** The `InterestRate` (or equivalent) input cell
   should be in `deal.input_map`. Use a small inputs `.xlsx` with one row:
   ```
   InterestRate    0.0625
   ```
   Then:
   ```
   fmcli update <deal_id> /tmp/rate-reset-<period>.xlsx
   ```

3. **Recompute and review.**
   ```
   fmcli extract <deal_id> --outputs InterestExpense,DSCR,LLCR
   ```

4. **Covenant check.** A rate increase can compress DSCR.
   ```
   fmcli covenant <deal_id>
   ```

5. **Draft the rate reset notice.**
   ```
   fmcli notice <deal_id> rate-reset-notice --period <YYYY-Qn>
   ```

## Notice contents (what the template renders)

- Effective date of the reset.
- Reference rate, spread, effective all-in rate.
- Interest period (start / end dates).
- Estimated interest amount for the period.
- Updated DSCR forecast for the period.

## What you don't do

- Don't choose the reference rate. The facility agreement specifies it
  (term, source). Confirm with the agent bank or treasury before applying.
- Don't apply rate caps/floors. If the deal has them, encode them in the
  model itself, not in the input.
