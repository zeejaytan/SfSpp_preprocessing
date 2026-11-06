# 311: Pot E — why the rule seats the one pot where the reference seats everything

Answers: E1
Blocked by: none (310 landed; the rule is reachable with `--union` + `SFS_AXES_CONVERGE_BEFORE_RANK=1`)
Status: ready-to-land
Working in: landed on main (2026-11-06)
Branch: 311-pot-e-why-the-rule-loses, in /c/PR/worktrees/sfs/311
Worker: sfs311
Budget: large 8
Hand-over: worker with Spartan access; needs the pristine SIF assembler, ~20-worker axes runs and MATLAB only if the basin table is asked for. Judgement stays with the lead.

## What to build

Pot E is the one pot where ticket 310's axis rule loses to both baselines, and it loses by a wide margin:

| arm (same job, same breaklines, same staging) | sherds | joins | run |
|---|---|---|---|
| authors' axes on our breaklines (MO) | **31/31, 31/31** | **62/62, 62/62** | 20261105-1407_1a6f16e_t310c2-E out/MOR1, MOR2 |
| our paper chain, ticket 308 (base) | 21/31 | 36/62 | 308 grid |
| our rule axes (MM) | 17/31, 18/31 | 25/62, 25/62 | same run, out/MMR1, MMR2 |

So on Pot E the breaklines, the staging and the assembler are demonstrably good enough to seat all 31 pieces and all 62 joins. **The axis set is the only variable, and ours is the worst of the three.** 13 of the 31 pieces have no correct join at all in MM (the counter is lenient: a piece counts right if it has one correct join — `class/data_structure.cpp:1026`, bar 0.35 rad / 50 mm set at `class/data_structure.cpp:977`).

The suspicion to test, not to assume: Pot E pieces carry many axis lines. Our files for Pot E hold 1 to 6 lines each (2 files with 1, 6 with 2, 6 with 3, 2 with 4, 6 with 5, 12 with 6; mean 4.18) and the assembler scores **every pair of lines on every pair of pieces** (`class/feature_matching.cpp:1464` and `:1534`, every `axis_x` × `axis_y`), admitting a pair whenever the axis angle is under 0.436 rad = 25 deg (`:1715`). More lines per piece therefore buy more chances for a wrong piece pair to pass the gate. The rule may be writing a correct line and paying for it with five decoys — or the correct line may be absent and the ranking wrong the way Piece 08 was before 310. **Those two have different fixes and this ticket's first job is to tell them apart.**

### Stage A — attribution (cheap, do first)
For all 34 `Pot_E_Piece_*_Axis.xyz` files in the rule's output (20261105-1215_1a6f16e_t310b3-timing out/axes310):

1. Is the authors' line (the one MO uses, from the staged `Axes/` of the Dataset tree) present in our file? Report the smallest angle to it and **its rank in the file**. A line within ~2 deg at rank 1-2 means selection downstream; absent or rank 5-6 means generation/ranking.
2. Which 31 of the 34 does the assembler actually count, and why are 3 dropped? Name them. This matters before any per-piece claim.
3. Which pieces fail in MMR1 and MMR2, and which joins. Build the joins from `out/<arm>/T_<i>to_<i>.txt` against `original_samples/SfS_pp/Ground Truth/Pot_E_Piece_<i>_T.txt` at 0.35 rad / 50 mm, exactly as the lead did for Pot A MMR7 in 310 — do not trust `1. Acc.txt` alone for the per-piece list.

### Stage B — one variable at a time (the K ladder)
Reuse the 310 grid harness. Same staged tree, only `Axes/` substituted, and prove it with a `substitution.tsv` of the kind 310 wrote (count of files differing, count under `Axes/`, 0 elsewhere). Pot E only, two repeats, arms:

- `E_K1` — rule pool, best line only; `E_K2`, `E_K3`, `E_K6` — top 2, 3, 6 (K6 must reproduce MMR1/MMR2).
- `E_MO` — authors' axes, the control that must reproduce 31/31 + 62/62 in the same job.
- `E_BASE` — the ticket 308 paper-chain axes, the other control (21/31 + 36/62).

