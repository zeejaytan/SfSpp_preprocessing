# 74 — Stop the break face at the three places it enters: cluster merge, growth, refinement

**What to build:** first a read-only correction stage, because Ticket 73's Stage 0 was
wrong in two ways, then three default-off arms that close the three doors the break face
comes through, tested one at a time and then together, on the 3x Juglet. **Stage 0** fixes
the attribution script (a branch-order bug made the "merged" origin unreachable and
reported 0 on every sherd) and tabulates every `mergePaper234` event on the nine sherds and
on Pot A. **Arm M** stops a break-face cluster being merged into the interior wall by
judging the two clusters as whole sets, not by one median point pair. **Arm G** makes the
growth judge a candidate's turn over a real chord (1.5 mm) against that chord's own angle
bound, instead of comparing a chord turn against a single-step limit. Both arms keep the
refinement gate from Ticket 73 at a tight angle. **Arm GM** runs both, because once Arm G
splits the break face off on sherds 6-8, Arm M is what stops the merge gluing it back on.

**Answers:** E1
**Depends on:** 72 (the trim, landed c27284c), 73 (the attribution, landed 9ff83e7), 59 (the
ray-pair signal), 328 (the wall side)
**Budget:** medium. Four 3x cells, three 1x cells, three Pot A cells, one read-only stage.

**Status:** ready-for-agent
**Working in:** chat on Thinkbook16 (2026-11-15)
**Branch:** to be created at dispatch
**Worker:** unassigned

## Given — what the numbers already say

1. **On the nine sherds there are exactly three merges**, from the stage dumps of the
   Ticket 73 run `20261115-2005_b394663_t73-arms` (`out/off3x_dump/<piece>/r3_after_merge.json`,
   one JSON per piece, written by the dump writer at `mesh_processing_headless.cpp:1846`):

   | piece | merge | pairs | nDot | inNDot | inC | what it is |
   |---|---|---|---|---|---|---|
   | 5 | 1190 -> 15895 | 61 | 0.9635 | **0.9776** | 0.00430 | break-face cluster into the interior wall |
   | 6 | 230 -> 766 | 11 | 0.9687 | 0.9331 | 0.04310 | small fragment into a small cluster, not the wall |
   | 9 | 102 -> 3915 | 46 | 0.9842 | 0.9172 | 0.00066 | benign: 0.36 mm nearest-neighbour, same surface |
   | 1, 2, 3, 4, 7, 8 | none | 15 / 45 / 78 / 21 / 66 / 28 tested | - | - | - | - |

2. **Sherd 5's merge is the only one that puts a differently oriented cluster into the
   interior wall.** Reading the pre-merge dump `r2_clusters_premerge.ply` (lead's script
   `C:/PR/artifacts/t74/merge_census.py`, on the copies fetched to
   `C:/PR/artifacts/t74/dump3x/`): the 1 190-point cluster's own points are a **mean-normal
   angle of 27.89 deg** from the 15 895-point cluster, **53.4 % of them sit below dot 0.75**
   against that cluster's mean normal, the median nearest-neighbour distance between the two
   sets is 1.25 mm, and their centroids are 10.3 mm apart. The conservator's independent
   read of the same dump: the 15 895-point cluster has **0 points more than 0.8 mm off the
   inner wall**, and all 300 off-lip points on the sherd live in the 1 190-point cluster.

3. **So `rhoInN` is not the lever, and this is a correction to the proposal.** The paper's
   internal check (`mesh_processing_headless.cpp:3875-3876`) compares the normals of the two
   clusters' *median internal points* and the Sherd 5 merge **passed it at dot 0.9776**
   (12.1 deg). Lowering `SFS_PAPER_RHOINN` (it exists, `:5808`) from 0.75 to anything that
   still admits the two other events (0.9331 and 0.9172) does not stop Sherd 5. What
   separates is a **cluster-level** term computed over the members: mean-normal dot 0.884
   (sherd 5, the bad one) against 0.891 (sherd 6, small-small) and 0.991 (sherd 9, benign).
   Arm M must therefore test a new cluster-level agreement term, not only a tighter
   `rhoInN`; a tighter `rhoInN` alone is expected to do nothing, and the ticket must show
   that or refute it.

4. **Ticket 73's Arm B tested the chord turn against the wrong limit.** Its 5 mm mean-normal
   turn was compared against `thetaDeg` at `:3695` (3.87-6.77 deg), where the measured wall
   turn over 5 mm is 22.8-27.2 deg and the off-lip turn 48.4-67.0 deg. That is why piece 1
   lost its interior (Surface_0 91 733 -> 6 753 points) and why Arm B is no evidence against
   a chord rule. The new arm needs its own bound, and the bound must be derived in Stage 0.

5. **The refinement is the third door.** In the trim-armed run, 39 of the 69 off-lip dots
   (56.5 %) were added back after the growth and the merge by
   `improveSurfaceBoundaryByFittingBSplineSurface` (19 by its own patch's fit, 20 from
   another cluster). Ticket 73's Arm A gated it at 40 deg and moved the pooled count only
   86 -> 82, because the pre-refinement cluster already covers the break face under the dot
   (80 of 86 dots have a grown or merged cluster point within a median 0.24 mm, 0.93-1.74 mm
   off the inner wall). A gate is a backstop, not the cure.

