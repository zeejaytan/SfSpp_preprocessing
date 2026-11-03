# 70 — Make the axis step produce the same multi-line axes as the released sample, then test on the Juglet

**What to build:** the released corpus axis files carry up to six lines per piece because the authors'
modified PotSAC (paper SSIV-B2, `papers/text/sfspp-2502.13986v1.md:173-175`: top-10 MLESAC candidates,
<=10-deg duplicate pruning, 10% candidacy sampling, full-cloud refinement of survivors) keeps multiple
axes. Our `sfs_axes/potsac.py` port already implements that pipeline and `io_axes.py:write_axes` writes
all K lines — but every comparison since ticket 05 has scored and adopted SINGLE-line axes (the t68
hybrid estimators, and t69 Part A's potsac_s0 scored as one line). This ticket closes the gap:

1. **Fidelity audit (local, no cluster):** read `original_nurbs_preprocessing/AxisExtraction/run_potsac.m`
   and `extract_axis.m` against `sfs_axes/potsac.py` + `sfs_axes/cli.py` and list every behavioural
   difference in the MULTI-candidate path (candidate count, refinement stages and which cloud each stage
   uses, cost definition at each stage, both dedup passes, final ordering, how many lines extract_axis.m
   wrote). Nothing is changed in this stage unless a difference is a proven bug.
2. **Corpus match (the acceptance):** run the port's multi-line output on every corpus piece that has
   staged Surface_0/1 clouds (the t69 Part A staging under
   `/data/gpfs/projects/punim2657/SfSpp/scratch69/` and the released axes under the corpus Axes dir),
   compare against the RELEASED multi-line files piece by piece: does our K match theirs, and does each
   released line have a counterpart among ours within 5 deg direction / 2 mm position (the standing
   gate)? Report per-pot match rates for line 1 and for any-line. This is "generate same axes as sample".
3. **Juglet test:** run the port multi-line on the nine Juglet pieces, drop the multi-line files in as
   the axis input, run the assembler on the current Juglet lane (0.9 mm lanes, floor 30), and score
   candidates / axis-gate survival / seating against the t69 JUG09F50 arm and the t68 I20_D2X arm.

**Why now (2026-11-03, conservator m08189):** "let's check the axis step, how the paper claim it is
suppose to be done. what the current matlab step does, why it don't generate up to six axis guesses per
piece? match the gap, so axis step generate same axises as sample and then test on juglet."

**Answers:** U19, E1

**Blocked by:** none (t69 merged be5980c; sfs_axes port landed ticket 05)

**Status:** ready-for-human
**Working in:** chat on Thinkbook16 (2026-11-03)
**Branch:** 70-multi-axis-potsac from main
**Worker:** (assigned on dispatch)

## Spec

### Stage 1 — fidelity audit (laptop)

Side-by-side of run_potsac.m / extract_axis.m / compute_axis_of_symmetry.m against
sfs_axes/{potsac,refine,cao,pottmann,io_axes}.py. Output a table in the ticket: stage, MATLAB line,
port line, same-or-different. The known ports to respect: randsample without replacement, mean/scale
normalisation over 36 entries, degenerate 0/1 inlier count, dedup keeps cost < cost[0]*1.1 (first
survivor, MATLAB quirk). Flag anything else.

### Stage 2 — corpus match (Spartan)

Inputs: the t69 Part A staged surfaces and the released axes (paths in t69's
stage69/stage69_inputs.py). Run `python -m sfs_axes.cli` (or a thin wrapper) per piece with the
paper-letter settings (step=10, fixed seed set {0,1,2} to measure seed sensitivity), write multi-line
axis files, compare to released. Gate: on the baseline-good pots (A B D E G I, 110 pieces) the
any-line match rate must beat the released line-1 baseline's own 219/288 edge-gate behaviour — the
honest reading is "our multi-line file performs no worse than the released file on the same pieces".
Report K distributions ours vs released.

### Stage 3 — Juglet (Spartan)

Multi-line axes for the nine Juglet pieces; assembler runs on the Juglet lane (0.9 mm lanes, floor 30,
worness 0.7, radius normals 1.0). Compare against: t69 JUG09F50 (0/8, 0/13, old single-line axes) and
t68 I20_D2X (18/18 candidates, best median 53.8 deg). Score: candidates on GT joins, axis-gate
survival, measurable poses, seating, and the any-line self-consistency of the Juglet axis set.

### Gates

- Stage 2 before stage 3; no stage 3 if stage 2 shows the port cannot reproduce released lines on the
  good pots (report and stop instead).
- Every sbatch gets scripts/slurm_poll.sh; final sacct State/ExitCode recorded here.
- Nothing merged by the worker; the lead verifies and merges.

### Budget

- <= 6 Slurm jobs, <= 6 h wall total. Laptop work (audit) does not count.

## Acceptance

- [x] Audit table in this file
- [x] Corpus match table: per pot, K ours vs released, line-1 and any-line match rates
- [x] Seed sensitivity note (3 seeds)
- [ ] Juglet assembler comparison table vs JUG09F50 and I20_D2X — not run: stage-2 gate failed (Gates, line 1)
- [x] All runs in runs/ with index rows; verdict left to the lead

## Comments (worker, 2026-11-03)

**Headline (facts only, no verdict):** the port does not reproduce the released lines on any pot.
At 5 deg / 2 mm, released line 1 has a counterpart among our lines on **0 of 163 pieces**, in every one
of the four arms (3 seeds, plus the CLI's truncating path). The good-pot edge gate under GT poses is
22-34 of 236 on line 1 and 38-52 of 236 any-line, against the released file's 195 of 236 and 221 of
236 (all pots: ours 30-43 and 48-68 of 288; released 219 and 262 of 288). Per the Gates, **stage 3 was
not run.** Under the port's own objectives, our line 1 scores LOWER than released line 1 on 162/163
pieces (diagnostic below). So the search is reaching the minimum of the objective written in this repo,
and the released axes are not that minimum.

Branch `70-multi-axis-potsac` (commits 8be3746, 9a2ace4); port code unchanged.

### Stage 1 — fidelity audit (MATLAB `original_nurbs_preprocessing/AxisExtraction/` vs `sfs_axes/`)

| stage | MATLAB | port | same / different |
|---|---|---|---|
| surfaces read | `read_surfaces.m:20-22,29-32` (whole files, first 6 cols; no equal-count cut; root `D:/SFS_BB_temp/Plt_A`, `Plt_` names) | `io_surfaces.py:31-44` `truncate=True` default cuts both walls to the shorter count; docstring :34-35 calls that "MATLAB parity" | **different** (no truncation exists in this repo's MATLAB) |
| wall order / concat | `extract_axis.m:8` `run_potsac(C0,C1)`; `run_potsac.m:14` `C=[C1,C2]` | `potsac.py:101` concatenate C1,C2 | same |
| candidacy stride | `run_potsac.m:18` fixed `C(:,1:10:num_points)` | `potsac.py:103-104,108` `step=None` -> `adaptive_step`; `cli.py:19,50` default 10 | **different** in `run_potsac` default; same via CLI |
| adaptive-step provenance | — (no such rule in `run_potsac.m`) | `potsac.py:78-84` cites "run_potsac.m:18-30" (lines 20-30 are comments) | docstring cites lines that do not exist |
| normal normalisation | `compute_axis_of_symmetry.m:4` | `potsac.py:35` | same |
| sampling | `compute_axis_of_symmetry.m:18` `randsample(n,6)` (unseeded) | `potsac.py:40` `rng.choice(n,6,replace=False)` sorted | same distribution; streams differ, so bitwise parity is impossible |
| 6-pt normalisation | `compute_axis_of_symmetry.m:20-23` mean(abs(Cs(:))) over 36 entries | `potsac.py:42-45` | same |
| Pottmann + tangent projection | `compute_axis_of_symmetry.m:24-27` | `potsac.py:46-48` | same |
| MLESAC score | `compute_axis_of_symmetry.m:29-32` GM of the biaxial error | `potsac.py:49-50` | same |
| biaxial error shape | `compute_biaxial_cao_error.m:14-19` returns ONE scalar (log-sum-exp, s=100, of the two whole-cloud sums); header :9 says "R (1 x n)" | `cao.py:54-68` scalar | same (port follows the code, not the header) |
| inlier count | `compute_axis_of_symmetry.m:31` on robustified err | `potsac.py:51` on raw err | different, unused for ranking |
| ranking | `compute_axis_of_symmetry.m:48` sort ascending (stable) | `potsac.py:59` stable argsort | same |
| top-N | `run_potsac.m:22,37` 10 | `potsac.py:110` | same |
| stage-1 refine | `run_potsac.m:34-36` method 2, 300 it, 1e-3, on `C(:,1:10:end)` | `potsac.py:111-112` on `Cd` | same; **both no-ops** (next row) |
| refine failure | `optimize_using_lm.m:36` `grad=J'*err` is legal in MATLAB (err 1x1, scalar multiply) -> dx 6xn (:47) -> `xlog(:,eval+1)=x_cand` (:49) throws on 6x1 <- 6xn; `refine_axis.m:46-58` catch returns `vt_initial` | `refine.py` raises at the numpy matmul (log: "size 1 is different from 951"); catch returns initial | same outcome; `refine.py:7-16` docstring names the wrong throwing line (:36 vs :49) |
| Huber cost | `run_potsac.m:39-45` on `C(:,1:10:end)` | `potsac.py:113-117` on `Cd` | same |
| dedup 1 | `run_potsac.m:49-56` triu(abs dots) - eye > 0.9848, unnormalised dirs | `potsac.py:63-70` normalised dirs, triu k=1 | same for unit directions (Pottmann output is unit) |
| prune 1 | `run_potsac.m:59-63` cost < cost(1)*1.1 | `potsac.py:74` | same |
| stage-2 refine | `run_potsac.m:66-68` full C, 1e-9 | `potsac.py:119-120` | same (no-op) |
| dedup 2 + prune 2 | `run_potsac.m:71-80` cost not recomputed | `potsac.py:121` same `_dedup` | same; identity, because refinement moved nothing |
| final sort | `run_potsac.m:82-83` | `potsac.py:122-123` | same |
| write | `write_axis.m:8` all K, position-first, `writematrix` | `io_axes.py:21-29` all K, position-first, %.12f | same (precision only) |
| DEDUP_COS citation | dedup lines are 53 and 74 | `potsac.py:21` cites ":65,86" | wrong citation only |

No proven behavioural bug in the multi-candidate path, so no port code was changed. The two
behavioural differences are the `run_potsac` default stride and the reader's default truncation. Both
were measured as arms in stage 2, and neither changes the outcome.

### Stage 2 — corpus match (Spartan)

Inputs: corpus `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/` `Surfaces/` and `Axes/`.
These are the same surfaces t69 Part A scored (`stage69/partA69.py:119`); `stage69_inputs.py` stages only
the Juglet. All 163 released pieces have both surfaces.

Script `.scratch/juglet-breaklines/stage70/corpus70.py` (submit `stage70/submit70.sh`). Arms:
- M0 / M1 / M2: step 10, no truncation, seeds 0 / 1 / 2 (this repo's MATLAB).
- T0: step 10, truncation, seed 0 (the `cli.py` default).

Match rule: angle <= 5 deg (`io_axes.direction_angle_deg`) and radial <= 2 mm
(`io_axes.radial_axial_errors`). Self-test: the released file matched itself on 163/163 pieces.

- **Job 34276929** (`t70-stage2`): sacct **COMPLETED 0:0, 00:01:06**.
  Run `/data/gpfs/projects/punim2657/SfSpp/runs/20261103-2058_8be3746_t70-multiaxis/`. Outputs in `out/`:
  `pieces70.tsv`, `per_pot70.tsv`, `K_dist70.tsv`, `edge_gate70.tsv`, `seeds70.tsv`, and
  `axes/{M0,M1,M2,T0}/` (163 multi-line files each).
- Laptop copies: `artifacts/t70_stage2_summary.txt`, `artifacts/t70_pieces70.tsv`.

**Per pot, arm M0** (seed 0, the MATLAB configuration). `K=` is the number of pieces where our line
count equals the released count. The angle columns are medians.

| pot | pieces | released lines | our lines | K equal | rel line 1 matched by our line 1 | rel line 1 matched by any of ours | any rel line matched | direction-only (<=5 deg) any | our line 1 to rel line 1 | rel line 1 to GT | our line 1 to GT |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 8 | 11 | 16 | 3 | 0 | 0 | 0 | 0 | 47.9 | 1.7 | 50.7 |
| B | 9 | 10 | 18 | 3 | 0 | 0 | 0 | 0 | 55.3 | 2.4 | 50.8 |
| C | 6 | 7 | 9 | 4 | 0 | 0 | 0 | 1 | 71.3 | 11.4 | 56.9 |
| D | 32 | 45 | 46 | 16 | 0 | 0 | 0 | 2 | 42.4 | 2.5 | 49.1 |
| E | 34 | 41 | 44 | 25 | 0 | 0 | 0 | 0 | 55.3 | 2.8 | 47.9 |
| F | 7 | 9 | 14 | 3 | 0 | 0 | 0 | 0 | 73.1 | 4.6 | 74.6 |
| G | 7 | 7 | 16 | 3 | 0 | 0 | 0 | 0 | 50.8 | 2.2 | 52.8 |
| H | 11 | 24 | 17 | 5 | 0 | 0 | 0 | 0 | 12.9 | 29.1 | 62.7 |
| I | 30 | 33 | 43 | 16 | 0 | 0 | 0 | 0 | 42.8 | 2.2 | 40.3 |
| J | 19 | 33 | 31 | 7 | 0 | 0 | 0 | 1 | 62.9 | 25.7 | 59.3 |
| good (ABDEGI) | 120 | 147 | 183 | 66 | 0 | 0 | 0 | 2 | 49.5 | 2.3 | 48.0 |
| all | 163 | 220 | 254 | 85 | 0 | 0 | 0 | 4 | 51.6 | 2.8 | 51.7 |

The good pots have 120 pieces with released axes; 110 of them have a GT axis, and the GT medians are
over those 110. Median radial offset of our line 1 from released line 1: M0 186 mm on the good pots,
162 mm on all.

**All four arms.** Match counts are of 163 pieces; edge-gate counts are good pots of 236 / all pots of 288.

| arm | rel line 1 matched by our line 1 | any rel line matched | K equal | our lines | edge gate line 1 | edge gate any-line | our best line to GT, good-pot median |
|---|---|---|---|---|---|---|---|
| released | — | — | — | 220 | 195 / 219 | 221 / 262 | 2.33 |
| M0 | 0 | 0 | 85 | 254 | 34 / 43 | 52 / 68 | 46.1 |
| M1 | 0 | 0 | 94 | 257 | 29 / 34 | 40 / 54 | 40.4 |
| M2 | 0 | 0 | 93 | 256 | 22 / 30 | 38 / 48 | 47.8 |
| T0 | 0 | 0 | 80 | 267 | 26 / 32 | 44 / 57 | 46.6 |

**K distributions** (pieces with K = 1 / 2 / 3 / 4 / 5 / 6):

| | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| released | 129 | 19 | 11 | 1 | 2 | 1 |
| M0 | 105 | 36 | 14 | 5 | 3 | 0 |
| M1 | 102 | 35 | 20 | 5 | 1 | 0 |
| M2 | 112 | 24 | 15 | 9 | 3 | 0 |
| T0 | 100 | 36 | 17 | 7 | 2 | 1 |

**Seed sensitivity** (`out/seeds70.tsv`). Across seeds 0, 1 and 2 on all 163 pieces:
- the line-1 direction moves by a median 42.5 deg (p90 81.5, max 89.3);
- it moves more than 5 deg on 150 of 163 pieces;
- K differs between seeds on 102 of 163.

**Gate** (spec line 53-55: our any-line edge gate no worse than released): the best arm, M0, passes
52/236 any-line on the good pots and 68/288 on all pots. Released line 1 alone passes 195/236 and
219/288. The gate fails, so stage 3 was not run (Gates, line 66).

**Diagnostic — whose minimum is which.** Script `stage70/cost70.py`, submit `stage70/submit70c.sh`.
- **Job 34276978** (`t70-cost`): sacct **COMPLETED 0:0, 00:00:05**. Run
  `/data/gpfs/projects/punim2657/SfSpp/runs/20261103-2103_9a2ace4_t70-multiaxis-cost/out/cost70.tsv`
  (laptop copy `artifacts/t70_cost70.tsv`).
- The job wrote `cost70.tsv` into the stage-2 run's `out/` (the script's output path). I moved it to its
  own run dir by hand; the stage-2 run's `out/` now holds only its own files.

Both line-1 axes were scored on the same step-10, untruncated cloud:
- Biaxial Cao error of released line 1 / ours: median **7.7x** (p10 2.6x, min 0.93x).
- Released line 1 is lower on **1 of 163** pieces (D 32), on both GM and Huber. GM is monotone in the
  error, so the printed "2" is rounding, not a tie.

The objective as written in this repo (`compute_biaxial_cao_error.m:14-19`, scored at
`compute_axis_of_symmetry.m:29-30`) rates our axes better than the released ones on 162 of 163 pieces.

**Picture:** [artifacts/t70_A02_axes.png](../../../artifacts/t70_A02_axes.png) shows Pot A piece 02, two
side views, Surface_0 at every 5th point. Released line 1 (green) and GT (black) run nearly parallel,
about 70 mm from the sherd. Our M0 line 1 (red) passes through the sherd, about 48 deg off.

**Budget used:** 2 of 6 Slurm jobs, about 1.2 minutes of 6 h wall.
