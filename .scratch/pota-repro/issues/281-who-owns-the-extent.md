# 281 — Who owns the extent: region growth, or a cluster we never kept?

Answers: E1
Status: results-in (H02 Bl1 = growth owns it; H10 Bl1 = the merge never kept its cluster)
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

## Pre-registration, written before any distance was computed (2026-10-24)

Nothing below was edited after the first number was printed. The four lanes, the metric and every
threshold are fixed here, and the results section quotes these rules rather than restating them in
a shape the numbers happen to fit.

**Metric.** M is every point in the dump. For reference dot d, m(d) is the nearest point of M in 3D;
if cluster(m(d)) = -1 the dot is re-mapped to the nearest labelled point and flagged `remap`.
s(d) is the local spacing: the median distance from m(d) to its 8 nearest other points of M.
b_clu(d) is the distance from m(d) to the nearest point of M carrying a *different* label in 0..K-1
(unclustered points do not count for b_clu; that is b_all). b_all(d) is the distance to the nearest
point of M with any different label, -1 included. Both are reported in units of s(d), spacings.

**Bands.** ON-BOUNDARY when b_clu <= 2 s; INTERIOR when b_clu >= 4 s; 2-4 s is MIDDLE and decides
nothing on its own.

**Lane verdict rule.** GROWTH when at least 60% of the lane's uncovered dots are INTERIOR.
BOUNDARY-OWNED when at least 60% are ON-BOUNDARY, and that case is split by the fate of the far
cluster: far cluster labelled >= 2 (dropped) is MERGE/DROPPED; far cluster labelled 0 or 1 (the other
kept surface) is a KEPT BOUNDARY, which this ticket did not frame; a far side of only -1 is a FREE
EDGE, also outside the framing. Anything else is MIXED and gets counts, arcs and both owners.

**Uncovered sets, reused verbatim from ticket 280:** H02 Bl1 indices 32-66 (35 dots) and H10 Bl1
indices 40-58 (19 dots). H10's 20th uncovered dot (index 74, 280's single class-C dot) is reported
separately and excluded from the lane share, because 280 already established it as a walk-set dot
that the bag does contain.

**Controls.** H02 Bl0 (156 reference dots) and H10 Bl0 (101) are fully covered, so they are read for
one purpose only: whether the metric separates at all. My prediction is that the Bl0 covered dots sit
ON a cluster boundary, because their line is the rim of the kept region and something else lies just
beyond that rim. If the Bl0 dots read INTERIOR instead, the metric is not measuring "this line runs
along the edge of the kept region" and every Bl1 number carries that caveat.