6. **`attrib73.py` has a branch-order bug** (`C:/PR/artifacts/t73/attrib73.py:117-121`):
   `if in_surf0 and r2c == 1: return "grown"` is tested before `if in_surf0 and r3c == 2:
   return "merged"`, so every merged point is counted as grown and "merged 0" was reported
   for every sherd. Correct order: r3c == 2 first.

7. **Pot A has no stage dumps in the Ticket 73 arms** (only the 3x Juglet arm ran with
   `SFS_DUMP_STAGE`). The lead has submitted a Pot A dump cell (job 35130532, arm 8 with the
   dump armed, `submit_potadump.sbatch` in the Ticket 73 run directory); Stage 0 must read
   its `r3_after_merge.json` files, and the baseline Pot A arm's own log shows one merge
   (P07, 51 -> 348).

8. **3x stays** (conservator's ruling, 2026-11-15): the sherds 5-8 defect is measured at 3x
   and the 1x arm is the control ruler only.

## Part A — Stage 0, read-only (stop rules bind)

**A1. Fix the attribution.** Correct `attrib73.py:117-121` to test `r3c == 2` before
`r2c == 1`, re-run it on the existing Ticket 73 dumps, and record the origin split per
sherd. Expected, from the census above: sherd 5 has 1 190 merged points, sherds 6 and 9
230 and 102, every other sherd 0. If the recount still shows 0 merged on sherd 5, stop and
say why.

**A2. The merge census.** Write `C:/PR/artifacts/t74/merge74.tsv`, one row per merge
*event*, columns
`arm, piece, tested_pairs, from_size, into_size, boundary_pairs, nDot, inNDot, inC, cluster_mean_dot, frac_member_dot_lt_075, nn_median_mm, into_is_wall, verdict`.
Cover the nine 3x sherds, the Pot A dump arm (job 35130532), and the 1x Juglet arm if a dump
exists. `cluster_mean_dot`, `frac_member_dot_lt_075` and `nn_median_mm` are computed from
`r2_clusters_premerge.ply` exactly as the lead's `merge_census.py` does (mean unit normal per
cluster, per-member dot against the other cluster's mean, cKDTree nearest neighbour).
`into_is_wall` = the receiving cluster is the interior wall (on the Juglet: size > 5 000 and
0 points more than 0.8 mm off the inner wall). `verdict` in {`same-wall`, `break-face`,
`small-small`}.

**Stop rule A2:** if `cluster_mean_dot` does not separate sherd 5's `break-face` event from
every `same-wall` event with a gap of at least 0.03, stop and record
`the-census-does-not-separate` rather than arming a gate.

**A3. The chord-turn distribution.** On all nine sherds at chords of 1.5 and 3.0 mm, report
the turn of the mean normal over the chord for (a) points on the inner wall (d_inner <= 0.2
mm) and (b) off-lip points (d_inner > 0.8 mm): median, p90 and p95 per class and pooled.
This sets `SFS_GROW_BASE_THETA_DEG`; report the value chosen and the margin to both classes.
The conservator's figures to reproduce or refute: 1.5 mm wall median 5.5-6.9 deg (p90
12.0-14.2), lip crease 26.5-35.4 (p90 35.4-63.2); 3.0 mm wall 26.7, off-lip 48.9.

## Part B — three arms, default off, no threshold change when unset

**Arm M — a cluster-level merge gate.** Add `SFS_MERGE_CLUSTER_DOT` (default `0.0` = off,
so every existing run is unchanged). In `mergePaper234` (`:3883`), after the existing tests
pass, refuse the merge when the mean unit normal over each cluster's member points gives a
dot below the switch value. Print one `[SFS-74] MERGEGATE` line per refused pair with the
dot and the two sizes, and count refusals per piece. Keep `SFS_PAPER_RHOINN` untouched; the
ticket's question is whether the cluster-level term adds anything the paper's median-point
term has not. Arm M also runs `SFS_REFINE_ADD_GATE=1 SFS_REFINE_ADD_ANGLE_DEG=12`.

