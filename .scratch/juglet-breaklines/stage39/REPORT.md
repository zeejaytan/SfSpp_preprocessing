# Ticket 39 — does `SFS_REASSIGN_MODE=own` keep the two faces apart?

Numbers only, from the run; no verdict on what they mean (the ticket's Status and `intent/` are untouched).

One run of record, one job, kept in full:

- **run 1** `/data/gpfs/projects/punim2657/SfSpp/runs/20261028-1624_ed0fc16_t39-ownmode/` (job **33926931**,
  commit `ed0fc16328efdb13991e2d9dba843fe7bddb174e`, `spartan-bm073.hpc.unimelb.edu.au`, `COMPLETED`
  00:01:47, ExitCode 0:0): every section below. Its record minus `build/`, minus the staged
  `instruments/` copy and minus the 1.5 MB built binary `out/bin-new` **is** `stage39/results/`: 89 of the
  90 files the run wrote outside `instruments/`, md5-compared one for one against the cluster copy, 89 of 89
  identical. `results/PROVENANCE.txt` maps every file back to its path in the run directory and records the
  binary's md5. There is no separate `run-<runid>/` directory
  beside it — stage 38 needed one because its `results/` drew on three runs, whereas here one run supplied
  everything and a second copy would be the same bytes twice.

Job budget: **1 of the 2** the ticket allows was used. No cell failed, so there was nothing to re-run.

The bar the lead reads against, restated from the ticket so the numbers below can be set beside it and not
judged here: shared points well under 10 %, mean-normal dot below -0.9, `med_along` about one wall thickness
(Juglet 2 **2.693 mm**, Juglet 9 **2.595 mm**, ticket 35's ray measurements), `med_across` small.

## 1. The cloud check — the same two clouds ticket 38 drew

Pass 1 of `run_cell39.sh` samples one cloud per piece and gates it against ticket 38's own numbers **before
any cell runs**. Both gates passed, and the gate is a hard stop: on a mismatch the driver prints
`STOP: the sampler did not reproduce ticket 38's clouds` and exits 9 without running a cell.

| piece | expected points (ticket 38) | regenerated points | expected median mm | regenerated median mm | count | spacing | gate |
|---|---|---|---|---|---|---|---|
| Juglet_Piece_2 | 6 259 | **6 259** | 0.209043 | **0.20904330739003849** | ok | ok | ok |
| Juglet_Piece_9 | 5 257 | **5 257** | 0.201511 | **0.201511365190472** | ok | ok | ok |

`out/cells-pipeline/cloud_gate.tsv` (`piece pot level expected_points actual_points expected_mm actual_mm
count_ok spacing_ok gate cloud cloud_md5`), rows verbatim except that the run-directory prefix of the cloud
path is abbreviated to `.../out/geometry/`:

```
Juglet_Piece_2	Juglet	1	6259	6259	0.209043	0.20904330739003849	yes	yes	ok	.../out/geometry/Juglet_Piece_2_synthetic_x1_spacing_0.21089557.pcd	c6cd2eab8a1df10b6e97951cc360d3af
Juglet_Piece_9	Juglet	1	5257	5257	0.201511	0.201511365190472	yes	yes	ok	.../out/geometry/Juglet_Piece_9_synthetic_x1_spacing_0.20341531.pcd	77e0f59d80bef8df1f92049622f97f59
```

`out/phase1.log`:

```
[CELL39] cloud gate Juglet_Piece_2: points 6259 (ticket 38: 6259) median 0.20904330739003849 mm (ticket 38: 0.209043) -> ok
[CELL39] cloud gate Juglet_Piece_9: points 5257 (ticket 38: 5257) median 0.201511365190472 mm (ticket 38: 0.201511) -> ok
[CELL39] both clouds reproduce ticket 38 exactly; the cells may run
[CELL39] wall clock left: 1487s
```

**Stronger than the check the ticket asked for:** the two clouds are byte-identical to ticket 38's, not merely
equal in count and spacing. Inside one piece the two arms' `inputs.md5` are byte-identical (cmp clean, no path
normalisation), and against ticket 38 the row that names the cloud matches after normalising the run-id path
(same md5s `c6cd2eab…` / `77e0f59d…`, same 6 259 / 5 257 points). `out/measure/sampler_validate_<piece>.json`
and `out/measure/sample_<piece>_x1.json` are byte-identical (cmp) to run `20261028-0528_511461e_t38-surfaces`.
Ticket 38's own `out/geometry` no longer exists, so that comparison is against its recorded md5 rows, not
re-hashed bytes.

Sampler proof, unchanged from ticket 38 (route 1 does not reproduce the shipped cloud, route 2 does, and the
job prints which one the clouds are gated on):

```
[VALIDATE] gate_route=instrument-validated-disclosed literal=FAIL route2=PASS
[VALIDATE] WARNING route 1 did not reproduce the shipped cloud; route 2 is what the synthetic clouds are gated on, and the disclosure file records both
```

| piece | shipped points | shipped median mm | sampled points | sampled median mm | count ratio | spacing ratio | voxel mm | gen points | area mm2 | triangles |
|---|---|---|---|---|---|---|---|---|---|---|
| Juglet_Piece_2 | 2 565 | 0.21089556657264594 | 6 259 | 0.2090148498171457 | 2.4401559454191033 | 0.9910822366441145 | 0.32133535403795244 | 245 587 | 491.0673765741189 | 5 126 |
| Juglet_Piece_9 | 2 094 | 0.2034153094689202 | 5 257 | 0.201511365190472 | 2.5105062082139447 | 0.9906401131585472 | 0.31128643174440906 | 163 253 | 373.7573691429208 | 4 184 |

## 2. The arm-A control against ticket 38, per piece

Arm A is `SFS_REASSIGN_MODE=radius`, the shipped default; the job unsets `SFS_REASSIGN_MODE` in its own
environment and sets it per invocation, so arm A is genuinely the default and not an inherited value. Both
cells reproduced ticket 38's two per-surface counts **exactly**, so neither cell is void and the comparison the
ticket asks for can be made.

| piece | arm | mode | clusters | spacing policy | outcome | Surface_0 | Surface_1 | ticket 38 S0/S1 | reproduced |
|---|---|---|---|---|---|---|---|---|---|
| Juglet_Piece_2 | A | radius | 8 | piece | two | **4 155** | **3 979** | 4 155 / 3 979 | **yes** |
| Juglet_Piece_2 | B | own | 8 | piece | two | 4 155 | 3 762 | — | — |
| Juglet_Piece_9 | A | radius | 7 | piece | two | **2 229** | **3 512** | 2 229 / 3 512 | **yes** |
| Juglet_Piece_9 | B | own | 7 | piece | two | 2 087 | 3 510 | — | — |

`out/phase1.log`:

```
[CELL39] control Juglet_Piece_2 reproduces ticket 38 exactly: 4155 / 3979
[CELL39] control Juglet_Piece_9 reproduces ticket 38 exactly: 2229 / 3512
```

Beyond the counts, stage 39's arm-A `mesh.log` is **identical** to ticket 38 run 6's `mesh.log` for the same
piece after masking the cell path and dropping the `Sampled indices` and two timing lines: **0 differing
lines** on both pieces (`diff` against
`/data/gpfs/projects/punim2657/SfSpp/runs/20261028-0528_511461e_t38-surfaces/out/cells-pipeline/<piece>_x1/logs/mesh.log`).

Everything except the admission rule was held fixed, from `out/phase1.log` (one line per cell; only the last
token differs):

```
[CELL39] env: SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0 SFS_DOWNSAMPLE_TARGET=6259 SFS_REASSIGN_MODE=radius
[CELL39] env: SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0 SFS_DOWNSAMPLE_TARGET=6259 SFS_REASSIGN_MODE=own
[CELL39] env: SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0 SFS_DOWNSAMPLE_TARGET=5257 SFS_REASSIGN_MODE=radius
[CELL39] env: SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0 SFS_DOWNSAMPLE_TARGET=5257 SFS_REASSIGN_MODE=own
```

One binary for all four cells: `out/bin-new`, md5 `180e68467eac391279675fdc3ffedfe1`, 1 582 080 bytes.
Spacing policy is unset in every cell, which is the shipped `piece` policy (the pipeline's own
`[SPACING-22] policy=piece` line says so); no dedupe switch, no single-cluster write, no window override.

## 3. The per-surface table, both arms, both pieces

`out/cells-pipeline/surfaces.tsv` (`piece arm surface points distinct ext_x ext_y ext_z diag cov_2mm fold_deg
normal_src ply_bytes`), all eight rows verbatim:

```
Juglet_Piece_2	A	0	4155	2471	7.022998000000001	24.7381	9.660949999999957	27.470530526739072	0.7680311890838206	3.104152556785976	ply	319604
Juglet_Piece_2	A	1	3979	3979	8.167999000000002	24.7381	9.53496999999993	27.74176368176507	1.0	3.013485934784664	ply	315847
Juglet_Piece_2	B	0	4155	2471	7.022998000000001	24.7381	9.660949999999957	27.470530526739072	0.7680311890838206	3.104152556785976	ply	323511
Juglet_Piece_2	B	1	3762	2142	6.161200999999998	22.20069	9.220950000000016	24.816465363564596	0.791812865497076	2.901643836867422	ply	300439
Juglet_Piece_9	A	0	2229	2229	5.927202999999999	8.74016	16.418030000000044	19.521112706751897	0.8137535816618912	2.9662320393249444	ply	173888
Juglet_Piece_9	A	1	3512	2015	6.782699000000001	13.0204401	16.418030000000044	22.024726450133052	0.7325692454632283	2.8033206206864536	ply	274977
Juglet_Piece_9	B	0	2087	1498	5.385601000000001	9.7238303	14.967039999999997	18.64322558453872	0.6829035339063992	3.3204094596622915	ply	163395
Juglet_Piece_9	B	1	3510	2013	6.6240999999999985	13.0204401	16.418030000000044	21.976402578415545	0.73018147086915	2.802466685118388	ply	274522
```

Tab-separated, in the file's own order; the column names are the backticked list above, which is the
file's header line.

`distinct` is the number of distinct positions at 1e-4 mm; `cov_2mm` is the fraction of the ORIGINAL piece
cloud within 2 mm of that surface; `fold_deg` is the median folded angle to the ORIGINAL mesh.

Two rows are worth their own line because they are equalities and inequalities rather than trends:

- **Piece 2 arm B Surface_0 is bit-identical to arm A Surface_0** — every column equal, and the two per-surface
  jsons are identical after masking the arm name (`cmp` clean). Own mode did not move surface 0 on that piece.
- Piece 2 arm B Surface_1 shrank 3 979 → 3 762 points, diag 27.7418 → 24.8165 mm, and its `cov_2mm` fell
  1.0 → 0.7918. Piece 9 arm B Surface_0 shrank 2 229 → 2 087 (diag 19.5211 → 18.6432, cov 0.8138 → 0.6829)
  and Surface_1 went 3 512 → 3 510.

The driver's own rounded lines, `out/phase1.log`:

```
[SURFACE] Juglet_Piece_2_x1_armA_Surface_0 points=4155 diag=27.471 mm cov2mm=0.7680 fold=3.104 deg (normals ply)
[SURFACE] Juglet_Piece_2_x1_armA_Surface_1 points=3979 diag=27.742 mm cov2mm=1.0000 fold=3.013 deg (normals ply)
[SURFACE] Juglet_Piece_2_x1_armB_Surface_0 points=4155 diag=27.471 mm cov2mm=0.7680 fold=3.104 deg (normals ply)
[SURFACE] Juglet_Piece_2_x1_armB_Surface_1 points=3762 diag=24.816 mm cov2mm=0.7918 fold=2.902 deg (normals ply)
[SURFACE] Juglet_Piece_9_x1_armA_Surface_0 points=2229 diag=19.521 mm cov2mm=0.8138 fold=2.966 deg (normals ply)
[SURFACE] Juglet_Piece_9_x1_armA_Surface_1 points=3512 diag=22.025 mm cov2mm=0.7326 fold=2.803 deg (normals ply)
[SURFACE] Juglet_Piece_9_x1_armB_Surface_0 points=2087 diag=18.643 mm cov2mm=0.6829 fold=3.320 deg (normals ply)
[SURFACE] Juglet_Piece_9_x1_armB_Surface_1 points=3510 diag=21.976 mm cov2mm=0.7302 fold=2.802 deg (normals ply)
```

## 4. The pair statistic between the two written surfaces, with the signed `t`

`out/cells-pipeline/surface_pairs.tsv` (`piece arm n0 n1 med_nn med_along med_across med_angle_deg coin
med_t_signed p05_t_signed p95_t_signed normal_src_a normal_src_b`):

| piece | arm | n0 | n1 | med_nn | med_along | med_across | med_angle_deg | coin | med_t_signed | p05 t | p95 t |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Juglet_Piece_2 | A | 4 155 | 3 979 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5911032922844935 | 0.0 | -2.5417101869858705 | 0.0 |
| Juglet_Piece_2 | B | 4 155 | 3 762 | 2.2847357995719397 | **2.2540777851087657** | 0.15926958694537513 | 12.977144972134433 | 0.0 | **-2.2540777851087657** | -2.654118883696664 | -1.5862942210477828 |
| Juglet_Piece_9 | A | 2 229 | 3 512 | 0.0 | 0.0 | 0.0 | 0.0 | 0.8246013667425968 | 0.0 | -0.004322898100523831 | 0.03986170855198336 |
| Juglet_Piece_9 | B | 2 087 | 3 510 | 2.175759811718171 | **2.134489859141274** | 0.1877338703672796 | 13.927093172798616 | 0.0 | **-2.134489859141274** | -2.4260113140511037 | -1.6615995307254277 |

Arm A's `med_nn` / `med_along` / `med_across` / `med_angle_deg` are **exactly 0.0** because every Surface_1
point coincides with a Surface_0 point; `coin` is the fraction of Surface_1 points within 1e-3 mm of a
Surface_0 point (`measure34.py:23`). `t` is signed along Surface_0's normal, so a negative median is Surface_1
lying on the far side of Surface_0 from Surface_0's own normal.

Percentiles and the p90s, from each cell's `measure/surfacepair_<tag>.json` (the json carries more than the
tsv columns):

