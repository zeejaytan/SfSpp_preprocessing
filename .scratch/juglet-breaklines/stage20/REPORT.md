# Ticket 20 — evidence for the five silent Juglet sherds

Worker report, 2026-10-27. Branch `20-why-five-sherds-produce-no-surface`.
Everything below is read out of a run directory or a source line, and every source line is
quoted with its file and line number. **No verdicts**: the lead marks H1–H4 supported or
refuted. Where a measurement disagrees with the pipeline, both numbers are given.

Piece numbers are Juglet pieces unless stated. The shipped operating point is
`theta=3.4, kappa=1.0, nb=10, rhoD=1.0, rhoN=0.95, rhoC=0.1, rhoInN=0.75, rhoInC=0.25,
k1=10, k2=30, downsample target 0` (`mesh_processing_headless.cpp:2547-2582`).

## 1. The five runs this report rests on

| run id | job | commit | sacct | what it is |
|---|---|---|---|---|
| `20261027-0131_bc58c3d_p20-sweep` | 33836033 | bc58c3d | FAILED 6:0 00:01:02 | aborted: stager not executable (mode 644) — nothing staged, nothing ran |
| `20261027-0136_ea1f11a_p20-sweep` | 33836128 | ea1f11a | COMPLETED 0:0 00:02:04 | the 53-variant sweep, all `mesh_exit=0` |
| `20261027-0138_e98f3e7_p20-analysis` | 33836171 | e98f3e7 | FAILED 1:0 00:00:07 | analysis only: my PLY reader asked for `normal_x`, the PLY writes `nx` |
| `20261027-0143_0dbd48d_p20-analysis2` | 33836302 | 0dbd48d | FAILED 1:0 00:00:07 | analysis only: `clusters[0]` on a piece with 0 clusters |
| `20261027-0148_f3896e4_p20-arm` | 33836433 | f3896e4 | COMPLETED 0:0 00:03:10 | density arm (10 variants) + the analysis + the renders |

Root prefix `R=/data/gpfs/projects/punim2657/SfSpp/runs`. No number in this report comes
from the three failed jobs: they wrote nothing that survived, and the two analysis failures
were my own instrument, not the pipeline.

The per-variant stage trees (geometry, per-variant logs) were deleted after harvesting, as
instructed, with a counted record in each run's `out/GEOMETRY_DELETED.txt` (§10). The
pipeline's own printouts survive verbatim in `out/A2_pipeline_printouts.tsv` and
`out/variants.tsv`; the raw per-variant `logs/mesh.log` line numbers cannot be re-derived
from them, so everywhere below the quoted text is cited to the column of that table that
holds it.

## 2. The pipeline's path, stage by stage, with its gates

1. **Downsample.** `mesh_processing_headless.cpp:2547-2549`:
   `int dsTarget244 = 0;` … `downsamplePointCloud(inputFilePath, 0.6F, dsTarget244);`.
   With `SFS_DOWNSAMPLE_TARGET=0` it takes the fixed-radius restore path
   (`:603-609`), with `<0` it skips (`:588-589`), otherwise the adaptive band
   `lowerBound=0.8*target, upperBound=1.2*target` (`:628-665`).
2. **Normals.** `:419-428`: `int nb_neighbors = std::max(5, std::min(20, (int)points.size()/1000));`
   then `CGAL::pca_estimate_normals<Concurrency_tag>(points, nb_neighbors, ...)`, and the
   count is printed at `:421` as `[ADAPTIVE CGAL] Using <n> neighbors for <N> points (density-aware)`.
3. **Growth.** `surfaceSegmentation` (`:2051-`), paper branch with `thetaDeg / kappaDeg / nb`
   printed as `[PAPER-234] paper grow: thetaDeg=… kappa=… nb=…`; the PCL alternative reads
   `smoothnessAngleThreshold` (printed as `[SPLITTER-234] … smoothDeg=…`).
4. **Merge.** `mergePaper234` (`:1387-1981`), banner `[PAPER-234] appendix-A merge: rhoD=…
   rhoN=… rhoC=… rhoInN=… rhoInC=… k1=10 k2=30`, then `[PAPER-234] pass 1: merge <j> into <i>`
   per fusion and `[PAPER-234] pass <p> done: <n> clusters` per pass.
5. **Classify.** `classifyAndOrderPaper234`, `:2004-2049` (§6).
6. **The write gate — this is where a sherd stops being a sherd.** `:2200`
   `if (clusters.size() > 1)` … the two improved-surface PLYs are written only inside that
   branch (`:2289-2291` `pcl::io::savePLYFile(tmp_path + "tmpSurfaceCluster_Improved_0.ply", …)`
   and `…_1.ply`). `:2316` `else if (clusters.size() == 1)` builds a cloud for cluster 0,
   edits `tmp_path`, and `break;` (`:2338`) — nothing is written for it.
   Then `:2600` `if (fs::exists(tempFileName0))` and `:2607` `if (fs::exists(tempFileName1))`,
   each with an `else` printing `Warning: Source file not found: …` (`:2604`, `:2611`).
7. **The count reported.** `:2163` `Number of clusters is equal to <n>`;
   `:2392-2396` `Warning: Could not achieve 2 clusters after <i> iterations. Final cluster
   count: <n>. Proceeding with available clusters.`

So a sherd reaches a NURBS surface only if, after the merge, at least two clusters survive.
One cluster produces two "Source file not found" lines and no `Surface_0/_1`; zero clusters
the same.

## 3. Where each silent piece is lost (acceptance 2)

