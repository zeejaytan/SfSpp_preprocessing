# 210 - Swap P02-P08 Bl0/Bl1 to the author convention + fresh re-seat (209 follow-up)

Status: ready-for-agent
Answers: E1-do-our-breaklines-let-sfs-find-joins

## Goal
User order (2026-10-20): swap our slot 0/1 edgelines to match the author
convention, then re-seat. Lead check (same day): the assembler (POT_A_ORIG
block, class/data_path.h:1610+) loads ONLY Breakline_0.pcd per piece -- so
the 208 fresh arm (7/8+9/15) seated while reading the opposite rims from the
green ORIG control on P02-P08. 209 proved both lanes are true edges
(matched-lane coincidence 100%<2mm all pieces), so filing the author-side
rim in slot 0 is legitimate (ticket-73 precedent). P01 slots already agree:
NO swap for P01. (P01-Bl1 short at 92 vs 214 stands as a separate open item
from 209 -- diagnose, do not fix inside this ticket.)

## Boundary
Spartan-side, new bundle copy pota210_bundle_v1 (copy of v0; NEVER modify
v0): for pieces 02-08 ONLY, swap Breakline_0 <-> Breakline_1 contents
(byte-identical copies, verify with md5 before/after). Everything else
(Mesh, Axes, GT, Surfaces, P01 files) identical to v0. Do NOT touch the
preprocessing sources, the live Spartan main checkout, or the 2 pre-E2E
stashes. Re-seat the FRESH arm only (same scorer b56bc80, same stage recipe
as 208 job 33505947); the ORIG control stays as run (no rerun). COMMIT
NOTHING (lead commits).

## Constraints
Standing submit sign-off covers sbatches (fresh-only recipe per 208:
request 24h; laptop-side poll per sbatch, sacct State/ExitCode in Comments).
Held allocation for iterative checks. If seating diverges from the 208
fresh run for non-swap reasons (different snapshot layout, missing files),
STOP and report -- do not reinterpret. No MATLAB re-run (axes as-is).

## Acceptance
Fresh arm seated on the swapped v1 bundle, reported as fragments x/8 +
joins y/15 with Acc-file verbatim lines, strict table (same robust-align
recipe as 208: align on pieces 2-8 excl. outliers, per-piece rot/trans),
and a side-by-side render vs the 208 fresh result. Comparison stated
plainly: swapped-v1 vs unswapped-v0 (7/8+9/15) vs ORIG control (8/8+15/15).

## Required evidence
Comments: v1 bundle path + swap md5 table (per piece: old-Bl0 md5 == new-Bl1
md5 and vice versa) + job ID/state + Acc verbatim + strict table + render
paths + the comparison. Final report: same, self-contained, plus verdict on
whether convention alignment moved seating.

## Comments (worker)