| piece | arm | p90_along | p90_across | p90_angle_deg | min_nn_minus_across |
|---|---|---|---|---|---|
| Juglet_Piece_2 | A | 2.4057114458666655 | 0.2660179329914922 | 18.2869444256792 | 0.0 |
| Juglet_Piece_2 | B | 2.5742658135240464 | 1.0019243168630458 | 50.7148642673156 | 0.2253030507802627 |
| Juglet_Piece_9 | A | 0.012113363315752636 | 0.7545153882755931 | 3.964590847072483 | 0.0 |
| Juglet_Piece_9 | B | 2.3673458076645217 | 1.077030458638634 | 29.70379510670713 | 0.259182374853975 |

## 5. The three derived quantities

`out/cells-pipeline/nest.tsv` (`piece arm n0 n0_distinct n1 n1_distinct shared shared_over_a shared_over_b
shared_over_smaller mean_normal_dot matched median_point_normal_angle_deg normal_src_a normal_src_b`):

| piece | arm | n0 | n0 distinct | n1 | n1 distinct | **shared** | of_a | of_b | **of smaller** | **mean-normal dot** | matched | median point-normal angle |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Juglet_Piece_2 | A | 4 155 | 2 471 | 3 979 | 3 979 | 2 352 | 0.9518413597733711 | 0.5911032922844935 | **0.9518413597733711** | **+0.9960274472338446** | 2 352 | 0.0 deg |
| Juglet_Piece_2 | B | 4 155 | 2 471 | 3 762 | 2 142 | **0** | 0.0 | 0.0 | **0.0** | **-0.9993570511406065** | 0 | na |
| Juglet_Piece_9 | A | 2 229 | 2 229 | 3 512 | 2 015 | 1 616 | 0.7249887842081651 | 0.8019851116625311 | **0.8019851116625311** | **+0.9993183797978673** | 1 616 | 0.0 deg |
| Juglet_Piece_9 | B | 2 087 | 1 498 | 3 510 | 2 013 | **0** | 0.0 | 0.0 | **0.0** | **-0.9999474210970047** | 0 | na |