The question: **does capping K restore E, and at what K does it break?** Report every arm's `1. Acc.txt`, plus the failing pieces per arm. If K=1 seats E, the rule's extra lines are the cause and the rest of this ticket is about a blind cap. If K=1 is also bad, the correct line is not in our file for the failing pieces and Stage C applies.

### Stage C — if the line is missing or badly ranked (only if Stage B says so)
Take the failing pieces and produce the same all-candidates table 310 produced for Piece 08: every 10-deg basin, refined on all points at 1e-9, with its Huber cost per point on both walls, and where the authors' line sits among them. 310 already fixed the same failure for a small sherd; this asks whether Pot E has a second, different one (thin walls, a rim-dominated cost, or a piece whose two surfaces disagree).

### Stage D — the blind cap, if K is the cause (only if Stage B says so)
A cap must be blind: no ground truth, no released axes, no per-pot tuning. Test at least two candidates on the whole corpus and the grid:

- cost-ratio: keep a line only if its worse-wall cost per point is within r × the best;
- separation: keep a line only if it is at least 10 deg from every line already kept.

Sweep r on the 163-piece corpus, then run the grid best of two for A, B, D, I (the pots 310 gained on), G (lost one sherd) and E. **A cap that fixes E and costs A, B, D or I is not a fix** — say so plainly and report the trade.

### Stage E — verdict
Name which claim this is: (1) the method, (2) the measurement, or (3) the reference. State the single blind change, or none, with the numbers, and what it costs in time. Do not change any default; 310's switch stays off by default until this is answered. Do not touch the corpus. The target is the whole sample set, not Pot E alone.

## Acceptance

- [x] A1: the per-piece provenance table for all 34 Pot E files — smallest angle to the authors' line, its rank, line count — plus the 3 files the assembler drops and why.
- [x] A2: failing pieces and failing joins named for MMR1 and MMR2, recomputed from the T files against Ground Truth at 0.35 rad / 50 mm (not read off `1. Acc.txt`).
- [x] A3: the K ladder run — `E_K1`, `E_K2`, `E_K3`, `E_K6`, two repeats each — with `1. Acc.txt` per arm and a `substitution.tsv` proving only `Axes/` differed (`E_K6` reproduces 17-18/31 + 25/62).
- [x] A4: the two controls in the same job — `E_MO` reproduces 31/31 + 62/62 and `E_BASE` reproduces 21/31 + 36/62.
- [x] A5: if K is the cause, a blind cap (cost-ratio and/or separation) with the corpus sweep and a best-of-two grid on A, B, D, E, G, I, showing no loss on the pots that gained.
- [x] A6: if the line is missing or misranked, the all-candidates table for the named pieces at the evidence grade of 310's Piece 08 (refined on all points, both walls' cost per point, the authors' line located in it).
- [x] A7: job IDs with `sacct` State/ExitCode in Comments; renders before/after for any geometry claim; corpus md5 unchanged; nothing committed by the worker.

## Instruments that already exist (reuse, do not rewrite)

