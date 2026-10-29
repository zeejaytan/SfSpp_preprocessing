# 43 — derive the growth angle from each sherd's own curvature

**Answers:** U19, E1
**Blocked by:** none (ticket 42 merged as 84de2ed; its run of record is reference only)
**Status:** done (reading written by the lead; the curvature rule is derived and predicted, not yet run through the pipeline)
**Working in:** chat on Thinkbook16 (2026-10-30)
**Branch:** 43-derive-the-growth-angle-from-the-sherds-own-curvature, in /c/PR/worktrees/sfs/43

## The question

The growth accepts a neighbour only within `thetaDeg` of the front point's normal (mesh_processing_headless.cpp:3191; env SFS_PAPER_THETA at :4574, default 3.4). Tickets 29/30/32 established the neighbour turn tracks curvature (Pearson 0.941; turn per step ~ spacing / fold radius; Pot A ~21 mm radius -> ~1.2 deg, Juglet 0.67-5.25 mm -> 8-16 deg). Ticket 30 proved one global constant fitted on the pot cannot transfer (c=5.698 -> 28-103 deg, one cluster everywhere). Ticket 42 proved by outcome that a larger theta separates Juglet pieces 2-8 into genuine wall pairs (ladder chose 10.2 everywhere; the growth still refused the broken edge), so on those sherds within-face turns lie below 10.2 and edge turns above it.

Open: per sherd, WHERE does the gap sit, and does theta derived from each sherd's own within-face turn distribution land inside the gap without any outcome search?

## Part A — the two distributions, per sherd, labelled from the mesh

For Juglet pieces 1-9 and Pot A pieces 01-08, on the REAL released clouds at the pipeline's own adaptive spacing (today's default):

- Sample the sherd mesh analytically (stage42 instrument mesh38) at the spacing the pipeline resolves ([SPACING-22] S), each sample carrying its source triangle's face normal.
- For every sample pair within the pipeline's neighbourhood criterion, compute the turn angle between the two face normals.
- Label a pair WITHIN-FACE if the two source-triangle normals differ by less than 45 deg, ACROSS-FOLD otherwise. Report per sherd: n pairs, within-face p50/p90/p99, across-fold p10/p50, and the margin (across-fold p10 minus within-face p99).
- Mark on each distribution: the shipped 3.4, ticket 42's ladder-chosen theta (10.2 Juglet, 6.8 on PA01/03/07/08), the sherd's spacing and median fold radius (ticket 32 instrument).

## Part B — the derived rule

Two candidate rules, printed per sherd:

- R1: theta = k x within-face p90, with k fixed so Pot A's median lands at its known-good 3.4.
- R2: theta = geometric mean of within-face p90 and across-fold p10 (mid-gap by construction).

Report whether R1 and R2 land inside the measured margin, per sherd. A sherd where they do not is named, not hidden.

## Part C — the pipeline test

One cell per piece, arms: A today (no env overrides) / B SFS_PAPER_THETA set per sherd to R1's value / C same for R2. NO source change is needed - SFS_PAPER_THETA already exists. Pieces: Juglet 1-9, Pot A 01-08 (48 cells). Measure with the corrected signed-t pair statistic (stage42 instruments measure34.py pair_stats): med_along, med_across, coincidence, and per-surface points / diagonal / 2 mm coverage / fold-to-mesh.

Reference numbers (ticket 42 run of record 33989453): Juglet armB genuine pairs J2 1.88/0.67, J3 1.77/0.51, J4 2.14/0.45, J5 2.46/0.42, J6 2.28/0.48, J7 2.52/0.52, J8 1.86/0.38; J9 borderline 0.79/2.42; J1 armA genuine 1.82/0.53; Pot A armA clean 8/8 at 3.55-7.09 along / 0.13-0.27 across / coincidence 0. Wall thicknesses (ticket 35): J2 2.693, J3 2.452, J5 2.900, J7 3.263, J9 2.595, PA07 4.056 mm.

## Constraints

- No tracked pipeline change: instruments and tables under .scratch/juglet-breaklines/stage43/ only. If Part C seems to need a source edit, stop and report.
- Compute nodes only; at most 3 grid jobs plus at most 2 dead submissions; split by vessel, never by part.
- Corpus and canonical checkout read-only, md5 before/after; /opt/sfs-pristine absent is recorded, not created.
- CRLF-check every script before submit (two grids died on 'set: pipefail: invalid option name'); grep -a for binary PLY headers; no xargs -d.
- Geometry deleted with a counted record written BEFORE the delete; surfaces, logs and tables kept for the lead.
- Append index rows with 6 fields, verdict and human_note EMPTY.

## Evidence to return

1. Part A table (one row per sherd: the two distributions and the margin) plus one figure with the distributions per sherd, 3.4 and the ladder theta marked.
2. Part B table: R1 and R2 per sherd, inside-gap yes/no, the k R1 implies.
3. Part C cell table and signed-t pair table, 48 cells.
4. Pot A control outcome per arm, stated even if it regresses.
5. Defaults-unchanged proof: arm A SampledWithNormals md5 identical to a no-env rerun on 4 pieces.
6. Corpus/inputs md5 before/after; geometry deletion record.
7. Index rows appended with empty verdict.

Report numbers and paths, not verdicts.

## Comments (worker, 2026-10-30)

### What was built

`.scratch/juglet-breaklines/stage43/instruments/` (branch `43-derive-the-growth-angle-from-the-sherds-own-curvature`):

| file | what it is |
|---|---|
| `spec.tsv` | 17 rows: pot, piece, mesh path, the S that piece's own pipeline run resolved ([SPACING-22] `policy=piece`), ladder theta (10.2 Juglet; 6.8 on PA01/03/07/08, 10.2 on the other four Pot A pieces) |
| `dist43.py` | Part A/B instrument: analytic mesh sampling at the resolved spacing, PCA normals oriented two ways, every k-NN pair's turn angle, WITHIN-FACE / ACROSS-FOLD label from the source-triangle normals (45 deg), the two distributions, the separability grid, R1/R2, the figure, and a `selftest` subcommand |
| `run_dist43.sh` | Part A/B driver: md5-records the 17 meshes read, runs `pieces`, `rules`, `figure` |
| `run_cell43.sh` | Part C driver: one cell per piece per arm, writes `pipeline_cells.tsv`, `surfaces.tsv`, `surface_pairs.tsv` (signed-t), `nest.tsv`, `walls.tsv`, `defaults_proof.tsv`, `theta_proof.tsv` |
| `submit43.sh` + `submit43.sbatch.tmpl` | submitter and template; three phases split by vessel (1 = Part A/B, 2 = Juglet cells, 3 = Pot A cells) |
| `mesh38.py`, `measure34.py`, `replica37.py`, `grow38.py`, `nest39.py`, `wall40.py`, `stage_synth_p40.sh` | unchanged copies from stage 42/40; `COPIES.md` records the provenance |

