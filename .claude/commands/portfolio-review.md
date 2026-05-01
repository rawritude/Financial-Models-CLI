---
description: Aggregate KPIs across every deal in the workspace and produce a portfolio-level summary suitable for an investment committee.
---

Run a portfolio review.

1. `fmcli portfolio` — pull live KPIs across every deal.
2. For each deal, also run `fmcli covenant <deal>` and capture the verdict
   counts (PASS / WATCH / BREACH).
3. Synthesize a one-page summary:

   ```
   Portfolio · as of <today>
   • <N> deals, <CAD total> committed
   • By sector: <breakdown>
   • DSCR distribution: low / median / high
   • Covenants: <total breach>, <total watch>
   • Watchlist (top 3 lowest DSCR or any breach): <list>
   • Outstanding draft notices in any deal's outputs/: <count, paths>
   ```

4. If any deal has a BREACH, lead with that deal at the top.
