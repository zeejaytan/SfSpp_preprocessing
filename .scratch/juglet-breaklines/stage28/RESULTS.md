# Ticket 28 — the region-growing replica, the calibration gate, and the grid

Instrument: `.scratch/juglet-breaklines/stage28/replica234.py` at commit `5227f8fc0300f21908eb6c1ac86ebab6c26e3356`
(branch `28-step-one-in-python`). Every number below came out of job 33861154 or job 33861235 on a
compute node (spartan-bm154, spartan-bm147); nothing here was computed on the login node or the laptop.

Run directories of record:

- `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-1537_5227f8f_t28-pota07-dump` (job 33861154,
  COMPLETED 0:0) — one Pot_A_Piece_07 pipeline run at today's defaults with SFS_DUMP_STAGE armed, then the
  calibration gate.
- `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-1539_5227f8f_t28-replica-grid` (job 33861235,
  COMPLETED 0:0) — the gate again, then the 36-cell grid. `out/cells/cells28.tsv` and one JSON per cell.

## 1. The calibration gate — pass

Input: the ticket-25 rung-2 dumps (arm B), which carry the cloud and the normals the growth saw.
theta 3.4, kappa 1.0, nb 10, floor 50, curvature recomputed as mesh_processing_headless.cpp:732 does
(k = max(10, min(50, npts/300))).

| piece | npts | curv_k | regions before floor | replica ≥50 | the dump's own clusters | |
|---|---|---|---|---|---|---|
| Juglet_Piece_2 | 1031 | 10 | 661 | [] | [] | match (no gate criterion) |
| Juglet_Piece_3 | 1467 | 10 | 825 | [169, 99] | [169, 99] | MATCH |
| Juglet_Piece_5 | 3021 | 10 | 1467 | [679] | [679] | MATCH |
| Juglet_Piece_7 | 4254 | 14 | 1951 | [326, 263, 77, 68, 65] | [326, 263, 77, 68, 65] | MATCH |

`[CAL] result=MATCH`, calibration exit 0, in both jobs (logs/calibration.log). The gate also checked that the
floor does not change the growth: `growth_floor_independent=True` on all four pieces.

## 2. Piece 2, arm B, theta 3.4 — the regions it grows and throws away

661 regions for 1031 points; the sizes sum to 1031 (every point is claimed, nothing is left over).

- `36, 15, 12, 12, 11, 9, 9, 8, 7, 7, 7, 6, 6, 6, 5, 5, 5, 5, 4×21, 3×33, 2×88, 1×501` (descending, with multiplicities)
- sizes ≥50: **none**. Largest region: **36 points**.
- The largest region was reached in **8 expansion steps** (max_depth 8; 36 pops off the front queue).
- Neighbour tests in that growth: 212 tests on 36 front points — 177 failed on the angle, **0 on the curvature**;
  36 were the point itself, 148 were already claimed.
- Over all 661 regions: **4703 failed on the angle, 0 on the curvature**. `curv_max` = 0.1784717 for the piece.

The curvature test cannot fail here: curvature is lambda0/(lambda0+lambda1+lambda2)
(pcl/features/impl/feature.hpp:61-88), so it is bounded by 1/3, and kappa is 1. `fail_curv` is 0 in all 36
cells of the grid, on every piece.

## 3. The grid, 36 cells on a compute node

B = today's defaults (0.6 mm), E = native density. The floor is applied to the finished regions only, so a
`floor=none` cell keeps every region listed under `regions_before`; the `floor=50` cell keeps exactly the
sizes ≥50 of the same run. `theta` in degrees, `nb` 10, `kappa` 1.0 everywhere.

