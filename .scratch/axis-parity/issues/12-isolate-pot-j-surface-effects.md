# 12: Which Pot J surfaces change the axes enough to recover joins?

**What to build:** Identify influential sherds by swapping one axis file at a time. Then compare those sherds' wall surfaces and test which measured difference reproduces the axis change.

**Answers:** E1
**Blocked by:** None. Frozen Ticket 03 inputs and the Ticket 08 surface audit are sufficient. Ticket 11 supplies trace context.
**Status:** in-progress
**Working in:** DSH: SfS++ axis-parity Ticket 12 (2026-11-22)
**Branch:** 12-isolate-pot-j-surface-effects, in /c/PR/worktrees/sfs/12
**Worker:** DeepSeek
**Budget:** medium 5
**Hand-over:** DeepSeek. Independent acceptance held by lead.

## Baseline and scope

Ticket 03 held our breaklines and the assembler fixed. Its selector on our walls gave 5/21 and 4/21 scored joins. The same selector on the authors' walls gave 15/21 and 16/21. Use the selector at `2e951d9` and the exact executable/configuration resolved from `20261121-1319_2e951d9_t03-ship` and `20261121-1600_2e951d9_t03-jctl`. Use their own-wall and author-wall axis outputs (`axes03_own` and `axes03_tri`) as the two sources. Author-wall axes here means re-estimated by our selector on those walls. The authors' released axes and ground-truth axes are different artifacts. Use reference labels only for scoring and diagnosis.

Keep selector, assembler, flags, breaklines, assembler surface inputs, named sherd set and scorer fixed. Record hashes, actual binary SHA, input frames and units, and paired seed/thread settings where supported. Read the project corpus caveats. Keep unscored sherds out of denominators, but include them in the swap census if their axis files are read by the assembler.

## A. Identify influential sherds

1. Replay the all-own and all-author-wall axis controls in two matched attempts each. Save repeat-level and per-seam results. Confirm the contrast is reproduced in both paired attempts before interpreting swaps. If it fails, locate the input/configuration mismatch or report inadequate repeatability.
2. On the all-own axis baseline, make one arm per sherd whose loaded axis file differs between sources. Replace exactly that sherd's entire axis file with its author-wall counterpart, preserving candidate count, ordering, line positions and directions from that file. Prove a one-file diff, run the same two attempt settings, and report gained and lost seam IDs, pose errors, final seated counts and axis changes. Count gains anywhere in the graph. Record identical files as no-op arms without launching them. Use one run directory and an array or bounded batches for the cells.
3. Rank by net scored joins gained in the weaker repeat, then by fewer baseline joins lost. A reproducible positive swap gains at least one net join in both paired attempts. Show best-of-two and how often it was reached. For up to two leading positive sherds, run one reciprocal one-file swap on the all-author-wall background with the same two settings to test context dependence. If no positive swap reproduces, report that no individual swap reproduced the full contrast and examine the two most divergent axis files as exploratory cases. No combined swaps in this ticket.

## B. Compare the surfaces and isolate a cause

For up to three sherds, inspect the strongest two positives (or exploratory cases) and one nonresponding comparison. Use native-frame wall overlays with matched views and scale. Confirm same sherd, coordinate frame, interior/exterior identity and units before comparing. Record per wall point counts, distinct positions, footprint and missing regions, symmetric surface distances on shared support, local spacing, and signed normal-angle distributions at matched points with distance and unmatched fractions. Render both original and changed axis lines from fixed views and show where the surfaces differ. Report line angle, origin offset and candidate rank, keeping physical dimensions in mm.

