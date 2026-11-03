# stage68 STATUS (ticket 68: axis method, guard merge, densify arm)

Worker state file. LF only. Worker measurements, not lead-verified.

## Turn 4 (2026-11-03): per-pair instrument (I20N) + densify arm -- job 34268041

Run `runs/20261103-1535_ffcb350_t68-densify` (commit ffcb350; setup68c.sh, submit68c.sbatch). One job
(budget: 2 of 4). Shims identical to t67's (G `056dfb91`, GA `bc2f2aed`); substitution gate 9/9 Axes/.
I20N = t67 attitude instrument on F20N's exact inputs (t66 lanes, axes68, floor 20). Table by
`pairs68.py` from `artifacts/68/runC/out/I20N/T67_*.tsv`; same totals as F20N (35 candidates, 0/9, 0/18).

Survivors of pruning: **(1,8) idx 11** -- a GT join, the first ever to survive on the Juglet, but its pose is
137.9 deg / 24.3 mm (centroid) from the GT relative pose: axes agree (fold 3.0) and the piece is spun about
the axis. The good (1,8) candidate, idx 9 (7 dots, 12 inliers, score 0.56, rot err **27.0 deg, centroid 2.4 mm**),
dies at the axis gate (fold 38.7 > 25). **(5,7) idx 29** -- NOT a GT edge (Juglet_simple_graph row 5 =
1 1 1 1 0 0 0 0 1), yet 5.1 deg / 0.8 mm from the GT relative pose; in the final F20N assembly 5-7 holds at
6.1 deg (origin-referenced translation 56.4 mm is lever arm). Either 5 and 7 touch and the GT graph omits it,
or the match is a coincidence -- not settled (claim 3 open).

| GT join | touches | GT axis fold (new axes) | lane dots f/m | contacts @GT | candidates | best by rot err: dots, inliers, score, fold, rot err, centroid mm | dies at |
|---|---|---|---|---|---|---|---|
| 1-2 | 2 | 15.6 | 59/32 | 5 | 2 | 7, 4, 11.00, 4.9, 100.9, 32.1 | score gate |
| 1-5 | 5 | 12.7 | 59/43 | 0 | 1 | 8, 14, 0.34, 69.3, 116.7, 14.8 | axis gate |
| 1-9 | 9 | 20.7 | 59/22 | 0 | 0 | - | no LCS |
| 2-5 | 2,5 | 5.3 | 32/43 | 0 | 0 | - | no LCS |
| 2-9 | 2,9 | 33.8 | 32/22 | 5 | 0 | - | no LCS |
| 3-5 | 5 | 9.9 | 44/43 | 5 | 1 | 8, 12, 0.54, 42.6, 147.5, 24.3 | axis gate |
| 4-5 | 5 | 3.6 | 31/43 | 0 | 1 | 7, 6, 0.41, 54.6, 137.2, 20.2 | axis gate |
| 5-9 | 5,9 | 29.0 | 43/22 | 0 | 0 | - | no LCS |
| 7-9 | 9 | 11.8 | 54/22 | 3 | 0 | - | no LCS |
| 8-9 | 9 | 27.0 | 40/22 | 0 | 0 | - | no LCS |
| 1-8 | placed | 20.7 | 59/40 | 19 | 4 | 7, 12, 0.56, 38.7, **27.0, 2.4** | idx 11 SURVIVES (137.9 deg); idx 9 axis gate |
| 7-8 | placed | 16.4 | 54/40 | 0 | 1 | 10, 0, 11.00, 30.5, 167.9, 30.0 | score gate |
| 1-4 | - | 11.6 | 59/31 | 12 | 1 | 7, 0, 11.00, 41.5, 166.5, 30.8 | score gate |
| 1-6 | - | 10.9 | 59/45 | 0 | 1 | 12, 0, 11.00, 28.3, 166.4, 25.5 | score gate |
| 3-7 | - | 7.4 | 44/54 | 0 | 1 | 9, 0, 11.00, 44.0, 162.3, 31.9 | score gate |
| 4-6 | - | 11.8 | 31/45 | 0 | 1 | 13, 0, 11.00, 74.8, 145.2, 32.3 | score gate |
| 6-7 | - | 8.2 | 45/54 | 16 | 1 | 9, 0, 11.00, 83.8, 135.8, 30.2 | score gate |
| 6-8 | - | 10.2 | 45/40 | 0 | 1 | 7, 0, 11.00, 16.4, 15.9, 42.9 | score gate |

