---
name: update-model
description: Propagate a borrower-submitted spreadsheet into a deal's project finance model, with auto-snapshot, formula recalc, and audit logging. Use when a borrower has sent in actuals or a forecast update and the model needs to absorb them.
---

# Update model from borrower submission

## When to use

- Quarterly / monthly monitoring submission has arrived from the borrower.
- Borrower issued a revised forecast (e.g. opex update, traffic forecast).
- Pre-funding update: refreshed inputs ahead of a drawdown.

## Inputs

- `deal_id` — folder name in `data/deals/`.
- `submission` — path to the borrower's `.xlsx`. Conventional location:
  `data/deals/<deal_id>/inputs/<filename>.xlsx`.
- Optional `--sheet <name>` — if the submission has multiple tabs.

## Steps

1. **Orient.**
   ```
   fmcli show <deal_id>
   fmcli inspect <path-to-submission>
   ```

2. **Dry-run first.** Always.
   ```
   fmcli update <deal_id> <submission> --dry-run
   ```
   Confirm:
   - Cells to be written look right.
   - "Unmatched labels" list is empty (or each unmatched label is genuinely
     ignorable — clarify with the user before continuing).

3. **Apply.**
   ```
   fmcli update <deal_id> <submission>
   ```
   The CLI will:
   - Snapshot the model into `.backups/`.
   - Write each mapped input cell.
   - Run a headless LibreOffice recalc to refresh cached output values.
   - Append a `model.update` row to `audit.log` recording before/after.

4. **Verify.**
   ```
   fmcli extract <deal_id>
   fmcli covenant <deal_id>
   ```

## Failure modes

- **No labels match `input_map`.** Stop. Either the submission is for the
  wrong deal, or the schema has drifted. Don't edit `deal.yaml` to "fix" it
  without authorization — drift is a signal.
- **Recalc warning.** LibreOffice failed to recompute. The writes succeeded,
  but `extract` will return stale values. Either install LibreOffice or open
  the file once in Excel/Calc to force a recalc, then re-run extract.
- **Restore needed.** `fmcli backups <deal_id>` lists snapshots;
  `fmcli restore <deal_id> <snapshot_name>` rolls back (and itself takes a
  pre-restore snapshot).