**Arm G — the chord turn with its own bound.** Add `SFS_GROW_BASE_THETA_DEG` (default `0.0` =
use today's `thetaDeg`, so the unset path is unchanged) and use it at the chord check
`mesh_processing_headless.cpp:3695` in place of `thetaDeg` **only when the chord term
replaced the per-step angle** (`used73`, the `cnt73 >= 3` branch at `:3683-3689`). Keep the
per-step check as a second, independent test (both must pass). `SFS_GROW_BASE_MM=1.5` and the
Stage 0 angle. Arm G also runs the refinement gate at 12 deg.

**Arm GM — both.**

Cells (each a cell of the existing driver `run_cell66.sh`, one array task each):

| cell | 3x Juglet | 1x Juglet | Pot A 1x |
|---|---|---|---|
| off (baseline) | nine pieces, no switch | nine pieces, no switch | eight pieces, no switch |
| M | nine pieces | nine pieces (J1 ruler) | eight pieces |
| G | nine pieces | nine pieces (J1 ruler) | eight pieces |
| GM | nine pieces | - | eight pieces |

3x inputs: `MESH_ROOT=/data/gpfs/projects/punim2657/SfSpp/runs/20261112-0218_b1e1580_t331-large`
(`mesh_large`, `cloud_mesh`, `pins/MANIFEST_JUGLET_LARGE.tsv`), `AXIS_DIR=/data/gpfs/projects/punim2657/Dataset/Juglet_large`,
`POT_NAME=Juglet_large`, `WORNESS=0.7`. 1x: `POT_NAME=Juglet`, `CLOUD_DIR=Dataset/Point/Juglet`,
`AXIS_DIR=Dataset/Axes/Juglet`, `MANIFEST=Dataset/Point/Juglet/MANIFEST_JUGLET_CC.tsv`. Pot A:
`POT_NAME=Pot_A`, clouds `original_samples/SfS_pp/Point/Pot_A`, axes `Dataset/Axes/Pot_A`,
manifest pinned from the clouds (Pot A ships none; say so).

## Part C — the gate

Write `C:/PR/artifacts/t74/gate74.tsv` (columns `group, metric, piece, off, M, G, GM, ref, verdict`)
with groups `primary` (off-lip dots and mm at 0.8 mm on sherds 5-8), `pairs` (the nine
touching pairs' median normal dot and opposed count, against Ticket 328's values),
`j1_ruler` (blind stretch, far-skin share, ring coverage, reverse coverage from
`/data/gpfs/projects/punim2657/SfSpp/runs/20261102-0450_05be12c_t57-sweep/check_separation.py`),
`pota` (dot counts and line length per piece), `coverage` (9 of 9 surfaces and lines every
arm) and `identity` (switches off vs the Ticket 73 off arm: pieces 2, 3, 4, 9 byte-identical
in 3x; state the metric).

Bars:

- Sherd 5: off-lip dots at 0.8 mm **<= 2 of 150** (baseline 21).
- Sherd 7: off-lip contour **< 12 mm** (baseline 31.2 mm shipped / 31.8 off_3x).
- Sherds 6 and 8: off-lip dots **not worse** than baseline (3 and 9).
- All nine surfaces and both lines present in every armed cell.
- Pair 1-4 **positive with 0 opposed dots**, 6-7 unchanged, no other pair moved by more
  than 0.10.
- J1's ruler: **no column worse by more than 10 %** than the off arm.
- Pot A: every piece within 1 dot of the off arm, 8 of 8.
- Render `C:/PR/artifacts/t74/render74_before_after.png`: per sherd 5-8 and Pot A, before
  above and the winning arm below, with the off-lip dots marked.

## Part D — readings (exactly one)

- `cluster-gate-cures-sherd-5-and-chord-growth-cures-6-8` — Arm GM passes the bars, and Arm
  M alone moves sherd 5 while Arm G alone moves 6-8.
- `the-merge-gate-is-the-cure-and-growth-is-not` — M alone passes the primary bars.
- `the-chord-growth-is-the-cure-and-merge-is-not` — G alone passes.
- `neither-arm-cures-the-line` — no arm passes the primary bar; say which doors stayed open.
- `the-census-does-not-separate` — Stop rule A2 fired.

## Part E — acceptance

- [ ] `attrib73.py` fixed and re-run; the origin split recorded per sherd, with sherd 5's
      1 190 merged points recovered (or the reason it is not).
- [ ] `merge74.tsv` present with the columns above, every event from the nine sherds, the
      Pot A dump arm (job 35130532 or its successor) and the 1x arm if dumped.
- [ ] Stage 0's chord-turn table present, with the chosen `SFS_GROW_BASE_THETA_DEG`, its
      margin to both classes, and the conservator's figures marked reproduced or refuted.
- [ ] `SFS_MERGE_CLUSTER_DOT` and `SFS_GROW_BASE_THETA_DEG` both default to the unchanged
      path, proven by a cell run with them unset that matches the off arm.
- [ ] Every cell's job ID, `sacct` State/ExitCode and run directory recorded; a run
      directory `runs/<YYYYMMDD-HHMM>_<git7>_t74-...` with `run.json` and `submit.sbatch`.
- [ ] `gate74.tsv`, the render, and exactly one reading slug.
- [ ] Off-path identity: the switches off reproduce the Ticket 73 off arm on the stated
      metric, blank noise stated.
- [ ] One End state line naming `ready`, `incomplete`, `blocked` or `stopped`.
- [ ] No commit; the ticket is the only file changed under `.scratch/`.

## Out of scope

- The trace guard (Tickets 75/78 in the Pot A lane) — still closed as a direction.
- Any threshold sweep on `thetaDeg` itself, `rhoInN` alone, or the curvature gate.
- Any change under `class/`, `hpc/` or the assembler; any edit to `Dataset/` or the pinned
  3x tree; any edit to `run_cell66.sh` itself (copy it if a step must change).
- Claiming a cure from the 1x arm alone; 3x is the measurement, 1x is the ruler.
