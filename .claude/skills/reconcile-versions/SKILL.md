---
name: reconcile-versions
description: Diff two versions of a deal model (or an analyst's working copy vs the canonical model) and surface unexpected output deltas. Use after a model update to verify expected changes propagated, or to vet an external party's version of the model.
---

# Reconcile versions

## When to use

- Borrower returned a copy of the model with their forecast embedded.
- Analyst built a working copy off-tree; verify it matches before merging.
- Investigate a suspected miscalculation by diffing against a snapshot.

## Steps

1. **Reconcile the live model against an external workbook.**
   ```
   fmcli reconcile <deal_id> path/to/other.xlsx
   ```

2. **Reconcile the live model against a prior snapshot:**
   ```
   fmcli backups <deal_id>           # list snapshot names
   fmcli reconcile <deal_id> data/deals/<deal_id>/.backups/<snapshot>.xlsx
   ```

3. **Read the table.** For each named output: model · other · delta. The
   reconciler does not normalize signs or units — if `Other` reports debt as
   negative and `Model` reports it positive, that's a sign convention
   mismatch the user should flag.

## Materiality threshold

Treat any delta > 1% of the model value as material. Smaller deltas are
typically rounding (the borrower's workbook may use different precision
settings).

## Common findings

- **Period misalignment.** Borrower used a stub period; their DSCR is
  computed over a different window. Confirm period definitions.
- **Sign convention.** Particularly for cash flows. Document the convention
  used in `deal.yaml > notes`.
- **Stale recalc.** If the "other" workbook hasn't been opened in a calc
  engine recently, its cached values are stale. Open and save once.

## What you don't do

- Don't merge the other workbook's values into the model. If the borrower's
  values are correct, ask them for a labeled `inputs` submission and run the
  `update-model` skill instead.