Use the same selector settings and paired random draws across a raw-control repeat and at most three single-factor comparisons per selected sherd. Choose the comparisons from the observed contrasts before scoring the changed axes. Separate normal effects (matched normal transfer on fixed positions with unchanged points outside shared support), spatial coverage (restrict to matched support), and sampling effects (equalise density on the same support with normals carried, recording the reduction). Use paired controls if point count must change with coverage. Save the input transformation manifest and audit which attributes changed. A surface feature is implicated only when changing it reproducibly moves the estimated line toward the author-wall estimate beyond raw-repeat spread, with no contradictory change in line offset or sign left unexplained. Confirm the best supported factor on at most one sherd by substituting its newly estimated axes alone into the frozen assembly replay. If no test isolates a factor, report the surviving explanations and what evidence would separate them. Ticket 08 already tested simple duplicate removal.

## Acceptance

- [ ] Hash manifest demonstrates fixed inputs and one changed axis file per swap. Export per-arm and per-seam tables with the two controls and both repeats. State any missing cells or unstable controls.
- [ ] Surface comparison includes aligned paired renders and matched metrics, plus raw-repeat and single-factor axis results. Fetch the small evidence into `C:/PR/artifacts/axis-parity-12/`. Keep geometry and transformation scripts/patches in the Spartan run record.
- [ ] Every submitted job is polled and has a final sacct State/ExitCode, run ID and index record. Verify corpus manifests unchanged. Heavy work stays on compute nodes.
- [ ] Write factual evidence and End state on the ticket branch. Only the ticket write-back may change in git. Leave the merge, close and research verdict to the lead.

## Comments

