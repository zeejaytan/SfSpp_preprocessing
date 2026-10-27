# Ticket 29 — what angle does each cloud's wall carry, and which theta would serve the Juglet

Answers U19. Measured by run `20261027-1637_7c3248f_t29-angle-survey` (job 33865557,
commit `7c3248fbbe5370636210fa7288eb5dc1f328910e`), which ran on a compute node and read the
rung-2 clouds and normals of 13 clouds in place: Juglet pieces 2, 3, 5, 7 in arms B, D, E
(from `20261027-0337_d69f76f_t25-dump-grid2`) and Pot A piece 07 at the defaults (from
`20261027-1537_5227f8f_t28-pota07-dump`).

## The answer

**No single theta in 2.0 … 12.0 serves both vessels. The gap is not marginal, it is an order of
magnitude in the input.** At the growth's own candidate set (k = 10 nearest neighbours) the median
angle between a point's normal and its neighbours' is **1.20 deg on Pot A 07** and **8.21–15.80 deg
on the Juglet's four pieces**. The shipped theta of 3.4 deg therefore admits 72.4 % of Pot A's
neighbour pairs and only 10.8–19.5 % of the Juglet's: on the Juglet, 3.4 deg is near the noise
floor, not a segmentation rule.

- **Juglet**: 0 of 4 clouds pass anywhere in 2.0–5.0 deg (kgate exactly 0.0000 — almost nothing is
  claimed by regions at or above 50 points). The first cloud passes at 6.0 deg (1 of 4), and all
  four only at **12.0 deg** (kgate 0.5015 on arm B and D, 0.7696 on arm E — 0.5015 is a hair over
  the 0.5 bar).
- **Pot A 07**: passes at **3.4 deg and nowhere else** — 8 regions at or above the floor at 3.4
  (3093 / 2850 intact), 6 at 4.0 and at 2.0 (at 2.0 the two big regions are themselves already
  broken, 3043 / 2761), and 3 at 12.0 where the two big regions stay intact (4529 / 3103) but the
  small-region structure is gone.
- **Closest on each side**: the Juglet's side is theta 12.0; Pot A's side is theta 3.4. Nothing
  between them moves both bars at once, so a theta-only change to the growth rule cannot be
  calibrated on these two clouds at the same time.

## Part A — the angle each cloud carries (k = 10, directed pairs, n·k per cloud)

| cloud | npts | pairs | p10 | p50 | p90 | p99 | ≤2.0 | ≤3.4 | ≤4.0 | ≤6.0 | ≤8.0 | ≤12.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B/Juglet_Piece_2 | 1031 | 10310 | 3.20 | 15.80 | 50.57 | 82.83 | 5.6 % | 10.8 % | 13.7 % | 21.3 % | 27.8 % | 40.6 % |
| B/Juglet_Piece_3 | 1467 | 14670 | 2.59 | 13.46 | 50.18 | 81.14 | 6.9 % | 15.0 % | 18.2 % | 28.6 % | 36.4 % | 46.4 % |
| B/Juglet_Piece_5 | 3021 | 30210 | 2.18 | 9.30 | 41.23 | 80.67 | 8.9 % | 19.2 % | 23.5 % | 36.0 % | 45.3 % | 58.1 % |
| B/Juglet_Piece_7 | 4254 | 42540 | 2.13 | 8.21 | 35.54 | 79.55 | 9.1 % | 19.5 % | 24.1 % | 38.2 % | 48.9 % | 63.8 % |
| E/Juglet_Piece_2 | 2565 | 25650 | 4.06 | 14.86 | 37.63 | 60.57 | 3.7 % | 7.9 % | 9.8 % | 17.5 % | 24.8 % | 39.9 % |
| E/Juglet_Piece_3 | 3486 | 34860 | 3.44 | 14.31 | 37.16 | 59.74 | 4.3 % | 9.8 % | 12.2 % | 20.4 % | 28.4 % | 42.8 % |
| E/Juglet_Piece_5 | 6208 | 62080 | 2.65 | 10.92 | 32.82 | 55.86 | 6.4 % | 14.0 % | 17.6 % | 28.9 % | 38.2 % | 54.2 % |
| E/Juglet_Piece_7 | 8421 | 84210 | 2.20 | 8.73 | 27.93 | 55.10 | 8.7 % | 18.5 % | 22.9 % | 36.2 % | 46.6 % | 62.7 % |
| PA/Pot_A_Piece_07 | 8598 | 85980 | 0.24 | 1.20 | 21.81 | 55.10 | 63.4 % | 72.4 % | 74.2 % | 78.0 % | 80.5 % | 84.3 % |

Arms B and D return bit-identical angle statistics for every piece, as they must: both run at
0.6 mm spacing, so the rung-2 cloud and its normals are the same cloud and only the clustering
differs (B `paper_chain` on, D off). Arm E is the native-resolution cloud and carries the largest
point counts. Full table incl. p25/p75/mean/max and every fraction threshold:
`results/angles.tsv` (npts and k on every row).

## Part D — one table per theta, both conditions stated

Juglet condition: ≥ 2 regions at or above 50 points **and** kgate ≥ 0.5. Pot A 07 condition:
≥ 8 regions at or above 50 points **and** its 3093- and 2850-point regions intact. Full grid in
`results/partD.tsv`; the ladder itself in `results/theta_ladder.tsv` (21 columns, 104 rows).