**Prediction.** GROWTH on both Bl1 lanes. 280 measured the uncovered stretch as the smoothest part of
the sheet (neighbour normal spread 6.42 / 7.24 deg median against 18.19 / 18.46 deg on the covered
dots; maximum angular gap 8.9 / 9.9 deg against the detector's 108 deg), and growPaper234's only
shape gate is a per-step normal-angle test of 3.4 deg at mesh_processing_headless.cpp:1770 with
curvature < 1.0 at :1766, so a smooth face is welded step by step with no crease to stop it.

**What would overturn that:** b_clu <= 2 s with a far cluster labelled >= 2 on at least 60% of the
uncovered dots, or a far cluster that is one of the two kept surfaces.

**Follow-up named in advance.** If GROWTH owns it, the knob is SFS_PAPER_THETA (3.4 deg,
mesh_processing_headless.cpp:2559 and :2561), a global threshold that would move all 214 scored lanes,
so the only local move is a new edge or crease test inside growPaper234, and that is the lead's
decision rather than this ticket's.

## Results

Read-only on the 276 Phase 3a dumps (`out/H02_diag`, `out/H10_diag`, theta 3.4, per-point cluster id
after merge plus the final surface assignment). No mesh run, no edge run, no build, no C++ edit, no
default changed. Covered / uncovered sets were reproduced exactly before any distance was computed
(`reproduced=True` on all four lanes against ticket 280's ranges).

### Local spacing, and the one place the pre-registration misfires

Two spacings are used and they must not be confused. The piece median 1-NN spacing is **0.3080 mm**
on Pot H 02 and **0.2956 mm** on Pot H 10. The pre-registered `s(d)` is the 8-neighbour radius, whose
lane median is **0.6842 mm** (H02 Bl0), **0.6753** (H02 Bl1), **0.6606** (H10 Bl0), **0.6648** (H10 Bl1).
Both `b_clu` and `b_all` are quoted in `s`.

The pre-registered caveat fired. The Bl0 controls do **not** read ON-BOUNDARY: on H02 Bl0 the 156
covered dots split 23 on-boundary / 63 middle / 70 interior, on H10 Bl0 the 101 covered dots split
24 / 54 / 23. The reason is mechanical: a kept cluster's free edge borders **unclustered** points,
not another cluster, so `b_clu` is large there by construction, while `b_all` — the distance to the
nearest point of any different label including -1 — is 0.272 mm on H02 Bl0 and 0.220 mm on H10 Bl0,
i.e. under half a spacing.

Consequence, stated before the numbers below are used: **`b_clu` is a seam detector, not a boundary
detector.** It can only fire where a second labelled cluster sits within a few spacings. On a lane
with no neighbouring cluster it reads GROWTH by construction. The H02 verdict therefore rests on the
cluster label of the nearest mesh point (35 of 35 dots in kept cluster 1) and on the pair census
(nothing within rho_d), not on `b_clu`; `b_clu` corroborates. On H10 it fires precisely because
material we never kept is adjacent — which is the MERGE case by definition.

### The four lanes

| lane | ref dots | covered | uncovered | arc | 1-NN spacing | s | b_clu/s cov med | b_clu/s unc med (p25-p75) | bands unc onb/mid/int | nearest cluster of uncovered dots |
|---|---|---|---|---|---|---|---|---|---|---|
| H02 Bl0 (control) | 156 | 156 | 0 | – | 0.3080 | 0.6842 | 3.49 | – | – | c0 x149 |
| H10 Bl0 (control) | 101 | 101 | 0 | – | 0.2956 | 0.6606 | 2.42 | – | – | c0 x91 |
| H02 Bl1 | 137 | 102 | 35 | 61.2 mm | 0.3080 | 0.6753 | 4.41 | 10.49 (9.28-11.36) | 0 / 0 / 35 | c1 x35 (kept) |
| H10 Bl1 | 88 | 68 | 20 | 32.4 mm (19-dot set) | 0.2956 | 0.6648 | 2.37 | 2.14 (1.40-2.99) | 9 / 10 / 1 | c5 x15 (dropped), c1 x5 (kept) |

Arc is intervals x 1.800 mm, the reference dots being on a 1.800 mm grid. In millimetres the
uncovered `b_clu` distances are 6.258 / 7.009 / 7.567 mm (p25/med/p75) on H02 Bl1 and
1.016 / 1.425 / 2.208 mm on H10 Bl1. `b_all` medians: 0.223 mm (H02 Bl1 covered) against 1.618 mm
(uncovered); 0.213 mm (H10 Bl1 covered) against 0.844 mm (uncovered).

The dump frame sits about one spacing off the reference frame — nearest-mesh distance median
0.82 mm on H02 and 0.75 mm on H10 — which is the floor on how finely a dot can be attributed to a
cluster; it does not move any of the readings above, whose gaps are 2-15 mm.

Per-cluster attribution of reference dots (`a281_clusters.tsv`, kept = surface flag 1):

| piece | cluster | size | kept | ref dots | of which uncovered |
|---|---|---|---|---|---|
| H02 | 0 | 17091 | yes | 149 (Bl0) | 0 |
| H02 | 1 | 13915 | yes | 132 (Bl1) | 35 |
| H02 | 4 / 5 / 6 | 976 / 539 / 449 | no | 2 / 2 / 1 (Bl1) | 0 |
| H10 | 0 | 4484 | yes | 91 (Bl0) | 0 |
| H10 | 1 | 3403 | yes | 76 (Bl1) | 5 |
| H10 | 5 | 629 | no | 30 (Bl1) | 15 |
| H10 | 3 / 6 | 745 / 186 | no | 1 / 1 (Bl1) | 0 |

### Owner of each failing lane

**H02 Bl1 — GROWTH owns it.** All 35 uncovered dots map to kept cluster 1 (13915 pts) and stay there
after remapping; `b_clu` median 10.49 s = 7.01 mm, minimum 5.20 s = 6.26 mm; the far clusters named per
dot (4, 8, 3, 9, 6 — sizes 976/167/1377/128/449) are all dropped and all 4.21-8.16 mm away. The pair
census closes the alternative: **no cluster on the piece has a single point within rho_d = 1.0 mm of
cluster 1** (nearest partners c1-c8 1.3712 mm, c1-c4 1.3876, c1-c9 1.4299, c1-c6 1.5731, c0-c1 3.9500).
Neither the merge nor the two-largest rule could have changed this lane — there was nothing to merge.
Region growing welded the rim face into Surface_1, and a boundary detector cannot see an edge inside a
single cluster. This is the pre-registered GROWTH reading at 100% interior against a 60% bar.

*Why the per-step gate did not stop it.* The rim is a real fold: across the reference line the two
sides' fitted normals differ by a median **14.13 deg** (n = 12 dots with material on both sides,
min 9.29, p25 13.05, p75 15.75, p90 19.05, max 19.72). Covered dots cannot be measured this way — their
free edge has no material on one side — so this is an uncovered-lane measurement only, as expected.
Measured step by step instead: of the **1265** adjacent sheet point pairs straddling the line (6-NN
within a 2 mm window), the normal difference is min 0.10, p10 1.27, p25 2.14, **median 3.23**, p75 4.85,
p90 6.40, max 15.33 deg, and **667 of 1265 = 52.7% are at or below the 3.4 deg growth gate** (22.6% at or
below 2.0 deg, 6.5% at or below 1.0 deg). Per dot the largest straddling step has median 5.78 deg
(p25 4.89, p75 7.66, max 15.33) and 33 of 35 dots have at least one straddling pair above 3.4 deg.
So the fold arrives as a staircase whose individual steps fall under a per-step angular gate: growth
can cross it where one step happens to be small. *Distinguishing "crossed at a sub-threshold step" from
"walked around the fold's end" needs a growth trace (claim order and which neighbour crossed), which
the dump does not carry — that is the measurement that would settle the mechanism.*

**H10 Bl1 — the MERGE owns it, specifically a cluster that was never kept.** Of 280's 19 uncovered
dots, **15 map to dropped cluster 5** (629 pts) and their nearest differently-labelled point is the kept
Surface_1 cluster 1 at 0.41-2.47 mm; the other 4 map to cluster 1 with cluster 5 nearest (0.41-3.03 mm);
index 74 (280's class-C dot) is separate — cluster 1, far cluster 6, `b_clu` 2.76 s, 2.28 mm from 280's
line. Band counts over those 19 dots are 9 on-boundary / 9 middle / 1 interior, i.e. the letter of the
pre-registered 60% rule says **MIXED rather than BOUNDARY-OWNED**, because the 2 s cut is too tight for a
seam whose width is itself 0.7-4.3 s. What decides the lane is the structural fact: **the reference dots
physically sit on material we dropped**, and the sheet whose interior they are supposedly inside is a
neighbour 0.32 mm away.

Step 1 of the merge was satisfiable and cannot be the refusal: minimum c5-to-c1 distance **0.3191 mm**,
35 points of c5 have a c1 point within rho_d = 1.0 mm and 37 the other way (within 0.5 mm: 2 and 2;
within 2 mm: 144 and 148; within 3 mm: 254 and 286). The refusal is therefore **Step 2 (rhoN 0.95) or
Step 3 (rhoInN 0.75)**. Every other cluster pair on H10 is far apart — zero points within 1 mm
(c1-c3 1.3887, c1-c4 1.4759, c1-c6 1.4905, c0-c1 3.6158, c1-c7 3.5017, c0-c5 9.9859) — so this is the
piece's only mergeable seam and the only cluster the merge could have saved.

Cluster 5 itself (`a281c.py`): 629 points spanning 21.66 / 3.20 / 1.76 mm, l3/l1 0.0812, best-fit plane
normal at 45.0 deg to the pot axis (`|n.axis|` 0.7071), local 10-NN plane normals agreeing with the global
plane at median `|dot|` 0.963 — a 22 x 3 mm thin ribbon, not a blob, meeting kept cluster 1 (27.29 / 13.98
/ 1.23 mm, `|n.axis|` 0.9581, i.e. near-perpendicular to the axis) at 0.32 mm. Axis read from
`stage/H10_diag/Dataset/Axes/Pot_H_Piece_10_Axis.xyz`; the 276 run dir has no `inputs/` tree.

### What contradicts the ticket's framing (three flags)

1. **`b_clu` is not a boundary detector.** Both Bl0 controls read mostly middle/interior because a kept
   cluster's free edge borders unclustered points; the pre-registered overturning condition assumed
   `b_clu <= 2 s` would mean "the line rides a kept cluster's edge", and on a control lane that reads
   2.4-3.5 s instead. The metric separates the two failure lanes from their controls, and that is all it
   does — its GROWTH reading on H02 had to be corroborated by the cluster labels.
2. **"The merge or the two-largest rule" conflates two stages that are not both in play.** The
   two-largest rule chooses among clusters that already exist; cluster 5 was never merged into the kept
   surface, so it never reached that choice. On H02 neither mechanism is reachable at all. Naming the
   two-largest rule as an owner on either lane would be wrong.
3. **Ticket 280's mechanism sentence needs narrowing.** "The uncovered stretch is the smoothest interior
   of Surface_1" was measured on the kept sheet; it does not establish that the reference line lies on
   kept material. On H02 that holds (35 of 35 dots in cluster 1). On H10 it does not: 15 of 19 dots lie on
   cluster 5, and the smooth kept sheet beside them is a neighbour, not the owner. The smoothness result
   stands as a property of Surface_1, not as the cause of the H10 loss.

### Recommendation (the decision is the lead's)

The lead's question has no single answer: the two failing lanes have **different owners**, on the same
pot. H02 Bl1 is a growth weld across a 14 deg rim fold that a per-step angular gate cannot refuse (52.7%
of its steps are under the gate). H10 Bl1 is a cluster the merge never kept, sitting 0.3191 mm from the
kept surface with the pair rule already satisfiable — the refusal is Step 2 or Step 3, which the dump
cannot name.

Two follow-ups, in order of cheapness:

1. **Name the rejecting test on H10** — one mesh run on Pot H 10 with `SFS_MERGE_PAIRS=1` (the ticket 276
   Phase 2 instrumentation already in the diag binary) prints nrm / curv / inner / icurv and the verdict
   per pair. Ceremony: `SFS_AXIS_FILE` must be set or the classify step falls back to size order.
2. **Measure the growth trace on H02** if the weld is to be attacked: the dump records cluster membership
   only, so the crossing step is not recoverable from it. Nothing should be decided about growth before
   that trace exists, and any gate change would move all 214 scored lanes, not just this one.

### Evidence

Run directory: `/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1730_24d9c06_p281-extent-owner/` —
`a281.py` (md5 7b989a4f50cd616cbe2502df0ac372bf; `a281_dots.tsv`, `a281_lanes.tsv`, `a281_clusters.tsv`,
`a281.log`), `a281b.py` (seam and pair census, fold angles), `a281c.py` (cluster shape, per-step gate test),
`a281d.py` (arcs, straddling-pair distribution), `a281e.py` (the coverage-split table above), plus their
logs and `run.json`. Worktree `C:/PR/worktrees/sfs/281` at `24d9c06`; nothing committed.


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

## Lead verdict (2026-10-24)

**Accepted, both lanes, and the pre-registration did what it is for.** The ticket predicted
GROWTH on both lanes and one came back on the merge side; it was reported as such rather than
bent to the prediction, which is the behaviour I want recorded.

**H02 Bl1 = growth, and the verdict does not rest on the metric.** 35 of 35 uncovered dots sit
interior to kept cluster 1, but the fact that settles it is that NO cluster on the piece lies
within rho_d = 1.0 mm of cluster 1 (nearest c1-c8 1.3712, c1-c4 1.3876, c1-c9 1.4299, c1-c6
1.5731 mm). With no qualifying pair anywhere along that rim, the merge cannot fire and the
two-largest rule has nothing to choose — these are unreachable by construction, not merely
unreached. The measured mechanism is the one that matters downstream: a real 14.13 deg fold that
arrives as a staircase (1265 straddling pairs, median step 3.23 deg, 52.7% at or below the 3.4
deg gate), which a per-step candidate-versus-frontier gate cannot refuse.

**H10 Bl1 = a cluster we never kept.** 15 of 19 uncovered dots on dropped cluster 5 (629 points,
a 21.66 x 3.20 x 1.76 mm ribbon 0.3191 mm from kept cluster 1), the other 4 nearest to it. This
is the second confirmed member of class K in the ledger, and it is NOT an extent problem: the
edge the authors drew exists, it belongs to a facet we dropped. Step 1 of Appendix A is
satisfiable there, so the refusal is Step 2 or Step 3 and the dump cannot say which.

**The three flags are accepted and they correct my framing, not the worker's work.**
1. The boundary-distance metric is a seam detector: a kept cluster's free edge borders
   unclustered points, so a lane with no neighbouring cluster reads "growth" by construction.
   Both Bl0 controls read mostly middle/interior. Recorded as a caveat that must travel with the
   numbers.
2. "The merge or the two-largest rule" conflated two stages. The two-largest rule only chooses
   among clusters that exist; on H02 nothing qualifies to merge, and on H10 c5 never became a
   candidate. Naming the two-largest rule as an owner on either lane would be wrong, and it is
   not named.
3. Ticket 280's "smoothest interior of Surface_1" is narrowed: true on H02 (35/35 in cluster 1),
   false on H10 (15/19 on c5, the smooth kept sheet 0.32 mm away). Smoothness is a property of
   the sheet, not the cause.

**One hypothesis recorded, deliberately not acted on:** the same per-step gate fails in opposite
directions here — too permissive on H02's graded fold, and refusing H10's clean 45 deg facet where
the paper's own rho_n = 0.95 requires >= 18.2 deg agreement. If that is right, "repair the merge"
is not the fix for H10 (merging c5 into c1 would be against the paper's rule) and no threshold on
the same quantity is the fix for H02. Any growth change moves all 214 scored lanes.

**Next step is a decision, not a build, and it is the lead's to bring to the user:** name the
refusing test on H10 with one mesh run of the ticket 276 Phase 2 instrumentation
(SFS_MERGE_PAIRS=1, SFS_AXIS_FILE set, or classify falls back to size order), and/or take a
growth trace on H02 before touching a gate that every scored lane depends on.