One-shot experiment. Ticket 03 establishes the surface-source contrast. [PotSAC](https://openaccess.thecvf.com/content_ICCVW_2019/papers/EH/Hong_PotSAC_A_Robust_Axis_Estimator_for_Axially_Symmetric_Pot_Fragments_ICCVW_2019_paper.pdf) motivates checking wall positions and normals separately.

## Worker write-back (factual) — DeepSeek, 2026-11-22

Run directory: `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-2359_2e951d9_t12-ctl` (selector and assembler pinned at `2e951d9`; harness copied from `20261121-1600_2e951d9_t03-jctl`). Ticket branch HEAD `2700e34`. Heavy work ran on compute nodes only; login-node work was reading logs and rendering figures from stored outputs.

| job | name | state | exit | elapsed | node | index row |
|---|---|---|---|---|---|---|
| 35493454 | t12-ctl | COMPLETED | 0:0 | 00:19:21 | spartan-bm138 | yes |
| 35493460 | t12-census | COMPLETED | 0:0 | 00:00:09 | spartan-bm179 | yes |
| 35493798 | t12-swap | COMPLETED | 0:0 | 01:37:39 | spartan-bm060 | yes |
| 35494299 | t12-foot | COMPLETED | 0:0 | 00:00:08 | spartan-bm164 | yes |
| 35495887 | t12-sel | COMPLETED | 0:0 | 00:06:14 | spartan-bm060 | yes |
| 35496135 | t12-swap1 | COMPLETED | 0:0 | 00:13:08 | spartan-bm136 | yes |
| 35496502 | t12-swap | COMPLETED | 0:0 | 00:16:48 | spartan-bm136 | yes |

Corpus manifests: the four jobs that stage geometry printed `CORPUS-UNCHANGED` from `logs/corpus_inputs_{before,after}.md5` (Mesh, Axes, Breakline_0, Surface_0, Surface_1, GT T per piece); no `CORPUS-CHANGED` line exists in any log. Census, footprint and selector jobs are read-only.

### Fixed inputs and one-file proof

- Both axis sources are the first three lines of each file from `20261121-1319_2e951d9_t03-ship/out/axes03_own` and `out/axes03_tri` (K<=3, as in the Ticket 03 runs). Per-piece md5 in `logs/axes3_own.md5` and `logs/axes3_tri.md5`.
- `out/partA/swap_manifest_check.tsv`: 26 swap arms have **exactly one** differing path, `Axes/Pot_J_Piece_NN_Axis.xyz` (own md5 -> tri md5); the 4 control arms have none; every arm manifest has 69 rows. Example J01 own `c74842b712a7a71a763fc93064d41f49` -> tri `4fa83c3f5253ff5bcf928588ba9f6578`; reciprocal `J_RP01R1` is the same pair reversed.
- No seed knob exists in the pinned stack: no `rand`/`srand`/`random_device` in `/opt/sfs-pristine`; the binary is compiled `NUMBER_OF_THREAD 12` (`class/data_structure.h:18`) and ceres is set to 12 threads, so the exported `OMP_NUM_THREADS=8` is inert. The selector's ten draws use `np.random.default_rng(seed)` over seeds 0..9 and are deterministic: the raw control re-estimate reproduced the pinned own axis line to 0.000 deg / 0.000 mm. Per-arm binary md5 in `logs/binary_<arm>.txt`.

### A1 Controls, two matched attempts each — contrast reproduced

| arm | joins | assembler sherd | assembler edge | wall s | seams passed |
|---|---|---|---|---|---|
| J_OWNR1 | 5/21 | 6/11 | 5/21 | 556 | 2-4, 2-10, 3-7, 4-10, 5-7 |
| J_OWNR2 | 5/21 | 8/11 | 5/21 | 569 | 2-4, 2-10, 3-7, 4-10, 5-7 |
| J_TRIR1 | 16/21 | 8/11 | 16/21 | 542 | 1-3, 1-4, 1-5, 1-6, 1-7, 2-4, 2-5, 2-6, 2-10, 3-6, 3-7, 4-5, 4-6, 4-10, 5-7, 5-10 |
| J_TRIR2 | 13/21 | 7/11 | 13/21 | 482 | as R1 minus 2-10, 4-10, 5-10 |

Gaps between paired attempts: 11 joins (R1) and 8 joins (R2). The own-wall arm is stable (5, 5, identical seam set); the author-wall arm is not (16 then 13).

### A2 One-file axis swaps on the all-own baseline (11 pieces x 2 attempts = 22 arms, job 35493798)

Twelve axis files differ between the sources; J09 is not an arm because its axis file is never read by the assembler (no lane breakline, shard off), so it is recorded as a no-op rather than launched. One run directory, two arms per wave, identical settings per arm.

| piece | axis file differs | joins R1/R2 | sherd R1/R2 | net R1/R2 | gained seams R1 | lost seams R1 |
|---|---|---|---|---|---|---|
| J01 | 44.23 deg / 65.05 mm | 17 / 17 | 9/11, 9/11 | +12 / +12 | 1-3, 1-4, 1-5, 1-6, 1-7, 2-5, 2-6, 3-6, 4-5, 4-6, 5-10, 6-11 | none |
| J02 | 0.31 / 0.15 | 2 / 7 | 6/11, 10/11 | +2 / -3 | 5-10, 6-11, 8-12 | 2-4, 2-10, 4-10 |
| J03 | 0.06 / 0.36 | 4 / 5 | 7/11, 6/11 | -1 / 0 | 6-11 | 2-10, 4-10 |
| J04 | 0.57 / 1.56 | 10 / 11 | 8/11, 7/11 | +5 / +6 | 2-5, 2-6, 4-5, 4-6, 5-10, 8-12 | 3-7 |
| J05 | 0.84 / 2.83 | 9 / 9 | 6/11, 6/11 | +4 / +4 | 2-5, 2-6, 4-5, 4-6, 5-10 | 3-7 |
| J06 | 5.52 / 41.10 | 6 / 4 | 6/11, 5/11 | +1 / -1 | 5-10 | 2-10, 3-7, 4-10 |
| J07 | 8.70 / 49.77 | 5 / 6 | 8/11, 6/11 | 0 / +1 | none | none |
| J08 | 7.03 / 33.13 | 5 / 6 | 6/11, 6/11 | 0 / +1 | 2-5, 5-10 | 5-7 |
| J10 | 0.57 / 0.53 | 5 / 5 | 6/11, 6/11 | 0 / 0 | none | none |
| J11 | 0.95 / 1.65 | 6 / 5 | 8/11, 6/11 | +1 / 0 | 8-12 | none |
| J12 | 12.14 / 65.22 | 4 / 5 | 7/11, 8/11 | -1 / 0 | 6-11 | 2-10, 4-10 |

Gains appear anywhere in the graph, not only at the swapped sherd: J01's gains include 2-5, 2-6, 3-6, 4-5, 4-6, 5-10 and 6-11, which do not involve piece 01; J04's include 5-10 and 8-12 and it loses 3-7, none of which involve piece 04. Per-seam angles and translations of every gained and lost join are in `out/partA/swap_vs_base.tsv` and `out/partA/per_seam.tsv`.

### A3 Ranking (weaker repeat first, then fewer baseline joins lost)

- **J01: +12 / +12, reproducible.** Best-of-two 17/21, reached in 2 of 2 attempts; no baseline join lost.
- **J04: +5 / +6, reproducible.** Best-of-two 11/21 (1 of 2); loses 3-7 in R1.
- **J05: +4 / +4, reproducible.** Best-of-two 9/21 (2 of 2); loses 3-7 in both.
- Then, not reproducible: J11 (+1/0), J07 (0/+1), J08 (0/+1), J10 (0/0, exact no-op on joins), J03 (-1/0), J12 (-1/0 in the rerun), J06 (+1/-1), J02 (+2/-3).
- J01's single axis file takes 5/21 to 17/21 twice, which is above the author-wall control's own best (16) — on this pot one sherd's axis file accounts for the whole surface-source contrast and then some.

### A4 Reciprocal swaps (author-wall background, same two settings, job 35496502)

- **J01**: own-file swapped into the author-wall baseline gives **5/21 and 5/21** (author-wall baseline 16 and 13). The contrast is carried by this one axis file in both directions.
- **J04**: own-file swapped in gives **16/21 and 16/21** — no loss. J04's axis file is not necessary for the contrast; its +5/+6 is a marginal, context-dependent gain on our background only.

### Failure and rerun (J12)

In job 35493798 the last wave launched `J_SP12R1` and `J_SP12R2` together and the wave's `wait` loop returned when R1 finished, so the job completed (exit 0:0) one second later and killed R2 mid-assembly: `logs/run_J_SP12R2.log` stops after the binary md5, `out/J_SP12R2` is empty, and no `##### DONE` line exists for it. Rerun as job 35496135 with `submit_swap1.sbatch` (one arm per wave, md5 `bfd72dc8af4fc00d6dfb4e54d83cfd1e`) and `work/arms_j12.txt`. J12 therefore has three attempts: 2/21 (original job 35493798, recorded in `logs/slurm-35493798.out`), 4/21 and 5/21 (rerun).

### B Surfaces: are they the same surface, and how do they differ?

Identity check, all 12 pieces: the matched pairs are A0-O0 (interior) and A1-O1 (exterior) — within 3 mm 99.8-100 % of points, median point-to-wall distance 0.227-0.235 mm, median normal-angle difference 0.85-2.93 deg. Same sherd, same frame, millimetres. The cross pairs A0-O1 / A1-O0 sit 5.3-5.6 mm apart with 0 % inside 3 mm, as expected for opposite walls.

| sherd | author interior / ours | author exterior / ours | ours distinct positions | spacing author -> ours | matched median dist | matched normal median |
|---|---|---|---|---|---|---|
| J01 | 13409 / 45356 | 13814 / 79624 | 23375, 42128 | 0.39/0.40 -> 0.296/0.287 mm | 0.229 / 0.228 mm | 0.89 / 0.85 deg |
| J04 | 10795 / 36948 | 12759 / 43745 | 19167, 22539 | 0.365/0.364 -> 0.271/0.308 | 0.227 / 0.230 | 1.81 / 1.69 |
| J07 | 5522 / 19013 | 6987 / 24088 | 9907, 12448 | 0.346/0.350 -> 0.293/0.267 | 0.229 / 0.231 | 2.08 / 1.71 |

Every wall of every piece: ours covers **all** of the authors' wall (author-unmatched fraction at 3 mm = 0.0000, 4 mm cell footprints). The only extra material is J01's exterior: 0.3974 of our points (31646, one cluster, 102.0 mm across) lie more than 3 mm from the authors' wall, 1632 mm2 against 6144 mm2 shared. J04 and J07 have none in either direction. Signed normal angle at matched points has median 0.0 deg and about 37-40 % of matched points have no tangential offset above 0.2 mm, so there is no systematic tilt — only per-point scatter (matched normal p90 3.8-5.9 deg).

Renders (own-wall axes blue, author-wall axes red, single-factor axes green, fixed views, 100 mm scale bar): `artifacts/axis-parity-12/Pot_J_Piece_{01,07,12}_paired.png`, `artifacts/axis-parity-12/factors/<stem>/<factor>/<stem>_paired.png`, `artifacts/axis-parity-12/footprint/<stem>_<pair>.png`.

### B Single-factor selector runs (13 arms, job 35495887)

Same pinned selector, same settings, one attribute changed at a time on our walls; the author walls only supply the reference. Target = the author-wall line nearest in direction to the raw run's rank-0 line (the authors' file does not use our candidate order). `toward` = gap(raw -> target) - gap(factor -> target); positive means closer to the author-wall estimate. Raw repeat is bit-identical (spread 0), so margins of 0.5 deg and 2 mm are used.