- **Shared points, both ways, and of the smaller** are the `shared`, `shared_over_a`, `shared_over_b`,
  `shared_over_smaller` columns. A position is shared when the two surfaces' coordinates agree after rounding
  to **1e-4 mm** — the same rounding stage 38's `check38.py:38` used, so these fractions are comparable with
  ticket 38's 2 471 / 3 979 (piece 2) and 1 616 / 2 015 (piece 9). Arm A reproduces them: 0.9518 and 0.8020.
  Arm B: **shared = 0 on both pieces**, so all four fractions are 0.0.
- **Mean-normal dot** is the dot product of each surface's normalised mean normal. Arm A **+0.9960274472338446**
  / **+0.9993183797978673** (ticket 38: +0.9960 / +0.9993); arm B **-0.9993570511406065** /
  **-0.9999474210970047**.
- **Median per-point folded angle between the two surfaces' normals at matching points** is **0.0 deg** in
  arm A, taken over 2 352 (piece 2) / 1 616 (piece 9) matched positions. In arm B it is null and printed `na`,
  because `matched = 0`: there are no shared positions to take an angle at.

The driver's own lines, `out/phase1.log`:

```
[NEST] Juglet_Piece_2_x1_armA n0=4155 (distinct 2471) n1=3979 (distinct 3979) shared=2352 of_a=0.9518 of_b=0.5911 of_smaller=0.9518 meandot=+0.9960 ang=0.000 deg (normals a:ply b:ply)
[NEST] Juglet_Piece_2_x1_armB n0=4155 (distinct 2471) n1=3762 (distinct 2142) shared=0 of_a=0.0000 of_b=0.0000 of_smaller=0.0000 meandot=-0.9994 ang=na deg (normals a:ply b:ply)
[NEST] Juglet_Piece_9_x1_armA n0=2229 (distinct 2229) n1=3512 (distinct 2015) shared=1616 of_a=0.7250 of_b=0.8020 of_smaller=0.8020 meandot=+0.9993 ang=0.000 deg (normals a:ply b:ply)
[NEST] Juglet_Piece_9_x1_armB n0=2087 (distinct 1498) n1=3510 (distinct 2013) shared=0 of_a=0.0000 of_b=0.0000 of_smaller=0.0000 meandot=-0.9999 ang=na deg (normals a:ply b:ply)
```