| piece | cloud | theta | npts | curv_k | regions before floor | sizes ≥50 (floor 50 keeps these) | largest |
|---|---|---|---|---|---|---|---|
| Juglet_Piece_2 | B | 3.4 | 1031 | 10 | 661 | — | 36 |
| Juglet_Piece_2 | B | 4.0 | 1031 | 10 | 580 | — | 41 |
| Juglet_Piece_2 | E | 3.4 | 2565 | 10 | 1798 | — | 30 |
| Juglet_Piece_2 | E | 4.0 | 2565 | 10 | 1644 | — | 30 |
| Juglet_Piece_3 | B | 3.4 | 1467 | 10 | 825 | 169, 99 | 169 |
| Juglet_Piece_3 | B | 4.0 | 1467 | 10 | 767 | 175, 113 | 175 |
| Juglet_Piece_3 | E | 3.4 | 3486 | 11 | 2308 | 284 | 284 |
| Juglet_Piece_3 | E | 4.0 | 3486 | 11 | 2108 | 319 | 319 |
| Juglet_Piece_5 | B | 3.4 | 3021 | 10 | 1467 | 679 | 679 |
| Juglet_Piece_5 | B | 4.0 | 3021 | 10 | 1292 | 805 | 805 |
| Juglet_Piece_5 | E | 3.4 | 6208 | 20 | 3572 | 757, 52 | 757 |
| Juglet_Piece_5 | E | 4.0 | 6208 | 20 | 3118 | 870 | 870 |
| Juglet_Piece_7 | B | 3.4 | 4254 | 14 | 1951 | 326, 263, 77, 68, 65 | 326 |
| Juglet_Piece_7 | B | 4.0 | 4254 | 14 | 1656 | 473, 429, 226 | 473 |
| Juglet_Piece_7 | E | 3.4 | 8421 | 28 | 4054 | 1162, 114, 66, 55 | 1162 |
| Juglet_Piece_7 | E | 4.0 | 8421 | 28 | 3430 | 1601, 143, 62, 56 | 1601 |
| Pot_A_Piece_07 | PA | 3.4 | 8598 | 28 | 1276 | 3093, 2850, 203, 170, 134, 120, 73, 71 | 3093 |
| Pot_A_Piece_07 | PA | 4.0 | 8598 | 28 | 1151 | 3106, 2874, 272, 222, 208, 145 | 3106 |

Counts at floor 50: piece 2 — 0 at every theta and cloud; piece 3 — 2/2 on B, 1/1 on E; piece 5 — 1/1 on B,
2 on E at 3.4 and 1 at 4.0; piece 7 — 5 on B at 3.4, 3 on B at 4.0, 4 and 4 on E; Pot A — 8 at 3.4, 6 at 4.0.

Largest region and its expansion depth per cell (the second number is the depth):

- piece 2: B 3.4 → 36 / 8, B 4.0 → 41 / 9, E 3.4 → 30 / 5, E 4.0 → 30 / 5
- piece 3: B 3.4 → 169 / 16, B 4.0 → 175 / 15, E 3.4 → 284 / 36, E 4.0 → 319 / 37
- piece 5: B 3.4 → 679 / 56, B 4.0 → 805 / 49, E 3.4 → 757 / 44, E 4.0 → 870 / 39
- piece 7: B 3.4 → 326 / 24, B 4.0 → 473 / 34, E 3.4 → 1162 / 60, E 4.0 → 1601 / 53
- Pot A 07: 3.4 → 3093 / 37, 4.0 → 3106 / 37

Angle-versus-curvature failures, totals over the whole growth: piece 2 B 4703/0 and 4510/0 (theta 3.4 / 4.0),
piece 2 E 12745/0 and 12453/0, piece 3 B 6189/0 and 5965/0, piece 5 B 11969/0 and 11277/0,
piece 7 B 16823/0 and 15556/0, Pot A 11508/0 and 10859/0.

## 4. Pot A 07, the control — one pipeline run, then the same replica