| sherd | factor | K | points | line vs raw | gap to author target | toward (deg / mm) | reading |
|---|---|---|---|---|---|---|---|
| J01 | raw (control) | 3 | 124980 | 0 / 0 | 44.23 / 262.59 | 0 / 0 | control |
| J01 | normals replaced | 2 | 124980 | 50.96 / 250.3 | 54.12 / 262.47 | -9.90 / +0.12 | candidate changed |
| J01 | coverage restricted to 3 mm | 2 | 93334 | 47.51 / 259.3 | 55.05 / 289.48 | -10.82 / -26.89 | candidate changed |
| J01 | sampling to author spacing | 2 | 56845 | 46.60 / 254.5 | 53.84 / 284.12 | -9.61 / -21.52 | candidate changed |
| J01 | same-count random control | 3 | 56845 | 0.87 / 5.63 | 44.71 / 264.66 | -0.48 / -2.07 | no move beyond spread |
| J04 | raw (control) | 1 | 80693 | 0 / 0 | 0.57 / 1.60 | 0 / 0 | control |
| J04 | normals replaced | 1 | 80693 | 0.53 / 1.48 | 0.10 / 0.25 | +0.47 / +1.35 | no move beyond spread |
| J04 | sampling to author spacing | 1 | 35782 | 0.12 / 0.37 | 0.55 / 1.54 | +0.02 / +0.06 | no move beyond spread |
| J04 | same-count random control | 1 | 35782 | 0.12 / 0.32 | 0.62 / 1.73 | -0.05 / -0.12 | no move beyond spread |
| J07 | raw (control) | 3 | 43101 | 0 / 0 | 8.70 / 47.33 | 0 / 0 | control |
| J07 | normals replaced | 2 | 43101 | 2.15 / 11.07 | 10.78 / 56.71 | -2.08 / -9.38 | moved away |
| J07 | sampling to author spacing | 3 | 18976 | 14.21 / 89.86 | 11.42 / 72.12 | -2.72 / -24.79 | candidate changed |
| J07 | same-count random control | 3 | 18976 | 0.17 / 0.83 | 8.54 / 46.66 | +0.16 / +0.67 | no move beyond spread |