`nest39.py` definitions (`stage39/instruments/nest39.py`): `ROUND=4` → `tuple(np.round(row, 4))`;
`distinct_index` (lines 56-62) keeps the first occurrence per rounded key; `mean_normal` (65-68) is the
normalised **mean** of all per-point normals; `mean_normal_dot` (85) is `mean_normal(nrm0) @ mean_normal(nrm1)`;
`median_point_normal_angle_deg` (87-90) is `np.median(M.folded_angle_deg(nrm0[a], nrm1[b]))` over the shared
positions only. `measure34.folded_angle_deg` (`measure34.py:262-264`) takes `np.abs` of the dot, so the folded
angle is **sign-blind by construction** — which is why `mean_normal_dot` is reported beside it, not instead of
it.

`nest39.py selftest` passes 3/3 on the cluster: `sheet 2 mm away: shared=0 meandot=+1.0000 distinct=25`;
`same sheet, normals flipped: shared=25 meandot=-1.0000 ang=0.0 deg (folded angle is sign-blind by definition,
meandot carries it)`; `same sheet 3e-5 mm away: shared=25 of_smaller=1.0000`. The job does **not** run the
selftest (see section 8).

## 6. The `[REASSIGN-22]` and `[WINDOW-26*]` lines, verbatim, per cell

Each cell's `logs/admission39.log` holds exactly eight lines: 1 × `[WINDOW-26-SWITCH]`, 1 × `[REASSIGN-22]`,
and per surface `[WINDOW-26]` + `[WINDOW-26-MEASURE]` + `[WINDOW-26-FINAL]`. The **order differs between the
modes** and the blocks below are in each file's own order: radius mode fits and finalises one surface at a time
(`mesh_processing_headless.cpp:2335` prints, 2351 finalises, per call), so its lines run surface 0 → surface 1;
own mode fits both surfaces, prints both, then finalises both (2478-2479 then 2481-2485), so both
`[WINDOW-26-FINAL]` lines come last. No ANSI escapes in these files, unlike `mesh.log`, which carries 39
ESC-bearing lines.

### Juglet_Piece_2_x1_armA (`SFS_REASSIGN_MODE=radius`)

```
[WINDOW-26-SWITCH] mode=literal k=5 clampMM=0.5,6 report=none
[REASSIGN-22] mode=radius
[WINDOW-26] piece=Juglet_Piece_2 surface=0 mode=literal k=5.0000 residual_mm=0.014188 other_mm=0.016868 raw_mm=3.000000 clamped_mm=3.000000 admitted_own=2003 admitted_other=2471
[WINDOW-26-MEASURE] piece=Juglet_Piece_2 surface=0 rule=literal reason=ok clamp_lo_mm=0.5000 clamp_hi_mm=6.0000 clamped=no clamped_from_mm=3.000000 residual_n=1684 other_n=1734 other_grid_mm=0.161515 other_proj_mm=0.016868 own_cluster_points=1684 other_cluster_points=1734 candidates=6259
[WINDOW-26-FINAL] piece=Juglet_Piece_2 surface=0 admitted_own=2003 admitted_other=2471 other_copied_over=yes final_points=4155
[WINDOW-26] piece=Juglet_Piece_2 surface=1 mode=literal k=5.0000 residual_mm=0.012174 other_mm=0.339594 raw_mm=3.000000 clamped_mm=3.000000 admitted_own=2359 admitted_other=2146
[WINDOW-26-MEASURE] piece=Juglet_Piece_2 surface=1 rule=literal reason=ok clamp_lo_mm=0.5000 clamp_hi_mm=6.0000 clamped=no clamped_from_mm=3.000000 residual_n=1620 other_n=1798 other_grid_mm=0.442792 other_proj_mm=0.339594 own_cluster_points=1620 other_cluster_points=1798 candidates=6259
[WINDOW-26-FINAL] piece=Juglet_Piece_2 surface=1 admitted_own=2359 admitted_other=2146 other_copied_over=no final_points=3979
```

