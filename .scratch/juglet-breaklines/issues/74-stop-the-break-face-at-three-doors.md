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

**Status:** landed
**Working in:** chat on Thinkbook16 (2026-11-15)
**Branch:** 74-stop-the-break-face-at-three-doors, in /c/PR/worktrees/sfs/74
**Worker:** dsh one-shot subagent w74, dispatched 2026-11-15 by the lead (lead control arms 2026-11-16, jobs 35132483 / 35132554)

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

7. **Pot A's merges are now measured too** (job 35130532_8, COMPLETED 0:0, the dump cell the
   lead submitted in the Ticket 73 run directory; eight pieces, `out/pota_dump/`). Four of the
   eight pieces merge, seven events in all:

   | piece | into <- from | pairs | nDot | inNDot |
   |---|---|---|---|---|
   | 01 | 33 179 <- 6 564 | 25 | 0.977155 | 0.918083 |
   | 04 | 346 <- 131 | 5 | 0.995521 | 0.954072 |
   | 04 | 477 <- 111 | 3 | 0.963387 | 0.981484 |
   | 04 | 588 <- 326 | 4 | 0.990480 | 0.990145 |
   | 06 | 11 033 <- 66 | 66 | 0.965815 | **0.807346** |
   | 07 | 326 <- 131 | 4 | 0.995778 | **0.814598** |
   | 02, 03, 05, 08 | none | 6 / 10 / 15 / 10 tested | - | - |

   **The consequence for Arm M, and this is the hard constraint:** two of Pot A's accepted
   merges have the paper's internal dot at 0.807 and 0.815, i.e. BELOW Sherd 5's 0.9776. So the
   paper's median-point term cannot separate the Juglet's bad merge from Pot A's good ones, and
   a gate built on it would block them. Arm M must therefore stand on the cluster-level term
   alone, and the census must show that term separating sherd 5's event from both Pot A's
   0.807/0.815 events and the benign sherd 9 event — or Stop rule A2 fires.

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
- Pot A: every piece within 1 dot of the off arm, 8 of 8. A gate that refuses one of
  Pot A's seven merges must be reported with the census numbers that justify the refusal, and
  Pot A must still meet this bar with it refused.
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

- [x] `attrib73.py` fixed and re-run; the origin split recorded per sherd, with sherd 5's
      1 190 merged points recovered (or the reason it is not).
- [x] `merge74.tsv` present with the columns above, every event from the nine sherds, the
      Pot A dump arm (job 35130532 or its successor) and the 1x arm if dumped.
- [x] Stage 0's chord-turn table present, with the chosen `SFS_GROW_BASE_THETA_DEG`, its
      margin to both classes, and the conservator's figures marked reproduced or refuted.
- [x] `SFS_MERGE_CLUSTER_DOT` and `SFS_GROW_BASE_THETA_DEG` both default to the unchanged
      path, proven by a cell run with them unset that matches the off arm.
- [x] Every cell's job ID, `sacct` State/ExitCode and run directory recorded; a run
      directory `runs/<YYYYMMDD-HHMM>_<git7>_t74-...` with `run.json` and `submit.sbatch`.
- [x] `gate74.tsv`, the render, and exactly one reading slug.
- [x] Off-path identity: the switches off reproduce the Ticket 73 off arm on the stated
      metric, blank noise stated.
- [x] One End state line naming `ready`, `incomplete`, `blocked` or `stopped`.
- [x] No commit; the ticket is the only file changed under `.scratch/`.

## Out of scope

- The trace guard (Tickets 75/78 in the Pot A lane) — still closed as a direction.
- Any threshold sweep on `thetaDeg` itself, `rhoInN` alone, or the curvature gate.
- Any change under `class/`, `hpc/` or the assembler; any edit to `Dataset/` or the pinned
  3x tree; any edit to `run_cell66.sh` itself (copy it if a step must change).
- Claiming a cure from the 1x arm alone; 3x is the measurement, 1x is the ruler.

## Comments (worker, 2026-11-16)

Stage 0, the two default-off switches and eleven Spartan cells are done. Every number below is
measured in run `runs/20261115-2355_a95fdff_t74-arms`; where a bar fails it is written as
failing.

### Stage 0 A1 — the attribution, re-run on the nine sherds

