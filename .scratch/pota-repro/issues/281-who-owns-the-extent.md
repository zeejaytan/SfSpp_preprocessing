# 281 — Who owns the extent: region growth, or a cluster we never kept?

Answers: E1
Status: ready-for-agent
Working in: C:/PR/worktrees/sfs/281 (read-only on existing dumps; no build, no C++)
Needs-eye: no

## Background

Ticket 280 closed one door: the Pot H 02 / H 10 Bl1 coverage loss is not the detector. Sixteen
honest boundary-estimator settings recover 0 of 35 and 1 of 20 of the uncovered reference dots,
and at the nearest surface point the maximum angular gap is 8.9-9.9 deg against a 108 deg
threshold — the uncovered stretch lies in the SMOOTH interior of Surface_1, the smoothest part
of the whole sheet. Our line is longer than the reference (271.926 mm against 245.168 mm) and
no stop rule fired, so we drew a different contour on a region that spans past their rim.

Two mechanisms remain, and they point at different parts of the pipeline:

1. **GROWTH** — the reference rim is interior to ONE cluster because region growing welded the
   rim face onto its neighbour, so there is no cluster edge for any detector to find.
2. **MERGE / DROPPED** — the reference rim sits on a boundary between clusters, but the
   cluster on the far side was dropped (never kept as a surface) or was wrongly merged away,
   so the surface we kept simply continues past it.

Ticket 279 established that the authors' own reference lines are always the boundary of the
surface they kept (163/163 lanes boundary-like, median largest angular gap 165 deg). So this
question is the same question for Pot H that 279 answered for Pot C 03 — but this time the
face we kept IS the face they kept, and the difference is only where it ENDS.

## Task

Use the existing 276 Phase 3a dumps (out/H02_diag, out/H10_diag, theta 3.4, one label per
mesh point: cluster id, post-merge, plus the final surface assignment where "surface 1" is
kept and 0 is dropped). Nothing is rebuilt or re-meshed.

For each of the four lanes (H02 Bl0, H02 Bl1, H10 Bl0, H10 Bl1):

1. Map every reference dot to its nearest mesh point and take that point's cluster id.
2. **Boundary distance**: for each reference dot, the distance from its nearest mesh point to
   the nearest mesh point carrying a DIFFERENT cluster id. Express it in sampling spacings
   (report the local median point spacing so the number is comparable across pieces).
3. Report the distributions separately for the COVERED dots and the UNCOVERED dots of that
   lane, plus the two Bl0 lanes as the worked control. The uncovered sets are already named in
   ticket 280 (H02 Bl1 indices 32-66, H10 Bl1 indices 40-58) — reuse those definitions exactly
   so the two tickets line up.
4. For each cluster touched by the uncovered dots: its point count, whether it survived into a
   surface, and how many of that lane's reference dots it carries.

## Pre-registered read (write this before looking at the numbers)

- Uncovered dots deep inside one cluster (boundary distance >> a few spacings) whose cluster is
  KEPT => **GROWTH owns it**. Follow-up: name the growth step and the parameter that would have
  to change, and state whether the change is local (a face the authors also separate) or global
  (a threshold that would move all 214 scored lanes).
- Uncovered dots sitting on a cluster boundary, with the far cluster DROPPED or merged into the
  near one => **MERGE / DROPPED owns it**. Follow-up: name the refused pair and the test that
  refused it, using the Phase 2 pair instrumentation pattern from ticket 276.
- If the two lanes disagree, say so — one answer per lane is acceptable and expected.

Do not tune anything, do not change a default, do not edit C++. This ticket ends with a
recommendation, and the decision is the lead's.

## Acceptance

- Four lanes reported with the boundary-distance distributions for covered and uncovered dots.
- The local sampling spacing stated for each piece, so the distances are interpretable.
- One named owner per failing lane, with the follow-up step it implies.
- A run directory under SfSpp/runs/ with run.json and an index.tsv row (the tag line may say
  read-only analysis).

## Evidence to report

- the per-lane table, with the uncovered-dot indices quoted so they can be matched to 280
- the cluster table touched by the uncovered dots
- the named owner and the evidence line that decides it
- anything in the dumps that contradicts this ticket's framing