The verbatim printouts are in `R/20261027-0148_f3896e4_p20-arm/out/A2_pipeline_printouts.tsv`
(columns `clusters`, `sizes`, `merge`, `classify`, `face_order`, `s0`, `s1`, `notfound`).

| piece | clusters printed | where it is lost | the printout that shows it |
|---|---|---|---|
| 2 | 0 | growth: nothing survives region-growing | `Number of clusters is equal to 0` — 21 identical retries, then both files missing (`notfound=2`) |
| 9 | 0 | growth: same | same, `notfound=2` |
| 5 | 1 | growth: one cluster only; `:2316` branch discards it | `Cluster 1 : 679`, then `Could not achieve 2 clusters after 1 iterations. Final cluster count: 1.`, `notfound=2` |
| 3 | 2 (169, 99) | the appendix-A merge fuses them | `pass 1: merge 99 into 169`, `pass 1 done: 1 clusters`, `Final cluster count: 1`, `notfound=2` |
| 8 (shipped defaults, stage-1 PLY) | 2 (224, 196) | the appendix-A merge fuses them | stage-1 run `20261027-0055_d8af9d2_p07-juglet-stage1`, ticket table; my replay of that PLY fires the same criterion (§5) |

Piece 8 also has a cell where it *does* produce surfaces — `p20-p8-nb30-t8` gives 712 and 548,
no fusion, `classify: face0 n=712 interior_frac=0.5871 face1 n=548 interior_frac=0.1515
satA=883.0000 satB=377.0000`, `kept -> Surface_0=interior`, `s0=yes s1=yes notfound=0`.

For pieces 3 and 8 the loss is *after* a successful two-face segmentation; for 2, 5 and 9 it
is before it.

## 4. H1 — do the normals degrade with density?

**Artefacts.**
- `R/20261027-0136_ea1f11a_p20-sweep/out/variants.tsv` (53 rows, 12 columns).
- `R/20261027-0148_f3896e4_p20-arm/out/A_segmentation_input.tsv` — md5 of the PLY that grew into segmentation, per piece, over variants.
- `…_p20-arm/out/D_normal_density.tsv` — 5-NN against 20-NN PCA normals on the same cloud.
- `…_p20-arm/out/arm_table.tsv` — the density arm.
- The adaptive line quoted from every log.

**The `nb` knob does not reach the normals.** All 13 piece-2 cells, all 6 piece-3 cells, all
12 piece-5 cells, all 3 piece-8 cells, all 12 piece-9 cells share one segmentation-input md5
(`A_segmentation_input.tsv`, column `distinct_md5_over_variants` = 1): piece 2
`9e5bab27c406fc4ec9baec2259b493a5` (76741 bytes), piece 3 `122b2fbbc7356c8305cff5b0d8699958`
(108396), piece 4 `286b60e0ea15b44862ee28b6bf39b3c9`, piece 5 `f1be45777b…`, piece 8
`77c5d18284…`, piece 9 `afde2f47c3…`, piece 7 `cadba02ac1…`, `Pot_A_Piece_07` `29536bde34…`.
`SFS_PAPER_NB` is read at `:2576` and printed at `:2587`, and every log shows it only in the
growth line (`paper grow: thetaDeg=… nb=<value>`); the normal estimate at `:420` is a separate
call site with its own count.