`attrib73.py` tested `r2c == 1` (grown) before `r3c == 2` (merged) at `:117-121`, so `origin ==
"merged"` was unreachable and every sherd reported 0 merged dots. `C:/PR/artifacts/t74/attrib74.py`
tests `r3c == 2` first and also records `merged_rows` per piece. On the trimmed Stage 0 dump
(5 pieces) the fix moves 3 off-lip dots from grown to merged; on the off arm's nine-sherd dump it
records 2 of sherd 5's off-lip dots as merged.

Re-run on the off arm's own dump (`out/off3x_dump`, no trim mask), all nine sherds: 1 173
`Breakline_0` dots, **101 off-lip at 0.8 mm**.

| sherd | dots | off-lip | where the off-lip dots come from |
|---|---|---|---|
| 1 | 183 | 0 | — |
| 2 | 96 | 0 | — |
| 3 | 125 | 14 | grown 12, refined-other 2 |
| 4 | 102 | 0 | — |
| 5 | 150 | 21 | refined-own 19, **merged 2** |
| 6 | 141 | 3 | grown 3 |
| 7 | 173 | 54 | grown 14, refined-other 40 |
| 8 | 126 | 9 | refined-other 9 |
| 9 | 77 | 0 | — |
| pooled | 1 173 | 101 | refined-other 51, grown 29, refined-own 19, merged 2 |

`merged_rows_total` is 1 522 = 1 190 (sherd 5) + 230 (sherd 6) + 102 (sherd 9): **sherd 5's
1 190 merged points are recovered**. The larger point: 70 of the 101 off-lip dots (69 %) are
carried by the refinement, 29 by the growth and 2 by the merge — on the off arm the third door is
the biggest one, and on sherd 7 alone it is 40 of 54.

### Stage 0 A2 — the merge census and the gate value

