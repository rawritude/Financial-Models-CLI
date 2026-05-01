---
name: annual-review
description: Prepare an annual credit review pack for a deal — refresh the model, run a multi-scenario sensitivity, summarize covenant trends, and draft the annual review letter. Use once a year per deal, or when the credit committee schedules an out-of-cycle review.
---

# Annual credit review

## When to use

- Annual review date for the deal (track in `deal.yaml > notes`).
- Out-of-cycle review triggered by a covenant watch, a sector event, or a
  rating change at the borrower.

## Pack contents

By the end of this skill, the deal's `outputs/` should contain:

1. `DRAFT_<date>_annual-review-letter.md` — borrower-facing cover letter.
2. `DRAFT_<date>_annual-review-internal.md` — credit-committee memo.
3. A sensitivity table (paste into chat or save to a CSV in `outputs/`).

## Steps

1. **Snapshot.**
   ```
   fmcli backup <deal_id> --reason annual-review-<year>
   ```

2. **Refresh the model.** If the borrower has submitted updated actuals,
   run `update-model`. Otherwise note in the audit log that the review uses
   the prior period's data:
   ```bash
   python3 -c "from fmcli import audit; audit.append('<deal>', 'review.basis', {'note': 'using <YYYY-MM-DD> actuals'})"
   ```

3. **Pull headline figures.**
   ```
   fmcli extract <deal_id>
   ```

4. **Covenant test.**
   ```
   fmcli covenant <deal_id>
   ```

5. **Trend.** Walk back through the audit log:
   ```
   fmcli audit <deal_id> --limit 100
   ```
   Compile period-over-period DSCR and debt-balance series. Mention the
   trajectory in the internal memo.

6. **Stress.** Run a multi-shock sensitivity:
   ```
   fmcli sensitivity <deal_id> \
     --shock "Revenue_*:mul:0.90" \
     --shock "Revenue_*:mul:0.80" \
     --shock "InterestRate:delta:0.01" \
     --shock "Opex_*:mul:1.10"
   ```
   (Replace `Revenue_*` with the actual input names from `deal.input_map`.)

7. **Draft the borrower letter.**
   ```
   fmcli notice <deal_id> annual-review-letter
   ```

8. **Draft the internal memo.** Use the credit-officer summary format from
   the `quarterly-monitoring` skill, expanded with the trend and stress
   sections.

## Review opinion

End every annual review with one of:
- **Maintain** — no rating action recommended.
- **Watch** — flag for closer monitoring; tighter reporting cadence.
- **Downgrade / restructure** — escalate to credit committee; outside scope.
