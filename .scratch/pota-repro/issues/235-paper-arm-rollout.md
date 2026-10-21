Status: ready-for-agent
Answers: E1

# Ticket 235: paper-arm rollout to the remaining problem pieces

## Goal
Run the landed paper-arm binary (mesh v3 d72979aa, build 33616944 -- rebuild from the branch if it has moved on, same-source check first) on P15, P25, P27 (untested on the paper arm) plus P16 and P01 as regression controls (both at bar on the old chain).

## Boundary
- Spartan only, fresh experiment copy (do NOT touch sfs-fix-234 or the branch worktree).
- Read-only on tickets 234/214/215/228/229; edit only this ticket (append Comments, Status results-in).
- No commits, no pushes.

## Constraints
- Same exam protocol as 234: gap table + post-merge cluster sizes + merges fired + classify votes + slot-verified lanes vs author (bar med<2 + cov>=90).
- P16 control must reproduce its cure (Bl0 0.56/97.4-era numbers at bar); P01 must stay at bar. If either regresses, STOP and report -- do not retune.
- Watch items from 234: P22-style edge pinch near forks (measure and locate any symmin < 1mm); Jug-style resample dupes (count exact-dupe filed points per piece).

## Acceptance
Per-piece table (P15/P25/P27/P16/P01): post-merge top2 share, merges fired + which clusters, classify vote, both lane scores straight+matched, pinch/dupe watch numbers. Verdict line per piece: AT-BAR / NEAR-MISS / FAIL + whether the piece is resolved. sacct COMPLETED for every job; binaries md5 cited.

## Required evidence to report
Job IDs + sacct states; binary md5s; the per-piece table with the numbers, not adjectives; verdict in ticket Comments; Status results-in; self-contained completion message to the parent.

## Comments