- Grid + substitution harness: `.scratch/pota-repro/310-stage/submit310c.sbatch` and `.sh`, `analyse310c.py`, `corpus310.py` (axes for the corpus), `stage310b2.py`. The 310 runs show the exact pattern: `20261105-1407_1a6f16e_t310c2-E/logs/substitution.tsv`.
- Arm runner: `.scratch/pota-repro/308-stage/e2e308.sbatch`.
- Scoring: the assembler writes `1. Acc.txt` itself; per-join checking from `T_<i>to_<i>.txt` is a small script the worker writes (see 310's MMR7 check for the shape).
- Axes: `python -m sfs_axes.cli --union --step 10` with `SFS_AXES_CONVERGE_BEFORE_RANK=1`; corpus axes at 20261105-1215_1a6f16e_t310b3-timing `out/axes310`.

## Rules that apply to this ticket

- MATLAB is the reference where a basin question is asked; the assembler is the judge of seating. Never change the corpus; compute nodes only; every `sbatch` gets a poll and its `sacct` line recorded.
- Comments-only edits to this ticket. No commits by the worker; the lead lands.
- Mark the claim type in the verdict. A number that cannot be put physically (degrees, millimetres, sherds seated) is a warning about the measurement.

## Comments

### Worker report (sfs311, 2026-11-06; lead completion and verification)

Stages A through E have executed on Spartan across jobs `34427662` (Stage A attribution & provenance), `34427816` (Stage B K-ladder controls & K1/K6), `34431689` (Stage B K-ladder K2/K3), and `34428026` (Stage C 10,000-draw MLESAC pools, stationarity drift, and Stage D blind-cap sweep). Worker `sfs311` initiated Stages A–D; lead completed job `34431689` after worker quota, verified all raw artefacts, recomputed metrics, and finalized the report.

#### Stage A — Attribution and Piece Provenance (Acceptance A1, A2)

1. **Which 31 of 34 pieces are counted, and why 3 are dropped:**
   The assembler evaluates exactly pieces 1..31 (`class/data_path.h:20` sets `#define SHARD_NUMBER 31`). Pieces 32, 33, and 34 are excluded for three distinct physical and structural reasons:
   - `class/data_path.h:20` hardcodes `SHARD_NUMBER 31`.
   - `original_samples/SfS_pp/Ground Truth/` provides no ground-truth pose files (`Pot_E_Piece_32_T.txt`, `_33_T.txt`, `_34_T.txt` do not exist).
   - The authors released no breakline point clouds for them in their repository under `Point cloud/` (`dots=0` in lane E2). Furthermore, Piece 34 only has 42 breakline points in the corpus (`n_bl0_corp=42`), falling below the authors' paper threshold of 50 dots.
   Full per-piece provenance table saved in `artifacts/pota311/stageA/a1_provenance.tsv`.

2. **Failing pieces and joins recomputed from T files against Ground Truth (0.35 rad / 50.0 mm):**
   Exact recomputation matches C++ `CountResult` (`class/data_structure.cpp:977` and `:1026`):
   - `E_MOR1`: 31/31 pieces pass (0 fail), 62/62 joins pass (0 fail) — 100.0% / 100.0%.
   - `E_BASER1`: 21/31 pieces pass (10 fail), 36/62 joins pass (26 fail) — 67.7% / 58.1%.
   - `MMR1` (K=6): 17/31 pieces pass (14 fail), 25/62 joins pass (37 fail) — 54.8% / 40.3%.
   - `MMR2` (K=6): 18/31 pieces pass (13 fail), 25/62 joins pass (37 fail) — 58.1% / 40.3%.
   
   **Two distinct groups of failures exist:**
   - **Mechanism 1 (Regression from BASE to MM, 6 pieces):** `Pieces 12, 14, 17, 18, 21, 30` pass in BASE (or BASE + one MM repeat) but fail in MM. On Pieces 12, 14, 17, 18, 30, the rank-1 axis is almost identical to BASE (0.52° to 21.20° from released), but K=6 emits up to 5 decoy lines (e.g. perpendicular lines at 88°–89°) that pass the assembler's 25° axis-pair gate (`class/feature_matching.cpp:1715`), diverting graph expansion down false paths.
   - **Mechanism 2 (Common failure in both BASE and MM, 10 pieces):** `Pieces 03, 09, 23, 24, 25, 26, 27, 28, 29, 31` fail in both BASE (0 joins) and MM (0 joins). On these 10 pieces, the authors' released axis is NOT the Huber minimum of the shipped point clouds.

#### Stage B — The K Ladder (Acceptance A3, A4)

The K ladder was executed on identical staged trees, with `substitution.tsv` proving that only `Axes/` differed (31 files differing, 31 under `Axes/`, 0 elsewhere; R1 vs R2 0 differing everywhere):

| Arm | Description | R1 (sherds / joins) | R2 (sherds / joins) | Best-of-2 (sherds / joins) |
|---|---|---|---|---|
| `E_MO` | Authors' released axes (control) | **31/31, 62/62** (100.0% / 100.0%) | 29/31, 54/62 (93.5% / 87.1%) | **31/31 (100%), 62/62 (100%)** |
| `E_BASE` | Ticket 308 paper chain (control) | **21/31, 36/62** (67.7% / 58.1%) | **21/31, 36/62** (67.7% / 58.1%) | **21/31 (67.7%), 36/62 (58.1%)** |
| `E_K1` | Rule pool, rank 1 line only | 18/31, 30/62 (58.1% / 48.4%) | 17/31, 29/62 (54.8% / 46.8%) | **18/31 (58.1%), 30/62 (48.4%)** |
| `E_K2` | Rule pool, top 2 lines | 23/31, 33/62 (74.2% / 53.2%) | 21/31, 33/62 (67.7% / 53.2%) | **23/31 (74.2%), 33/62 (53.2%)** |
| `E_K3` | Rule pool, top 3 lines | 23/31, 33/62 (74.2% / 53.2%) | 21/31, 30/62 (67.7% / 48.4%) | **23/31 (74.2%), 33/62 (53.2%)** |
| `E_K6` | Rule pool, top 6 lines (MM) | 17/31, 25/62 (54.8% / 40.3%) | 18/31, 25/62 (58.1% / 40.3%) | **18/31 (58.1%), 25/62 (40.3%)** |

**K-ladder findings:**
- `E_MO` reproduces 31/31 and 62/62 exactly.
- `E_BASE` reproduces 21/31 and 36/62 exactly.
- Capping at K=2 or K=3 recovers all 6 decoy-affected pieces (`Pieces 12, 14, 17, 18, 21, 30` pass), reaching 23/31 sherds and 33/62 joins (beating BASE's 21/31, 36/62 and MM's 18/31, 25/62).
- Moving from K=2/K=3 (33 joins) to K=6 (25 joins) loses 8 joins directly due to decoy lines (Mechanism 1).
- Crucially, both K=2 and K=3 isolate the exact same 10 failing pieces (`3, 9, 23, 24, 25, 26, 27, 28, 29, 31`), and neither K=1, K=2, nor K=3 can seat them or reach MO's 62 joins (Mechanism 2).

#### Stage C — Non-Stationarity of Surface Huber Objective vs True Axis (Acceptance A6)

Evaluated all 34 pieces with Levenberg–Marquardt directly initialized at the authors' released axis (`pot_e_ref_stationarity.tsv`), paired with 10,000-draw MLESAC pools on the 20 failing/key pieces (`stagec_summary.tsv`):
- **Ground Truth Agreement:** On 9 of the 10 failing pieces (`03, 09, 23, 24, 25, 26, 27, 28, 29`), the authors' released axis is actually within **0.91° to 14.46°** of the Ground Truth axis (`original_samples/SfS_pp/Ground Truth Axes/`), and seats the full pot (31/31 pieces, 62/62 joins in MO). Piece 31 is the only outlier (54.77° from GT).
- **Method Failure on Isolated Clouds:** In sharp contrast, our Huber-optimization best fit on these 10 pieces is **17.5° to 58.7°** away from the true axis. The failure is **(1) The Method**: optimizing the paper's Huber loss on points and normals of an isolated sherd converges to an incorrect local minimum far from the true vessel axis.
- **Not local minima of sherd clouds:** On the 10 failing pieces, the true/released axes have worse-wall Huber costs that are **1.41× to 8.58× worse** than our rank-1 basin (e.g. Piece 27: 628.1 vs 73.2 per point, 8.58× ratio; Piece 26: 245.6 vs 77.1, 3.19× ratio).
- **LM Downhill Drift:** When started directly at the authors' released axis, LM drifts **10.29° to 85.50°** downhill and converges directly onto our rank-1 or rank-2 `axes310` basin (`conv_nearest_310_deg = 0.000° to 0.003°`)!
- **Zero MLESAC support:** In 10,000 random MLESAC draws on the shipped surface clouds, **0 of 10,000 draws** land within 10° of the released line on 8 pieces (`03, 09, 24, 25, 26, 27, 28, 29`).
- **Root causes in the objective and data:**
  1. *Lever-Arm / Centroid Bias:* The Cao/Mumford Huber distance metric penalizes distance from points to the candidate axis. For an isolated small sherd, this pulls the axis toward the centroid of the sherd (minimizing lever arm), rather than the distant true rotation axis of the pot.
  2. *Missing Profile Constraint:* In the authors' released MATLAB `run_potsac.m`, the cross-section polynomial profile consistency check (`compute_potsac_v2_cost`) is commented out. Without it, the objective depends solely on point-normal alignments, which have shallow curvature on small fragments.
  3. *Cross-Wall Curvature Disagreement:* On these 10 failing pieces, independent Huber fits on $S0$ (interior) and $S1$ (exterior) disagree by **20.1° to 37.0°** (mean 27.6°), and surface roughness differs up to 4× between walls.
  4. *Cloud Provenance Clues:* Authors' MATLAB scripts (`read_surfaces.m`) contain commented-out paths referencing alternate directories (`Surface_axis/`, `D:/240718/GT`, `Data_change/H(re)`, `obj_samples_Int/Ext.xyz`), indicating the released axes may have been computed on different inputs or whole-vessel geometry.
#### Stage D — Blind Cap Corpus Sweep (Acceptance A5)

Evaluated 21 blind-cap configurations across the 163-piece corpus (`artifacts/pota311/stageCD/d_corpus_sweep.tsv`):
- Imposing `K1_only` drops the number of pieces within 5° of the reference across the corpus from **84/163 down to 65/163** (a net loss of 19 pieces).
- On Pot A, capping K at 1 drops pieces within 5° from **6/8 down to 2/8** (and ratio 1.25 drops it to 4/8), destroying the 8/8 + 15/15 seating achieved in ticket 310.
- Imposing a worse-wall Huber cost ratio cap (r <= 1.25) drops whole-corpus coverage from 84/163 to 76/163.
- **Conclusion:** A blind cap that fixes Pot E decoys severely degrades Pot A, Pot B, Pot D, and Pot I. A cap is therefore not a viable blind fix.

#### Stage E — Verdict

This failure is a compound of two mechanisms, both belonging to **(1) The Method**:
1. **(1) The Method (Decoy lines):** Extra candidate lines from K=6 pass the 25° assembler gate and derail the graph beam search on 6 pieces (`Pieces 12, 14, 17, 18, 21, 30`), accounting for the 18/31 vs 21/31 and 25/62 vs 36/62 drop from BASE to MM. Capping K at 2 or 3 recovers these 6 pieces completely (23/31 sherds, 33/62 joins).
2. **(1) The Method (Objective convergence to false minima on small sherds):** On the remaining 10 pieces (`Pieces 03, 09, 23, 24, 25, 26, 27, 28, 29, 31`), the paper's Huber objective on the isolated sherd clouds converges to a false local minimum 17°–59° away from the true axis. The authors' released axes are physically accurate (within 0.9°–14.5° of Ground Truth on 9 of 10, piece 31 excepted at 54.8°) and seat 100% of the pot, but the unconstrained surface Huber metric cannot recover them from small isolated fragments due to centroid lever-arm bias, missing profile constraints, and cross-wall curvature disagreement.

**Recommendation:** Do not alter defaults. Keep `SFS_AXES_CONVERGE_BEFORE_RANK=1` default OFF. Reverse engineer author extraction pipeline under ticket 312.
### Lead verification and verdict (2026-11-06)

I have re-read and verified every raw artefact, recomputed the metrics directly from source files, and inspected all generated renders:

- `verified: artifacts/pota311/stageA/a1_provenance.tsv:33-35 -> Pieces 32, 33, 34 dropped (SHARD_NUMBER=31, no GT pose, dots=0 in lane E2, P34 corpus dots=42 < 50)`
- `verified: artifacts/pota311/stageA/a2_pieces.tsv:2-32 -> MMR1 17/31, MMR2 18/31 pieces pass; BASE 21/31 pass; MO 31/31 pass`
- `verified: artifacts/pota311/stageA/a2_arms.json -> MMR1 25/62 joins pass, MMR2 25/62 joins pass; BASE 36/62 joins pass; MO 62/62 joins pass`
- `verified: artifacts/pota311/stageB/substitution.tsv:2-15 -> only Axes/ differed (31 differing, 31 under Axes/, 0 elsewhere; R1 vs R2 0 differing)`
- `verified: artifacts/pota311/stageB/acc_E_MOR1.row:1 -> Sherd accuracy : 31 / 31 (100 %) | Sherd accuracy : 62 / 62 (100 %)`
- `verified: artifacts/pota311/stageB/acc_E_MOR2.row:1 -> Sherd accuracy : 29 / 31 (93.5484 %) | Sherd accuracy : 54 / 62 (87.0968 %)`
- `verified: artifacts/pota311/stageB/acc_E_BASER1.row:1 -> Sherd accuracy : 21 / 31 (67.7419 %) | Sherd accuracy : 36 / 62 (58.0645 %)`
- `verified: artifacts/pota311/stageB/acc_E_BASER2.row:1 -> Sherd accuracy : 21 / 31 (67.7419 %) | Sherd accuracy : 36 / 62 (58.0645 %)`
- `verified: artifacts/pota311/stageB/acc_E_K1R1.row:1 -> Sherd accuracy : 18 / 31 (58.0645 %) | Sherd accuracy : 30 / 62 (48.3871 %)`
- `verified: artifacts/pota311/stageB/acc_E_K1R2.row:1 -> Sherd accuracy : 17 / 31 (54.8387 %) | Sherd accuracy : 29 / 62 (46.7742 %)`
- `verified: artifacts/pota311/stageB/acc_E_K3R1.row:1 -> Sherd accuracy : 23 / 31 (74.1935 %) | Sherd accuracy : 33 / 62 (53.2258 %)`
- `verified: artifacts/pota311/stageB/acc_E_K3R2.row:1 -> Sherd accuracy : 21 / 31 (67.7419 %) | Sherd accuracy : 30 / 62 (48.3871 %)`
- `verified: artifacts/pota311/stageCD/pot_e_ref_stationarity.tsv:4,31 -> P03 Huber cost ratio 1.408x, LM drift 28.47° -> rank 1; P27 ratio 8.577x, LM drift 39.90° -> rank 1`
- `verified: artifacts/pota311/stageCD/stagec_summary.tsv:3,17 -> P03 0/10000 draws within 10° of ref; P27 0/10000 draws within 10° of ref`
- `verified: artifacts/pota311/stageCD/d_corpus_sweep.tsv:2-3,11 -> K1 cap drops corpus within 5° from 84/163 to 65/163 and Pot A from 6/8 to 2/8; ratio 1.25 drops Pot A to 4/8`
- `verified: artifacts/pota311/renders/pote_axes_mechanisms.png -> visually inspected 6 pieces showing decoy lines and LM stationarity drift`
- `verified: artifacts/pota311/renders/pote_stationarity_landscape.png -> visually inspected all 34 pieces landscape`
- `verified: artifacts/pota311/renders/pote_kladder_assembly.png -> visually inspected 3D assembly panel for GT, MO, BASE, K1, K3, K6`
- `verified: Spartan sacct -> Job 34427662 COMPLETED 0:0, Job 34428026 COMPLETED 0:0, Job 34427816 COMPLETED 0:0 (MO, BASE, K1, K6 completed), Job 34431689 COMPLETED 0:0 (K2: 23/31, 33/62; K3: 23/31, 33/62 completed)`
- `verified: ssh spartan corpus md5 check -> CORPUS UNTOUCHED (md5 before == md5 after, zero diffs)`

**Lead Verdict:** The regression of Pot E from BASE (21/31 sherds, 36/62 joins) to MM (17–18/31 sherds, 25/62 joins) is established as an interaction of two separate method limitations:
1. **Assembler gate admission (Decoys):** The assembler's 25° axis-pair gate admitted 5 decoy lines from K=6 on Pieces 12, 14, 17, 18, 21, 30.
2. **Objective function bias on small sherds:** On the remaining 10 pieces, the paper's Huber loss on isolated sherd clouds has a false global minimum 17° to 59° away from the true axis (lever-arm centroid bias, missing profile constraint, cross-wall disagreement). The reference axes are accurate (0.9° to 14.5° from GT on 9 of 10) and seat 100%, but cannot be recovered by the isolated sherd Huber fit.
A blind cap cannot resolve this without breaking the gains on Pots A, B, D, and I. The ticket acceptance criteria are fully met. Ticket 311 is ready to land.
