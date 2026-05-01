---
description: Run the full monthly/quarterly monitoring loop for one deal — absorb actuals, recompute outputs, test covenants, draft the monitoring notice, and produce a credit-officer summary.
argument-hint: <deal_id> [submission_path]
---

Run the **quarterly-monitoring** workflow for `$ARGUMENTS`.

Use the **deal-orchestrator** agent. The orchestrator will:

1. Verify the deal exists with `fmcli show`.
2. Take a pre-flight snapshot.
3. Find the most recent submission in `data/deals/<deal>/inputs/` (or use
   the path passed as the second argument).
4. Delegate to `model-updater` to absorb the submission.
5. Delegate to `output-extractor` for the headline KPIs.
6. Delegate to `covenant-checker`.
7. Delegate to `notice-drafter` with template `quarterly-monitoring`.
8. Return a credit-officer summary in this format:

   ```
   <deal> · <period>
   • DSCR: x.xxx (prev x.xxx)  — verdict
   • LLCR: x.xxx                — verdict
   • Debt balance / DSRA / Available commitment
   • Covenants: N PASS, N WATCH, N BREACH
   • Action items: ...
   • Draft notice: <path to DRAFT_*.md>
   ```

Stop after the draft is produced. Do not finalize the notice.