| theta | Juglet B (pass/4, min kgate) | Juglet D | Juglet E | Pot A regions | Pot A 3093/2850 | Pot A passes | both |
|---|---|---|---|---|---|---|---|
| 2.0 | 0/4, 0.000 | 0/4, 0.000 | 0/4, 0.000 | 6 | 3043 / 2761 — **broken** | no | no |
| 3.4 | 0/4, 0.000 | 0/4, 0.000 | 0/4, 0.000 | 8 | 3093 / 2850 — intact | **yes** | no |
| 4.0 | 0/4, 0.000 | 0/4, 0.000 | 0/4, 0.000 | 6 | 3106 / 2874 — intact | no | no |
| 5.0 | 0/4, 0.000 | 0/4, 0.000 | 0/4, 0.000 | 6 | 3130 / 2910 — intact | no | no |
| 6.0 | 1/4, 0.125 | 1/4, 0.125 | 0/4, 0.000 | 7 | 3144 / 2936 — intact | no | no |
| 8.0 | 2/4, 0.274 | 2/4, 0.274 | 2/4, 0.280 | 6 | 3168 / 2979 — intact | no | no |
| 10.0 | 2/4, 0.453 | 2/4, 0.453 | 4/4, 0.556 | 5 | 3281 / 3030 — intact | no | no |
| 12.0 | **4/4**, 0.502 | **4/4**, 0.502 | **4/4**, 0.770 | 3 | 4529 / 3103 — intact | no | no |

## Part C — the calibration gate (ran first; the run would have stopped here)

`MATCH`. The four arm-B Juglet clouds reproduce the pipeline's own rung-2 region sizes exactly
(piece 3: 169,99; piece 5: 679; piece 7: 326,263,77,68,65; piece 2: no region reaches 50 points in
either), and Pot A 07 at 8 regions with a worst per-region delta of 10 points (144 vs 134) — the
same 10-point delta stage 28 measured. Pot A's 3093 and 2850 are in the replica's own output.
Arms D and E are **NOT-GATED**, not failures: their rung-2 sidecars say `"paper_chain": false`, so
those clusters came from `pcl::RegionGrowing` (`mesh_processing_headless.cpp:3477-3487`), not from
`growPaper234` (`:2972-3030`, called at `:3470`). The replica's sizes are printed beside them as
evidence of the difference (e.g. E piece 7: 1701,453,147,… against the replica's 1162,114,66,55)
and never as a verdict. `results/calibration.tsv`.

## What this does and does not license

The replica reproduces **region growing only**. It knows nothing about the merge step, nothing
about the 3 mm reassignment, and nothing about the curvature-driven normal estimation that runs
before the growth. A theta that looks right here is a candidate for a pipeline run on the same
clouds, not a result — and on this evidence the candidate is not a single number: the two vessels
need theta ~12 and theta ~3.4 respectively. That points at theta as a per-cloud quantity (a
quantile of the cloud's own pair-angle distribution), which is the change to the growth rule this
ticket unblocks; it is not a case for raising the production default.

## Figure

`results/fig29_angles_vs_theta.png` — 18.0 x 11.0 in, 2880 x 1760 px at dpi 160, 0.15875 mm/px on
both axes; one panel per cloud (13 angle histograms, log y, 0.25 deg bins, 0–60 deg, dashed
shipped 3.4 / dotted paper 4.0) plus kgate-against-theta and regions-against-theta panels; one
figure legend, arm colours B `#1f77b4`, D `#2ca02c`, E `#d62728`, Pot A `#000000`; scale bars
10 deg, 0.25 kgate, 8 regions. Metadata beside it in `results/fig29_angles_vs_theta.txt`.

The job's own figure is `out/ticket29_angles_vs_theta.png` in the run directory. Its x axis ran to
83 deg (the Juglet's p99 is 82.8 deg) while its histogram bins end at 60 deg, and the panel
annotation then named 83 deg while measuring the share beyond 60 deg. The instrument now clamps
the axis to the histogram range and names the real bound; the committed figure is that corrected
render, redrawn by `fig29_replay.py` from the run's own `angles.tsv`, `angles_hist.json` and
`theta_ladder.tsv`. No measurement was repeated and no number changed.

## Record and limits of this delivery

- Run directory: `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-1637_7c3248f_t29-angle-survey`
  (`run.json`, `submit.sbatch`, `logs/`, `out/`, `instruments/`). Job 33865557, sacct `COMPLETED`,
  `ExitCode 0:0`, elapsed 00:00:18. One index row, verdict and human_note left empty for the
  coordinating session.
- **Two jobs, so two index rows for this ticket.** The first attempt, job 33864736 in
  `20261027-1628_d53028d_t29-angle-ladder`, died in 14 s with `replica29.py: error: unrecognized
  arguments: survey` — the batch script passed a subcommand the flat CLI does not take. That run
  measured nothing; its row stays because the index is append-only.
- Borrowed dumps untouched: 130 files (65 `.ply`), inventory and md5 identical before and after
  the run. No geometry was written by the job, so there was nothing to delete
  (`out/GEOMETRY_DELETED.txt`, 0 written / 0 deleted). The corpus listing is identical before and
  after (1803 rows) and `/opt/sfs-pristine` is ABSENT.
- No tracked source was modified. The whole change set is under `.scratch/juglet-breaklines/stage29/`.