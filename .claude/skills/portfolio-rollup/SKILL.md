---
name: portfolio-rollup
description: Aggregate live KPIs across every deal in the workspace — DSCR distribution, total commitments by sector, deals on watchlist, etc. Use for portfolio-level reporting, monthly committee packs, or scanning for outliers.
---

# Portfolio rollup

## When to use

- Monthly portfolio review.
- Building an investment-committee deck.
- Hunting for outliers (lowest-DSCR deal, highest-leverage deal).
- Sector concentration reporting.

## Steps

1. **Pull the rollup.**
   ```
   fmcli portfolio
   fmcli portfolio --csv > /tmp/portfolio.csv   # for downstream analysis
   ```
   The CLI iterates every deal in `data/deals/`, reads each model's named
   output cells, and joins with `deal.yaml` metadata.

2. **Slice the result.** Common cuts:
   - **By sector:** group on `sector`, sum `commitment`.
   - **By DSCR band:** count of deals with DSCR < 1.20x, 1.20–1.40x, ≥1.40x.
   - **Watchlist:** deals where any covenant is `WATCH` or `BREACH` —
     iterate with `fmcli covenant <deal>` per deal.

3. **Surface the headline.** Lead the report with:
   - Total commitments (CAD).
   - Number of deals.
   - Count of watchlist + breach deals.
   - Lowest current DSCR and which deal.

## Example credit-committee one-pager

```
Portfolio · as of <date>
• 2 deals, CAD 670M committed
• Sectors: Transportation 75%, Clean power 25%
• DSCR range: 1.31x – 1.42x
• Covenants: 0 breach, 1 watch (Highway 407 ext, DSCR lock-up margin 12%)
• Drawdown activity (last 30d): 1 advance, CAD 25M
• Snapshots/audit events (last 30d): 8
```

## Limitations

- The rollup only reads cached values. Run `update-model` on each deal to
  ensure values are current before aggregating.
- Cross-currency rollups don't FX-translate. CIB is mostly CAD; if a future
  deal is USD-denominated, declare currency in `deal.yaml` and post-process.