Read from the table: on J01 every single attribute change re-selects a different edgeline (K 3 -> 2) and moves the rank-0 line 47-51 deg away from our own, about 10 deg farther from the author estimate, while the paired same-count random thinning moves it only 0.87 deg / 5.6 mm — the estimate is hypersensitive to which points are sampled, not to how many. On J04 everything stays inside the margin: its axis difference (0.57 deg / 1.56 mm) is below what these swaps can resolve, yet the whole-file swap still moves joins 5 -> 10/11, i.e. the join decision is marginal at that scale. On J07 neither transferred normals nor author-spacing subsampling moves the line toward the author estimate; both move it away.

Input transformation manifests per arm (which attribute changed, point counts before/after, spacing, digests, distance to the author wall) are the `run.json` files under `out/sel/P<nn>/<factor>/`; `out/partB/partB_axis.tsv` is the audit table, `artifacts/axis-parity-12/tables/out/partB/` the fetched copy.

No single tested surface attribute (normals, coverage, sampling density) moves the estimated line toward the author-wall estimate on any of the three sherds, so no surface feature is implicated by this ticket's criterion and there is no best-supported factor to substitute into the frozen assembly replay.

Surviving explanations, and the evidence that would separate them:

1. The difference is in the combination of attributes rather than in one of them. Separating evidence: apply normals and sampling together (a two-factor run), or run the binding constraint test below.
2. Our selector sits near a selection boundary on these sherds, so the author-wall estimate is a different basin rather than a small shift of the same line. Separating evidence: the reverse single-factor run — take the **authors'** positions, replace their normals with ours, and re-estimate: if the authors' line then moves toward our estimate, normals are implicated; if it jumps to a third basin, the selection boundary is the explanation. Not run here because the ticket allows at most three single-factor comparisons per sherd and all three slots went to the own-wall direction.
3. The effective difference lies outside the wall point cloud (segmentation of the support region, or the lane breaklines that the selector also reads, which are fixed by Ticket 03 and were not varied here). Separating evidence: re-extract on the authors' walls with our breaklines vs their support region alone, holding the other fixed.

