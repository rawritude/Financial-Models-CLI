---
description: Run a full covenant review for one deal — test every covenant, classify by severity, and if any are in breach, draft a covenant-breach notice.
argument-hint: <deal_id>
---

Run a covenant review for `$ARGUMENTS`.

1. Use the **covenant-checker** agent: `fmcli covenant $ARGUMENTS`.
2. If all covenants are PASS or WATCH, return a one-line summary:
   `<deal> · N PASS, M WATCH, 0 BREACH`. Stop.
3. If any covenant is BREACH:
   - Lead the response with the breach (which covenant, actual vs threshold,
     margin).
   - Use the **notice-drafter** to render `covenant-breach-notice`.
   - Return the path to the draft and a recommendation that credit/risk
     review the cure provisions in the facility agreement.
   - Append a `covenant.breach` audit event noting the response was drafted.
