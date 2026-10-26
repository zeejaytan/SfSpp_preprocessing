# 22: the two constants that merge the walls — a 3 mm reassignment and a one-size density step

**Answers:** U19 (vessel level), E1 (preprocessing half)
**Blocked by:** none
**Status:** ready-for-agent

A ticket on the *method*, not the record. It changes `mesh_processing_headless.cpp` behind
environment switches whose defaults reproduce today's behaviour exactly, and it measures what
each switch does. Judgement stays with the lead: report evidence, do not declare a winner.

## What is already established (lead-measured, not to be re-litigated)

Run `20261027-0300_4cbb2b2_juglet-raw-vs-improved` (job 33838059), notes in that run's
`out/NOTES.md`. The old arm keeps both artefacts, so the clustering and the step after it can be
compared directly:

| piece | clustering dot | gap mm | after the boundary step: dot | share of Surface_1 on Surface_0 |
|---|---|---|---|---|
| 1 | -0.9440 | 2.141 | +0.9727 | 0.705 |
| 2 | +0.4626 | 2.506 | +0.5098 | 0.128 |
| 3 | -0.9831 | 1.898 | +0.9971 | 0.964 |
| 4 | -0.9953 | 2.136 | +0.9993 | 0.842 |
| 5 | -0.8228 | 3.328 | +0.7126 | 0.004 |
| 6 | -0.8724 | 2.547 | +0.9530 | 0.909 |
| 7 | -0.9968 | 3.433 | -0.9877 | 0.000 |
| 8 | +0.6986 | 2.571 | +0.8589 | 0.244 |
| 9 | -0.9895 | 0.750 | +0.6725 | 0.734 |

Read: **the clustering separates the two walls on seven of nine pieces** (dot -0.82 to -0.997,
walls 0.75-3.43 mm apart). Pieces 2 and 8 are fused before that step and are outside this
ticket's reach. The step that collapses the rest is
`improveSurfaceBoundaryByFittingBSplineSurface` (`mesh_processing_headless.cpp:810`): it fits a
NURBS surface to **one** cluster, then iterates **every point of the whole sherd**
(`:911`, first argument `sampledPointCloudNormal` at `:2264`) and admits a point when its
distance to that fitted surface is **< 3 mm** (`:965`, `:976`). The result replaces the cluster
(`:2265-2271`) and is what every downstream stage reads (`:2592`). Against walls 0.75-2.55 mm
apart, a 3 mm radius cannot tell the two walls apart. The only pair that survives intact, piece 7,
is the one whose walls are 3.43 mm apart. Pot A is unharmed because its walls are 3.4-4.06 mm
apart.

Two independent admissions, and the conservator has asked for both to be made adaptive:

1. **The reassignment radius is a length compared against a wall thickness.** A radius is the
   wrong shape of test: a point should belong to the wall it is nearest, not to every wall within
   3 mm.
2. **The 0.6 mm density step is one size for every sherd** (`:2547-2549`, `downsamplePointCloud`
   called with a fixed `0.6F`). On 23-63 mm Juglet sherds it leaves 787-1,467 points for both
   walls; on a 126 mm Pot A piece it is a sensible spacing. The conservator's constraint, which
   the design must keep: **the step stays, and stays a fixed physical spacing within a piece**, so
   the point cloud is uniform and every millimetre threshold downstream keeps its meaning. What
   becomes adaptive is the *value* of that spacing, per piece.

## What to build

All three switches are environment variables. **With none of them set, behaviour must be
identical to today** — that is an acceptance criterion, not a nicety.

1. `SFS_REASSIGN_MODE` = `radius` (default) | `own`.
   `own`: a candidate point may join surface A only if its distance to A's fitted spline is less
   than its distance to the *other* cluster's fitted spline. Keep the existing 3 mm and angle gates
   as outer caps. This needs both clusters' fits available before either is rewritten — the two
   calls at `:2264` and `:2269` are independent today and must not be.
2. `SFS_SPACING_POLICY` = `fixed` (default, 0.6 mm) | `piece`.
   `piece`: choose the spacing so the piece's longest extent spans a fixed number of samples:
   `S = clamp(diag / N, s0, 0.6)` where `diag` is the piece's bounding-box diagonal, `s0` the
   cloud's own median nearest-neighbour spacing (never invent density the scan does not have) and
   `N` from `SFS_SPACING_SAMPLES`. Measure **three** values of N — 100, 200, 400 — and report all
   three; the choice between them is the lead's, on the numbers.
3. `SFS_COUNT_SCALE` = `off` (default) | `auto`.
   The count thresholds were calibrated at 0.6 mm. `auto` multiplies every count threshold whose
   meaning is "points per fixed physical patch" by `(0.6 / S)^2`: `minCluster` at `:2136` and any
   other fixed `k` that is a neighbourhood size in points rather than a distance. List what was
   scaled and what was left alone, with `file:line`, in the report. Distance thresholds
   (`rhoD 1.0 mm`, `planeDistMM 2.0`, the 50 mm assembler tolerance) are **not** scaled.

## The arms to measure

For every arm, all nine Juglet pieces plus Pot A pieces 01-08 through the same surface stage:
cluster counts and sizes, whether two surfaces were written, and for each written pair the four
statistics this ticket's table uses (mean-normal dot, median cross distance, share of Surface_1
points coinciding with a Surface_0 point, fraction of the pair's normals pointing opposite).

| arm | switches |
|---|---|
| A baseline | none |
| B ownership only | `SFS_REASSIGN_MODE=own` |
| C spacing only | `SFS_SPACING_POLICY=piece` × N in {100, 200, 400}, counts scaled |
| D both | B + C |

A piece counts as **a real wall pair** when dot <= -0.9, median cross distance >= 1.5 mm and share
<= 0.05 — Pot A's own shape, stated here so nobody has to invent a bar.

## Acceptance

1. `git diff --stat main..HEAD` shows the change confined to `mesh_processing_headless.cpp`
   (plus whatever small build/instrument files it needs) — no other tracked source.
2. Defaults proven unchanged: with no switches set, the arm-A run's surfaces are identical to a
   run of the code before the change (md5 per piece, or a stated maximum displacement if byte
   equality is not achievable — say which and why).
3. The arm table above, complete, with the switches and count values used at each cell.
4. Pot A 01-08 under arm D: stated piece by piece as unchanged or changed, with the numbers.
5. Which Juglet pieces reach the wall-pair bar in which arm, and — separately — which pieces were
   already fused before the boundary step (2 and 8 at least) and therefore cannot be helped.
6. One rendered before/after of the same Juglet piece, at a scale that resolves the 2 mm wall gap,
   with the number of pixels per millimetre written on it. `visual-qa/` staging only if the lead
   asks for a conservator's eye; a ticket-local PNG is enough here.
7. Corpus md5 before and after, unchanged; geometry deleted with a counted record; nothing written
   outside the run directory and the ticket; branch pushed.

## What this cannot settle

Whether a two-surface result is *correct* — that needs the breakline and join stages, which stay
paused behind this repair. Whether an adaptive spacing is right for the corpus at large: the
scored corpus pieces are 54-173 mm, so the `piece` policy would move many of them, and no corpus
bar is measured here. Nothing about pieces 2 and 8 beyond reporting them as already fused.
