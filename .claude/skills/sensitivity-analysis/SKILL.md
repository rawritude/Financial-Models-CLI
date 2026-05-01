---
name: sensitivity-analysis
description: Run a one-at-a-time sensitivity on a deal model — shock revenue, opex, interest rate, inflation, etc., and see the impact on DSCR / LLCR / debt balance. Use for credit-committee what-ifs, downside scenarios, or annual review stress tests.
---

# Sensitivity analysis (one-at-a-time)

## When to use

- Credit committee wants downside scenarios.
- Annual review stress tests.
- Pre-approval for an amendment that changes input assumptions.

## Steps

1. **List the inputs you can shock.** They're the keys of `deal.input_map`
   in `deal.yaml`. Common ones:
   - `Revenue_*` — period revenue (toll, energy, availability payment)
   - `Opex_*` — period operating expense
   - `InterestRate` — applicable rate
   - `Inflation` — CPI assumption

2. **Choose the shocks.** Three operations:
   - `mul:<factor>` — multiply current value (e.g. `mul:0.90` for −10%).
   - `delta:<amount>` — add to current value.
   - `abs:<value>` — set to absolute value.

3. **Run.** The CLI snapshots first, restores after every shock, and again
   at the end:
   ```
   fmcli sensitivity <deal_id> \
     --shock "Revenue_Q1:mul:0.90" \
     --shock "Revenue_Q1:mul:0.80" \
     --shock "InterestRate:abs:0.075" \
     --shock "Opex_Q1:mul:1.10"
   ```

4. **Report.** Table the result: scenario · DSCR · LLCR · DebtBalance · Δ.
   For each shock that breaks a covenant, call out which one and by how much.

## Example output (for the deck)

| Scenario | DSCR | LLCR | DSRA |
|---|---|---|---|
| Base | 1.42x | 1.55x | CAD 18.4M |
| Revenue −10% | 1.28x | 1.45x | CAD 18.4M |
| Revenue −20% | 1.14x ⚠ breach | 1.32x | CAD 16.1M |
| Rate to 7.5% | 1.31x | 1.42x | CAD 18.4M |
| Opex +10% | 1.36x | 1.51x | CAD 18.4M |

## Safety

- The CLI restores the baseline after every shock and at the end.
- If you suspect the baseline drifted, run:
  ```
  fmcli backups <deal_id>
  fmcli restore <deal_id> <pre-sensitivity snapshot>
  ```