(1-5 is both a 2/5/9 join and a placed-set join.) Against t67 A20 (old axes): joins touching 2/5/9 forming
candidates 1/10 -> **4/10** (1-2, 1-5, 3-5, 4-5); none survives (3 axis gate, 1 score gate); all six with no
LCS involve piece 9 or the 2-5 pair. GT-edge candidates 16 of 35; matched runs 6-13 dots (median 7, mean 8.1;
t67: 6-11, mean 8.2). Every GT axis fold is now 3.6-33.8 deg (t67: up to 86.4), yet the ICP poses on GT pairs
still fold 4.9-83.8 deg against each other: the axis gate now rejects poses ICP produced, not axis files.

## Turn 3 (2026-11-03): Part A run landed; Part B patch prepared (not committed)

Job **34267653**: sacct COMPLETED 0:0, 00:01:03, MaxRSS 6875732K (polled with scripts/slurm_poll.sh;
sacct via `read68.sh`). Index row appended (verdict/note empty). Run
`runs/20261103-1523_4b516be_t68-axis-method`; harvest `artifacts/68/runA/harvest_t68a.tar.gz`
md5 `1188b8d5e4fdd91d3b8cf6644d667e7d`. Substitution gate held: `logs/axes_subst.log` = 9 differences, all Axes/.
Both arms compiled from the same source `F20*.cpp` md5 `90b5091bd4e191e411c618e50b10de14` (= t67 F20 source).

| arm | axes | candidates | after pruning | pieces with a T | seated (<= 4.596 mm) | chamfer mm | Acc.txt |
|---|---|---|---|---|---|---|---|
| t67 F20 | old | 23 | 1 (2,6; not GT) | 2, 6 | 0 | 19.69, 21.52 | 0/9, 0/18 |
| F20O | old | 23 | 1 | 2, 6 | 0 | (= t67, same T set) | 0/9, 0/18 |
| **F20N** | t68 hybrid | **35** | **2** | **1, 5, 7, 8** | **0** | 1: 42.94, 5: 41.08, 7: 36.29, 8: 56.06 | 0/9, 0/18 |

- F20O reproduces t67 F20 (23 / 1 / pieces 2,6): the substitution is the only change between the arms.
- New axes: +12 candidates (23 -> 35); 2 pairs survive pruning (was 1); graph: Node Sequence
  `7(11), 5(9), 1(6), 8(4), 2(0), 3(0), 4(0), 6(0), 9(0)` (binary_F20N.log) -> piece 5 enters the graph
  for the first time. 2, 3, 4, 6, 9 have 0 surviving partners.
- GT edges among the placed four (score58 per_edge): 1-5 163.9 deg / 516 mm, 1-8 141.0 / 450, 7-8 26.0 / 151;
  none pass. Render: the four pieces sit as one compact cluster at a wrong attitude (piece 1 on its side);
  `artifacts/68/render/F20N_assembly.png`, `F20N_perpiece.png` (F20O renders beside them).
- NOT yet measured: per-GT-pair candidate formation / axis-gate / rotation error for the 10 joins involving
  2/5/9. The shipped shim does not list pairs; it needs t67's attitude instrument (GA.cpp via
  patch_attitude67.py, job-2 recipe `submit67b.sbatch`) on the axes68 tree. That is the next job (2 of 4).

### Part B (prepared, NOT committed -- lead reviews and pushes)