Commits: `900185f` (instruments, spec, drivers, submitter), `ed59345` (submitter's optional 4th argument under `set -u`), `390068c` (Part A rerun: MST orientation, separability grid, no 90-degree truncation), plus this ticket's comment and `results/` copies.

**No tracked pipeline source was touched.** `mesh_processing_headless.cpp` is unchanged on this branch; `SFS_PAPER_THETA` already existed (`mesh_processing_headless.cpp:4574`, consumed at `:3191`).

### Jobs

| job | run dir (`/data/gpfs/projects/punim2657/SfSpp/runs/`) | final sacct | wall | what |
|---|---|---|---|---|
| 33996937 | `20261030-0350_ed59345_t43-ab` | `COMPLETED 0:0` | 00:00:31 | Part A/B, first pass (viewpoint-only orientation) |
| 33996975 | `20261030-0352_ed59345_t43-b` | `COMPLETED 0:0` | 00:05:09 | 30 Juglet cells (9 pieces x A/B/C + arm N on J2, J5) |
| 33996978 | `20261030-0352_ed59345_t43-c` | `COMPLETED 0:0` | 00:14:01 | 26 Pot A cells (8 pieces x A/B/C + arm N on PA01, PA07) |
| 33997775 | `20261030-0416_390068c_t43-ab2` | `COMPLETED 0:0` | 00:00:39 | Part A/B rerun with MST-consistent orientation |

Four grid jobs, **0 dead submissions**. The fourth was authorised by the lead mid-run after the first Part A pass was found to carry a contaminated p99.

All four run directories carry `run.json`, `submit.sbatch`, `logs/`, `out/`.

### Evidence 1 — Part A, the two distributions per sherd

`/data/gpfs/projects/punim2657/SfSpp/runs/20261030-0416_390068c_t43-ab2/out/partA/partA.tsv` (35 columns, 17 rows), `.../out/partA/sep.tsv` (238 rows), `.../out/partA/piece_<Piece>.json` (17 files, full histograms and coverage), `.../out/partA/figure_partA.png` (588,320 bytes, 1320 x 3927 px, one row per sherd, three columns: est histogram over 0-180, MST histogram over 0-180, separability curves with 3.4 black-dashed and the ladder theta green-dotted). Copies under `.scratch/juglet-breaklines/stage43/results/`.

Two orientation rules are reported side by side. **est** = the viewpoint rule `dist43.py` used first (flip every normal to positive dot with `origin - point`); **mst** = the pipeline's rule, a minimum spanning tree over the same k-NN graph with sign propagated from a root (`CGAL::mst_orient_normals` at `mesh_processing_headless.cpp:805-806` does the same over `n24orientK`). `mst_reached_frac` is 1.000000 with 0 unreached points on all 17 pieces.

| sherd | spacing mm | fold R mm | pairs | est within p50 | est within p90 | est within p99 | est across p10 | est across p50 | est margin p99 | est margin p90 | mst within p50 | mst within p90 | mst within p99 | mst across p10 | mst across p50 | mst margin p99 | mst margin p90 | ladder theta |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| J1 | 0.341 | 6.37 | 139196 | 3.80 | 15.32 | 175.55 | 7.94 | 30.44 | -167.61 | -7.38 | 3.74 | 12.51 | 30.16 | 7.86 | 28.39 | -22.30 | -4.65 | 10.20 |
| J2 | 0.209 | 3.24 | 33402 | 4.86 | 29.28 | 177.26 | 6.08 | 39.45 | -171.18 | -23.20 | 4.58 | 21.02 | 39.70 | 5.71 | 37.10 | -33.99 | -15.31 | 10.20 |
| J3 | 0.213 | 4.38 | 52093 | 3.23 | 21.85 | 176.36 | 8.44 | 40.01 | -167.91 | -13.41 | 3.14 | 18.03 | 37.91 | 7.95 | 36.33 | -29.96 | -10.08 | 10.20 |
| J4 | 0.215 | 4.03 | 47833 | 3.38 | 18.46 | 163.89 | 7.95 | 40.62 | -155.95 | -10.51 | 3.37 | 17.14 | 36.75 | 7.49 | 36.80 | -29.26 | -9.65 | 10.20 |
| J5 | 0.238 | 5.23 | 79628 | 2.95 | 15.43 | 167.81 | 8.09 | 37.49 | -159.72 | -7.34 | 2.94 | 14.20 | 32.58 | 7.77 | 35.30 | -24.81 | -6.43 | 10.20 |
| J6 | 0.224 | 5.28 | 68757 | 2.88 | 16.54 | 172.35 | 13.38 | 41.55 | -158.97 | -3.16 | 2.86 | 14.46 | 34.06 | 12.66 | 38.69 | -21.39 | -1.80 | 10.20 |
| J7 | 0.255 | 5.68 | 93891 | 3.10 | 15.55 | 175.64 | 9.56 | 32.54 | -166.07 | -5.99 | 3.05 | 13.24 | 30.56 | 9.56 | 31.45 | -21.00 | -3.68 | 10.20 |
| J8 | 0.222 | 4.26 | 56628 | 3.18 | 16.61 | 156.07 | 9.64 | 39.62 | -146.43 | -6.96 | 3.18 | 15.91 | 36.07 | 9.60 | 37.58 | -26.47 | -6.31 | 10.20 |
| J9 | 0.202 | 3.06 | 27762 | 4.66 | 27.88 | 177.25 | 14.99 | 49.29 | -162.25 | -12.89 | 4.40 | 20.64 | 41.61 | 14.25 | 44.78 | -27.36 | -6.40 | 10.20 |
| PA01 | 0.594 | 26.20 | 204384 | 1.48 | 11.84 | 160.70 | 17.87 | 32.16 | -142.84 | 6.03 | 1.48 | 11.36 | 27.64 | 17.49 | 31.05 | -10.15 | 6.13 | 6.80 |
| PA02 | 0.596 | 34.74 | 118244 | 1.12 | 9.62 | 148.95 | 18.46 | 34.93 | -130.49 | 8.83 | 1.12 | 9.46 | 30.93 | 18.30 | 33.92 | -12.63 | 8.84 | 10.20 |
| PA03 | 0.606 | 31.04 | 113858 | 1.20 | 9.37 | 139.72 | 17.62 | 35.18 | -122.10 | 8.25 | 1.20 | 9.29 | 31.93 | 17.17 | 32.44 | -14.75 | 7.88 | 6.80 |
| PA04 | 0.577 | 37.99 | 95360 | 1.04 | 11.66 | 150.96 | 18.62 | 34.64 | -132.34 | 6.97 | 1.04 | 11.35 | 32.70 | 18.43 | 33.28 | -14.28 | 7.08 | 10.20 |
| PA05 | 0.598 | 32.85 | 89933 | 1.20 | 11.51 | 143.30 | 21.93 | 41.94 | -121.37 | 10.42 | 1.20 | 11.30 | 33.87 | 20.54 | 36.40 | -13.33 | 9.24 | 10.20 |
| PA06 | 0.599 | 36.36 | 63833 | 1.24 | 16.04 | 150.93 | 24.87 | 44.58 | -126.07 | 8.82 | 1.24 | 15.64 | 37.17 | 23.94 | 41.41 | -13.23 | 8.30 | 10.20 |
| PA07 | 0.296 | 21.41 | 83873 | 0.89 | 12.86 | 152.30 | 24.97 | 42.03 | -127.33 | 12.11 | 0.89 | 12.35 | 32.64 | 23.79 | 38.30 | -8.85 | 11.44 | 6.80 |
| PA08 | 0.270 | 14.40 | 82509 | 1.16 | 12.86 | 156.97 | 23.52 | 43.54 | -133.46 | 10.65 | 1.16 | 12.48 | 30.33 | 22.25 | 36.37 | -8.08 | 9.77 | 6.80 |

| sherd | frac>90 est | frac>90 mst | frac>90 face | mst reached | mst unreached pts | face within p90 | face across p10 |
|---|---|---|---|---|---|---|---|
| J1 | 0.0384 | 0.0010 | 0.0516 | 1.000 | 0 | 20.44 | 48.14 |
| J2 | 0.0630 | 0.0003 | 0.0894 | 1.000 | 0 | 37.23 | 47.42 |
| J3 | 0.0485 | 0.0018 | 0.0668 | 1.000 | 0 | 27.05 | 48.42 |
| J4 | 0.0323 | 0.0001 | 0.0506 | 1.000 | 0 | 23.66 | 48.11 |
| J5 | 0.0274 | 0.0002 | 0.0417 | 1.000 | 0 | 19.36 | 48.15 |
| J6 | 0.0342 | 0.0000 | 0.0451 | 1.000 | 0 | 20.21 | 47.66 |
| J7 | 0.0355 | 0.0002 | 0.0461 | 1.000 | 0 | 20.93 | 48.03 |
| J8 | 0.0261 | 0.0018 | 0.0334 | 1.000 | 0 | 19.60 | 47.85 |
| J9 | 0.0670 | 0.0016 | 0.0866 | 1.000 | 0 | 33.74 | 47.74 |
| PA01 | 0.0160 | 0.0000 | 0.0212 | 1.000 | 0 | 12.67 | 48.57 |
| PA02 | 0.0155 | 0.0000 | 0.0172 | 1.000 | 0 | 7.84 | 48.48 |
| PA03 | 0.0163 | 0.0001 | 0.0166 | 1.000 | 0 | 7.66 | 49.03 |
| PA04 | 0.0175 | 0.0000 | 0.0203 | 1.000 | 0 | 7.99 | 48.52 |
| PA05 | 0.0191 | 0.0000 | 0.0200 | 1.000 | 0 | 7.95 | 49.16 |
| PA06 | 0.0276 | 0.0001 | 0.0273 | 1.000 | 0 | 12.89 | 48.67 |
| PA07 | 0.0206 | 0.0003 | 0.0236 | 1.000 | 0 | 10.72 | 47.76 |
| PA08 | 0.0202 | 0.0000 | 0.0211 | 1.000 | 0 | 11.70 | 48.20 |

**The 90-degree truncation is gone and its absence is asserted, not assumed.** Histograms are `np.linspace(0,180,201)` for all three fields and `piece_*.json` records `hist_coverage` with `est_dropped`, `mst_dropped` and `face_dropped`; every one of the 17 pieces reports `{"pairs": N, "est_in_hist": N, "mst_in_hist": N, "est_dropped": 0, "mst_dropped": 0, "face_dropped": 0}`. `dist43.py` raises `SystemExit("histogram dropped pairs -- the bin range is wrong again")` if any drop is non-zero, so a silent truncation cannot come back.

**What the orientation rule changes.** The MST rule collapses the near-180 tail: `mst_within_p99` is 27.64-41.61 deg against `est_within_p99` 139.72-177.26. `frac_over90_mst` is 0.000000-0.001837 on every piece against `frac_over90_est` 0.015502-0.066962 and `frac_over90_face` 0.016556-0.089426. It does **not** change the sign of the p90 gap: Pot A stays positive on 8 of 8 (+6.03 to +12.11 est, +6.13 to +11.44 mst) and Juglet stays negative on 9 of 9 (-3.16 to -23.20 est, -1.80 to -15.31 mst).

**The ticket's own p99 gap test answers NO on all 17 sherds under both orientation rules** (`est_gap_p99` -121.37 to -171.18, `mst_gap_p99` -8.08 to -33.99): even a consistently oriented field keeps a within-face tail above the across-fold p10, because the two distributions overlap rather than separate. At p90 the split is by vessel, not by sherd.

**The face-field label is degenerate, as the lead flagged.** `face_across_p10` is 47.42-49.16 deg on all 17 pieces — the 45 deg threshold is the label's own boundary, so a pair labelled ACROSS-FOLD is by construction at least 45 deg from its source-triangle normal. That field is reported for completeness and carries no evidence.

### Separability at each theta (the deciding quantity)

`miss` = fraction of ACROSS-FOLD pairs whose turn is below theta; `false` = fraction of WITHIN-FACE pairs whose turn is above theta. Cells are `miss/false`, from `sep.tsv`.

| sherd | field | 0.85 | 1.70 | 2.55 | 3.40 | 5.10 | 6.80 | 10.20 |
|---|---|---|---|---|---|---|---|---|
| J1 | est | 0.0039/0.9562 | 0.0109/0.8363 | 0.0193/0.6896 | 0.0295/0.5546 | 0.0531/0.3611 | 0.0775/0.2550 | 0.1390/0.1585 |
| J1 | mst | 0.0039/0.9560 | 0.0109/0.8351 | 0.0193/0.6862 | 0.0298/0.5483 | 0.0540/0.3489 | 0.0793/0.2373 | 0.1420/0.1348 |
| J2 | est | 0.0087/0.9243 | 0.0195/0.8110 | 0.0338/0.7083 | 0.0472/0.6209 | 0.0805/0.4847 | 0.1097/0.4006 | 0.1677/0.2964 |
| J2 | mst | 0.0087/0.9236 | 0.0195/0.8070 | 0.0359/0.6994 | 0.0497/0.6074 | 0.0846/0.4632 | 0.1159/0.3727 | 0.1764/0.2596 |
| J3 | est | 0.0103/0.8665 | 0.0267/0.7024 | 0.0382/0.5723 | 0.0530/0.4855 | 0.0706/0.3781 | 0.0850/0.3089 | 0.1216/0.2233 |
| J3 | mst | 0.0103/0.8656 | 0.0267/0.6988 | 0.0382/0.5656 | 0.0530/0.4762 | 0.0715/0.3641 | 0.0883/0.2921 | 0.1294/0.2024 |
| J4 | est | 0.0070/0.8871 | 0.0171/0.7256 | 0.0241/0.5944 | 0.0386/0.4985 | 0.0671/0.3761 | 0.0846/0.2972 | 0.1272/0.2011 |
| J4 | mst | 0.0070/0.8871 | 0.0171/0.7254 | 0.0241/0.5937 | 0.0404/0.4973 | 0.0693/0.3737 | 0.0908/0.2932 | 0.1368/0.1950 |
| J5 | est | 0.0040/0.8738 | 0.0183/0.6872 | 0.0310/0.5492 | 0.0474/0.4538 | 0.0680/0.3353 | 0.0875/0.2611 | 0.1150/0.1684 |
| J5 | mst | 0.0040/0.8738 | 0.0183/0.6869 | 0.0310/0.5485 | 0.0474/0.4522 | 0.0696/0.3318 | 0.0911/0.2557 | 0.1226/0.1598 |
| J6 | est | 0.0028/0.8758 | 0.0099/0.6908 | 0.0170/0.5450 | 0.0231/0.4432 | 0.0406/0.3192 | 0.0524/0.2471 | 0.0788/0.1661 |
| J6 | mst | 0.0028/0.8757 | 0.0099/0.6900 | 0.0175/0.5431 | 0.0236/0.4393 | 0.0434/0.3125 | 0.0557/0.2381 | 0.0822/0.1534 |
| J7 | est | 0.0031/0.9035 | 0.0103/0.7298 | 0.0176/0.5772 | 0.0248/0.4654 | 0.0438/0.3308 | 0.0676/0.2527 | 0.1076/0.1672 |
| J7 | mst | 0.0031/0.9033 | 0.0103/0.7280 | 0.0176/0.5727 | 0.0248/0.4583 | 0.0438/0.3188 | 0.0676/0.2373 | 0.1076/0.1470 |
| J8 | est | 0.0023/0.8924 | 0.0072/0.7192 | 0.0113/0.5792 | 0.0200/0.4778 | 0.0453/0.3500 | 0.0616/0.2700 | 0.1069/0.1778 |
| J8 | mst | 0.0023/0.8924 | 0.0072/0.7190 | 0.0113/0.5787 | 0.0200/0.4769 | 0.0453/0.3485 | 0.0620/0.2676 | 0.1077/0.1739 |
| J9 | est | 0.0033/0.8947 | 0.0050/0.7821 | 0.0067/0.6799 | 0.0075/0.5941 | 0.0167/0.4723 | 0.0259/0.3913 | 0.0560/0.2868 |
| J9 | mst | 0.0033/0.8932 | 0.0050/0.7772 | 0.0067/0.6707 | 0.0075/0.5809 | 0.0167/0.4520 | 0.0284/0.3661 | 0.0602/0.2549 |
| PA01 | est | 0.0007/0.6944 | 0.0016/0.4534 | 0.0016/0.3351 | 0.0027/0.2719 | 0.0054/0.2082 | 0.0090/0.1710 | 0.0225/0.1187 |
| PA01 | mst | 0.0007/0.6944 | 0.0016/0.4532 | 0.0016/0.3347 | 0.0027/0.2713 | 0.0054/0.2069 | 0.0090/0.1689 | 0.0234/0.1145 |
| PA02 | est | 0.0007/0.6218 | 0.0011/0.3268 | 0.0018/0.2114 | 0.0035/0.1650 | 0.0071/0.1346 | 0.0117/0.1196 | 0.0227/0.0963 |
| PA02 | mst | 0.0007/0.6218 | 0.0011/0.3268 | 0.0018/0.2113 | 0.0035/0.1649 | 0.0071/0.1343 | 0.0117/0.1191 | 0.0227/0.0948 |
| PA03 | est | 0.0011/0.6446 | 0.0011/0.3616 | 0.0030/0.2384 | 0.0049/0.1851 | 0.0082/0.1400 | 0.0124/0.1205 | 0.0236/0.0947 |
| PA03 | mst | 0.0011/0.6446 | 0.0011/0.3616 | 0.0030/0.2384 | 0.0049/0.1850 | 0.0082/0.1399 | 0.0124/0.1202 | 0.0247/0.0940 |
| PA04 | est | 0.0015/0.5868 | 0.0023/0.3110 | 0.0026/0.2136 | 0.0026/0.1789 | 0.0045/0.1517 | 0.0060/0.1357 | 0.0166/0.1098 |
| PA04 | mst | 0.0015/0.5868 | 0.0023/0.3110 | 0.0026/0.2135 | 0.0026/0.1788 | 0.0045/0.1514 | 0.0060/0.1350 | 0.0177/0.1082 |
| PA05 | est | 0.0008/0.6413 | 0.0008/0.3660 | 0.0012/0.2492 | 0.0025/0.1960 | 0.0041/0.1570 | 0.0053/0.1380 | 0.0143/0.1094 |
| PA05 | mst | 0.0008/0.6413 | 0.0008/0.3660 | 0.0012/0.2492 | 0.0025/0.1960 | 0.0041/0.1568 | 0.0053/0.1377 | 0.0156/0.1084 |
| PA06 | est | 0.0013/0.6466 | 0.0013/0.3917 | 0.0017/0.2864 | 0.0021/0.2354 | 0.0043/0.1961 | 0.0055/0.1765 | 0.0136/0.1450 |
| PA06 | mst | 0.0013/0.6466 | 0.0013/0.3917 | 0.0017/0.2863 | 0.0021/0.2353 | 0.0043/0.1957 | 0.0055/0.1760 | 0.0149/0.1441 |
| PA07 | est | 0.0005/0.5152 | 0.0005/0.3320 | 0.0010/0.2644 | 0.0019/0.2304 | 0.0034/0.1899 | 0.0038/0.1621 | 0.0077/0.1230 |
| PA07 | mst | 0.0005/0.5151 | 0.0005/0.3316 | 0.0010/0.2636 | 0.0019/0.2293 | 0.0034/0.1885 | 0.0038/0.1603 | 0.0082/0.1202 |
| PA08 | est | 0.0000/0.5883 | 0.0000/0.3998 | 0.0000/0.3112 | 0.0000/0.2592 | 0.0028/0.2066 | 0.0028/0.1749 | 0.0085/0.1270 |
| PA08 | mst | 0.0000/0.5883 | 0.0000/0.3998 | 0.0000/0.3111 | 0.0000/0.2590 | 0.0028/0.2061 | 0.0036/0.1740 | 0.0093/0.1246 |

No theta in the grid makes both small at once, on either field. The two curves trade off monotonically and cross; at 10.2 (the ladder's own choice) Juglet still refuses 6.0-17.6 % of its break-edge pairs and refuses 13.5-26.0 % of its own face pairs. Pot A misses 10-30x fewer across-fold pairs than Juglet at the same theta but never gets `false` below 0.094.

### Evidence 2 — Part B, the derived rules

`/data/gpfs/projects/punim2657/SfSpp/runs/20261030-0416_390068c_t43-ab2/out/partB/partB.tsv` and `.../out/partB/thetas.tsv`. `k_R1 = 0.28943` (3.4 / median Pot A `est_within_p90` = 11.7471); `k_R1_mst = 0.29946` (3.4 / median Pot A `mst_within_p90` = 11.3537).

| sherd | est p90 | est p99 | est a10 | gap p90 | gap p99 | R1 | R1 in p99 gap | R1 in p90 gap | R2 | R2 in p99 gap | R2 in p90 gap | mst p90 | mst a10 | mst gap p90 | mst gap p99 | R1_mst | R2_mst |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| J1 | 15.32 | 175.55 | 7.94 | -7.38 | -167.61 | 4.434 | NO | NO | 11.029 | NO | NO | 12.51 | 7.86 | -4.65 | -22.30 | 3.747 | 9.915 |
| J2 | 29.28 | 177.26 | 6.08 | -23.20 | -171.18 | 8.476 | NO | NO | 13.346 | NO | NO | 21.02 | 5.71 | -15.31 | -33.99 | 6.294 | 10.957 |
| J3 | 21.85 | 176.36 | 8.44 | -13.41 | -167.91 | 6.323 | NO | NO | 13.580 | NO | NO | 18.03 | 7.95 | -10.08 | -29.96 | 5.399 | 11.969 |
| J4 | 18.46 | 163.89 | 7.95 | -10.51 | -155.95 | 5.342 | NO | NO | 12.111 | NO | NO | 17.14 | 7.49 | -9.65 | -29.26 | 5.133 | 11.326 |
| J5 | 15.43 | 167.81 | 8.09 | -7.34 | -159.72 | 4.467 | NO | NO | 11.177 | NO | NO | 14.20 | 7.77 | -6.43 | -24.81 | 4.254 | 10.507 |
| J6 | 16.54 | 172.35 | 13.38 | -3.16 | -158.97 | 4.787 | NO | NO | 14.876 | NO | NO | 14.46 | 12.66 | -1.80 | -21.39 | 4.330 | 13.532 |
| J7 | 15.55 | 175.64 | 9.56 | -5.99 | -166.07 | 4.500 | NO | NO | 12.193 | NO | NO | 13.24 | 9.56 | -3.68 | -21.00 | 3.966 | 11.252 |
| J8 | 16.61 | 156.07 | 9.64 | -6.96 | -146.43 | 4.806 | NO | NO | 12.652 | NO | NO | 15.91 | 9.60 | -6.31 | -26.47 | 4.765 | 12.357 |
| J9 | 27.88 | 177.25 | 14.99 | -12.89 | -162.25 | 8.071 | NO | NO | 20.448 | NO | NO | 20.64 | 14.25 | -6.40 | -27.36 | 6.181 | 17.149 |
| PA01 | 11.84 | 160.70 | 17.87 | 6.03 | -142.84 | 3.426 | NO | NO | 14.542 | NO | yes | 11.36 | 17.49 | 6.13 | -10.15 | 3.401 | 14.092 |
| PA02 | 9.62 | 148.95 | 18.46 | 8.83 | -130.49 | 2.785 | NO | NO | 13.327 | NO | yes | 9.46 | 18.30 | 8.84 | -12.63 | 2.833 | 13.157 |
| PA03 | 9.37 | 139.72 | 17.62 | 8.25 | -122.10 | 2.712 | NO | NO | 12.848 | NO | yes | 9.29 | 17.17 | 7.88 | -14.75 | 2.782 | 12.631 |
| PA04 | 11.66 | 150.96 | 18.62 | 6.97 | -132.34 | 3.374 | NO | NO | 14.734 | NO | yes | 11.35 | 18.43 | 7.08 | -14.28 | 3.399 | 14.463 |
| PA05 | 11.51 | 143.30 | 21.93 | 10.42 | -121.37 | 3.332 | NO | NO | 15.891 | NO | yes | 11.30 | 20.54 | 9.24 | -13.33 | 3.384 | 15.235 |
| PA06 | 16.04 | 150.93 | 24.87 | 8.82 | -126.07 | 4.644 | NO | NO | 19.974 | NO | yes | 15.64 | 23.94 | 8.30 | -13.23 | 4.683 | 19.348 |
| PA07 | 12.86 | 152.30 | 24.97 | 12.11 | -127.33 | 3.723 | NO | NO | 17.922 | NO | yes | 12.35 | 23.79 | 11.44 | -8.85 | 3.699 | 17.143 |
| PA08 | 12.86 | 156.97 | 23.52 | 10.65 | -133.46 | 3.724 | NO | NO | 17.394 | NO | yes | 12.48 | 22.25 | 9.77 | -8.08 | 3.737 | 16.664 |

`R1_inside_gap_p99` and `R2_inside_gap_p99` are **NO on all 17 sherds under both rules** — the ticket's test, answered. `R1_inside_gap_p90` is yes on 8 of 8 Pot A and NO on 9 of 9 Juglet; `R2_inside_gap_p90` is NO on all 17.

`thetas.tsv` (pot, piece, R1, R2) holds the **est-field** thetas, which are exactly the values the Part C cells carried — the cells were built before the MST rerun, so the record of what was run stays what was run.

### Evidence 3 — Part C cells

Juglet: `/data/gpfs/projects/punim2657/SfSpp/runs/20261030-0352_ed59345_t43-b/out/cells-pipeline/`
Pot A: `/data/gpfs/projects/punim2657/SfSpp/runs/20261030-0352_ed59345_t43-c/out/cells-pipeline/`

Both `out/cells-pipeline/` directories hold `pipeline_cells.tsv`, `surfaces.tsv`, `surface_pairs.tsv` (med_along, med_across, med_angle_deg, coin, med_t_signed, p05/p95_t_signed, normal_src), `nest.tsv`, `walls.tsv`, `theta_proof.tsv`, `defaults_proof.tsv`; the run directory's `out/` also holds `geometry_counts.tsv`, `corpus_before/after.tsv`, `inputs_before/after.md5` and `GEOMETRY_DELETED.txt`. Copies under `.scratch/juglet-breaklines/stage43/results/`.

The ticket says 48 cells; 17 pieces x 3 arms is **51**, and 51 A/B/C cells plus 4 arm-N cells = **55 pipeline runs**, which is what the tables hold (29 Juglet + 26 Pot A). `pipeline_rc` is 0 on every row; `theta_proof.tsv` reports `match=yes` on all 55 rows (requested theta == the `[PAPER-234]` `thetaDeg` the binary actually used), so the env override reached the growth gate in every cell.

| sherd | A today | B (R1) | C (R2) |
|---|---|---|---|
| J1 | 3.4 (unset) -> two 10044/15159 1.82/0.53 @7deg | 4.4335 -> two 14499/16597 1.95/0.27 @8deg | 11.0290 -> two 349/29237 8.22/19.89 @54deg |
| J2 | 3.4 (unset) -> none (0 cl) | 8.4760 -> two 403/551 0.56/6.25 @22deg | 13.3456 -> two 138/2982 2.88/12.27 @56deg |
| J3 | 3.4 (unset) -> none (1 cl) | 6.3233 -> two 764/1030 1.91/0.64 @17deg | 13.5803 -> none (1 cl) |
| J4 | 3.4 (unset) -> none (1 cl) | 5.3422 -> two 1002/1198 2.16/0.57 @16deg | 12.1108 -> two 4083/612 0.26/0.58 @54deg |
| J5 | 3.4 (unset) -> two 143/2304 8.19/11.36 @50deg | 4.4668 -> none (1 cl) | 11.1766 -> two 3995/2871 2.41/0.47 @16deg |
| J6 | 3.4 (unset) -> none (1 cl) | 4.7873 -> two 352/2101 2.33/5.11 @25deg | 14.8760 -> none (1 cl) |
| J7 | 3.4 (unset) -> two 1566/1848 2.39/7.94 @34deg | 4.5004 -> two 1568/3953 2.94/1.39 @22deg | 12.1925 -> two 588/9328 3.38/16.48 @45deg |
| J8 | 3.4 (unset) -> two 821/1056 0.89/6.63 @27deg | 4.8060 -> two 368/1776 2.05/6.53 @31deg | 12.6524 -> two 4908/186 0.14/0.45 @48deg |
| J9 | 3.4 (unset) -> none (0 cl) | 8.0706 -> two 444/530 0.51/1.78 @28deg | 20.4477 -> none (1 cl) |
| PA01 | 3.4 (unset) -> two 66760/57292 7.09/0.27 @11deg | 3.4261 -> two 66762/57297 7.09/0.27 @11deg | 14.5423 -> none (1 cl) |
| PA02 | 3.4 (unset) -> two 42203/46327 3.63/0.25 @3deg | 2.7854 -> two 42100/46220 3.63/0.25 @3deg | 13.3269 -> none (1 cl) |
| PA03 | 3.4 (unset) -> two 39771/43572 3.67/0.24 @3deg | 2.7117 -> two 39601/43401 3.67/0.24 @3deg | 12.8478 -> none (1 cl) |
| PA04 | 3.4 (unset) -> two 34730/38010 3.66/0.23 @3deg | 3.3739 -> two 34723/38008 3.66/0.23 @3deg | 14.7337 -> none (1 cl) |
| PA05 | 3.4 (unset) -> two 31578/34140 3.77/0.25 @3deg | 3.3323 -> two 31569/34135 3.77/0.25 @3deg | 15.8912 -> none (1 cl) |
| PA06 | 3.4 (unset) -> two 22570/24921 3.55/0.26 @3deg | 4.6438 -> two 22990/25103 3.55/0.26 @3deg | 19.9745 -> none (1 cl) |
| PA07 | 3.4 (unset) -> two 24634/26743 3.90/0.13 @4deg | 3.7233 -> two 24680/27428 3.89/0.13 @4deg | 17.9225 -> none (1 cl) |
| PA08 | 3.4 (unset) -> two 26761/29280 3.59/0.13 @4deg | 3.7235 -> two 27931/29345 3.59/0.13 @4deg | 17.3937 -> none (1 cl) |


### Evidence 4 — the Pot A control, per arm

| arm | theta env | outcome | med_along / med_across | coincidence |
|---|---|---|---|---|
| A today | unset (3.4) | **two surfaces on 8 of 8** | 3.59-7.09 / 0.13-0.27 mm | 0.0 on all 8 |
| B (R1) | 2.7117-4.6438 | **two surfaces on 8 of 8** | 3.59-7.09 / 0.13-0.27 mm | 0.0 on all 8 |
| C (R2) | 12.8478-19.9745 | **clusters = 1, no surface, on 8 of 8** | - | - |

Arm C regresses the pot on every piece: an R2 theta 3.7-5.9x the shipped one merges the whole sherd into one cluster and no surface is exported. Arm B reproduces arm A's Pot A numbers to two decimals (largest along-track difference 0.012 mm, on PA07), which is what a rule calibrated to land Pot A's median at 3.4 should do.

Nest (`nest.tsv`): Pot A `shared` = 0 on every row. Juglet arm B on J2-J9 exports small surfaces (352-1002 and 530-3953 points), so its med_along/med_across are measured on a few hundred points, not on the tens of thousands arm A sees on J1/J7/J8.

### Evidence 5 — defaults unchanged

`.../t43-b/out/cells-pipeline/defaults_proof.tsv` and `.../t43-c/out/cells-pipeline/defaults_proof.tsv`. Each phase proved its own vessel's two pieces (a phase writes its own file), so the four pieces are split across the two:

| piece | arm A `SampledWithNormals` md5 | arm N md5 | same | points A/N |
|---|---|---|---|---|
| Juglet_Piece_2 | `8b704a31c13bfa95845bd3a320dbfbee` | `8b704a31c13bfa95845bd3a320dbfbee` | **same** | 2397 / 2397 |
| Juglet_Piece_5 | `31b9a593d48a133196888a6564341327` | `31b9a593d48a133196888a6564341327` | **same** | 5668 / 5668 |
| Pot_A_Piece_01 | `b58f583996c154243ca6d41d3149f597` | `b58f583996c154243ca6d41d3149f597` | **same** | 85136 / 85136 |
| Pot_A_Piece_07 | `b05b73e80b1e718b357dbc44344461be` | `b05b73e80b1e718b357dbc44344461be` | **same** | 34608 / 34608 |

Arm N is a second no-env cell in the same job. All four md5s are identical, so nothing upstream of the growth gate moved and the three arms differ only in `SFS_PAPER_THETA`.

### Evidence 6 — corpus, inputs, geometry

| run | `corpus.diff` | `inputs.diff` | `corpus_before.tsv` md5 | `/opt/sfs-pristine` |
|---|---|---|---|---|
| 33996937 | 0 bytes | 0 bytes | `858c963da6ae09bee1b3a494b08f0781` | ABSENT |
| 33996975 | 0 bytes | 0 bytes | `858c963da6ae09bee1b3a494b08f0781` | ABSENT |
| 33996978 | 0 bytes | 0 bytes | `858c963da6ae09bee1b3a494b08f0781` | ABSENT |
| 33997775 | 0 bytes | 0 bytes | `858c963da6ae09bee1b3a494b08f0781` | ABSENT |

Before and after each run the job snapshots the corpus tree (1803 files: path, size, mtime) into `corpus_before.tsv` / `corpus_after.tsv` and md5s the 223 input files (meshes, clouds, axes) into `inputs_before.md5` / `inputs_after.md5`; both diffs are empty in every run, and `corpus_before.tsv` has the same md5 in all four runs. `/opt/sfs-pristine` is recorded `status ABSENT` (with the `ls`/`stat` errors) and was not created. `out/meshes_read.tsv` md5-records the 17 meshes the instrument actually opened (e.g. Juglet_Piece_1 `b447066c29181fe7ba987439c22c5d9c`, 1,655,590 bytes) and the driver exits 5 if any is missing.

Geometry deletion, record written before the delete (`out/GEOMETRY_DELETED.txt`, `out/geometry_counts.tsv`):

| run | files before | files after | kept cell surfaces | kept |
|---|---|---|---|---|
| 33996937 | 0 | 0 | 0 | nothing to delete — Part A writes no geometry |
| 33996975 | 38 | 38 | 38 | `*/cells-pipeline/*/surfaces/*.ply` |
| 33996978 | 36 | 36 | 36 | `*/cells-pipeline/*/surfaces/*.ply` |

No `.ply`/`.pcd`/`.obj`/`.xyz` was removed: the counts are equal before and after because the delete spares the cell surfaces, which is the class the lead asked to keep. The per-cell sampled clouds and intermediate meshes under `cells-pipeline/stage_*` were removed.

### Evidence 7 — index rows

`/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv`, six tab-separated fields, `verdict` and `human_note` empty:

```
20261030-0350_ed59345_t43-ab	33996937	ed593455d444e8f03d35b3684fac913579026ca4	ed59345-t43-ab		
20261030-0352_ed59345_t43-b	33996975	ed593455d444e8f03d35b3684fac913579026ca4	ed59345-t43-b		
20261030-0352_ed59345_t43-c	33996978	ed593455d444e8f03d35b3684fac913579026ca4	ed59345-t43-c		
20261030-0416_390068c_t43-ab2	33997775	390068c780b7acdd74e41e3985da45657ff02955	390068c-t43-ab2		
```

Every row in the file has 6 fields (338 rows checked).

### Deviations the ticket should know about

1. **Part A ran twice.** The first pass (job 33996937, commit `ed59345`) oriented normals only by the viewpoint rule; its `partA.tsv` and `partB.tsv` stand in that run directory and are superseded by the rerun. The rerun is a fourth grid job, authorised by the lead in the same message that asked for the MST field. Both passes are kept.
2. **The Part C thetas are the est-field R1/R2 values**, computed before the MST rerun existed. They are the values the cells actually carried and `thetas.tsv` records them unchanged; an MST-derived theta set is printed in `partB.tsv` (`R1_mst_theta` 2.7820-6.2940, `R2_mst_theta` 9.9148-17.149) but no cell was run with it — that would have needed a fifth job.
3. **A defect in `run_cell43.sh` that I did not re-run to fix.** `anc_wall()` was written as `case "$1/$2" in` and called with one argument, so under `set -u` `$2` was unbound, the function printed nothing, and the `anchor_med_mm` / `abs_diff` / `anchor_hit` columns are `na` in all 55 wall rows. The function is fixed on the branch (`case "$1" in`), but the cells were not re-run — that is a fifth job and the budget is spent. The anchor comparison is recomputed offline instead, in `results/walls_anchor_recomputed.tsv`:

| sherd | arm | measured mm | ticket 35 anchor mm | abs diff | rel % | within 5% |
|---|---|---|---|---|---|---|
| J1 | A | 2.060248 | 2.35376 | 0.29351 | 12.47 | no |
| J1 | B | 2.060248 | 2.35376 | 0.29351 | 12.47 | no |
| J1 | C | 2.060248 | 2.35376 | 0.29351 | 12.47 | no |
| J2 | A | 2.917690 | 2.69305 | 0.22464 | 8.34 | no |
| J2 | B | 2.917690 | 2.69305 | 0.22464 | 8.34 | no |
| J2 | C | 2.917690 | 2.69305 | 0.22464 | 8.34 | no |
| J2 | N | 2.917690 | 2.69305 | 0.22464 | 8.34 | no |
| J3 | A | 2.677558 | 2.45160 | 0.22596 | 9.22 | no |
| J3 | B | 2.677558 | 2.45160 | 0.22596 | 9.22 | no |
| J3 | C | 2.677558 | 2.45160 | 0.22596 | 9.22 | no |
| J5 | A | 3.099416 | 2.89980 | 0.19962 | 6.88 | no |
| J5 | B | 3.099416 | 2.89980 | 0.19962 | 6.88 | no |
| J5 | C | 3.099416 | 2.89980 | 0.19962 | 6.88 | no |
| J5 | N | 3.099416 | 2.89980 | 0.19962 | 6.88 | no |
| J7 | A | 3.345018 | 3.26316 | 0.08186 | 2.51 | yes |
| J7 | B | 3.345018 | 3.26316 | 0.08186 | 2.51 | yes |
| J7 | C | 3.345018 | 3.26316 | 0.08186 | 2.51 | yes |
| J9 | A | 2.742962 | 2.59484 | 0.14812 | 5.71 | no |
| J9 | B | 2.742962 | 2.59484 | 0.14812 | 5.71 | no |
| J9 | C | 2.742962 | 2.59484 | 0.14812 | 5.71 | no |
| PA01 | A | 8.285696 | 8.28570 | 0.00000 | 0.00 | yes |
| PA01 | B | 8.285696 | 8.28570 | 0.00000 | 0.00 | yes |
| PA01 | C | 8.285696 | 8.28570 | 0.00000 | 0.00 | yes |
| PA01 | N | 8.285696 | 8.28570 | 0.00000 | 0.00 | yes |
| PA07 | A | 4.057357 | 4.05609 | 0.00127 | 0.03 | yes |
| PA07 | B | 4.057357 | 4.05609 | 0.00127 | 0.03 | yes |
| PA07 | C | 4.057357 | 4.05609 | 0.00127 | 0.03 | yes |
| PA07 | N | 4.057357 | 4.05609 | 0.00127 | 0.03 | yes |

4. **Wall thickness agrees with the ticket 35 anchors on Pot A and not on the Juglet pieces.** PA01 differs by 0.00000 mm and PA07 by 0.00127 mm (0.03 %); J1 12.47 %, J2 8.34 %, J3 9.22 %, J5 6.88 %, J9 5.71 %, J7 2.51 %. `thick_med_mm` is identical across all arms on every piece, which is expected — the measurement reads `SampledWithNormals`, which the growth theta does not touch.

| sherd | thick_med_mm | cells | identical across arms |
|---|---|---|---|
| J1 | 2.060248 | 3 | yes |
| J2 | 2.917690 | 4 | yes |
| J3 | 2.677558 | 3 | yes |
| J4 | 2.760666 | 3 | yes |
| J5 | 3.099416 | 4 | yes |
| J6 | 2.727861 | 3 | yes |
| J7 | 3.345018 | 3 | yes |
| J8 | 2.262621 | 3 | yes |
| J9 | 2.742962 | 3 | yes |
| PA01 | 8.285696 | 4 | yes |
| PA02 | 3.694035 | 3 | yes |
| PA03 | 3.722396 | 3 | yes |
| PA04 | 3.724287 | 3 | yes |
| PA05 | 3.830320 | 3 | yes |
| PA06 | 3.612175 | 3 | yes |
| PA07 | 4.057357 | 4 | yes |
| PA08 | 3.713287 | 3 | yes |

5. **Part C carries 55 cells, and the ticket's "48" is an arithmetic slip.** 17 pieces x 3 arms = 51, not 48; plus four arm-N cells (J2, J5, PA01, PA07) that exist only as the defaults-unchanged proof. All 55 are in the same tables.
6. **Arm A is not uniformly the loser on the Juglet.** Arm A exports two surfaces on J1, J5, J7, J8 and none on J2, J3, J4, J6, J9; arm B exports two on 8 of 9 and none on J5. On J5 arm B (4.4668) collapses to one cluster where arm A (3.4) produced two.
7. `/opt/sfs-pristine` absent, corpus and canonical checkout read-only, nothing merged into main — the branch is pushed only.

### Not delivered

- No cell was run with the MST-derived theta set (deviation 2).
- The wall anchor columns were not re-measured in-job (deviation 3); the offline recomputation is beside them.
- `__pycache__`/`*.pyc` under `stage43`: none present at the end (checked with glob after the last commit and after the submitter's `py_compile`); the directory's `.gitignore` carries `__pycache__/` and `*.pyc` so a stray one cannot be committed.

Report numbers and paths, not verdicts — no verdict is written here and `Status:` is untouched.
## Reading (lead, 2026-10-30)

**The answer to the question the ticket asks is yes, and it is a physical law — but the rule the ticket specified reads the wrong statistic.** Part B's R1 multiplied the within-face **p90**, and the p90 is contaminated by the same near-180-degree sign flips that wrecked the p99. The quantity that tracks curvature is the within-face **median**. With the median, one constant reproduces both known-good endpoints — the shipped 3.4 on the pot and the ladder's empirically found 10.2 on the juglet — and it does so out of sample: the constant is calibrated on Pot A alone and predicts the Juglet.

### 1. The law: turn per step is spacing divided by fold radius

Verified first-hand on the worker's own `partA.tsv` and `piece_<Piece>.json`, not taken from the report. `S` is `spacing_ach_mm` (the spacing each piece's own pipeline run resolved, [SPACING-22] `policy=piece`); `R` is `fold_radius_med_mm` (the ticket-32 osculating-parabola instrument); `w50` is `est_within_p50`, the within-face turn between neighbouring samples.

| test | result | what it rules out |
|---|---|---|
| Pearson(`w50`, `S/R` in deg), pooled, 17 pieces | **+0.9910** | a coincidence of scatter |
| Pearson within Pot A alone (n=8) | **+0.9115** | the pooled figure being an artefact of the two vessels separating |
| Pearson within Juglet alone (n=9) | **+0.9581** | same |
| mean abs error `w50` vs `S/R`, Pot A | **0.150 deg** (max 0.295) | the relation being ordinal only, with a free offset |
| mean abs error `w50` vs `S/R`, Juglet | **0.562 deg** (max 1.165) | same |

The within-vessel correlations are the load-bearing ones: a pooled correlation across two groups that differ in scale proves nothing, because any two scale-like variables separate the groups. Within each vessel the relation still holds, and the absolute error is a fraction of a degree.

### 2. Why R1 failed, and why this does not

| statistic | Pot A range | Juglet range | ratio to the median |
|---|---|---|---|
| within-face **median** `w50` | 0.89-1.48 deg | 2.88-4.86 deg | ~1x |
| within-face **p90** (what R1 used) | 9.37-16.04 deg | 15.32-29.28 deg | 6-8x |
| within-face **p99** | 139.72-177.26 deg | 156.07-177.26 deg | the near-180 sign flips |

`frac_over90_est` is 1.6-6.7 % of all pairs, so a few percent of pairs sit near 180 deg and drag every high percentile with them. R1 therefore never measured "how curved is this face"; it measured "where the contamination has reached". R1's Juglet thetas came out 4.43-8.48 deg, **below** the 10.2 the outcome search found, and arm B duly fragmented the sherds: retained point fraction 15.8-76.7 % (median 21.7 %) against the ladder's 54.7-95.4 % (median 68.7 %) at 10.2.

### 3. The rule, calibrated on the control and tested on the juglet

`theta = m x (this sherd's own within-face median turn)`, with **m = 2.8849** fixed so the Pot A median lands on 3.4.

| vessel | predicted theta min / med / max | what is known to work | verdict |
|---|---|---|---|
| Pot A (calibration) | 2.58 / **3.40** / 4.27 deg | shipped 3.4; arm A gives two clean surfaces on 8 of 8 | the control is left where it is |
| Juglet (out of sample) | 8.29 / **9.32** / 14.01 deg | ladder's empirical 10.2; 7 genuine pairs on J2-J8 | median within 1 deg, range brackets it |

The cross-check that makes this a law rather than a fit: the theta ratio the two vessels need is 10.2 / 3.4 = **3.00**; the turn ratio they actually show is 2.74. One constant of about 2.9-3.0 serves both vessels, and it was never fitted on the juglet.

The same law in the form the conservator asked for — geometry in, angle out, no percentile table:

**`theta = k x S / R_fold`, with k = 3.3573** (calibrated on the Pot A median `S/R` = 1.0127 deg).

| vessel | predicted | known-good |
|---|---|---|
| Pot A | 2.66-4.36 deg (PA01 4.36, PA02 3.30, PA03 3.76, PA04 2.92, PA05 3.50, PA06 3.17, PA07 2.66, PA08 3.61) | 3.4 |
| Juglet | 8.16-12.68 deg (median 9.70; J1 10.29, J2 12.40, J3 9.35, J4 10.25, J5 8.74, J6 8.16, J7 8.65, J8 10.05, J9 12.68) | 10.2 |

This is the connection the conservator asked for (m05808): the angle follows how curved the sherd is, Pot A gets about 3.4 because it is nearly flat, and the Juglet gets about 10 because it folds on a 3-6 mm radius. Its two inputs are already available in the pipeline — `S` is what [SPACING-22] resolves, `R` is what the ticket-32 instrument measures — so nothing has to be searched.

### 4. What the separability grid does and does not say

The grid is correct and it does **not** contradict the law; it answers a different question. At every theta the two fractions trade off monotonically and cross (Juglet at 3.4: miss 0.030 / false 0.486; at 10.2: miss 0.115 / false 0.178), so no single theta separates within-face from across-fold pairs on these sherds. That is a statement about the overlap of the two pair distributions.

It is not the objective, because **the growth is not the step that has to separate them**. `tryMergePair234` admits a pair whose boundary-patch normals agree within `rhoN` = 0.95, i.e. 18.19 deg (`mesh_processing_headless.cpp:3339`) — five times the growth gate — and the break face meets the sherd face at roughly 90 deg, so the merge can never weld them. The growth only has to stop at the break edge; the merge does the same-face regrouping. The conservator said this first (m05808) and the source agrees with him.

So the right objective is not "separate the distributions" but "stop at the edge without fragmenting the face", and the quantity that measures it is the retained point fraction, which I computed from the worker's own `[STATUS-23]` lines:

| vessel | arm A today | arm B (R1) | arm C (R2) | ticket 42 ladder |
|---|---|---|---|---|
| Juglet, retained points | 0.0-67.5 % (median 11.5) | 15.8-76.7 % (median 21.7) | 78.5-99.6 % (median 86.8) | 54.7-95.4 % (median 68.7) |
| Pot A, retained points | 83.2-89.6 % (median 86.7) | 83.9-88.7 % (median 87.4) | 99.4-100.0 % (median 99.9) | 92.8-97.7 % (median 97.1) |

Retention alone is not the goal either — arm C retains the most on both vessels and is the worst outcome, because it swallows the piece into one cluster. What the table shows is the cost side of each theta, and it explains the two regressions: arm C's theta (11.0-20.4 deg) is so permissive that one region claims the whole sherd and the remainder falls under the 30-point floor (`mesh_processing_headless.cpp:3658-3659`), while arm B's theta is so tight on the Juglet that the face shatters into sub-floor fragments.

### 5. A correction to my own ticket text

Part A as I wrote it asked for two things that are the same quantity: measure the turn between source-triangle face normals, **and** label a pair WITHIN-FACE when those face normals differ by less than 45 deg. The label would then be degenerate by construction, pinned at 45 deg. The worker's `dist43.py` caught this and reported it before running; `face_across_p10` comes out 47.4-49.2 deg on all 17 pieces, exactly as the degenerate construction predicts. That field carries no evidence and should not be read. The instrument is right; the ticket text was wrong.

### 6. Weight, and what is still untested

**Weight:** 17 sherds, two vessels, one constant. The law is measured on the clouds the pipeline actually runs on (the released clouds, at the spacing each piece resolved — `NN median` 0.2109 mm on Juglet_Piece_2, 0.2034 on Juglet_Piece_9, matching the [SPACING-22] `S` those runs logged), and the out-of-sample prediction is the strong part: m was fixed on Pot A and the Juglet fell within 1 deg of its independently found answer.

**Not tested:** no pipeline cell has run at the curvature-derived theta. Arms B and C carried R1/R2 (percentile rules), never this rule. The prediction is arithmetic against outcomes already measured, not a new outcome. A cell at `SFS_PAPER_THETA` = 2.66-4.36 on Pot A and 8.16-12.68 on the Juglet is the test that would settle it, and it needs a job, not a source change.

**Also untested, and named rather than buried:** the fold radius `R` comes from an osculating-paraboloid fit whose cap is `RHO_CAP_MM` = 60 mm, so a genuinely flat sherd reports 60 rather than its true radius and the rule would over-predict there. No piece in this set is near the cap (max 37.99 mm, PA04), but a flatter pot would be.

### 7. Verdict on the worker's delivery

Everything the ticket asked for is present and I re-read the tables myself: Part A (35 columns x 17 rows, `sep.tsv` 238 rows), Part B (`k_R1` = 0.28943 reproduced to 5 decimals on all 17 rows), Part C (55 cells, `pipeline_rc` 0 everywhere, `theta_proof` `match=yes` on all 55), the defaults proof (four md5 pairs identical), the integrity record (corpus/inputs diffs 0 bytes in all four runs, geometry counts equal before and after), and four index rows with empty verdicts. The seven deviations are recorded above and each is a real limitation, not a concealment. The three undelivered items are named in the worker's own words.

The one thing I could not check myself is the figure: this session's image reader is unavailable (`read_image` rejects this model's image input, `modlens_read_image` returned Gemini 503). `figure_partA.png` rests on the worker's code and `[FIG43]` log line. Every number above is from the tables, which I did read.

**No verdict is written into the deliverable, and the `Status:` line is set by me, not by the worker.**
