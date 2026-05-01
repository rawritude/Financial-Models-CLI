---
name: quarterly-monitoring
description: Run the full end-of-period monitoring loop for one deal — absorb the borrower's actuals, recompute outputs, test covenants, draft the monitoring report, and produce a credit-officer summary. Use at every quarter or month close.
---

# Quarterly monitoring loop

## When to use

- The borrower has submitted period-end actuals.
- A scheduled monthly/quarterly close is due.

## Steps

1. **Pre-flight snapshot.**
   ```
   fmcli backup <deal_id> --reason pre-Q<n>-close
   ```

2. **Update the model.**
   ```
   fmcli update <deal_id> data/deals/<deal_id>/inputs/<submission>.xlsx
   ```

3. **Extract the headline outputs.**
   ```
   fmcli extract <deal_id>
   ```
   Note period-over-period changes vs the previous monitoring report (find
   the previous notice in `data/deals/<deal_id>/outputs/`).

4. **Run covenants.**
   ```
   fmcli covenant <deal_id>
   ```

5. **Draft the monitoring report.**
   ```
   fmcli notice <deal_id> quarterly-monitoring --period <YYYY-Qn>
   ```

6. **Review the draft.** Replace `§[ref]` placeholders with the correct
   facility-agreement section numbers. Polish the cover paragraph.

7. **Produce a credit-officer summary** (do this in the chat, not in a file):

   ```
   <deal_id> · <period>
   • DSCR: 1.42x (prev 1.38x)  — PASS, 18% above 1.20x lock-up
   • LLCR: 1.55x (prev 1.55x)  — PASS
   • Debt balance: CAD 412.8M  (down CAD 5.2M from scheduled amortization)
   • DSRA: CAD 18.4M (target met)
   • Covenants: 3 PASS, 1 WATCH (DSCR lock-up — within 12%)
   • Action items: confirm Q2 traffic forecast revision with borrower
   ```

## Outputs

After this skill runs, the deal should have:
- One new snapshot in `.backups/`.
- One new `model.update` audit row.
- One new `covenant.test` audit row.
- One DRAFT notice in `outputs/`.
- A credit-officer summary in chat.