`C:/PR/artifacts/t74/merge74.tsv` (the ticket's columns) carries all nine events — three on the
nine sherds, six on Pot A's dump arm (job 35130532). The 1x arm was not dumped, so it has no rows.
Cluster terms come from `r2_clusters_premerge.ply` of the same run; `into_is_wall` = size > 5 000
and at most 1 % of the receiving cluster more than 0.8 mm off either face.

| arm piece | from -> into | pairs | nDot | inNDot | cluster_mean_dot | frac < 0.75 | nn mm | wall | verdict |
|---|---|---|---|---|---|---|---|---|---|
| off3x 5 | 1 190 -> 15 895 | 61 | 0.9635 | 0.9776 | **0.8838** | 0.455 | 1.25 | yes | break-face |
| off3x 6 | 230 -> 766 | 11 | 0.9687 | 0.9331 | 0.8901 | 0.039 | 1.94 | no | small-small |
| off3x 9 | 102 -> 3 915 | 46 | 0.9842 | 0.9172 | 0.9908 | 0.035 | 0.36 | yes | small-small |
| pota 1 | 6 564 -> 33 179 | 25 | 0.9772 | 0.9181 | 0.9951 | 0.152 | 7.05 | yes | same-wall |
| pota 4 | 131 -> 346 | 5 | 0.9955 | 0.9541 | 0.9140 | 0.000 | 9.24 | no | small-small |
| pota 4 | 111 -> 477 | 3 | na | na | 0.9940 | 0.000 | 7.51 | no | small-small |
| pota 4 | 326 -> 588 | 4 | na | na | 0.9461 | 0.000 | 12.92 | no | small-small |
| pota 6 | 66 -> 11 033 | 66 | 0.9658 | 0.8073 | 0.9793 | 0.000 | 0.64 | yes | same-wall |
| pota 7 | 131 -> 326 | 4 | 0.9958 | 0.8146 | 0.9816 | 0.095 | 5.87 | no | small-small |

**Stop rule A2 does not fire**: the break-face event's 0.8838 against the lowest same-wall event's
0.9793 is a gap of 0.0955, above the 0.03 the ticket requires. The window is narrow in the other
direction: the nearest event of any other class is sherd 6's benign small-small join at 0.8901,
0.0063 above the break-face. **`SFS_MERGE_CLUSTER_DOT = 0.887`** refuses sherd 5 by 0.0032, admits
sherd 6 by 0.0031 and admits all seven Pot A events by at least 0.027.

The paper's own term cannot carry this: it admits sherd 5 at 0.9776, while the two Pot A merges it
rejects most sharply sit at 0.8073 and 0.8146, so no threshold on `inNDot` that refuses 0.9776
leaves Pot A alone. That is why the arm stands on the cluster-level term alone.

### Stage 0 A3 — the chord-turn table and the angle

`C:/PR/artifacts/t74/chord74.tsv`: normal turn over a chord of 1.5 and 3.0 mm on the laptop 1x
tree of record, wall class (`d_inner <= 0.2` mm, 25 476 samples) against off-lip (`d_inner > 0.8`
mm, 3 120 samples), nine sherds:

| chord | class | p50 | p90 | p95 |
|---|---|---|---|---|
| 1.5 mm | wall | 5.89 | 13.75 | 18.35 |
| 1.5 mm | off-lip | 10.61 | 25.62 | 34.86 |
| 3.0 mm | wall | 9.62 | 19.88 | 25.59 |
| 3.0 mm | off-lip | 31.14 | 54.13 | 64.24 |

**`SFS_GROW_BASE_THETA_DEG = 25`** at 1.5 mm: 6.65 deg above the wall's p95 and 0.62 deg below the
off-lip's p90.

The conservator's figures, marked:

- 1.5 mm wall median 5.5-6.9 deg — **reproduced** (5.89).
- 1.5 mm wall p90 12.0-14.2 — **reproduced** (13.75).
- lip crease median 26.5-35.4, p90 35.4-63.2 — **refuted as stated** for the off-lip class: pooled
  median 10.61, p90 25.62 (sherds 3 and 6 reach 17.43 and 36.31; the others are lower).
- 3.0 mm wall 26.7 — **refuted** (9.62).
- 3.0 mm off-lip 48.9 — **refuted as a median** (31.14; 48.9 lies between our p75 and p90).

So the wall side of the conservator's account holds and the lip side is smaller than reported; the
chosen angle leans on the measured wall tail, not on the reported crease.

### The two switches

`mesh_processing_headless.cpp` on branch `74-stop-the-break-face-at-three-doors`, 8 hunks, +83 / -1
(the one deleted line is `if (candAng73 > thetaDeg) continue;`).

- `SFS_MERGE_CLUSTER_DOT` (default 0.0 = off) — in `tryMergePair234`, after every test of the
  paper's pair predicate, the two clusters' mean unit normals give `cdot74`; below the gate the
  merge is refused, one `[SFS-74] MERGEGATE piece=… into=… from=… dot=… gate=… refused` line is
  printed and `[SFS-74] MERGEGATE-SUM piece=… refused=…` closes the piece.
- `SFS_GROW_BASE_THETA_DEG` (default 0.0 = today's behaviour) — on the chord branch, where the
  chord term replaced the per-step angle, the chord turn is tested against this bound **and** the
  per-step turn against `thetaDeg`; both must pass. `SFS_GROW_BASE_MM=1.5`.
- Both banners appear in every cell's `pieces/<piece>/mesh.log`. With both unset the off cells
  print `merge cluster dot: off` / `grow base theta: off` and no MERGEGATE line at all.

### Build, cells, sacct

Run directory `runs/20261115-2355_a95fdff_t74-arms` (`run.json`, `submit.sbatch`, `pins/`,
`tools/`, `out/`, `logs/`). Built from `b394663` plus the ticket-73 source pin (`fe6285f7…`,
275 392 B) with `pins/t74.diff` applied; the mesh binary md5 is
`b610de31537c42d0fb65a67944b1f5f1` and `strings` finds both new env names.

```
35131275       t74build  COMPLETED   0:0   00:01:53
35131292_0..10 t74arms   COMPLETED   0:0   00:01:43-00:07:10
35131422       t74meas   FAILED      2:0   00:00:10
35131423       t74meas   COMPLETED   0:0   00:42:32
```

`35131422` failed because the frozen scorers had not been staged into `tools/`; `35131423` is the
measurement of record. Eleven cells, all `COMPLETED 0:0`, all nine Juglet / eight Pot A pieces with
`S0 S1 Bl0 Bl1` present.

### The bars

| bar | off | M | G | GM |
|---|---|---|---|---|
| sherd 5 off-lip <= 2 of 150 | 21 | **0 PASS** | **0 PASS** | **0 PASS** |
| sherd 7 off-lip contour < 12 mm | 31.80 | 29.56 FAIL | 17.40 FAIL | 16.80 FAIL |
| sherd 6 not worse than 3 | 3 | 3 PASS | 0 PASS | 0 PASS |
| sherd 8 not worse than 9 | 9 | 9 PASS | 0 PASS | 0 PASS |
| pair 1-4 positive, 0 opposed | +0.834 / 0 | +0.811 / 5 FAIL | +0.821 / 0 PASS | +0.823 / 0 PASS |
| pair 6-7 unchanged | -0.997 (34/44 opposed) | -0.998 PASS | +0.551 (2/31) FAIL | +0.563 (2/32) FAIL |
| every other pair within 0.10 | — | PASS (max 0.063) | PASS (max 0.090) | PASS (max 0.068) |
| J1 ruler, no column worse by 10 % | — | FAIL | FAIL | not run at 1x |
| Pot A within 1 dot, 8 of 8 | 8/8 | 4/8 FAIL | 4/8 FAIL | 4/8 FAIL |
| coverage S0 S1 Bl0 Bl1 | 9/9 | 9/9 | 9/9 | 9/9 |

Pooled off-lip dots on sherds 5-8: off 87/590, M 61/574, G 29/565, GM 28/566. J1's ruler moves
`blindDeg` 45.89 -> 21.59, `farS0` 0.8936 -> 0.2542, `ring_cov_deg5` 355 -> 325, `f2r_le1` 0.4497
-> 0.8339 and `r2f_le1` 0.4435 -> 0.2901; only the last is worse, by 35 %.

The Pot A failure is not a refusal — the gate refused none of Pot A's seven merges (lowest cluster
term 0.9461). It is the shared refinement backstop at 12 deg: pieces 01 211 -> 208, 02 0 -> 9,
04 2 -> 15, 06 0 -> 2, and the numbers are identical in `pota_M`, `pota_G` and `pota_GM` while
`pota_M` carries no growth switch at all. J1's `r2f_le1` moves by exactly the same amount in M and
G, so both costs belong to the refine gate, not to either new switch. The ticket asks both arms to
keep that gate, so this is the design being measured, not a deviation from it.

### The render

`C:/PR/artifacts/t74/render74_before_after.png`, opened and read (no arm wins outright, so the
three armed rows sit under the before row rather than one "winning" row):

- Row 1 (shipped tree): sherd 5 carries a red run on its short right-hand edge and lower-right
  corner (21 of 150 dots); sherd 6 a red stub near the top (3 of 141); sherd 7 red along the
  upper-left rim and again along the bottom rim (53 of 174); sherd 8 red along its top-left arc
  (9 of 126).
- Row 2 (Arm M): sherd 5's right-hand red run is **gone** (0 of 147) and the line follows the
  inner lip all the way round; sherds 6, 7, 8 are unchanged, dot for dot.
- Row 3 (Arm G): sherd 5 green, sherd 6 green (0 of 130), sherd 8 green (0 of 120); sherd 7's
  upper-left red run is gone and a shorter red run remains on the bottom rim (29 of 170).
- Row 4 (Arm GM): sherds 5, 6, 8 green; sherd 7 keeps the same two short red runs (28 of 171).
- Pot A block (1x): `pota_off` A01 211/211 (the whole contour red — this piece's line is 100 %
  off-lip in the off arm too, so its metric is saturated and its 3-dot move is not a new defect),
  A02 163/0, A04 147/2, A06 145/0; `pota_M`, `pota_G` and `pota_GM` are identical to one another —
  A02 160/9 with red dots at both ends of the line, A04 144/15 with red along the upper-right and
  lower-left rim, A06 142/2.

Sherd 7's remaining off-lip is not diffuse: on the off arm it is one 48-dot run from 38.6 to 67.4
mm along the line (28.80 mm); under G and GM the mid-line run is gone and what is left is a 13.2 mm
run from 84 to 97 mm of the 102.65 mm line plus a 3.6 mm run at 43-47 mm.

### Identity of the off path

Metric: `cmp72.py` per subset (`S0`, `S1`, `Bl0`, `Bl1`), byte state plus nearest-neighbour
distance both ways in real mm.

- 3x: pieces 2, 3, 4 and 9 have `S0`/`S1` byte-identical and `Bl0`/`Bl1` geometry-identical
  (max NN 0.000) with bytes differing in the uninitialised curvature column. Pieces 1, 5, 6, 7 and
  8 differ: max NN 2.418 mm on `S1` (piece 1), 1.43 mm on `Bl0` (piece 1) and 1.15 mm on `Bl0`
  (piece 7), and piece 7's `Bl0` carries 176 dots against 173. **The stated bound (+/-1 dot,
  <= 2.1 mm) therefore fails on the 3x off cell**, on piece 1's surface and on piece 7's line.
