---
name: generate-report
description: Generate an internal-facing report — either a per-deal credit committee memo or a portfolio-level investment-committee briefing. Use when the team needs a structured document for internal distribution (Credit Risk, Portfolio Management, Investment Committee), as opposed to a borrower-facing notice.
---

# Generate an internal report

## Two report types

| Report | Audience | Command |
|---|---|---|
| `credit-memo`       | Credit Risk · Portfolio Management · Investment Committee | `fmcli report credit-memo <deal_id>` |
| `portfolio-review`  | Investment Committee — quarterly briefing                  | `fmcli report portfolio` |

External-facing communications (notices to the borrower) use `fmcli notice`,
not `fmcli report`. Reports never leave the bank.

## Deal-level credit memo

```bash
fmcli report credit-memo <deal_id> --period 2026-Q1
```

What it includes:
- Recommendation (Maintain / Watch / Restructure) — placeholder for the
  credit officer to fill in.
- Headline outputs vs prior period (Δ column placeholder).
- Covenant compliance with verdicts.
- Material developments / stress / outlook (analyst free-form sections).
- Last 10 audit events for the deal.

Output: `data/deals/<deal_id>/outputs/INTERNAL_<date>_credit-memo.md`.

The `INTERNAL_` prefix flags the file as not for borrower distribution.

## Portfolio review

```bash
fmcli report portfolio
```

What it includes:
- Snapshot: total committed, sector list, watchlist count, breach count.
- Deal-level KPI table.
- Watchlist (deals with any covenant in WATCH).
- Breaches (deals with any covenant in BREACH).
- Sector concentration table.
- 30-day activity rollup (model updates, covenant tests, notices, backups).

Output: `data/INTERNAL_<date>_portfolio-review.md` (root of the workspace).

## After generation

1. **Read the file back** — verify all placeholder sections are flagged for
   the human to complete (`_credit officer name_`, `_prior_`, etc.).
2. **Hand the path to the user.** Do not finalize, do not paste into Slack
   or email. Internal reports often contain sensitive figures.
3. **If a breach is present in the portfolio review**, lead the conversation
   with that deal — don't bury it in the table.

## What you don't do

- Don't fill in the `Recommendation` section yourself. That's a credit
  decision; the credit officer makes it.
- Don't invent prior-period figures. The Δ column is a placeholder until
  prior-period data is wired up (out of scope for this prototype).
- Don't merge the credit memo and portfolio review into a single document
  — they serve different audiences and approval flows.