### Missing cells, unstable controls, caveats

- J12 has three attempts (2, 4, 5) instead of two because the first attempt's second arm was lost to the job-script bug above; its best-of-two is 5/21 and it never exceeds the 5/21 baseline.
- The author-wall control is unstable (16 vs 13 joins) — the assembler has no seed knob and repeated identical inputs differ, so single-attempt swap cells carry that spread. The own-wall control is stable (5, 5).
- `score305`'s per-piece column is 0/11 in both sources because the estimated piece pose is in the mesh frame while the ground-truth translation is in the capture frame; joins are the metric, and both counters (score305 joins, assembler Sherd/Edge accuracy) are quoted above. The piece-pose column is not an error measure.
- Each submit script rewrote `score/acc.tsv` with only its own arms; the union was rebuilt from the per-arm `score/acc_<label>.row` files by `work/rebuild_acc.py` (30 arms). Its `time_s` column is unreliable; wall times above come from the `##### DONE ... wall=N s` lines.
- J04 and J05 gains partly overlap the assembler's own repeat jitter (the author-wall control drops 2-10, 4-10, 5-10 on its second attempt), so their six-seam gains are not all attributable to the swap.
- Two Swap arms compile their own binary (`logs/binary_<arm>.txt`); identical labels reuse identical binary md5, but results still differ between repeats.

### Evidence landings

- `artifacts/axis-parity-12/footprint/` — footprint and missing-region panels, `footprint.tsv`.
- `artifacts/axis-parity-12/factors/` — paired axis renders with the single-factor line in green.
- `artifacts/axis-parity-12/tables/` — `out/partA/{per_arm,per_seam,swap_vs_base,rank,swap_manifest_check}.tsv`, `out/partB/partB_axis.tsv`, `out/axis_compare/`, `out/surface_census/`, `logs/panel.tsv`, and the transformation/report scripts.
- Spartan run record keeps geometry and transformation scripts, patches, per-arm logs, per-arm binaries and the staged trees.

## End state

ready
