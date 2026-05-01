# Financial Models CLI

An agent-driven workbench for infrastructure-finance teams. Update models from
borrower submissions, recompute covenants, draft notices, and ship audit-ready
artifacts — all from a Claude Code session.

Built with the Canada Infrastructure Bank (CIB) workflow in mind: long-tenor
project finance, periodic monitoring, drawdown and repayment events, covenant
testing (DSCR / LLCR), and structured borrower communications.

## Why this exists

Analysts spend hours on the same monthly loop:

1. Borrower submits actuals (an Excel workbook, a PDF, or both).
2. Analyst opens the project model, copies values into the inputs tab.
3. Recalculates outputs — DSCR, debt balance, available drawdown.
4. Drafts a notice (drawdown confirmation, interest payment, covenant test).
5. Logs the change. Files everything. Hopes nothing was missed.

This repo turns that loop into a multi-agent workflow. A team of specialized
Claude agents, a Python CLI for the deterministic spreadsheet operations, and
a library of skills + slash commands so the whole team can run the same plays.

## Quick start

```bash
# 1. Clone, install
git clone <this repo>
cd Financial-Models-CLI
pip install -e .

# 2. Open in Claude Code
claude

# 3. Inside the session, try one of these
> /monthly-update highway-407-extension
> /covenant-review broadband-northern-ontario
> /new-drawdown highway-407-extension --amount 25000000
```

The `CLAUDE.md` at the root tells Claude how to use the agents and tools.
You don't need to memorize anything.

## What ships in this repo

```
.claude/
  agents/        Specialist subagents (model updater, covenant checker, ...)
  skills/        Reusable workflows the agents (and you) can invoke
  commands/      Slash commands for common end-to-end plays
fmcli/           Python CLI for deterministic spreadsheet + notice work
data/
  deals/         One folder per deal: model, inputs, deal.yaml, audit log
  templates/     Notice templates (Jinja2) for borrower communications
```

## The agent team

| Agent | Role |
|---|---|
| `deal-orchestrator` | Plans a multi-step workflow across agents for a given deal event. |
| `model-updater` | Propagates borrower-submitted actuals into the project model. |
| `output-extractor` | Pulls named output cells (DSCR, debt balance, etc.) with units + context. |
| `covenant-checker` | Tests covenants against the deal's `deal.yaml` and flags breaches. |
| `notice-drafter` | Drafts borrower notices from templates, fills in figures + dates. |
| `reconciler` | Diffs two model versions or compares model output against borrower submission. |
| `audit-logger` | Appends every change to the deal's audit trail with source + timestamp. |

Agents are defined in `.claude/agents/` and Claude will route work to them
automatically based on the task. You can also call them directly:

```
> Use the covenant-checker agent on deal highway-407-extension.
```

## The CLI: `fmcli`

The CLI does the deterministic work — read/write cells, render Jinja
templates, append to audit logs. Agents call `fmcli` for anything that needs
to be reproducible.

```bash
fmcli list                                        # list deals
fmcli show highway-407-extension                  # deal summary
fmcli update highway-407-extension <inputs.xlsx>  # propagate inputs
fmcli extract highway-407-extension --outputs DSCR,LLCR,DebtBalance
fmcli covenant highway-407-extension              # test all covenants
fmcli notice highway-407-extension drawdown --amount 25000000  # borrower-facing
fmcli report  credit-memo highway-407-extension   # internal credit memo
fmcli report  portfolio                           # portfolio-level briefing
fmcli sensitivity highway-407-extension --shock "Revenue_Q1:mul:0.90"
fmcli portfolio                                   # cross-deal KPI rollup
fmcli audit highway-407-extension                 # show audit trail
fmcli backup highway-407-extension --reason pre-quarter-close
fmcli reconcile <deal_id> <other_model.xlsx>      # diff outputs vs another workbook
```

### External vs internal artifacts

- `fmcli notice <deal> <template>` — **borrower-facing**. DRAFT_ prefix until
  the user finalizes. Templates: drawdown confirmation, quarterly monitoring,
  covenant breach, interest payment, rate reset, waiver, annual review.
- `fmcli report <kind>` — **internal**. INTERNAL_ prefix. Kinds: `credit-memo`
  (per deal), `portfolio` (cross-deal investment-committee briefing).

Every write goes through the audit logger. Nothing in this repo silently
mutates a model.

## Demo: 60-second walkthrough

```bash
# Inspect a deal
fmcli show highway-407-extension

# Drop in this month's borrower submission
fmcli update highway-407-extension data/inputs/h407-2026-q1-actuals.xlsx

# See what changed
fmcli extract highway-407-extension --outputs DSCR,LLCR,DebtBalance,DSRA

# Covenants
fmcli covenant highway-407-extension

# Draft the borrower notice
fmcli notice highway-407-extension quarterly-monitoring
```

Or, in a Claude Code session, one line:

```
> /monthly-update highway-407-extension
```

…which spins up the deal-orchestrator and runs the whole thing end-to-end,
asking you to confirm before any external-facing artifact is finalized.

## Design principles

1. **Deterministic where it matters.** Cell reads/writes go through the CLI,
   not through an LLM. Agents plan; the CLI executes.
2. **Audit by default.** Every model write logs a row: who, when, source file,
   target cell, before/after.
3. **Small, named outputs.** Models declare their output cells in `deal.yaml`
   (e.g. `DSCR -> Outputs!B14`). Agents work with names, not coordinates.
4. **Templates over freehand.** Borrower notices are Jinja templates with a
   declared schema. The drafter fills in fields; it doesn't invent them.
5. **Human-in-the-loop on external artifacts.** Anything that leaves the
   bank (a notice, a covenant breach letter) requires explicit confirmation.

## Status

Prototype. The sample deals, model structure, and notice templates are
illustrative. Wire to your actual model schema by editing `deal.yaml` for
each deal — no code changes required.
