---
name: deal-onboarding
description: Set up a brand-new deal in this workspace — create the folder, write the deal.yaml, register output cells and the input_map, and seed an initial backup. Use when bringing a newly closed deal into the monitoring system.
---

# Onboard a new deal

## When to use

- A new facility just closed. Bring it under monitoring.
- An existing deal needs to be re-onboarded (e.g. after a major model rebuild).

## Inputs you need from the deal team

1. **Deal ID** — slug used in URLs/paths. Lowercase, hyphenated.
   e.g. `oneida-energy-storage`.
2. **Project name** and **borrower** legal name.
3. **Facility metadata**: commitment, currency, closing date, maturity date,
   sector (transportation / clean-power / broadband / trade-corridor / green).
4. **The model file** — put it at `data/deals/<deal_id>/model.xlsx`.
5. **Output cell map** — for each KPI, the `Sheet!Cell` reference.
   Must include at least: DSCR, LLCR, DebtBalance, AvailableCommitment.
6. **Input map** — labels the borrower will use on submissions, mapped to
   `Inputs!Cell` references. The labels here are the canonical labels;
   borrower-side drift is handled by the `model-updater` skill.
7. **Covenants** — name, output, operator, threshold, severity.

## Steps

1. **Create the folder structure.**
   ```bash
   mkdir -p data/deals/<deal_id>/inputs
   mkdir -p data/deals/<deal_id>/outputs
   touch data/deals/<deal_id>/audit.log
   ```

2. **Drop the model.xlsx in `data/deals/<deal_id>/`.**

3. **Author `data/deals/<deal_id>/deal.yaml`** following this skeleton (and
   modeled on the existing deals in the workspace):

   ```yaml
   borrower: "Borrower Legal Name Inc."
   project: "Project Name"
   sector: "Clean power"           # or Transportation, Broadband, Green, Trade
   facility: "Senior secured term loan"
   currency: CAD
   commitment: 200000000
   closing_date: 2024-06-30
   maturity_date: 2044-06-30
   inputs_sheet: Inputs
   notes: |
     Free-form context: project structure, reference rate, special features.
   parties:
     borrower:
       legal_name: "..."
       contact: "..."
     lender:
       legal_name: "Canada Infrastructure Bank"
       contact: "monitoring@cib-bic.ca"
   outputs:
     DSCR:                Outputs!B14
     LLCR:                Outputs!B15
     DebtBalance:         Outputs!B16
     DSRA:                Outputs!B17
     AvailableCommitment: Outputs!B18
   input_map:
     Revenue_Q1:    Inputs!B5
     Opex_Q1:       Inputs!B6
     InterestRate:  Inputs!B7
   covenants:
     - name: DSCR Lock-up
       description: "Distribution lock-up if DSCR < 1.20x"
       output: DSCR
       operator: ">="
       threshold: 1.20
       severity: breach
     - name: LLCR Floor
       description: "LLCR must remain >= 1.30x"
       output: LLCR
       operator: ">="
       threshold: 1.30
       severity: breach
   ```

4. **Validate.**
   ```
   fmcli show <deal_id>
   ```
   Every output cell should resolve to a value. Every covenant should test
   cleanly. If `fmcli show` errors out, fix `deal.yaml` before continuing.

5. **Take an onboarding snapshot.**
   ```
   fmcli backup <deal_id> --reason onboarding-baseline
   ```

6. **Run a baseline covenant test** to capture the deal's opening state in
   the audit log:
   ```
   fmcli covenant <deal_id>
   ```

## Done when

- `fmcli list` includes the deal.
- `fmcli show <deal_id>` renders without errors and shows live output values.
- `fmcli covenant <deal_id>` returns a verdict for every covenant in the deal.
- `data/deals/<deal_id>/.backups/` contains an `onboarding-baseline` snapshot.
- `data/deals/<deal_id>/audit.log` has at least the baseline covenant test.
