Status: ready-for-agent

# Ticket 246: full E2E Pot A + Pot C on the restored-density main

Answers: whether the density restore holds whole pots end to end.
Needs-eye: no.

## Goal
Run the full chain (mesh -> trace -> seat vs author) on current origin/main (restore live since 93c33bc) for Pot A and Pot C, fresh-arm, with author-code control arms per the 208/239 protocol. PASS = match-or-beat each pot's prior best.

## Boundary
- Fresh worktree of origin/main + fresh Spartan copy. Rebuild the paper chain (expect b8eb3759 byte-identical on the same node; identical-or-explained).
- Pot A: same protocol as 210/236 (fresh 8/8+15/15, strict 8/8 from 236 is the bar).
- Pot C: same E2E shape as 239 (fresh + ORIG arms, swap-straight slots, strict counts). The worker pulls Pot C's bar from the ticket record (tickets 34, 197 and the C02/C03 join work) and states it in Comments BEFORE scoring -- no moving goalposts.
- P03 note: Bl0 is the proven lane (0.72/97.8); Bl1 ridge-lock is a known open tracer caveat and does NOT fail this ticket -- but the worker reports both lanes' scores honestly.
- Main worktree (user 204-edit) off limits except ticket commit+push (lead lands). No commits to main. No other pots touched.

## Constraints
- Spartan: pull --ff-only first, STOP and report on divergence.
- Same build node for md5 comparisons. sacct COMPLETED for every job, in-ticket.
- Jobs are the 208/239 shape (pipe/diag/stage/fresh-only); cite all IDs.

## Acceptance
- Pot A: fresh 8/8+15/15 AND strict 8/8 (match 236), ORIG control arm valid.
- Pot C: fresh scores match-or-beat the stated bar; ORIG control arm valid.
- Binary md5 cited. Full E2E verdict per pot in Comments.

## Required evidence to report
Bars stated before scoring; all job IDs + sacct states; fresh + ORIG scores per pot; binary md5; verdict in ticket Comments; Status results-in; self-contained completion message to parent agent session-1ca83938-6e86-4736-bb84-2f4e58807e35.
