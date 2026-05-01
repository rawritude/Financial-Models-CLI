# Working in this repo

You are operating in **Financial Models CLI**, an agent-driven workbench for
infrastructure-finance teams (think CIB: long-tenor project finance,
quarterly/monthly monitoring, drawdowns, covenant testing, borrower notices).

Read this file before starting any task.

## Mental model

Two things move work:

1. **`fmcli`** — a deterministic Python CLI. It reads and writes Excel cells,
   renders notice templates, appends to audit logs, runs covenant tests.
   **All spreadsheet writes go through `fmcli`.** Never edit `.xlsx` files by
   hand or by writing your own Python — use the CLI.
2. **Agents in `.claude/agents/`** — specialists that plan and reason. They
   call `fmcli` for the deterministic parts and only handle the judgment
   parts themselves (interpreting borrower submissions, drafting prose,
   deciding which covenant test applies).

For multi-step jobs, hand off to the **`deal-orchestrator`** agent. It sequences
the other agents and asks the user to confirm before any external-facing
artifact is finalized.

## Repo layout

```
.claude/
  agents/        Specialist subagents (see "The team" below)
  skills/        Reusable how-tos (update-model, draft-notice, ...)
  commands/      Slash commands for end-to-end plays
fmcli/           Python CLI source
data/
  deals/<deal>/  One folder per deal
    model.xlsx       The project finance model
    deal.yaml        Deal metadata: covenants, named output cells, parties
    inputs/          Borrower-submitted spreadsheets, drop them here
    outputs/         Generated notices, extracted reports
    audit.log        Append-only audit trail
  templates/     Jinja2 notice templates (drawdown, covenant, monitoring, ...)
```

## The team (subagents)

| Agent | When to use |
|---|---|
| `deal-orchestrator` | Any multi-step job (monthly update, new drawdown, covenant review). Plans + sequences. |
| `model-updater` | Borrower submitted actuals; need to propagate values into the project model. |
| `output-extractor` | Need DSCR / LLCR / debt balance / DSRA from the model with units + period labels. |
| `covenant-checker` | Test the deal's covenants against current model outputs. |
| `notice-drafter` | Draft a borrower-facing notice from a template (drawdown, breach, monitoring). |
| `reconciler` | Diff two model versions, or compare borrower submission against model. |
| `audit-logger` | Append a row to the deal's audit trail (the other agents already do this). |

Claude will route work automatically. You can also call directly:

> Use the covenant-checker agent on deal `oneida-energy-storage`.

## How to do common tasks

### Monthly monitoring update (the main loop)

```
> /monthly-update <deal>
```

Or step by step, if you prefer:

1. `fmcli update <deal> <path-to-borrower-submission.xlsx>`
2. `fmcli extract <deal> --outputs DSCR,LLCR,DebtBalance,DSRA`
3. `fmcli covenant <deal>`
4. `fmcli notice <deal> quarterly-monitoring`
5. Review the rendered notice in `data/deals/<deal>/outputs/`.
6. Hand it to the user for sign-off before sending.

### New drawdown request

```
> /new-drawdown <deal> --amount <amount>
```

Checks availability against the drawdown schedule, updates the model,
recomputes outputs, drafts a drawdown confirmation.

### Covenant review

```
> /covenant-review <deal>
```

Pulls outputs, runs every covenant in `deal.yaml`, flags any breach with
severity, drafts a covenant test certificate.

## Conventions

- **Money:** Always include currency. CIB deals are CAD unless flagged.
- **Periods:** Use `YYYY-Qn` or `YYYY-MM`. Never bare quarter numbers.
- **Cells:** Refer to outputs by name (`DSCR`), not coordinates (`Outputs!B14`).
  The mapping lives in `deal.yaml`.
- **Drafts vs finals:** Anything in `outputs/` with `DRAFT` in the filename
  is not yet approved. Don't strip the `DRAFT` until the user confirms.
- **Audit:** Every write to a model must append to `audit.log`. The CLI does
  this; if you bypass the CLI, you bypassed the audit trail.

## How recalc works

openpyxl writes cell values but does not evaluate formulas. After every
input write, `fmcli` calls `fmcli.compute.recompute()` — a deterministic
Python recomputation of the model's outputs. The arithmetic for each
supported model schema lives in `fmcli/compute.py`. To onboard a deal with
a new schema, add a method there (and reference it via `compute_method`
in `deal.yaml`).

## What not to do

- Don't open `.xlsx` files in pandas or write your own openpyxl scripts. Use
  `fmcli`. If the CLI is missing a capability, add it to `fmcli/` rather than
  working around it.
- Don't invent figures in notices. The drafter pulls every number from the
  model via the extractor. If a figure isn't in the model, ask.
- Don't finalize a borrower-facing artifact without explicit user confirmation.
- Don't skip covenant tests because "the numbers look fine". Run them.

## Getting started in a fresh session

```
> fmcli list
> fmcli show highway-407-extension
> /monthly-update highway-407-extension
```
