# 39: Does the own-mode admission keep the two faces apart?

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-10-28)
**Branch:** 39-does-own-mode-keep-the-two-faces-apart, in /c/PR/worktrees/sfs/39
**Answers:** U19
**Blocked by:** none
**Blocks:** none

## Why this exists

Ticket 38 showed that resolution is a real limiter and that the two exported surfaces are not two
faces. On evenly sampled clouds both silent sherds grow two large regions — sherd 2: 8 clusters,
surfaces of 4 155 and 3 979 points; sherd 9: 7 clusters, 2 229 and 3 512 — each surface covering the
sherd and sitting about 3 deg from the mesh. But the two surfaces then **nest**: 95 % (sherd 2) and
80 % (sherd 9) of the smaller one's points are also in the larger, and their mean normals point the
**same** way (+0.9960 / +0.9993). The pipeline prints the reason itself — the literal 3 mm boundary
admission hands each surface about half the whole sherd
(`[WINDOW-26] ... own_cluster_points=589 other_cluster_points=2237 candidates=5256 admitted_own=1610
admitted_other=1640`).

The pipeline already carries the rival rule. `SFS_REASSIGN_MODE=own`
(`mesh_processing_headless.cpp:3903-3925`) fits both clusters first and sends each candidate point to
the fitted surface it is nearer to, instead of to every surface within 3 mm. It has never been run on
clouds where the two clusters are actually separated — the one condition under which the two rules
can differ. That is this ticket.

## What to run

Two cells, one job. Regenerate the **same two clouds** ticket 38 grew on, with the stage-38
instruments already on main (`.scratch/juglet-breaklines/stage38/instruments/`: the mesh sampler, the
midpoint subdivision, the route-2 instrument gate):

| piece | level | expected points | expected median spacing |
|---|---|---|---|
| Juglet_Piece_2 | x1 | 6 259 | 0.209043 mm |
| Juglet_Piece_9 | x1 | 5 257 | 0.201511 mm |

The clouds must be checked against those two numbers **before** the cells run; if the sampler does not
reproduce them, stop and say so. (Ticket 38's own PLYs are deleted under the geometry rule; the sampler
is deterministic, so the check is count + median spacing, not a byte comparison.)

Arms, per piece:

- **A — control**: today's default, `SFS_REASSIGN_MODE=radius` (or unset). It must reproduce ticket
  38's numbers: sherd 2 surfaces 4 155 / 3 979, sherd 9 2 229 / 3 512. If it does not, the cell is
  void and the comparison cannot be made.
- **B — the test**: `SFS_REASSIGN_MODE=own`.

Everything else stays at the shipped defaults (`SFS_PAPER_CHAIN=1`, `SFS_PAPER_THETA=3.4`,
`SFS_SPACING_POLICY=piece`, no single-cluster write, no dedupe switch, no window override).

**Pot A is deliberately not in this job.** Its own-mode behaviour is a separate question, and the last
Pot A cell on the 1 000 000-point released cloud ran out the wall clock. Do not add it.

## What to measure, per cell

For **every written surface**: point count, distinct point count, extents and bounding-box diagonal
(mm), the fraction of the ORIGINAL piece's cloud within 2 mm of it, and the median folded angle to the
ORIGINAL mesh.

Between **Surface_0 and Surface_1 of the same cell**, with the corrected pair statistic that keeps the
signed component (`stage38/instruments/measure34.py`, `pair_pointwise`): `med_nn`, `med_along`,
`med_across`, `med_angle_deg`, `coin`, and the signed `med_t` with its p05/p95.

Three derived quantities, because they are what the question turns on:

1. **Shared points**: the count and fraction of the smaller surface's distinct points that also appear
   in the larger (round to 1e-4 mm), and the same the other way round.
2. **Mean-normal dot** between the two surfaces, and the median per-point folded angle between the two
   surfaces' normals at matching points.
3. **The admission line**: `[REASSIGN-22]` and every `[WINDOW-26]` line the pipeline prints for each
   cell, quoted verbatim.

## The bar the lead will read against (do not judge it yourself)

Two surfaces that are an inside and an outside of one wall should have: **shared points well under
10 %**, **mean-normal dot below -0.9** (they face opposite ways), **med_along about one wall thickness**
(Juglet 2 2.693 mm, Juglet 9 2.595 mm, ticket 35's ray measurements), and **med_across small**. Report
the numbers; the lead decides whether they meet it.

## Constraints

- **No change to tracked pipeline behaviour.** This ticket runs existing switches. If a switch is
  missing or does not do what its comment says, stop and report — do not edit `mesh_processing_headless.cpp`.
- Instruments and tables under `.scratch/juglet-breaklines/stage39/`; reuse stage 38's sampler and
  subdivision rather than writing new ones.
- Compute nodes only; **at most two jobs** (one to run, one to re-run if the first dies on plumbing).
  Split by piece, never by arm — a control that ran in a different job than its test is not a control.
- Synthetic clouds labelled synthetic in every table, figure and filename, staged inside the run
  directory only; never into the frozen corpus.
- Frozen corpus and `/opt/sfs-pristine` read-only, md5 before/after, compared; record ABSENT if absent.
- CRLF-check every script before submitting; `bash -n` the rendered batch script.
- Geometry dies with the ticket: clouds and surfaces deleted at the end with a counted record written
  **before** the delete. Keep tables, logs, per-surface jsons, the pipeline's own log lines.
- Index row with `verdict` and `human_note` left EMPTY.
- Report evidence, not verdicts: no "this shows", no Status change, no `intent/` writes, no merge.

## Evidence to report

1. The cloud check (regenerated points and median spacing beside the two expected numbers, both pieces).
2. The arm-A control against ticket 38's numbers, per piece — and a plain statement if it does not
   reproduce them.
3. The per-surface table, both arms, both pieces.
4. The pair table, both arms, both pieces, with the signed `t` and its percentiles.
5. The three derived quantities (shared points both ways, mean-normal dot, median normal angle).
6. The `[REASSIGN-22]` and `[WINDOW-26]` lines, verbatim, per cell.
7. Corpus and pristine md5 before/after; the geometry deletion record; job ids with `sacct` states; the
   pushed branch head.
8. Anything not done, with the exact command or line that failed.