`stage68/partB/guard68.patch` (md5 `00b655b9f73fc75ff29811640b9f6d17`, 13 insertions, CRLF preserved),
generated by `partB/make_guard68.py` from copies; `git apply --check` passes on C:/PR/structure-from-sherds-pp
@ cc1d859; that tree stays clean (0 changes). Message: `partB/COMMIT_MSG.txt`.
- `class/ranking_system.cpp` StateManager::Initialize: before `num_init_prio_ = ext_state_[0]...` (:727),
  `if (ext_state_.empty())` print `SFS-NO-CANDIDATES ...`, num_init_prio_ = 0, return. BuildStep then sees
  0 states, next_state_set empty -> "Finish build graph" with out_state_ empty (:900-916).
- `main.cpp` and `hpc/tools/main_pristine_batch.cpp`: after `manager.BuildStep();`, if out_state_ empty ->
  print SFS-NO-CANDIDATES, return 0 (both read out_state_[0] after, main.cpp:235 / shim :229).
- Covers the case t67's shim guard missed (non-empty pruned list, empty root graph).
- NOT compiled yet. Lead check before push: build in the SIF and rerun F50G (expect exit 0, the message)
  and Pot A (expect 8/8, 15/15) -- the Part B control in the spec.

## Turn 2 (2026-11-03): full table, GT-selected hybrid, run dir prepped -- usable set, NOT submitted

Gate re-aimed by the lead: practical bar = every piece's median folded angle to the other eight
<= ~20-25 deg (the six working released axes read 15.6-29.3 and their true joins all formed candidates).

Script `hybrid68.py` (log `hybrid68_run3.log`, committed). Inputs as turn 1. Eight estimators per piece,
all computed from the piece's own walls only (no GT): old file (authors' MATLAB PotSAC, Sep-16 run),
nperp (both walls), nperpS1 (exterior wall only), Pottmann all / S0 / S1, Pottmann + Cao refine
(call fixed; it reads identical to plain Pottmann to 0.1 deg on all nine), PotSAC seeds 0/1/2.

**The selection between estimators sees the GT gate; the estimators do not.** Coordinate descent over
pieces, minimising (max, sum) of the per-piece gate, every estimator as start. This is fitting the
CHOICE to the answer: with 10 estimators per piece, the gate value of the chosen set is optimistic,
most of all where only one estimator passes (P9: only PotSAC seed 0).

Position: every chosen direction gets its axis point from the walls' normal lines (least-squares point
the normals, projected perpendicular to the axis, pass through). The Pottmann positions are degenerate
on these sherds (median radius 97-765 mm on a 65 mm pot), so they are not used.

### Full per-piece table: GT gate (deg, median folded to the other eight, that estimator on all nine)

| piece | wall pts | old | nperp | nperpS1 | pott | pottS0 | pottS1 | pott_ref | potsac s0 | s1 | s2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P1 | 29335 | 26.8 | 19.1 | 25.3 | 28.5 | 47.9 | 27.4 | 28.5 | 47.7 | 58.5 | 37.6 |
| P2 | 2678 | 77.3 | 16.1 | 35.7 | 43.8 | 82.5 | 41.8 | 43.8 | 46.9 | 44.1 | 50.8 |
| P3 | 4382 | 29.9 | 14.6 | 22.9 | 41.3 | 64.3 | 22.6 | 41.3 | 61.5 | 52.4 | 50.8 |
| P4 | 4050 | 27.1 | 14.0 | 21.1 | 59.4 | 58.8 | 53.4 | 59.4 | 65.9 | 72.0 | 76.3 |
| P5 | 9012 | 55.2 | 43.4 | 44.6 | 33.2 | 53.9 | 23.2 | 33.2 | 52.7 | 44.0 | 54.5 |
| P6 | 6960 | 18.7 | 13.8 | 23.5 | 29.4 | 47.2 | 20.6 | 29.4 | 52.7 | 59.9 | 36.9 |
| P7 | 12934 | 24.0 | 70.8 | 67.7 | 30.7 | 44.6 | 23.0 | 30.7 | 68.3 | 45.7 | 39.5 |
| P8 | 5738 | 18.0 | 18.3 | 24.0 | 44.3 | 54.1 | 38.2 | 44.3 | 83.2 | 69.2 | 69.9 |
| P9 | 2192 | 63.6 | 53.2 | 55.6 | 76.9 | 76.9 | 75.6 | 76.9 | 54.0 | 61.5 | 40.3 |

