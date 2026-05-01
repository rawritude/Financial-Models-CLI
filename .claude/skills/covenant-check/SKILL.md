---
name: covenant-check
description: Run all covenant tests for a deal against the current model state and classify each as PASS / WATCH / BREACH. Use after any model update, ahead of a drawdown, before a period close, or whenever a credit officer asks "where do we stand?".
---

# Covenant check

## When to use

- After every `update-model` run.
- Before approving a drawdown.
- Before drafting a `quarterly-monitoring` notice.
- Ad-hoc, when credit/risk asks for current standing.

## Steps

1. **Run the tests.**
   ```
   fmcli covenant <deal_id>
   ```
   Output shows actual vs threshold and a coloured verdict.

2. **Classify each result:**
   - `PASS` — green light, > 10% headroom.
   - `WATCH` — passes but within 10% of threshold. Not a breach, but the
     deal is heading there. Surface this — don't bury it.
   - `BREACH` — the test failed. Lead with this in any summary.

3. **If any BREACH, escalate immediately:**
   - Append a note to the audit trail (the CLI does this for the test itself).
   - Hand off to `draft-notice` with template `covenant-breach-notice`.
   - Recommend the user check the facility-agreement cure provisions —
     this repo doesn't track cure periods.

## Reading the deal's covenants

`deal.yaml` declares them. Each covenant has:

```yaml
- name: DSCR Lock-up
  description: Distribution lock-up if DSCR < 1.20x
  output: DSCR
  operator: ">="
  threshold: 1.20
  severity: breach
  tested_periods: current
```

The `output` value must match a key in the deal's `outputs` map.

## Exit codes

`fmcli covenant` exits 0 on all-pass-or-watch, 2 on any breach. Useful in CI
or scheduled checks.