### Juglet_Piece_2_x1_armB (`SFS_REASSIGN_MODE=own`)

```
[WINDOW-26-SWITCH] mode=literal k=5 clampMM=0.5,6 report=none
[REASSIGN-22] mode=own
[WINDOW-26] piece=Juglet_Piece_2 surface=0 mode=literal k=5.0000 residual_mm=0.014188 other_mm=0.016868 raw_mm=3.000000 clamped_mm=3.000000 admitted_own=0 admitted_other=2471
[WINDOW-26-MEASURE] piece=Juglet_Piece_2 surface=0 rule=literal reason=ok clamp_lo_mm=0.5000 clamp_hi_mm=6.0000 clamped=no clamped_from_mm=3.000000 residual_n=1684 other_n=1734 other_grid_mm=0.161515 other_proj_mm=0.016868 own_cluster_points=1684 other_cluster_points=1734 candidates=6259
[WINDOW-26] piece=Juglet_Piece_2 surface=1 mode=literal k=5.0000 residual_mm=0.012174 other_mm=0.339594 raw_mm=3.000000 clamped_mm=3.000000 admitted_own=0 admitted_other=2142
[WINDOW-26-MEASURE] piece=Juglet_Piece_2 surface=1 rule=literal reason=ok clamp_lo_mm=0.5000 clamp_hi_mm=6.0000 clamped=no clamped_from_mm=3.000000 residual_n=1620 other_n=1798 other_grid_mm=0.442792 other_proj_mm=0.339594 own_cluster_points=1620 other_cluster_points=1798 candidates=6259
[WINDOW-26-FINAL] piece=Juglet_Piece_2 surface=0 admitted_own=0 admitted_other=2471 other_copied_over=yes final_points=4155
[WINDOW-26-FINAL] piece=Juglet_Piece_2 surface=1 admitted_own=0 admitted_other=2142 other_copied_over=yes final_points=3762
```

The `[WINDOW-26]` and `[WINDOW-26-MEASURE]` lines of arm B are **identical** to arm A's on this piece except for
`admitted_own` and `admitted_other` — same `residual_mm`, same `other_mm`, same clamp, same `residual_n`, same
`other_n`, same `candidates`. In own mode **no point at all was admitted to Surface_0** on this piece
(`admitted_own=0`), and `admitted_other` fell 2 146 → 2 142 on surface 1.

### Juglet_Piece_9_x1_armA (`SFS_REASSIGN_MODE=radius`)

```
[WINDOW-26-SWITCH] mode=literal k=5 clampMM=0.5,6 report=none
[REASSIGN-22] mode=radius
[WINDOW-26] piece=Juglet_Piece_9 surface=0 mode=literal k=5.0000 residual_mm=0.007744 other_mm=0.056367 raw_mm=3.000000 clamped_mm=3.000000 admitted_own=1610 admitted_other=1640
[WINDOW-26-MEASURE] piece=Juglet_Piece_9 surface=0 rule=literal reason=ok clamp_lo_mm=0.5000 clamp_hi_mm=6.0000 clamped=no clamped_from_mm=3.000000 residual_n=589 other_n=2237 other_grid_mm=0.084629 other_proj_mm=0.056367 own_cluster_points=589 other_cluster_points=2237 candidates=5256
[WINDOW-26-FINAL] piece=Juglet_Piece_9 surface=0 admitted_own=1610 admitted_other=1640 other_copied_over=yes final_points=2229
[WINDOW-26] piece=Juglet_Piece_9 surface=1 mode=literal k=5.0000 residual_mm=0.007436 other_mm=0.245060 raw_mm=3.000000 clamped_mm=3.000000 admitted_own=1755 admitted_other=2015
[WINDOW-26-MEASURE] piece=Juglet_Piece_9 surface=1 rule=literal reason=ok clamp_lo_mm=0.5000 clamp_hi_mm=6.0000 clamped=no clamped_from_mm=3.000000 residual_n=1497 other_n=1329 other_grid_mm=0.394550 other_proj_mm=0.245060 own_cluster_points=1497 other_cluster_points=1329 candidates=5256
[WINDOW-26-FINAL] piece=Juglet_Piece_9 surface=1 admitted_own=1755 admitted_other=2015 other_copied_over=yes final_points=3512
```

### Juglet_Piece_9_x1_armB (`SFS_REASSIGN_MODE=own`)