### Fit residuals per piece (own geometry, no GT), for old / nperp / chosen

cyl = median angle of wall normals off the plane perpendicular to the axis (0 = perfect cylinder);
mer = median angle of normals off the meridian plane (0 = a perfect surface of revolution about this
axis); r = median wall distance to the axis (the juglet's real wall radius is ~10-30 mm).

| piece | old cyl/mer/r | nperp cyl/mer/r | chosen | chosen cyl/mer/r | gate old -> chosen |
|---|---|---|---|---|---|
| P1 | 17.4 / 2.3 / 13 | 16.0 / 5.6 / 12 | nperpS1 | 16.4 / 5.1 / 12.3 | 26.8 -> 12.3 |
| P2 | 18.5 / 38.0 / 3 | 6.5 / 3.2 / 16 | nperp | 6.5 / 3.2 / 16.1 | **77.3 -> 15.3** |
| P3 | 24.0 / 3.2 / 14 | 3.5 / 2.8 / 15 | nperpS1 | 3.4 / 2.9 / 15.4 | 29.9 -> 10.8 |
| P4 | 5.5 / 2.1 / 16 | 5.0 / 2.2 / 15 | nperpS1 | 4.7 / 2.2 / 15.6 | 27.1 -> 11.7 |
| P5 | 26.1 / 2.6 / 15 | 11.9 / 3.7 / 16 | pottS1 | 21.1 / 1.9 / 14.0 | **55.2 -> 11.3** |
| P6 | 7.7 / 2.3 / 16 | 5.1 / 1.9 / 16 | nperp | 5.1 / 1.9 / 16.0 | 18.7 -> 10.5 |
| P7 | 37.9 / 3.1 / 12 | 17.3 / 3.9 / 14 | pottS1 | 47.1 / 2.3 / 11.4 | 24.0 -> 14.2 |
| P8 | 6.4 / 2.1 / 17 | 6.0 / 2.5 / 15 | nperpS1 | 6.1 / 2.5 / 15.5 | 18.0 -> 16.4 |
| P9 | 9.2 / 51.2 / 3 | 7.5 / 56.5 / 3 | potsac_s0 | 11.7 / 40.0 / 3.9 | **63.6 -> 23.8** |

Hybrid set: max 23.8, all nine <= 25, eight <= 16.4 (old: max 77.3, six > 25).

Readings:
- P2, P3, P4, P6, P8: a clean cylinder fit (cyl 3.4-6.5, mer 2.2-3.2, r 15-16 mm) -- these walls
  constrain their axis. P2's old file was the outlier (mer 38.0, r 3 mm: an axis through the sherd).
- P1, P5, P7: doubly-curved walls (shoulder/neck: cyl 16-47) but a clean surface of revolution about
  the chosen axis (mer 1.9-5.1, r 11-14 mm). A cylinder model is wrong there by construction; the
  exterior-wall Pottmann direction is the one that fits.
- **P9: too weakly curved to constrain an axis from its own geometry.** Every estimator puts the axis
  3-4 mm from the wall with normals 37-57 deg off the meridian plane; the 23.8 deg it reaches is a
  single PotSAC seed (seeds 1/2: 61.5/40.3) picked by the GT gate. Treat its axis as GT-selected, not
  measured. 2192 wall points, the smallest piece (22-dot Bl0 lane).

### Run dir (prepped, not submitted)

`setup68.sh` (run via rsh.ps1) creates `/data/gpfs/projects/punim2657/SfSpp/runs/<stamp>_<git7>_t68-axis-method/`
from the pushed commit: `axes68/` (9 axes + selection.tsv), `instruments/` (t67 patch_guard67.py,
stage67_inputs.py, arm67.sh from git; submit68.sbatch, hybrid68.py, fit68.py), `submit.sbatch`,
`run.json` ("submitted": false), `logs/axes_provenance.log` (md5 of new axes; old axes and GT in BOTH
Dataset trees). No index.tsv row until submission.
`submit68.sbatch` = t67's submit67.sbatch with: stage as t67, then copy the staged Juglet tree to
`trees/juglet_ax68` and replace only `Axes/` (job refuses unless `diff -rq` shows exactly 9 differences,
all under Axes/); arms F20O (old axes, baseline = t67 F20) and F20N (t68 axes), floor 20, guarded shim;
score58.py on both.

**Created:** `/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1523_4b516be_t68-axis-method` (commit 4b516be;
`logs/axes_provenance.log`). axes68 md5: P1 cd798478, P2 20434553, P3 a29159d4, P4 f9f8b531, P5 4a2b49e7,
P6 c39a3f1d, P7 7b05f75e, P8 c18976b6, P9 28648e69 (LF; the laptop CRLF copies hashed differently).
Old axes and GT are byte-identical in `punim2657/Dataset` and `sfs_preprocessing/Dataset` (9/9 + 10/10 md5),
so the 0.1-3.7 deg gap between my old-file gate and the lead's t67 numbers is NOT a tree difference -- still
open (P7's two-line file read, or the median definition).

To submit next turn: `cd $RUN && sbatch --parsable submit.sbatch`, append the index row, poll with
scripts/slurm_poll.sh, record sacct. Budget: 0 of 4 jobs used.

## Turn 1 (2026-11-03): Stage 0 + Part A start -- DONE, gate NOT met

- [x] STATUS scaffold
- [x] Stage 0 provenance
- [x] Stage 0 estimator survey (three estimators run, not just read)
- [~] Part A: nine axes estimated by every estimator; NONE meets the GT bar
- [x] commit worktree (stage68 scripts + this file only)

Nothing on Spartan was written. No Slurm job (0 of 4 budget). Dataset/, t66, t67 untouched (read-only
probe `probe68.sh`, then `scp` of 37 small files to the gitignored laptop landing zone
`SfSpp_preprocessing/artifacts/68/in/`). Candidate axis files written only to
`SfSpp_preprocessing/artifacts/68/axes/s{0,1,2}/` (PotSAC; scratch, not for use).

## Stage 0: provenance of Dataset/Axes/Juglet (2026-09-29 00:35)

- The files were COPIED, not generated, on 2026-09-29: SfSpp_preprocessing commit `8a30f977`
  (2026-09-29 00:37, "Juglet axes staged") says, in the ticket-16 addendum: "The MATLAB axis step DID
  run for the Juglet: all 9 axes sit in `Juglet_Dataset_20260916/SfS_pp/Axes/` (single-candidate, one
  line each, same format as Pot_A's) ... now staged at `Dataset/Axes/Juglet/`". Ticket 16 adds:
  "`Dataset/Axes/` is produced by MATLAB (`AxisExtraction/*.m`, PotSAC ...), not by the C++ pipeline."
- So the generator is the authors' MATLAB AxisExtraction (PotSAC = RANSAC over the Pottmann normal-line
  fit, then Cao LM refine), run on the 2026-09-16 Juglet bundle -- the bundle that U19 (:530-533) says
  does not survive. `Juglet_Dataset_20260916` is not at `/data/gpfs/projects/punim2657/` top level
  (probe68.sh: "No such file or directory"); not searched deeper (no recursive find under /data/gpfs).
- Consistent with that: our PotSAC port, seed 0, lands 10.2 deg from the old file on P2 (seeds 1/2:
  16.0/20.3) -- the same instrument family, run-to-run unstable.
- Open: which surfaces the Sep-16 MATLAB run read (pre-t47 vertex-dump era), and its seed.
  Piece 7's file has two lines (124 bytes; two PotSAC candidates).

## Stage 0: estimators surveyed (all run on the t66 arm-U S0/S1 walls)

Inputs: `runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom/Juglet_Piece_N.S{0,1}` (PLY ascii,
x y z nx ny nz curvature; 1,040-16,672 points per wall).

1. (b) `sfs_axes` (committed at repo root, this branch): Python port of the authors' MATLAB, proven equal
   to MATLAB on Pot A (pota-repro ticket 05, `tests/test_regression_pota.py` 8/8). Runs on laptop
   numpy 2.3.1; 1-9 s per piece. Ran PotSAC (step 1, MATLAB equal-count truncation, seeds 0/1/2) and
   plain Pottmann on all points.
2. (a) plain cylinder fit ("nperp"): direction minimising sum (n.d)^2 over both walls' unit normals
   (smallest eigenvector of N^T N). Deterministic, no seed.
3. (c) CSC lineage: not run this turn. `CSC/scripts/juglet_outline.py` (docs/lessons.md:467) fits the
   axis of the WHOLE juglet for outline work; it is not a per-sherd estimator.

## Part A results: GT gate, per-piece median folded angle (deg) to the other eight

Script: `fit68.py` (log `artifacts/68/fit68_run1.log`), `pott68.py` (log `artifacts/68/pott68_run1.log`).
Directions mapped by GT R (first 12 numbers of Juglet_Piece_N_T.txt, row-major 3x4).

| piece | old file | nperp | PotSAC s0 | s1 | s2 | Pottmann all | Pottmann S1 only |
|---|---|---|---|---|---|---|---|
| P1 | 26.8 | 19.1 | 47.7 | 58.5 | 37.6 | 28.5 | 27.4 |
| P2 | 77.3 | **16.1** | 46.9 | 44.1 | 50.8 | 43.8 | 41.8 |
| P3 | 29.9 | 14.6 | 61.5 | 52.4 | 50.8 | 41.3 | 22.6 |
| P4 | 27.1 | 14.0 | 65.9 | 72.0 | 76.3 | 59.4 | 53.4 |
| P5 | 55.2 | 43.4 | 52.7 | 44.0 | 54.5 | 33.2 | 23.2 |
| P6 | 18.7 | 13.8 | 52.7 | 59.9 | 36.9 | 29.4 | 20.6 |
| P7 | 24.0 | 70.8 | 68.3 | 45.7 | 39.5 | 30.7 | 23.0 |
| P8 | 18.0 | 18.3 | 83.2 | 69.2 | 69.9 | 44.3 | 38.2 |
| P9 | 63.6 | 53.2 | 54.0 | 61.5 | 40.3 | 76.9 | 75.6 |
| pieces <=10 / >25 | 0 / 6 | 0 / 3 | 0 / 9 | 0 / 9 | 0 / 9 | 0 / 9 | 0 / 5 |

- Bar (<=10 all) met by nothing. nperp is best (6 of 9 under 25, max of those 19.1), fixes P2
  (77.3 -> 16.1) but not P5 (43.4) or P9 (53.2), and breaks P7 (24.0 -> 70.8).
- PotSAC is seed-unstable on these sherds: same piece, three seeds, the axis moves 10-88 deg
  (P1 old-vs-new 49.5/45.7/66.1; P4 14.7/40.1/38.5). Pottmann S0-vs-S1 disagree 63.5 deg on P3,
  72.6 on P2.
- nperp eigenvalue ratio (how far normals are from all being perpendicular to one line; 0 = perfect
  cylinder): P1 0.157, P7 0.150, P5 0.081, P2 0.060, P3 0.052, P8 0.049, P9 0.038, P6 0.029, P4 0.027.
  P1 and P7 are doubly curved (neck/shoulder), where a cylinder model is wrong by construction.
- Two independent estimators agree on P1 (old vs nperp 9.0), P4 (2.8), P6 (6.1), P8 (1.9); yet those
  four still read 13.8-19.1 against each other in the GT frame. So either a ~15 deg floor is the
  estimator limit on 43-100 mm sherds, or the derived Juglet GT carries ~15 deg of attitude spread.
  Not separated this turn.

## Discrepancies to flag to the lead

- My old-file gate reads P1 26.8 / P2 77.3 / P3 29.9 / P4 27.1 / P5 55.2 / P6 18.7 / P7 24.0 / P8 18.0 /
  P9 63.6; the lead's t67 verification reads 23.1 / 77.2 / 29.3 / 25.0 / 55.0 / 17.1 / 23.1 / 15.6 / 63.5.
  Same ranking, differences 0.1-3.7 deg. Suspect: how the 2-line P7 file and the T-file layout were read
  (I take P7 line 1 and the first 12 numbers as row-major 3x4). Must be reconciled before any gate claim.
- `pott68.py` calls `refine_axis(vt, C)` with vt shape (6,), which the port rejects (matmul mismatch,
  "Returning initial axis estimate"), so the "pott_ref" column equals "pott": the Cao refine was NOT
  measured. My call bug, not a port bug; fix = pass vt[:, None].

## Estimator choice (worker's recommendation, for the lead)

Primary for next turn: **nperp (wall-normal cylinder fit), with the sfs_axes Pottmann line-complex as the
fallback on doubly-curved pieces** -- because it is the only estimator measured here that moves the
broken pieces in the right direction (P2 77.3 -> 16.1) and halves the hard fails (6 -> 3), it is
deterministic (the t67 axis gate and the matcher need a stable input; PotSAC moved 10-88 deg between
seeds), and it reuses existing code (the boot_axis.py idea, stage20). It does NOT meet the bar: P5, P7,
P9 fail. The honest reading so far is claim (1), method-limit on small sherds, with claim (3) (GT spread)
not excluded.

## Next turn

1. Reconcile the old-file gate with the lead's numbers (P7 two-line read, T layout).
2. Fix the refine call and measure Cao-refined Pottmann; try a profile-aware fit (normals as lines
   meeting the axis, robust IRLS over both walls, deterministic start = nperp) to address P1/P5/P7/P9.
3. Per-piece rule: pick the estimator by the nperp eigenvalue ratio (cylinder-like < ~0.06) -- decided
   from geometry only, never from the GT gate, to avoid fitting to the answer.
4. Only if a set reaches <= 25 deg on all nine (hard fail) stage it in a new run dir by substitution
   (t301 way) and rerun the t67 F20 panel (scripts in ../stage67/: submit67.sbatch, arm67.sh,
   stage67_inputs.py; floor 20, t66 lanes). If none does, rerun F20 with nperp anyway as a measured arm
   and report P5/P7/P9 as the open pieces.

## Turn 6-7 -- final (2026-11-03 16:05)

- **Job 2 (34268041):** COMPLETED 0:0, 00:08:49, MaxRSS 6.78 GB.
  - Harvest `harvest_t68c.tar.gz` md5 `8cb06185...`, unpacked at `artifacts/68/runC`.
  - D190 matches t66 at 0.000 mm on all lanes. The surfaces match byte for byte; the lane bytes differ only in an uninitialised 7th column.
  - I20N against I20_D190 shows a 35/34 candidate spread on identical geometry.
- **Job 3 (34268623):** D2X (resample 0.95 + `sphereRadius` 0.9). COMPLETED 0:0, 00:05:37, MaxRSS 7.32 GB.
  - Harvest `harvest_t68d.tar.gz` md5 `5805fdde81aa2a92e0c457bbf205005c`, unpacked at `artifacts/68/runD`.
  - Bl0 dots 123/68/94/66/90/94/112/84/49, spacing 0.90 mm.
  - 293 candidates, 18/18 true joins formed. Best is 1-8 at 7.7 deg / 0.2 mm, which dies at the axis gate on a 25.7 deg fold.
  - 9 T files, seated 0/9, Acc 0/9 and 0/18, chamfers 360-384 mm (frame offset), best edge 6-8 at 40.1 deg.
- **Renders:** `artifacts/68/render/I20_D095_*`, `I20_D190_*`, `I20_D2X_*`.
- **Ticket:** Results complete. Part A, Part B (patch, uncompiled), Part C with the densify answer, the sacct table and best-of-N are written. Controls are not run.
- **Open:** the median best-pose figure is 53.8 deg on the lead's pull and 48.3 deg on `pairs68.py`'s best column; the definitions differ. Also open: the old-axis gate discrepancy against t67 (0.1-3.7 deg), and compiling Part B.