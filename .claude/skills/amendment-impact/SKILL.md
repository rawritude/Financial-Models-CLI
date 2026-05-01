---
name: amendment-impact
description: Quantify the impact of a proposed facility amendment (rate change, tenor extension, covenant reset, repayment-schedule change) on the deal's outputs and covenants — without permanently altering the model. Use when credit is evaluating an amendment request.
---

# Amendment impact analysis

## When to use

- Borrower has requested a facility amendment.
- Credit committee needs the "what changes" quantified before approving.
- Legal needs the figures for the amendment letter.

## Approach

The amendment is evaluated as a temporary scenario. The model is snapshotted,
shocked with the proposed change, recomputed, and then **restored** to
baseline. No permanent change to the canonical model unless the amendment is
later approved and applied as a normal `update-model` cycle.

## Steps

1. **Snapshot with a meaningful tag.**
   ```
   fmcli backup <deal_id> --reason pre-amendment-<short-name>
   ```

2. **Identify the affected inputs.** Examples:
   - Rate change → `InterestRate`
   - Tenor extension → `MaturityYears` or per-period repayment cells
   - Covenant reset → handled in `deal.yaml`, not the workbook (separate flow)
   - Repayment holiday → a cluster of period repayment cells

3. **Apply the shock(s) using the sensitivity helper:**
   ```
   fmcli sensitivity <deal_id> \
     --shock "InterestRate:abs:0.06" \
     --shock "Repayment_Q3_2026:abs:0"
   ```
   The sensitivity flow will restore baseline after each shock; for an
   amendment you usually want all shocks active simultaneously, in which
   case use `update-model` with a synthetic submission file and **explicitly
   restore at the end:**

   ```bash
   # Build a synthetic inputs file (analyst, not the agent)
   fmcli update <deal_id> /tmp/amendment-scenario.xlsx
   fmcli extract <deal_id>
   fmcli covenant <deal_id>
   fmcli restore <deal_id> <pre-amendment snapshot name>
   ```

4. **Tabulate the result.**
   - Output deltas: DSCR, LLCR, MinDSCRForecast, weighted-average life.
   - Covenant impact: any new breaches? any new watches?
   - Effective interest cost: present-value the change.

5. **Restore the baseline before closing the analysis.** Confirm restoration:
   ```
   fmcli reconcile <deal_id> data/deals/<deal_id>/.backups/<pre-amendment>.xlsx
   # all deltas should be 0
   ```

6. **Hand back a one-page summary** with the impact table, breach flags,
   and the restoration confirmation.

## Output format

```
Amendment · <short name> · <deal_id>
Proposed change: <one line>

Output impact:
  DSCR      1.42x → 1.31x   (−0.11x)
  LLCR      1.55x → 1.48x   (−0.07x)
  Min DSCR  1.28x → 1.18x   (now below 1.20x lock-up forecast)

Covenant impact:
  • DSCR Lock-up: forecast WATCH for Q3-2027 (3 quarters)
  • All other covenants: no change.

Recommendation:
  <neutral, decision-ready statement>

Baseline restored: ✓ (reconcile against pre-amendment snapshot returned all zeros)
```