**The normal estimator's neighbourhood, as printed.** `Using 5 neighbors for N points
(density-aware)` on every Juglet piece in every log examined, and `Using 8 neighbors for 8598
points` for `Pot_A_Piece_07` — i.e. the adaptive rule at `:420` gives the smallest allowed
count (5) to every Juglet cloud, whatever else changes.

**How much the normal estimate depends on neighbourhood size on these clouds**
(`D_normal_density.tsv`, unsigned angle between a 5-NN PCA normal and a 20-NN PCA normal at the
same point, ≤1500-point sample per piece):

| piece | sampled points | median ° | p90 ° | frac > 30° | frac > 60° |
|---|---|---|---|---|---|
| Juglet_Piece_2 | 1031 | 11.14 | 28.56 | 0.087 | 0.0087 |
| Juglet_Piece_3 | 1467 | 10.98 | 31.06 | 0.110 | 0.0089 |
| Juglet_Piece_4 | 1530 | 8.40 | 25.59 | 0.061 | 0.0013 |
| Juglet_Piece_5 | 1511 | 6.67 | 24.06 | 0.062 | 0.0013 |
| Juglet_Piece_7 | 2127 | 5.52 | 22.05 | 0.057 | 0.0080 |
| Juglet_Piece_8 | 1988 | 7.76 | 30.96 | 0.105 | 0.0141 |
| Juglet_Piece_9 | 787 | 12.97 | 38.84 | 0.147 | 0.0330 |
| Pot_A_Piece_07 | 1720 | 0.88 | 14.65 | 0.024 | 0.0017 |

The two silent-by-growth pieces (2 and 9) are the two with the largest median (§11.1 and 12.97°)
and the largest tail (0.147 and 0.087 above 30°); the control `Pot_A_Piece_07` is the smallest
(0.88°).

**The density arm does not move these clouds.** `arm_table.tsv`, pieces ×
`{SFS_DOWNSAMPLE_TARGET=19000, -1}`, points into clustering:

| piece | target 19000 | target -1 | clusters (19000 / -1) |
|---|---|---|---|
| 2 | 2564 | 2565 | 0 / 0 |
| 3 | 3490 | 3486 | 1 / 1 |
| 5 | 6211 | 6208 | 2 (747, 52) / 2 (757, 52) |
| 8 | 4478 | 4478 | 2 (257, 209) / 2 (257, 209) |
| 9 | 2094 | 2090 | 0 / 0 |

Why: these clouds are far below the band the adaptive branch wants. Piece 2, target 19000:
`[DOWNSAMPLING RESULT] Target=19000 points, Bounds=[15200-22800], Result=2565 points,
Radius(leaf)=0.00135`; target -1: `[NO DOWNSAMPLING] Using raw point cloud with 2565 points`.
Neither arm writes a surface for 2, 3 or 9, and both write both surfaces for 5 and 8.

## 5. H2 — the merge applied to 99–224-point clusters

**What the paper says the criteria are** (`C:/PR/papers/text/sfspp-2502.13986v1.md`):
Table I at `:464-473` — `k1=10` neighbours for boundary evaluation, `k2=30` for normal
estimation, `rho_d=1.0` "distance threshold for boundary pairs", `rho_n=0.95` "normal sim.
threshold", `rho_c=0.1` "curvature diff. threshold", `rho_in,n=0.75`, `rho_in,c=0.25`.
`:477` — boundary pairs are found within `rho_d`, "at least three boundary point pairs must be
detected. If the number of boundary point pairs is less than three, the cluster pair is
considered to contain noisy or unstable boundary information and is excluded from merging";
normals are averaged over `k2` neighbours; merge when the dot product is at least `rho_n` and
the mean-curvature difference below `rho_c`. `:479` — an internal representative point, "the
median point sorted by perpendicular distance to the principal axis", then `rho_in,n` and
`rho_in,c`. `:155` — "we select the two largest clusters, representing the inner and outer
surfaces", and `:151` — their own operating point is `n_b=10, tau_theta=4, tau_kappa=1`
(the shipped default in code is `theta=3.4`, `:2573`).

**Measured, per cluster pair** (`R/20261027-0148_f3896e4_p20-arm/out/B_merge_criteria.tsv`,
my replay of `mergePaper234` on the PLY the pipeline itself wrote; the thresholds are the
ones the pipeline printed in its own banner):

| piece | pair | pairs found (≥3 needed) | min pair dist (rho_d 1.0 mm) | dot normals (rho_n 0.95) | dCurv (rho_c 0.1) | dot internal (rhoInN 0.75) | dCurv internal (rhoInC 0.25) | outcome |
|---|---|---|---|---|---|---|---|---|
| 3 | 169 / 99 | 5 | 0.520166 | 0.970041 | 0.000217 | 0.971461 | 0.00194 | fired |
| 8 | 224 / 196 | 4 | 0.51495 | 0.961161 | 0.010478 | 0.782891 | 0.00693 | fired |
| 4 | 244 / 51 | 10 | 0.490473 | 0.988503 | 0.001244 | 0.991981 | 0.00737 | fired in replay, **not** in the pipeline |
| 7 | 326 / 263 | 0 | — | — | — | — | — | too few pairs |
| 7 | 326 / 77 | 6 | — | 0.98154 | — | — | — | fired (pipeline's own `merge 77 into 326`) |
| 7 | 403 / 263 | 10 | — | 0.969783 | — | 0.409647 | — | stopped at rhoInN |
| Pot A 07 | 120 / 71 | 7 | — | 0.997768 | — | 0.978151 | — | fired (pipeline's own `merge 71 into 120`) |

Every other cluster pair on `Pot_A_Piece_07` reports `too-few-pairs`.

So on pieces 3 and 8 the pair clears **every** threshold at once and by a wide margin: the
normal test is the tightest `(0.970 and 0.961 against 0.95)`, and the pair count is 5 and 4
against a floor of 3. On the one pair that is *not* fused despite ten boundary pairs
(piece 7, 403/263) the stopping criterion is the internal normal, 0.4096 against 0.75.

**Piece 4 is where replay and pipeline part company**, and it matters because piece 4 is the
"non-fusing comparison" that does produce surfaces: the pipeline printed `Cluster 1 : 242`,
`Cluster 2 : 51`, `Calling mergePaper234 function.`, then `pass 1 done: 2 clusters` — no
fusion; my replay grows 244 and 51 from the same PLY and every criterion passes. Two points of
growth decide it. `Pot_A_Piece_07` differs by one cluster the same way (pipeline `…144…`,
replay `…134…`). Pieces 3, 5, 7 and the p8 default PLY reproduce exactly (168/99, 679,
326/263/77/68/65, 224/196).

**What the merge does to the pipeline downstream of itself.** The fusion leaves one cluster,
and one cluster then hits the write gate at `:2200` and dies at `:2316-2338` — measured in
§3: pieces 3 and 8 print `notfound=2` and `s0=no s1=no` at the shipped defaults.

## 6. H4 — the interior test, its quantity, and its threshold

**The code** (`mesh_processing_headless.cpp:2004-2049`), verbatim behaviour:

- `:2008` `if (pclusters.size() < 2) return;` — with fewer than two clusters the test never runs.
- `:2009-2020` reads `SFS_AXIS_FILE`: six numbers, an axis point and a direction.
- `:2022-2034` per face: for each point, `w = pp - axPt`, `t = w.dot(axDir)`, `cp = axPt + t*axDir`,
  `v = cp - pp`, `if (v.dot(nn) > 0.0f) ++inN;` — the quantity is **the fraction of a face's
  points whose normal points toward the axis**.
- `:2036-2037` `satA = inFrac[0]*n0 + (1.0-inFrac[1])*n1;` and `satB = (1.0-inFrac[0])*n0 + inFrac[1]*n1;`
- `:2041-2048` `if (satB > satA)` swap, else keep. **There is no threshold and no third
  branch**: the decision is a strict comparison of two scores, and when both `inFrac` are 0 the
  scores reduce to `satA = n1`, `satB = n0` — the swap is then decided purely by relative
  cluster size (`n0` against `n1`). Both scores are printed, so the margin is in the log.

**Measured margins.** Two runs are quoted, each with the axis file its `[STAGE]` line names:

- `…_p20-arm/out/A2_pipeline_printouts.tsv` (my job 33836433, axis `out/axes/<P>_Axis.xyz`,
  md5 `9e0097dd1a27107ef09c3f5ae974235e` for piece 4);
- the stage-1 run's per-attempt logs `R/20261027-0055_d8af9d2_p07-juglet-stage1/out/logs/`,
  which contain **pairs of attempts on the same piece with the same clusters and only the axis
  file changed** — one staged from `out/boot/<P>_boot_Axis.xyz` (md5
  `4af30e54d854bcff7778a9f14a95feec` for piece 4), the other from `out/axes/<P>_Axis.xyz`.
- `B_classify_replay.tsv` for the replay rows; the replay's axis resolver prefers the boot file,
  so those rows are comparable with the boot cells only.

| piece / cell | axis | face0 n, interior_frac | face1 n, interior_frac | satA | satB | margin | decision |
|---|---|---|---|---|---|---|---|
| 1, `attempt-default` | boot | 3489, 0.0000 | 626, 0.0000 | 626.0 | 3489.0 | 2863 (**pure size**) | swapped |
| 1, `final` | axes | 3489, 0.0000 | 626, 0.0000 | 626.0 | 3489.0 | 2863 (pure size) | swapped |
| 4, `attempt-default` | boot | 242, 0.0000 | 51, 0.0000 | 51.0 | 242.0 | 191 (pure size) | swapped |
| 4, `final` | axes | 242, 0.0826 | 51, 0.9412 | 23.0 | 270.0 | 247 | swapped |
| 6, `attempt-default` | boot | 365, 0.0822 | 213, 0.2207 | 196.0 | 382.0 | 186 | swapped |
| 6, `final` | axes | 365, 0.0000 | 213, 0.0000 | 213.0 | 365.0 | 152 (pure size) | swapped |
| 7, `attempt-default` | boot | 403, 0.1836 | 263, 0.0000 | 337.0 | 329.0 | **8** | swapped |
| 7, `final` | axes | 403, 0.0000 | 263, 0.3878 | 161.0 | 505.0 | 344 | swapped |
| 8, `nb30 t8` (mine) | axes | 712, 0.5871 | 548, 0.1515 | 883.0 | 377.0 | 506 | kept |
| Pot A 07 (mine) | axes | 3093, 0.0000 | 2850, 1.0000 | 0.0 | 5943.0 | 5943 | swapped |
| 3, replay | boot | 169, 0.1953 | 99, 0.0202 | 130 | 138 | **8 of 268 points** | swapped |
| 4, replay | boot | 244, 0.0 | 51, 0.0 | 51 | 244 | 193 (pure size) | swapped |
| 7, replay | boot | 326, 0.2270 | 263, 0.0 | 337 | 252 | 85 | kept |
| 8, replay | boot | 224, 0.0714 | 196, 0.1429 | 184 | 236 | 52 | swapped |

**The axis file alone moves the evidence.** Pieces 4, 6 and 7 each have two attempts in the
stage-1 logs whose cluster counts and sizes are identical (`242/51`, `365/213`, `403/263`)
and whose `interior_frac` differs, because only the staged axis differs: piece 6 goes from
`0.0822 / 0.2207` (boot) to `0.0000 / 0.0000` (axes); piece 7 from `0.1836 / 0.0000` to
`0.0000 / 0.3878`; piece 4 from `0.0000 / 0.0000` to `0.0826 / 0.9412`. The two axis files are
byte-fixed (`out/axes` `9e0097dd…` and `out/boot` `4af30e54…`, identical md5 in both runs), so
this is not run-to-run noise: it is two different axes giving two different interior fractions
for the same 242 points. On pieces 1 and 6 (axes cell) both fractions are exactly 0.0000, and
then `satA = n1`, `satB = n0` — the "interior" label is decided by which face has more points.
The smallest margin measured on a Juglet piece is 8 points out of 268 (piece 7, boot; piece 3,
replay).

The Juglet faces on piece 3 carry mostly normals that point away from the axis:
`B_classify_replay.tsv` gives `cos_med -0.743923` on the 169-point face and `-0.696748` on the
99-point face, with only `0.201183` of the first face above |cos| 0.9. The control piece
separates completely (0.0000 against 1.0000).

**What the four silent pieces get from this test.** Pieces 2, 5 and 9 have fewer than two
clusters at the shipped defaults, so `:2008` returns before the test runs — there is no
interior_frac for them at all (`classify=none` in `A2_pipeline_printouts.tsv`). Pieces 3 and 8
pass through it only if the merge leaves two clusters. No code path reports "the evidence is
too thin to decide": `:2041` has two outcomes, and `:2038-2040` prints the scores without
gating on them.

## 7. H3 — measured on the mesh, not on the pipeline (acceptance: mesh measurements)

**Wall thickness and sheets** (`…_p20-arm/out/C_mesh.tsv`; 800 rays cast along `-n` from
points offset 1 µm inward, my own Möller–Trumbore intersector, mm):

| piece | verts / faces | area mm² | watertight | rays / hits | thickness med / p10 / p90 mm | frac in 1–3 mm | hits/ray med, max | rays with ≥2 sheets |
|---|---|---|---|---|---|---|---|---|
| 2 | 2565 / 5126 | 491.07 | True | 1031 / 1028 | 2.693 / 2.139 / 6.751 | 0.598 | 2, 10 | 1027 |
| 3 | 3493 / 6982 | 752.90 | True | 1467 / 1463 | 2.452 / 1.857 / 7.139 | 0.671 | 2, 9 | 1460 |
| 4 | 3651 / 7298 | 705.44 | True | 1530 / 1530 | 2.562 / 2.047 / 6.937 | 0.676 | 2, 10 | 1530 |
| 5 | 6211 / 12418 | 1401.63 | True | 1007 / 1005 | 2.900 / 2.316 / 6.517 | 0.541 | 2, 9 | 1005 |
| 7 | 8421 / 16838 | 1980.18 | True | 851 / 850 | 3.263 / 2.325 / 5.785 | 0.339 | 2, 8 | 847 |
| 8 | 4479 / 8954 | 850.38 | True | 994 / 989 | 2.094 / 1.722 / 4.250 | 0.798 | 2, 8 | 990 |
| 9 | 2094 / 4184 | 373.76 | True | 787 / 782 | 2.595 / 2.066 / 8.183 | 0.614 | 2, 8 | 783 |
| Pot A 07 | 63522 / 21174 | 2005.19 | False | 860 / 860 | 4.056 / 3.501 / 11.974 | 0.009 | 2, 2 | 860 |

Five of the nine Juglet pieces (2, 3, 5, 8, 9) are closed two-sheet surfaces with a median wall
2.09–2.90 mm thick in the middle of the 1–3 mm band; every ray on every Juglet piece enters at
least one more sheet, and the control `Pot_A_Piece_07` is an open shell with a 4.06 mm median
and 0.93 % of rays in the 1–3 mm band.

**Are the two clusters two sheets, or one sheet split in two?**
(`…_p20-arm/out/B_two_clusters.tsv`, pre-merge, on the pipeline's own PLYs):

| piece | n0 / n1 | dot(mean normals) | nn distance min / med mm | offset along n0 med (p10, p90) mm | centroid distance mm |
|---|---|---|---|---|---|
| 3 | 169 / 99 | **+0.741637** | 0.520166 / 4.38377 | −3.49232 (−6.9192, −1.58969) | 11.7959 |
| 8 | 224 / 196 | **+0.717114** | 0.51495 / 6.49725 | −4.21725 (−7.7885, −1.40327) | 12.515 |
| 4 | 244 / 51 | +0.924154 | 0.490473 / 1.97947 | −0.911295 | 7.57436 |
| 7 | 326 / 263 | +0.456437 | 3.14587 / 11.3602 | −8.30541 | 16.9892 |
| Pot A 07 | 3093 / 2850 | **−0.998866** | 3.29776 / 3.94054 | −3.83651 (−4.75219, −3.2321) | 3.9727 |

On the two fused pieces the two clusters' mean normals point the *same* way (+0.74, +0.72) and
their nearest points are 0.52 mm apart — the two clusters face outward together and touch at a
seam. On the control, the two clusters' mean normals are antiparallel (−0.9989) and their
nearest neighbours are 3.30 mm apart: the two walls of the sherd, 3.9 mm apart along the axis.

**Read on the renders** (§8): on piece 3 the 169-point (red) and 99-point (blue) clusters lie on
one arc, one after the other along z, inside the same radial band; on `Pot_A_Piece_07` the two
clusters are two parallel radial bands.

**The code has no honest one-wall branch.** Measured in §2 and §3: with one cluster the write
block at `:2200` is skipped, `:2316-2339` builds a cloud and throws it away
(`break;` at `:2338`), and `:2600-2612` reports two missing files. The only trace of a
one-cluster result is the warning at `:2392-2396`, which is printed and does not act.

## 8. Renders (acceptance 5)

In `C:/PR/worktrees/sfs/20/.scratch/juglet-breaklines/stage20/renders/`, made on sapphire by
job 33836433 (`out/renders/`), PNG, 2250×750 px (three panels: full side view, zoom, s
histogram):

| file | bytes | scale of the zoom panel | caption |
|---|---|---|---|
| `Juglet_Piece_3.png` | 118021 | 31.06 mm across 750 px = 0.0414 mm/px; 1 mm bar drawn | pre-merge clusters [169, 99] from `Juglet_Piece_3_SampledWithNormals.ply`, axis `Juglet_Piece_3_boot_Axis.xyz` |
| `Pot_A_Piece_07.png` | 217871 | 46.65 mm across 750 px = 0.0622 mm/px; 1 mm bar drawn | pre-merge clusters [3093, 2850] from `Pot_A_Piece_07_SampledWithNormals.ply`, axis `Pot_A_Piece_07_Axis.xyz` |
| `Juglet_Piece_2_theta8.png` | 111136 | same construction | the clusters theta 8 recovers on piece 2 |
| `Juglet_Piece_5_theta8.png` | 159996 | same construction | piece 5 at theta 8 |
| `Juglet_Piece_9_theta8.png` | 107011 | same construction | the clusters theta 8 recovers on piece 9 |

At 0.0414 mm/px a 1–3 mm separation is 24–72 px, and both sheets of each piece are drawn under
the clusters, so "two sheets, one scribbled on each" and "one sheet, two colours" are
distinguishable by eye. Captions also in `renders/CAPTIONS.txt` and
`R/20261027-0148_f3896e4_p20-arm/out/E_captions.txt`: on piece 3 the two clusters' median
radial coordinate s is 2.492 mm and 3.298 mm (separation 0.805 mm, overlapping histograms); on
`Pot_A_Piece_07` 35.005 mm and 31.872 mm (separation 3.133 mm, disjoint histograms).

## 9. What would restore surfaces, costed (acceptance 6) — not implemented

Nothing below was run for effect; each item names what it touches and what this ticket measured
about its cost.

1. **Environment only, `SFS_PAPER_THETA=8`** (no source change; `:2573,2575`). Measured cells:
   piece 2 → 4 clusters (107, 104, 71, 70) surfaces yes; piece 9 → 2 (127, 69) yes; piece 3 →
   from the theta-8 cells available: `p3-nb30-t8` → 3 (338, 263, 58) yes, `p3-nb50-t12` → 4
   (588, 444, 62, 60) yes; piece 5 at theta 8 → 6 clusters (901, 418, 134, 130, 57, 54) with
   two fusions, yes; piece 8 already produces at `nb30 t8`. Cost: one variant ≈ 2.3 s of
   pipeline time (53 variants in a 2 m 04 s job, `33836128`), i.e. a nine-piece rerun is
   ~21 s of compute inside an existing container; no rebuild. Not measured in this ticket:
   `Pot_A_Piece_07` and pieces 1, 4, 6, 7 at theta 8, so the collateral cost on pieces that
   already work is an open number.
2. **Environment only, `SFS_PAPER_CHAIN=0`** (falls back to PCL region growing with the
   smoothness ladder, `:2572`). Measured cells: piece 2 → 2 (174, 65) yes — the ladder moves
   here, `Increasing angle threshold (+2) and trying again`, then `Number of clusters is equal
   to 2`; piece 3 → 1 (343) no; piece 5 → 2 (828, 63) yes; piece 8 → 1 (582) no; piece 9 → 1
   (50) no. Same per-variant cost as (1).
3. **Source change, an honest one-cluster branch** (`:2316-2339` and `:2600-2612`): write the
   improved-surface PLY for `clusters[0]` and skip the missing second file. Effect measured
   this ticket: pieces 5 (679 points) and 3 (1 cluster after fusion) would reach the B-spline
   stage instead of `notfound=2`; the pipeline already fits one B-spline per cluster
   (`51 points in data set`, `242 points in data set` in piece 4's log), so the added cost is
   one fit per one-cluster piece. Needs a rebuilt binary: the container is fixed at
   `/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif` and each job builds the
   checkout from a git archive (`logs/fetch.log`, `logs/cmake.log`, `logs/make.log` in every
   run dir), so a source change means either a new image or building inside the job as now.
4. **Source change, stop the 21 identical retries** (`:2392-2396` / the retry loop): the paper
   branch does not read `smoothnessAngleThreshold` (`SFS_SMOOTHNESS_DEG`), so the ladder cannot
   change anything under `SFS_PAPER_CHAIN=1`. Measured: `p3-sm3.0` and `p3-sm45.0` differ in
   exactly one printed token (`smoothDeg=3.00000` against `smoothDeg=45.00000` at `:2584-2587`)
   and are otherwise identical (2 clusters, 169 / 99, same merge); pieces 2 and 9 print
   `Single cluster found` 21 times with one distinct `paper grow` line each
   (`thetaDeg=3.40000`). Cost: the wasted work is 21 identical segmentations per piece
   (`elapsed_s` per variant is in `variants.tsv`); a source fix removes it, an env workaround
   cannot.
5. **Source change, relax `rhoInN`** — measured *not* to touch the silent pieces: on pieces 3
   and 8 the internal normal is 0.971 and 0.783, both above 0.75; the only pair this ticket
   found stopped by `rhoInN` is piece 7's 403/263 at 0.4096, on a piece that already produces
   surfaces.
6. **New stage, decide interior/exterior from the mesh instead of `classifyAndOrderPaper234`**:
   the ray probe in `instruments/replay_analysis.py` (`ray_hits`, 800 rays per piece) measures
   the two sheets and their offset directly, at ~1 s per piece (part of a 3 m 10 s job that also
   ran 10 pipeline variants). It is downstream of (1)–(3): with fewer than two clusters there
   are still two surfaces to label.

## 10. The sweep table (acceptance 3) and the arm

**Run directory for every row:** `R/20261027-0136_ea1f11a_p20-sweep` (job 33836128, commit
`ea1f11a`). Row tag = the variant; its harvested record is the row of the same tag in
`out/variants.tsv` and `out/A2_pipeline_printouts.tsv`; the per-variant stage tree was
`<run>/stage/<tag>` and was deleted with §10's counted record. `clusters` is the count printed
when the retry loop ended; `(n1, n2, …)` are the cluster sizes; `nf` is the number of
`Source file not found` lines, so `nf 2` means no surface was written.

| tag | piece | env | clusters | sizes | surfaces | nf |
|---|---|---|---|---|---|---|
| p2-nb10-t3.4 | 2 | NB=10 THETA=3.4 | 0 | — | no | 2 |
| p2-nb10-t5 | 2 | NB=10 THETA=5 | 0 | — | no | 2 |
| p2-nb10-t8 | 2 | NB=10 THETA=8 | 4 | 107, 104, 71, 70 | yes | 0 |
| p2-nb10-t12 | 2 | NB=10 THETA=12 | 3 | 253, 197, 67 | yes | 0 |
| p2-nb30-t3.4 | 2 | NB=30 THETA=3.4 | 0 | — | no | 2 |
| p2-nb30-t5 | 2 | NB=30 THETA=5 | 1 | 52 | no | 2 |
| p2-nb30-t8 | 2 | NB=30 THETA=8 | 3 | 235, 185, 91 | yes | 0 |
| p2-nb30-t12 | 2 | NB=30 THETA=12 | 2 | 454, 248 | yes | 0 |
| p2-nb50-t3.4 | 2 | NB=50 THETA=3.4 | 0 | — | no | 2 |
| p2-nb50-t5 | 2 | NB=50 THETA=5 | 1 | 52 | no | 2 |
| p2-nb50-t8 | 2 | NB=50 THETA=8 | 2 | 355, 194 | yes | 0 |
| p2-nb50-t12 | 2 | NB=50 THETA=12 | 2 | 499, 254 | yes | 0 |
| p2-chainoff | 2 | SFS_PAPER_CHAIN=0 | 2 | 174, 65 | yes | 0 |
| p3-sm3.0 | 3 | SMOOTHNESS_DEG=3 | 2 → 1 | 169, 99 → 268 | no | 2 |
| p3-sm45.0 | 3 | SMOOTHNESS_DEG=45 | 2 → 1 | 169, 99 → 268 | no | 2 |
| p3-nb30-t8 | 3 | NB=30 THETA=8 | 3 | 338, 263, 58 | yes | 0 |
| p3-nb50-t12 | 3 | NB=50 THETA=12 | 4 | 588, 444, 62, 60 | yes | 0 |
| p3-chainoff | 3 | SFS_PAPER_CHAIN=0 | 1 | 343 | no | 2 |
| p3-chainoff-sm3.0 | 3 | CHAIN=0 SMOOTHNESS=3 | 2 | 167, 79 | yes | 0 |
| p4-default | 4 | shipped | 2 | 242, 51 | yes | 0 |
| p5-nb10-t3.4 | 5 | shipped | 1 | 679 | no | 2 |
| p5-nb10-t5 | 5 | NB=10 THETA=5 | 1 | 841 | no | 2 |
| p5-nb10-t8 | 5 | NB=10 THETA=8 | 6 | 901, 418, 134, 130, 57, 54 | yes | 0 |
| p5-nb10-t12 | 5 | NB=10 THETA=12 | 5 | 1115, 942, 123, 61, 50 | yes | 0 |
| p5-nb30-t3.4 | 5 | NB=30 THETA=3.4 | 1 | 701 | no | 2 |
| p5-nb30-t5 | 5 | NB=30 THETA=5 | 4 | 855, 292, 92, 78 | yes | 0 |
| p5-nb30-t8 | 5 | NB=30 THETA=8 | 4 | 1026, 909, 89, 62 | yes | 0 |
| p5-nb30-t12 | 5 | NB=30 THETA=12 | 4 | 1154, 1152, 176, 50 | yes | 0 |
| p5-nb50-t3.4 | 5 | NB=50 THETA=3.4 | 3 | 716, 65, 50 | yes | 0 |
| p5-nb50-t5 | 5 | NB=50 THETA=5 | 3 | 865, 472, 210 | yes | 0 |
| p5-nb50-t8 | 5 | NB=50 THETA=8 | 4 | 1066, 910, 102, 68 | yes | 0 |
| p5-nb50-t12 | 5 | NB=50 THETA=12 | 4 | 1198, 1180, 184, 58 | yes | 0 |
| p5-chainoff | 5 | SFS_PAPER_CHAIN=0 | 2 | 828, 63 | yes | 0 |
| p5-sm3.0 | 5 | SMOOTHNESS_DEG=3 | 1 | 679 | no | 2 |
| p5-sm45.0 | 5 | SMOOTHNESS_DEG=45 | 1 | 679 | no | 2 |
| p7-default | 7 | shipped | 5 → 4 | 326, 263, 77, 68, 65 (77 fused into 326) | yes | 0 |
| p8-nb30-t8 | 8 | NB=30 THETA=8 | 2 | 712, 548 | yes | 0 |
| p8-nb50-t12 | 8 | NB=50 THETA=12 | 5 | 789, 621, 65, 59, 58 | yes | 0 |
| p8-chainoff | 8 | SFS_PAPER_CHAIN=0 | 1 | 582 | no | 2 |
| p9-nb10-t3.4 | 9 | shipped | 0 | — | no | 2 |
| p9-nb10-t5 | 9 | NB=10 THETA=5 | 0 | — | no | 2 |
| p9-nb10-t8 | 9 | NB=10 THETA=8 | 2 | 127, 69 | yes | 0 |
| p9-nb10-t12 | 9 | NB=10 THETA=12 | 3 | 203, 104, 51 | yes | 0 |
| p9-nb30-t3.4 | 9 | NB=30 THETA=3.4 | 0 | — | no | 2 |
| p9-nb30-t5 | 9 | NB=30 THETA=5 | 1 | 62 | no | 2 |
| p9-nb30-t8 | 9 | NB=30 THETA=8 | 2 | 169, 73 | yes | 0 |
| p9-nb30-t12 | 9 | NB=30 THETA=12 | 3 | 366, 105, 68 | yes | 0 |
| p9-nb50-t3.4 | 9 | NB=50 THETA=3.4 | 0 | — | no | 2 |
| p9-nb50-t5 | 9 | NB=50 THETA=5 | 2 | 62, 50 | yes | 0 |
| p9-nb50-t8 | 9 | NB=50 THETA=8 | 3 | 206, 75, 71 | yes | 0 |
| p9-nb50-t12 | 9 | NB=50 THETA=12 | 3 | 418, 107, 71 | yes | 0 |
| p9-chainoff | 9 | SFS_PAPER_CHAIN=0 | 1 | 50 | no | 2 |
| pota07-default | Pot A 07 | shipped | 8 → 7 | 3093, 2850, 203, 170, 144, 120, 73, 71 (71 fused into 120) | yes | 0 |

Two facts the table carries on its own: at `theta=3.4` no cell of pieces 2 and 9 reaches even
one cluster above 52 points, and `nb` never changes which cells succeed at a given `theta`
(piece 2 works from `theta=8` on, piece 9 from `theta=8` on), while `nb` does change the
cluster sizes and the number of clusters a successful cell produces.

**The density arm** (`R/20261027-0148_f3896e4_p20-arm`, job 33836433, commit `f3896e4`,
`out/arm_table.tsv`, 10 rows, no fusion fired in any row) is the table in §4.

**The theta composition the lead asked for** (`out/H_theta_recovered.tsv`, replay at theta 8):

| piece | N | clusters (n, frac of cloud, mean curvature, mean abs dot(normal, axis)) |
|---|---|---|
| 2 | 1031 | 104 (0.1009, 0.00897, 0.3275), 71 (0.0689, 0.01034, 0.4937), 69 (0.0669, 0.00681, 0.4343) — the replay gives 3 where the pipeline printed 4 (107, 104, 71, 70) |
| 9 | 787 | 127 (0.1614, 0.01058, 0.1422), 69 (0.0877, 0.03889, 0.1205) |
| 5 | 3021 | 901 (0.2982), 418 (0.1384), 134 (0.0444), 130 (0.0430), 57 (0.0189), 54 (0.0179) |

So at `theta=8` the largest cluster on piece 2 is 10 % of the cloud and on piece 9 16 % — the
surfaces come from a tenth to a sixth of the points, against 66 % and 36 % for the two clusters
of piece 3 at the shipped setting (`169+99` of 268 clustered, 1467 in the cloud).

## 11. Accounting (acceptance 7)

- **Corpus untouched.** `out/corpus_verdict.txt` in both completed runs: `frozen corpus md5
  unchanged: yes (21 files)`, computed from `out/corpus_md5_before.tsv` and
  `out/corpus_md5_after.tsv`.
- **Geometry deleted, counted.**
  - Sweep (`33836128`): `out/GEOMETRY_DELETED.txt` — obj 53 / 15728760 B, other 53 / 21438 B,
    pcd 141 / 41768593 B, ply 275 / 28306803 B, txt 87 / 3546 B, xyz 223 / 17790572 B,
    **total 832 files / 103619712 B**; `du_before` 107537054, `du_after` of the ticket's run
    trees 12834423.
  - Arm (`33836433`): obj 10 / 2376750 B, other 10 / 4030 B, pcd 24 / 4083940 B, ply 44 /
    8958905 B, txt 14 / 572 B, xyz 38 / 5793567 B, **total 140 files / 21217764 B**;
    `du_before` 21956884, `du_after` 4929112.
  - Aborted job (`33836033`): 300 files / 1378584 B in
    `20261027-0131_bc58c3d_p20-sweep/out/GEOMETRY_DELETED_ABORTED_JOB.txt`.
- **Ledger.** `/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv` has one row per run
  directory, `verdict` and `human_note` empty, and now holds 249 lines. **Wart to declare:**
  the aborted job `33836033` appended 50 per-variant rows before it died; the index is
  append-only, so those rows were left in place and are declared void in
  `20261027-0131_bc58c3d_p20-sweep/out/VOID_VARIANT_ROWS.txt` (60 lines naming the 50 runids).
- **Job budget:** 5 of 6 used — three failures, two completions; one job spare. The failure of
  `33836033` was my harness, not the pipeline: the stager was executed as `"$STAGER"` out of a
  `git archive`, which restores mode 644, so it exited 126 and nothing was staged.

## 12. What is not in this report

- `Pot_A_Piece_07`, and Juglet pieces 1, 4, 6, 7, at `theta=8`: no cells, so the collateral
  effect of the env option in §9.1 on the pieces that already work is unmeasured.
- My replay grows 244/51 on piece 4 where the pipeline prints 242/51, and one cluster of
  `Pot_A_Piece_07` at 134 against 144. Pieces 3, 5, 7 and the piece-8 default PLY reproduce
  exactly. Where the two disagree, the pipeline's own printout is given first in every table.
- The replay also drifts at `theta=8` on piece 2 (3 clusters against the pipeline's 4).
- The replay's axis resolver prefers `out/boot/<P>_boot_Axis.xyz` over
  `out/axes/<P>_Axis.xyz`; my pipeline cells staged the axes file. Growth does not read the axis,
  so the cluster counts are comparable; the `interior_frac` numbers are not, which is why §6
  gives both where both exist.
- Per-variant `logs/mesh.log` line numbers are not cited because those trees were deleted as
  instructed; the printout strings survive in `A2_pipeline_printouts.tsv`.
- No verdict on H1–H4, and no recommendation among §9's options.
