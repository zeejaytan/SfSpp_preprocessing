# 284 — Re-score every rollout lane at theta 3.4 on the shipped binary

Answers: E1
Status: ready-for-agent
Working in: C:/PR/worktrees/sfs/284 (Phase 0 is read-only inventory; Phases 1-3 run on Spartan)
Needs-eye: yes -- a per-pot overlay picture for any lane that moves across the bar

## Why

Every rollout score in this repo (tickets 250-259, 214 lanes across ten pots) was collected at
**SFS_PAPER_THETA = 4.0** and on the **pre-strip** binary. Main now ships theta 3.4 plus the
no-discard full walk, the 12 mm stop rule, the vote-order host and the ticket 274 clamp, with the
five rejected arms removed (538357c, 67ff3d7). Ticket 271 showed 3.4 is not free — Pot H 10 Bl1
went 96.59% -> 79.55% kept-% — so the rollout numbers in the ledger are no longer a statement
about the program we ship. This ticket replaces them.

## Phase 0 — inventory first, no compute (this is the gate on everything else)

For each piece scored in tickets 250-259, report:

1. the pot, the piece id, the lanes scored, and each lane's score at 4.0 from the ticket;
2. whether the author breakline files for those lanes are still present (path + md5);
3. whether the piece's mesh still exists in the authors' sample tree, and **whether it is the
   plain mesh or a downsampled one** — most survivors are _Mesh_DS.obj, and a cloud sampled from
   a DS mesh is coarser and not byte-identical;
4. whether any surface pair or edge output from the original 4.0 run survives on Spartan
   (pota2xx trees were pruned; check before assuming);
5. the lane count that can be reproduced honestly, and the lane count that cannot, with the
   reason for each refusal.

**Phase 0 output is a table plus a go/no-go.** If a piece can only be reproduced from a coarse
cloud, say so and score it in a separate column — never mix it into the number that replaces the
ledger.

## Phase 1 — mesh and edge at the shipped settings

For the reproducible set: mesh at theta 3.4 with SFS_AXIS_FILE set (verify the classify line; a
missing axis file silently keeps size order — ticket 277), then edge with **defaults only**, no
overrides. Record the binary md5 and the source md5 in every run.json, and prove the binary
contains the three shipped markers ([STOP-267], [FULL-263], [VOTE-247]).

## Phase 2 — score

Score every lane against its own author lane with the standing definition (one-way precision:
each of our resampled dots to the nearest author dot; med = median; cov = share within 2 mm;
jumps = consecutive step > 10 mm) **and** the author-side coverage, which is mandatory — a short
line lying on the author's line scores 100 one-way.

Report per lane: 4.0 baseline, 3.4 result, and the delta in all three numbers. Then per pot.

## Pre-registered rules

- A lane "at bar" means cov >= 90 and med <= 2.0 mm, as in the rollout tickets.
- Every lane that leaves the bar and every lane that enters it gets named with its numbers; no
  pot-level average may hide a lane. Report the count in each direction first, then the detail.
- Quote medians to one decimal: the mesh stage draws 30 random ray-cast points from an unseeded
  generator (mesh_processing_headless.cpp:1526-1527), which moves P03's median by ~0.1 mm run to
  run. Coverage and jumps survive that noise; a 0.05 mm delta does not.
- No retuning. If a lane fails, it is reported as a failure with its numbers.

## Phase 3 — write it back

Append a ledger section (K.2 or L) replacing the stale 4.0 scores, state plainly whether the
shipped program is better or worse than the numbers it replaces, and list the lanes that still
fail with their family from the ledger (growth / dropped cluster / partition / unresolved).

## Acceptance

- Phase 0 table with an explicit go/no-go and the honest lane count.
- Every reproducible lane scored at 3.4 with both directions of coverage.
- Counts: lanes at bar before, at bar after, entered, left.
- The ledger updated and the stale 4.0 claim marked superseded.
- One overlay PNG per pot containing a lane that crossed the bar in either direction.

## Evidence to report

- the Phase 0 table and the lane arithmetic
- the per-lane score table with both coverage directions
- the entered/left lists with numbers
- binary and source md5s, and the marker check output