```
[WINDOW-26-SWITCH] mode=literal k=5 clampMM=0.5,6 report=none
[REASSIGN-22] mode=own
[WINDOW-26] piece=Juglet_Piece_9 surface=0 mode=literal k=5.0000 residual_mm=0.007744 other_mm=0.056367 raw_mm=3.000000 clamped_mm=3.000000 admitted_own=1498 admitted_other=2
[WINDOW-26-MEASURE] piece=Juglet_Piece_9 surface=0 rule=literal reason=ok clamp_lo_mm=0.5000 clamp_hi_mm=6.0000 clamped=no clamped_from_mm=3.000000 residual_n=589 other_n=2237 other_grid_mm=0.084629 other_proj_mm=0.056367 own_cluster_points=589 other_cluster_points=2237 candidates=5256
[WINDOW-26] piece=Juglet_Piece_9 surface=1 mode=literal k=5.0000 residual_mm=0.007436 other_mm=0.245060 raw_mm=3.000000 clamped_mm=3.000000 admitted_own=262 admitted_other=2013
[WINDOW-26-MEASURE] piece=Juglet_Piece_9 surface=1 rule=literal reason=ok clamp_lo_mm=0.5000 clamp_hi_mm=6.0000 clamped=no clamped_from_mm=3.000000 residual_n=1497 other_n=1329 other_grid_mm=0.394550 other_proj_mm=0.245060 own_cluster_points=1497 other_cluster_points=1329 candidates=5256
[WINDOW-26-FINAL] piece=Juglet_Piece_9 surface=0 admitted_own=1498 admitted_other=2 other_copied_over=no final_points=2087
[WINDOW-26-FINAL] piece=Juglet_Piece_9 surface=1 admitted_own=262 admitted_other=2013 other_copied_over=yes final_points=3510
```

On this piece own mode moved the split rather than emptying it: surface 0 went `admitted_other` 1 640 → **2** and
surface 1 went `admitted_own` 1 755 → **262**, with the measured window, residual and candidate counts
unchanged from arm A.

Two facts about the lines themselves, so they are not read as more than they say:

- `[WINDOW-26-SWITCH] mode=literal` reports `g_windowMode` — the **window scheme**
  (literal/residual/other/both, `SFS_WINDOW_MODE` at `mesh_processing_headless.cpp:4424`, default `literal`
  at 1254, printed at 4445-4447). It is not the reassign mode. The reassign switch appears only in
  `[REASSIGN-22]`.
- `other_copied_over` is `(otherBefore > ownBefore) ? "yes" : "no"` — a count comparison, not a copy flag.

The pipeline's other lines for the same cells, quoted from each cell's `logs/mesh.log` (ESC-prefixed there;
`logs/lines39.log` is the driver's own grep of them and carries the `[SPACING-22]`, `[DOWNSAMPLING RESULT]` and
`[PAPER-234]` lines but not the `[DEDUPE-27]` ones, which are read from `mesh.log` directly):

```
[SPACING-22] policy=piece diagMM=28.2305 s0MM=0.209045 samples=200 rawMM=0.141153 S=0.209045          (piece 2, both arms)
[SPACING-22] policy=piece diagMM=23.3454 s0MM=0.201486 samples=200 rawMM=0.116727 S=0.201486          (piece 9, both arms)
[DOWNSAMPLING RESULT] Target=6259 points, Bounds=[5007-7510], Result=6259 points, Radius(leaf)=0.04235   (piece 2, both arms)
[DOWNSAMPLING RESULT] Target=5257 points, Bounds=[4205-6308], Result=5256 points, Radius(leaf)=0.03502   (piece 9, both arms)
[PAPER-234] classify: face0 n=1684 interior_frac=0.5238 face1 n=1620 interior_frac=0.0000 satA=2502.0000 satB=802.0000   (piece 2, both arms)
[PAPER-234] classify: kept -> Surface_0=interior                                                      (piece 2, both arms)
[PAPER-234] classify: face0 n=1497 interior_frac=0.2953 face1 n=589 interior_frac=0.0000 satA=1031.0000 satB=1055.0000    (piece 9, both arms)
[PAPER-234] classify: swapped -> Surface_0=interior                                                   (piece 9, both arms)
[DEDUPE-27] surface=0 mode=off in=4155 out=2471     (piece 2 arm A)
[DEDUPE-27] surface=1 mode=off in=3979 out=3979     (piece 2 arm A)
[DEDUPE-27] surface=0 mode=off in=4155 out=2471     (piece 2 arm B)
[DEDUPE-27] surface=1 mode=off in=3762 out=2142     (piece 2 arm B)
[DEDUPE-27] surface=0 mode=off in=2229 out=2229     (piece 9 arm A)
[DEDUPE-27] surface=1 mode=off in=3512 out=2015     (piece 9 arm A)
[DEDUPE-27] surface=0 mode=off in=2087 out=1498     (piece 9 arm B)
[DEDUPE-27] surface=1 mode=off in=3510 out=2013     (piece 9 arm B)
```

`[SPACING-22]`, `[DOWNSAMPLING RESULT]` and `[PAPER-234]` are byte-identical between the two arms of a piece;
the classify line says `Surface_0=interior` in all four cells (piece 2 kept, piece 9 swapped), so both arms of
a piece labelled the same face interior. `Normals flipped: false` in all four cells
(`checkNormalsIntersection`, `mesh_processing_headless.cpp:2935-2958`), so the global flip never fired. The
only pipeline warning in the run is on piece 2, once in each arm: `[WARNING] Cluster 0 has no boundary points!
Skipping getPointsInSequence.` / `[WARNING] This may indicate the boundary radius (50mm) is too small for the
point spacing.` Piece 9 has neither line.

**What actually differs between the two arms of a piece**, measured: 12 differing lines each way (24 total)
after masking the arm name and the dump path, in exactly these classes — `[REASSIGN-22]` (1), `[WINDOW-26]` (2),
`[WINDOW-26-MEASURE]` (1), `[WINDOW-26-FINAL]` (2), `[DEDUPE-27]` (2), `[STATUS-23]` (1), `Sampled indices`
(1), `Time after processing` (1), `Total time elapsed` (1). Nothing else in the 152-line (piece 2) / 146-line
(piece 9) logs differs. The `Sampled indices` line is `checkNormalsIntersection`'s `std::random_device` draw
(`mesh_processing_headless.cpp:2935-2958`) and is the only nondeterminism in the run.