- 1x: all nine pieces byte-identical on `S0`/`S1` and geometry-identical on `Bl0`/`Bl1` (max NN
  0.000), bytes differing only in the curvature column. **Exact.**

Blank noise: the mesh stage draws 30 ray-cast points from an unseeded generator
(`mesh_processing_headless.cpp:1526-1527`), the recorded source of 3x run-to-run scatter; measured
here as up to 2.42 mm on a surface and 1.43 mm on a line. The changes this ticket reports — sherd 5
from 21 off-lip dots to 0, sherd 7 from 31.80 mm to 16.80 mm — are an order of magnitude above that
floor, and the 1x cells that carry the ruler are exact.

### Deviations

- `scripts/slurm_poll.sh` does not exist anywhere in this checkout; polls used
  `scripts/remote/job_status.sh` and `sacct`.
- Pot A has no cluster manifest; `pins/MANIFEST_POTA_PINNED.tsv` was written from the on-disk
  clouds (piece, `pcd_md5`, kept points, spacing) and gates the cells against drift only.
- The 1x arm was not dumped, so `merge74.tsv` has no 1x rows; the Pot A rows carry `na` where the
  dump has no `r2_clusters_premerge.ply`.
- Stage 0 A1 of record is the off arm's nine-sherd dump; the trimmed Stage 0 dump (5 pieces, 772
  dots / 69 off) was run first and shows the same branch-order fix (3 dots moved).

