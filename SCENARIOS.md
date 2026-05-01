# Scenario library

Pre-built borrower-submission workbooks for both demo deals. Use these to
exercise the CLI/agents against different stories without having to fabricate
inputs by hand.

## Where they live

```
data/deals/highway-407-east-extension/inputs/scenarios/
data/deals/oneida-energy-storage/inputs/scenarios/
```

## Rebuild any time

```bash
python3 scripts/build_scenarios.py
```

The script overwrites the scenarios from a known-good template, so you can
mutate any of them during a demo and reset with one command.

## Highway 407 East Extension scenarios

Baseline: DSCR ≈ **1.24x** (already on the watchlist; lock-up at 1.20x).

| Scenario | What happens | Expected outcome |
|---|---|---|
| `q1-clean.xlsx`        | ~On-plan actuals, slight rate refix              | DSCR ≈ 1.24x — stays in WATCH |
| `q1-stress-rev.xlsx`   | Sustained availability deduction (~12%)          | DSCR drops below 1.10x — **BREACH** of lock-up |
| `q1-stress-opex.xlsx`  | Winter lifecycle event; opex +38%                | DSCR through lock-up — **BREACH** |
| `q1-stress-rate.xlsx`  | CORRA spike +200bps                              | DSCR drops; LLCR also drops |
| `q1-upside.xlsx`       | Bonus payment + opex underrun + rate down        | DSCR climbs to ~1.32x |
| `q1-mislabeled.xlsx`   | `AvailPayment_Q1` + `OperatingExpense_Q1` (wrong) | Two unmatched labels surfaced; only rate updated |
| `q1-partial.xlsx`      | Opex_Q1 omitted, others present                  | Two cells written; partial update succeeds |
| `q2-clean.xlsx`        | Next-period actuals (CPI uplift, modest refix)   | Rolls the model forward into Q2 |

## Oneida Energy Storage scenarios

Baseline: DSCR ≈ **1.56x** (clean PASS).

| Scenario | What happens | Expected outcome |
|---|---|---|
| `q1-clean.xlsx`             | Capacity payment fixed, arbitrage close to plan | DSCR ≈ 1.55x — PASS |
| `q1-stress-arbitrage.xlsx`  | Arbitrage spreads collapse 50%+ (mild winter)   | DSCR drops; lock-up at 1.25x tested |
| `q1-stress-opex.xlsx`       | Augmentation + insurance step-up; opex +60%     | DSCR squeeze |
| `q1-stress-rate.xlsx`       | Rate spike to 8.5%                              | Interest expense up; DSCR drop |
| `q1-upside.xlsx`            | Exceptional spreads + cost discipline           | DSCR climbs above 1.70x |
| `q1-mislabeled.xlsx`        | `CapacityRevenue_Q1`, `Arbitrage_Q1` (wrong)    | Two unmatched labels surfaced |
| `q2-clean.xlsx`             | Next-period actuals                             | Rolls the model forward |

## Demo plays

### Play 1 — Watchlist deal slides into BREACH

```bash
fmcli covenant highway-407-east-extension      # baseline: 3 WATCH, 1 PASS
fmcli update highway-407-east-extension \
  data/deals/highway-407-east-extension/inputs/scenarios/q1-stress-rev.xlsx
fmcli covenant highway-407-east-extension      # now 2 BREACH, 1 WATCH, 1 PASS
fmcli notice  highway-407-east-extension covenant-breach-notice --period 2026-Q1
fmcli report  credit-memo highway-407-east-extension --period 2026-Q1
```

### Play 2 — A clean upside quarter

```bash
fmcli covenant oneida-energy-storage           # baseline: PASS / WATCH mix
fmcli update oneida-energy-storage \
  data/deals/oneida-energy-storage/inputs/scenarios/q1-upside.xlsx
fmcli covenant oneida-energy-storage           # all PASS, headroom built
fmcli notice  oneida-energy-storage quarterly-monitoring --period 2026-Q1
```

### Play 3 — Borrower submitted bad labels

```bash
fmcli update highway-407-east-extension \
  data/deals/highway-407-east-extension/inputs/scenarios/q1-mislabeled.xlsx \
  --dry-run
# Two labels surface as unmatched; the CLI refuses to silently apply them.
```

### Play 4 — Multi-quarter roll

```bash
fmcli update highway-407-east-extension \
  data/deals/highway-407-east-extension/inputs/scenarios/q1-clean.xlsx
fmcli update highway-407-east-extension \
  data/deals/highway-407-east-extension/inputs/scenarios/q2-clean.xlsx
fmcli audit highway-407-east-extension         # both updates appear in the trail
```

## Reset to baseline between demos

```bash
python3 scripts/build_sample_models.py
```

This rebuilds the deal models from scratch (and resets the borrower-submission
fixture used elsewhere in the docs). It does not touch the scenarios in
`inputs/scenarios/`. Use `python3 scripts/build_scenarios.py` to rebuild those.
