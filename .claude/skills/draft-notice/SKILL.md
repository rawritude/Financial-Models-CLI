---
name: draft-notice
description: Draft a borrower-facing notice (drawdown confirmation, monitoring report, covenant test certificate, breach letter, rate reset, waiver acknowledgement, annual review letter) using a template and live model figures. Use when an external-facing document is needed.
---

# Draft a borrower notice

## When to use

After any event that triggers a borrower communication: drawdown, period
close, covenant test, rate reset, waiver, annual review.

## Available templates

```
fmcli templates
```

| Template | Trigger |
|---|---|
| `drawdown-confirmation` | Borrower drew down; confirm advance + new balance. |
| `quarterly-monitoring` | End-of-period monitoring report with covenant verdicts. |
| `covenant-breach-notice` | Formal notification of a covenant breach. |
| `interest-payment-notice` | Reminder of an upcoming interest payment. |
| `rate-reset-notice` | Floating-rate refixing for the next interest period. |
| `waiver-acknowledgement` | Confirming a waiver granted by the lender. |
| `annual-review-letter` | Cover letter for annual credit review. |

## Steps

1. **Pull live figures so the template renders against current outputs.**
   ```
   fmcli extract <deal_id>
   ```
   Confirm DSCR / debt balance / DSRA / etc. are non-blank.

2. **Render the draft.**
   ```
   fmcli notice <deal_id> <template> [--amount AMT] [--period 2026-Q1]
   ```
   The CLI writes `data/deals/<deal_id>/outputs/DRAFT_<date>_<template>.md`.

3. **Read it back. Polish prose where the template invites judgment.**
   - Cover paragraph: tighten to 3 sentences.
   - Section headers should use the borrower's deal name.
   - If a field is `—`, do NOT delete the section — surface it to the user.

4. **Hand the path back to the user. Never strip the `DRAFT_` prefix.** The
   user finalizes by renaming the file (or by re-running with `--final` once
   approved).

## Style guide

- Formal tone. No contractions, no marketing language, no emoji.
- Reference facility-agreement section numbers as `§[ref]` placeholders if
  unknown.
- Currency amounts: include the currency code (CAD).
- Date format: ISO (YYYY-MM-DD) in machine-readable contexts; long form
  ("May 1, 2026") in prose paragraphs.

## What you don't do

- Don't invent figures. Every number traces to a model cell or `deal.yaml`.
- Don't send. Drafts only.