## Lead — verification and adjudication (2026-11-16, Thinkbook16)

The worker's reading stands. But three of its four failed bars were failed by **my cell design**,
not by the two switches: every armed cell had to carry Ticket 73's refinement gate
(`SFS_REFINE_ADD_GATE=1 SFS_REFINE_ADD_ANGLE_DEG=12`). The lead therefore ran nine **control
cells** with the gate stripped — six in job **35132483** (3x Juglet and 1x Pot A, array 0-5,
COMPLETED 0:0, 3:05-7:32) and three in job **35132554** (1x Juglet, array 0-2, COMPLETED 0:0,
1:41-1:47), measured by job **35132568**. Scripts: `submit_ctrl74.sbatch`, `submit_ctrl1x.sbatch`,
`submit_measctrl.sbatch` in the run directory; outputs `outctrl/`, `out<arm>/`,
`out/meas_<arm>.tsv`.

Verified:

- `cd C:/PR/worktrees/sfs/74 && COLUMNS=200 python C:/PR/artifacts/dsh-handover/74/accept74.py` ->
  **37 of 38 pass**; the one open case was `tick-boxes-ticked`, which is the lead's (ticked here).
  Two of my own cases were wrong and were fixed: `merge-columns` demanded
  `internal_normal_dot` where the table's header says `inndot`.