`SFS_DUMP_STAGE` armed for Pot_A_Piece_07 only, today's defaults, one pipeline run (pipeline exit 0,
retry 1, 8598 points, spacing 0.6 mm). Kept: `out/dump/Pot_A_Piece_07/r1..r5` (5 ply, 5 json, 2,738,106 B).
`r1_downsampled.ply` 8598 points, md5 `ff5760cb88140e4f3cfa8f56082ad6a0`; `r2_clusters_premerge.ply`
md5 `d82d0bc94c8388ffed9d498d6869c5f5`. Geometry deleted after the run: 19 files, 36,445,005 bytes
(`out/GEOMETRY_DELETED.txt`); no stage tree left on disk.

The pipeline's own rung-2 sidecar for that run: `[3093, 2850, 203, 170, 144, 120, 73, 71]`, 6724 points
claimed, 8 regions ≥50. The replica on the same cloud and normals at theta 3.4 returns
`[3093, 2850, 203, 170, 134, 120, 73, 71]` — **seven of eight regions identical, one differs (144 vs 134,
10 points)**. At theta 4.0 the replica returns `[3106, 2874, 272, 222, 208, 145]` and the pipeline's own
clusters at that theta are not available (the sidecar records only the run's own theta).

## 5. Two facts about the inputs that the columns rest on

- **The E column is not growPaper234's output as the pipeline ran it.** `SFS_PAPER_CHAIN=0` selects a
  different segmentation: mesh_processing_headless.cpp:3436 `if (paperChain) { ... growPaper234 ... }`,
  :3444-3455 the `else` branch runs `pcl::RegionGrowing` with `dynK`, `smoothnessAngleThreshold` and
  `curvatureThreshold`. The E rung-2 sidecars say `"paper_chain": false`, so their `clusters` values
  ([94, 80, 61] for piece 2, [487] piece 3, [1000, 60, 58] piece 5, [1701, 453, 147, 108, 100, 64, 63, 63,
  53, 50] piece 7) come from PCL's region growing, not from the function this ticket replicates. The E cells
  above are the replica's growPaper234 run **on the native cloud and its normals**; they cannot be checked
  against those numbers.
- The replica recomputes curvature in float64 from the float32 coordinates; PCL computed it in float32. The
  gate on arm B matched on all four pieces, so this did not change the B seeds' order; the Pot A 144/134
  difference is the one place the two disagree and the cause is not established.

## 6. Paper lines relied on

- `C:/PR/papers/text/sfspp-2502.13986v1.md:151`: "This algorithm starts from the point with the minimum
  curvature and expands by combining the $n_{b}=10$ neighboring points that have a curvature value of less
  than $\tau_{\kappa}$ and a normal angle less than $\tau_{\theta}$ with the point's normal. We set the values
  of $\tau_{\theta}$=4 and $\tau_{\kappa}$=1 to achieve clear separation of interior, exterior, and fractured
  surfaces."
- `C:/PR/papers/text/sfspp-2502.13986v1.md:155`: "Finally, we select the two largest clusters, representing
  the inner and outer surfaces."

## 7. Record

- corpus `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp`: 1803 rows hashed before and after
  each job, `corpus.diff` 0 bytes in both run directories. `/opt/sfs-pristine`: **ABSENT** (recorded, not created).
- `index.tsv`: two rows appended, one per job, each read back as 6 fields with `verdict` and `human_note` empty.
- The ticket-25 rung-1 dumps this ticket reads were not touched: the job-2 inventory lists the same md5s
  (B p2 r2 `08dd10308416a90c40b9b87240b9513a`, B p3 `e8c0c11de6b5334cce6f4954435a5cb7`, B p5
  `9f770674625cc38be17ce717a50ce063`, B p7 `baa58514f37f3fc5250b1fa322b609a8`, E p2
  `58e1ebfcb4f45afa85677908e82915be`, E p3 `9c4d82c5e613f74ada07d030bed8f9c9`, E p5
  `ed473dc4b09d4d6afc4dc6c04ae036ed`, E p7 `30bd5b4a7ae4245844e6b2bc7427c528`).
