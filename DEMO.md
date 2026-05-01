# Demo script

A 5-minute walkthrough you can run from a terminal during the presentation.
Two narrative arcs: (1) a quarterly monitoring loop on a deal that's
already on the watchlist, (2) a portfolio rollup + stress test.

## Setup

```bash
pip install -e .
python3 scripts/build_sample_models.py    # rebuild fresh demo data
fmcli list                                  # confirm the two deals are loaded
```

You should see two deals: **Highway 407 East Extension** (CAD 480M senior
debt, transportation P3) and **Oneida Energy Storage** (CAD 170M senior
debt, battery storage).

---

## Act 1 — Quarterly monitoring loop (3 min)

> "It's quarter close. The borrower on Highway 407 just sent in their
> Q1-2026 actuals. Watch what happens."

```bash
fmcli show highway-407-east-extension
```

Highlights:
- Live DSCR is **1.24x** — already in WATCH (within 10% of the 1.20x lock-up).
- Four covenants declared. Three currently WATCH, one PASS.

```bash
fmcli covenant highway-407-east-extension
```

Now drop the borrower submission in:

```bash
fmcli update highway-407-east-extension \
  data/deals/highway-407-east-extension/inputs/h407-2026-q1-actuals.xlsx
```

What happened, in order:
1. **Snapshot** taken automatically (`backup: model_2026...xlsx`).
2. **3 cells written** — availability payment, opex, interest rate.
3. **Outputs recomputed** in Python (deterministic, no Excel needed).
4. **Audit trail** appended.

Re-test covenants:

```bash
fmcli covenant highway-407-east-extension
```

> "DSCR has slipped to 1.18x. We're now in BREACH on the lock-up. Watch
> what the system does next."

```bash
fmcli notice highway-407-east-extension covenant-breach-notice --period 2026-Q1
fmcli notice highway-407-east-extension quarterly-monitoring     --period 2026-Q1
```

Open the resulting drafts:

```bash
ls data/deals/highway-407-east-extension/outputs/
cat data/deals/highway-407-east-extension/outputs/DRAFT_*_covenant-breach-notice.md
```

> "The breach notice is fully populated with live figures. The DRAFT_
> prefix is intentional — nothing leaves the bank without a human on the
> sign-off."

Show the audit trail:

```bash
fmcli audit highway-407-east-extension
```

Show that we can roll back at any time:

```bash
fmcli backups highway-407-east-extension
fmcli restore highway-407-east-extension <pre-update-snapshot-name>
```

---

## Act 2 — Portfolio rollup + stress test (90 sec)

```bash
fmcli portfolio
```

> "One command, every deal in the portfolio, live KPIs."

```bash
fmcli sensitivity oneida-energy-storage \
  --shock "ArbitrageRevenue_Q1:mul:0.50" \
  --shock "InterestRate:abs:0.085" \
  --shock "Opex_Q1:mul:1.20"
```

> "Sensitivities are one-shot, fully isolated. The model is snapshotted,
> shocked, recomputed, and restored — three times here. Baseline is back
> exactly where it was."

```bash
fmcli extract oneida-energy-storage   # confirm baseline restored
```

---

## Act 3 — In a Claude Code session (the wow)

> "Same workflow, but driven by an AI agent. Spin up a Claude Code session
> in this repo."

```
claude
```

Then in the session:

```
> /monthly-update highway-407-east-extension
```

The orchestrator agent reads `CLAUDE.md`, plans the workflow, delegates
to the model-updater, output-extractor, covenant-checker, notice-drafter
in sequence, then returns a credit-officer summary.

Other plays:

```
> /covenant-review oneida-energy-storage
> /portfolio-review
> /stress-test highway-407-east-extension
> /new-drawdown oneida-energy-storage --amount 10000000
```

Or freeform:

```
> The borrower on Highway 407 wants to reset their interest rate to 5.40%
> for Q1. Walk me through the impact and draft a rate reset notice.
```

---

## Talking points

1. **Two layers, clean separation.** Deterministic spreadsheet ops in
   Python (`fmcli`), judgment work in agents. No LLM ever silently
   mutates a model cell.
2. **Audit by default.** Every write logs who, when, source file, before
   value, after value. Backups taken automatically.
3. **Templates over freehand.** Notices are Jinja templates; the agent
   fills in named figures, doesn't invent them.
4. **Plug-and-play.** New deal = drop a model.xlsx + write a deal.yaml.
   No code changes for new covenants, new outputs, or new templates.
5. **Same tools, the whole team.** Anyone on the team can `claude` into
   the repo and run the same plays. Skills + slash commands codify the
   workflows so they're consistent across analysts.