## 7. Corpus, pristine, deletion, job, branch

- **Corpus and frozen inputs unchanged**: `out/corpus_before.tsv` and `corpus_after.tsv` 1 803 lines each,
  md5 `858c963da6ae09bee1b3a494b08f0781` both; `out/inputs_before.md5` and `inputs_after.md5` 215 lines each,
  md5 `c325e0c0d798a75da903f347dc95a6f9` both; `out/corpus.diff` and `out/inputs.diff` **0 bytes**. Both
  re-verified with `cmp` on the cluster after the job.
- **`/opt/sfs-pristine`: ABSENT** on the compute node, recorded in `out/pristine.txt` (197 B):

  ```
  # /opt/sfs-pristine, recorded from the compute node
  status ABSENT
  ls: cannot access '/opt/sfs-pristine': No such file or directory
  stat: cannot statx '/opt/sfs-pristine': No such file or directory
  ```

- **Geometry deleted, counted first.** `out/GEOMETRY_DELETED_phase1.txt` (205 B) was written **before** the
  delete and `out/geometry_counts_phase1.tsv` holds the per-extension counts:

  ```
  ext    files      bytes
  pcd        2    691 816
  ply       12  3 820 607
  TOTAL     14  4 512 423      after deletion: 0 files under out/
  ```

  Per cell, counted into that cell's `geometry_counts.tsv` before its own delete (29 files each):

  ```
  cell                    json      obj       other     pcd        ply         xyz        TOTAL
  Juglet_Piece_2_x1_armA    5/4187  1/159681  3/539   3/632458  12/4416096   5/1326043  29/6539004
  Juglet_Piece_2_x1_armB    5/3613  1/159681  3/538   3/632458  12/4392579   5/1318451  29/6507320
  Juglet_Piece_9_x1_armA    5/3348  1/128277  3/539   3/536219  12/3533667   5/1054266  29/5256316
  Juglet_Piece_9_x1_armB    5/2775  1/128277  3/539   3/536219  12/3510888   5/1046462  29/5225160
  ```

  What survives: every `*.tsv`, every `*.json`, each cell's `cell.tsv`, `inputs.md5`, `status_raw.tsv` and
  its whole `logs/` tree (`mesh.log`, `lines39.log`, `admission39.log`), `run.json`, `submit.sbatch`, the
  instruments as run, and the figures — no figure in this ticket. **0** geometry files remain under `out/`.
  The 401 geometry files still under the run directory's `build/new/src` are the extracted commit's **own**
  tracked files, not cell output: the commit tracks 409 geometry-extension paths, 401 exist there and 0 exist
  there that the commit does not track; all 401 regular blobs are md5-identical to
  `git cat-file blob ed0fc16:<path>` and the remaining 8 (`NURBS_Dataset_20251103/SfS_pp/Axes/Pot_A_Piece_0{1..8}_Axis.xyz`)
  are symlinks in the commit (mode 120000) whose targets `readlink` matches with 0 mismatches.
- **Job and state** (`sacct -j 33926931 -X`):

  ```
  JobID     JobName      State      Start                End                  Elapsed  ExitCode  NodeList       Partition  AllocCPUS
  33926931  t39-ownmode  COMPLETED  2026-10-28T16:25:30  2026-10-28T16:27:17  00:01:47 0:0       spartan-bm073  sapphire   8
  ```

  `33926931.batch` and `33926931.extern` also COMPLETED; `logs/slurm-33926931.err` is 0 bytes. Budget: **1 of
  the 2** the ticket allows. The job closed its own record — there is no `CLOSED-BY-HAND` file for this ticket.
- **Index row appended** (`runs/index.tsv` line 320; header `runid\tjobid\tcommit\ttag\tverdict\thuman_note`),
  last two fields empty:

  ```
  20261028-1624_ed0fc16_t39-ownmode<TAB>33926931<TAB>ed0fc16328efdb13991e2d9dba843fe7bddb174e<TAB>t39-ownmode<TAB><empty><TAB><empty>
  ```

- **Anti-drift gate passed**: `out/instruments_commit.md5` and `out/instruments_rundir.md5` are identical,
  8 rows — `grow38.py 2935869749eea7ae44341bdfe1d9e17a`, `measure34.py 055090a5577ca1e8066a6e4f5146a3f2`,
  `mesh38.py a5e8ff2523229a592189acd82be02cef`, `nest39.py 03a747b72d3acb65062451ca8a8b5685`,
  `replica37.py e190a7948fdf1d65a9f7195e0450a764`, `run_cell39.sh f509f05e066e38be6d6a436a56cfef14`,
  `stage_synth_p38.sh 9bb59676bc08157687010955d1d9ebc8`, `submit39.sh 616df11f7153234b81f900a06a92efa0`.
- **Environment** (`out/versions.txt`): host `spartan-bm073.hpc.unimelb.edu.au`, utc 2026-10-28T05:25:40Z,
  commit `ed0fc16…`, python 3.10.20, numpy 2.2.6, scipy 1.15.2, apptainer 1.3.3. Build of the arm's binary:
  `logs/build-new.log` 68 342 B, ends `[100%] Linking CXX executable MeshPreprocessingHeadless` /
  `[100%] Built target MeshPreprocessingHeadless`; the binary is 1 582 080 B, md5 `180e68467eac391279675fdc3ffedfe1`.