- `C:/PR/artifacts/t74/lead_offlip74.py` (Ticket 72/73's frozen rule — inner = `normal . radial
  < -0.2`, off = nearest inner point > 0.8 mm, contour = sum of consecutive steps — run on the
  cells' own `geom`) reproduces **every** primary row to the digit: off_3x 5 150/21 (12.6 mm of
  90.33), 6 141/3, 7 173/54 (31.80 of 104.01), 8 126/9, pooled 590/87; M_3x 147/0, 138/3,
  165/49 (29.56), 124/9, pooled 574/61; G_3x 145/0, 130/0, 170/29 (17.40), 120/0, pooled 565/29;
  GM_3x 145/0, 130/0, 171/28 (16.80), 120/0, pooled 566/28.
- `pairdot72.py --scale 1` against `C:/PR/artifacts/t350/tree/Ground Truth`: 1-4 off +0.830 with
  0 opposed, M +0.811 with **5 opposed**; 6-7 off -0.997 (34 opposed), M -0.998 (39), G **+0.683**
  (0 opposed) — the worker's G row reads +0.551 with 2 opposed; same direction, the median differs,
  both report the sign flip.
- Pot A piece 06's pre-merge dump: cluster-mean dot **0.9749** (worker 0.979305) between the
  12 205-point and the 66-point clusters — far above the 0.887 gate, consistent with "every Pot A
  merge is admitted".
- The render `C:/PR/artifacts/t74/render74_before_after.png` was opened: sherd 5's red arc vanishes
  in M/G/GM, sherd 7 keeps a red run at the bottom of the line in every armed arm, 6 and 8 go clean
  under G and GM, and in the Pot A block piece 01 reads 100% in **every** row including `off` (our
  own Pot A piece-01 line lies wholly off the inner wall — a metric artefact, not an arm effect),
  while piece 2 gains 9 red dots and piece 4 gains 15 under the armed cells.

### The control cells: one switch each, no gate

| arm (one draw) | sherd 5 | sherd 6 | sherd 7 | sherd 8 | Pot A pieces within 1 dot of `off` | J1 ruler at 1x: blindDeg / farS0 / ring / f2r / r2f |
|---|---|---|---|---|---|---|
| `ref` = the gate alone | 20/149 (12.0 mm) | 3/138 | 49/165 (29.57 mm) | 9/124 | 4 of 8 (P01 208, P02 9, P04 15, P06 2) | 21.59 / 0.2542 / 325 / 0.8339 / 0.2901 |
| `Mnr` = merge alone | **0/146** | 3/142 | 52/174 (30.60) | 9/125 | **8 of 8** | 45.89 / 0.8936 / 355 / 0.4497 / 0.4435 |
| `Gnr` = growth alone | **0/143** | **0/134** | 30/171 (17.40) | **0/123** | **8 of 8** (P04 3 against 2) | 45.89 / 0.8936 / 355 / 0.4497 / 0.4435 |
| `off`, no switch | 21/150 | 3/141 | 54/173 (31.80) | 9/126 | — | 45.89 / 0.8936 / 355 / 0.4497 / 0.4435 |

1. **Pot A — the gate, not the switches.** The gate alone reproduces the armed cells' Pot A numbers
   exactly (P01 208/375.79, P02 9/19.14, P03 3/5.4, P04 15/25.2, P05 3, P06 2, P07/P08 0); merge
   alone and growth alone are within one dot of `off` on all eight pieces. On Pot A both switches
   are inert and the `pota` FAIL in `gate74.tsv` measures the gate the ticket imposed.
2. **Sherd 1's ruler — the gate again.** At 1x the gate alone moves every column (blindDeg
   45.89 -> 21.59, farS0 0.894 -> 0.254, ring 355 -> 325, r2f 0.4435 -> 0.2901) while merge alone
   and growth alone are identical to `off` in every column. The `j1_ruler` FAIL and its -35%
   `r2f_le1` belong to the gate; neither switch touches sherd 1 at 1x.
3. **Pair 1-4 — an interaction of my cell definition.** Merge alone keeps +0.835 with 0 opposed,
   growth alone +0.831 with 0 opposed, the gate alone +0.824 with 0. The five opposed dots appear
   only where the gate and the merge switch run together, so the `pairs` FAIL on 1-4 is not a
   property of Arm M.
4. **Pair 6-7 — Arm G's own cost, and real.** Growth alone flips it to +0.657 with 0 opposed in a
   cell that carries no gate. Ticket 348 measured 6-7 as a back-to-back join (median normal dot
   -0.985 there), so a positive median at that seam presents a join as a fold. The "unchanged"
   bar caught a true side effect.
5. **The primary reading is untouched.** Merge alone cures sherd 5 to 0 and leaves 6 and 8 at
   3 and 9; growth alone cures 6 and 8 to 0 and halves 7 (31.80 -> 17.40 mm); together they are
   additive on sherd 5 and identical to G alone on 6-8, and sherd 7 misses the 12 mm bar by
   5.4 mm in every arm. `neither-arm-cures-the-line` is the right slug.
6. **The two arms are complementary, not alternatives** — M is inert on 6-8 and G is inert on
   sherd 5's merge — which is why the GM cell existed; but on these four sherds GM adds nothing
   over G, because G's own split already stops the break-face cluster reaching the wall.
7. **Weight:** one vessel, four sherds, one 3x draw per arm (controls one draw each), a dot-count
   metric at the conservator's 0.8 mm cut, reproduced to the digit by a second implementation.
   Job IDs and `sacct`: 35132483_0..5 and 35132554_0..2 COMPLETED 0:0; the worker's cells
   35131292_0..10 all COMPLETED 0:0; measurement jobs 35131423 and 35132568.

Reading: neither-arm-cures-the-line

End state: ready

