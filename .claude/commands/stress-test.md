---
description: Run a one-at-a-time sensitivity analysis on a deal — revenue down 10/20%, opex up 10%, rate up 100bps — and report covenant impact.
argument-hint: <deal_id>
---

Run a stress test on `$ARGUMENTS`.

1. Inspect the deal's `input_map` to identify the right input names. They
   may be period-specific (e.g. `Revenue_Q1_2026`) or umbrella (`Revenue`).
2. Build a standard CIB stress set:
   - Revenue ×0.90
   - Revenue ×0.80
   - Opex ×1.10
   - InterestRate +100bps (`delta:0.01`)
3. Run:
   ```
   fmcli sensitivity <deal_id> --shock "...:mul:0.90" --shock "...:mul:0.80" --shock "...:mul:1.10" --shock "InterestRate:delta:0.01"
   ```
4. Report the result as a clean Markdown table with columns:
   `scenario | DSCR | LLCR | DSRA | covenant impact`.
5. For each scenario, run a quick covenant test mentally against the
   thresholds in `deal.yaml` and flag any new breaches.
6. Confirm the baseline was restored (`fmcli reconcile <deal>` against the
   pre-sensitivity snapshot).
