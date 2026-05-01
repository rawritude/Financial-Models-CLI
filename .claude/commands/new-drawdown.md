---
description: Process a new drawdown request end-to-end — verify availability, snapshot, record the drawdown, recompute outputs, and draft the drawdown confirmation notice.
argument-hint: <deal_id> --amount <amount>
---

Process a new drawdown for: `$ARGUMENTS`

Use the **deal-orchestrator** agent. Follow the `new-drawdown` skill exactly.

1. Confirm the requested amount is ≤ AvailableCommitment (`fmcli extract`).
2. If amount is feasible, take a `pre-drawdown` snapshot.
3. Build a small inputs `.xlsx` with the drawdown row, save it to
   `data/deals/<deal>/inputs/`. Use the `model-updater` to apply.
4. Recompute outputs and run covenants.
5. Draft `drawdown-confirmation` with `--amount`.
6. Return a one-paragraph summary:
   - Amount drawn (CAD).
   - New debt balance, new available commitment.
   - Updated DSCR, LLCR.
   - Path to the DRAFT confirmation notice.

If AvailableCommitment is insufficient, **do not** proceed. Report the
shortfall and stop.
