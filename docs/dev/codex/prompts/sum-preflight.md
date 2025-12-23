---
description: SUM preflight: sync branch to origin/develop + print theme build checklist
argument-hint: [TICKET_ID=<THEME-###>]
---
/set env TICKET_ID={{ .args.TICKET_ID }}
/comment Running SUM preflight for $TICKET_ID
/shell make preflight
/diff
/comment ready to start $TICKET_ID — if you changed theme templates/tailwind inputs, rebuild theme CSS + fingerprint before pushing. Resolve generated CSS/fingerprint conflicts by regenerating, not hand-merging.