- **Branch**: `39-does-own-mode-keep-the-two-faces-apart`. The job built from
  `ed0fc16328efdb13991e2d9dba843fe7bddb174e` (its 11 `stage39/instruments/` files); this report, the run
  record and the ticket's progress note are committed on top and pushed to `origin`.
  `git diff --stat main -- mesh_processing_headless.cpp` is **empty**: no tracked pipeline behaviour was
  changed, as the ticket requires. `git diff --name-only main...HEAD` is 105 files — the 11 instruments, the
  93 report-and-results files, and the ticket's own markdown. The ticket's `**Status:**` line reads
  `in-progress`; that line and its two `Working in` / `Branch` companions were written by
  `scripts/ticket_start.sh` when the ticket was opened (`git diff b02c476^ b02c476`), and nothing this ticket
  committed has touched it since.

## 8. Not done, with the exact command or line

1. **The second job was not run** — nothing failed, so there was nothing for it to fix. Budget used: 1 of 2.
2. **No `SAMPLER-GATE-DISCLOSURE_<piece>.txt` file exists for this run.** Stage 38 wrote one per piece
   (`stage38/instruments/run_targets38.sh:55-68`); `run_cell39.sh` does not, so the route-1/route-2
   disclosure survives only as the two `[VALIDATE]` lines quoted in section 1 and in `out/phase1.log`. No
   command failed; the file was never written.
3. **`nest39.py selftest` is not run by the job.** `run_cell39.sh` only sets `NEST39=$INSTR/nest39.py` (line
   30) and calls its `count` and `pair` commands. The 3/3 result quoted in section 5 was produced by hand on
   the login node, from the run directory's instruments copy:
   `python3 instruments/nest39.py selftest`.
4. **Two things are not mirrored into the worktree.** The `build/` tree (435 MB: `build/new` 220 MB +
   `build/src` 215 MB) stays in the cluster run directory as it did for stage 38, and so does the built binary
   `out/bin-new` (1 582 080 B). Everything else the run wrote — 89 of its 90 files outside `instruments/` — is
   in `results/`, md5-compared one for one against the cluster copy (89 of 89 identical). The staged
   `instruments/` copy in the run directory is not copied here either, because it is byte-identical to
   `stage39/instruments/` (11 of 11 md5s equal, compared against the cluster); `out/instruments_commit.md5`
   and `out/instruments_rundir.md5` record that equality as the job's own anti-drift gate.
5. **Pot A is not in this run** — the ticket excludes it deliberately (it is the reference from the other
   density group, not a silent sherd, and stage 38's run 6 showed its cell is what the wall clock kills). This
   is a scope decision recorded in the ticket, not a failure.
6. **No figure was produced** for this ticket; the ticket asks for none. `SFS_WINDOW_REPORT` was left unset, so
   no `[WINDOW-26]` TSV report exists and the lines quoted in section 6 are the only record of the windows.

## Where the surviving numbers live

```
stage39/results/PROVENANCE.txt                    every file below mapped to its path in the run directory
stage39/results/out/phase1.log                    the driver's own log, 324 lines: cloud gate, per-cell env,
                                                  [SURFACE] / [SURFACEPAIR] / [NEST] lines, geometry census
stage39/results/out/cells-pipeline/cloud_gate.tsv         item 1, both pieces
stage39/results/out/cells-pipeline/pipeline_cells.tsv     item 2, 4 rows, with ctrl38_reproduced
stage39/results/out/cells-pipeline/surfaces.tsv           item 3, 8 rows
stage39/results/out/cells-pipeline/surface_pairs.tsv      item 4, 4 rows with signed t and percentiles
stage39/results/out/cells-pipeline/nest.tsv               item 5, 4 rows
stage39/results/out/cells-pipeline/<cell>/logs/admission39.log   item 6, the 8 lines per cell verbatim
stage39/results/out/cells-pipeline/<cell>/logs/mesh.log          the pipeline's own stdout/stderr
stage39/results/out/cells-pipeline/<cell>/logs/lines39.log       the fixed grep set over mesh.log
stage39/results/out/cells-pipeline/<cell>/cell.tsv               that cell's parameters and STATUS-23 values
stage39/results/out/cells-pipeline/<cell>/inputs.md5             the staged cloud, mesh and axis with md5s
stage39/results/out/cells-pipeline/<cell>/geometry_counts.tsv    that cell's census, written before its delete
stage39/results/out/cells-pipeline/<cell>/status_raw.tsv         the pipeline's raw status rows
stage39/results/out/cells-pipeline/<cell>/measure/*.json         per-surface, per-pair, per-nest, spacing
stage39/results/out/measure/sampler_validate_<piece>.json        route-1/route-2 sampler proof
stage39/results/out/measure/sample_<piece>_x1.json               the cloud actually drawn
stage39/results/out/measure/spacing39_<piece>_x1.txt             the spacing pass 1 gated and pass 2 used
stage39/results/out/pristine.txt                                 /opt/sfs-pristine ABSENT
stage39/results/out/versions.txt, out/run-meta_phase1.txt        host, utc, versions, jobid, phase_rc=0
stage39/results/out/GEOMETRY_DELETED_phase1.txt                  the record written before the delete
stage39/results/out/geometry_counts_phase1.tsv                   the same counts, per extension
stage39/results/out/instruments_{commit,rundir}.md5              the anti-drift gate, 8 rows, equal
stage39/results/out/corpus.diff, out/inputs.diff                 0 bytes each
stage39/results/logs/slurm-33926931.out / .err                   Slurm stdout (0 B stderr)
stage39/results/logs/build-new.log, fetch.log, submit.log, sbatch_phase1.txt
stage39/results/run.json, stage39/results/submit.sbatch           the run's parameters and the script that ran
stage39/instruments/                                              the sources (md5 equal to the run's copies)
```
