# Ticket 38 — does more resolution give the silent sherds a face?

Numbers only, from the runs; no verdict on what they mean (the ticket's Status and `intent/` are untouched).

Two runs of record, both kept:

- **run 4** `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-1615_92d6871_t38-resolution/` (job 33890365,
  commit `92d6871022fdf75f63170a5af65b30e31c9e843a`, `spartan-bm174.hpc.unimelb.edu.au`): sections 1-5, the
  control table and the ticket-37 anchors. Copied into `stage38/run-20261027-1615_92d6871/`.
- **run 5** `/data/gpfs/projects/punim2657/SfSpp/runs/20261028-0414_2a34d86_t38-resolution/` (job 33892259,
  commit `2a34d86a54467ac1f0238eed214bc11bdf7be208`): the corrected pair statistic, the real pipeline cells, the
  Part E redraws, the five-piece aggregate and the re-rendered figures — sections 6-8 and everything in
  `stage38/results/` that is marked run 5. It repeated phases 1 and 2 and reproduced their numbers.

The geometry both runs made was deleted on the cluster with per-extension counts recorded before the delete
(item 9).

## 1. Instrument proof, printed by the job on both target pieces

`[VALIDATE]` lines, verbatim, from `out/phase1.log`:

```
[VALIDATE] Juglet_Piece_2 mesh v=2565 f=5126 area=491.0674 mm2  edge_median=0.3387 edge_cv=1.107 angle_median=55.8 deg angle_min=0.1 deg frac(tri min angle<20 deg)=0.110
[VALIDATE] shipped cloud: points=2565 median_nn=0.2109 p10=0.1609 p90=0.4131 mm density_index=0.232 (points*s^2/area)
[VALIDATE] route 1 literal: sampled at 0.2109 mm -> points=6259 median_nn=0.2090 p10=0.1653 p90=0.2851 mm (voxel 0.3213 mm, 2 merge iterations) | count_ratio=2.4402 spacing_ratio=0.9911 (accept 0.95-1.05)
[VALIDATE] route 1 context: a uniform covering of 491.0674 mm2 at that spacing carries 11041 points = 4.30x the shipped count, so the literal count comparison cannot hold on this input
[VALIDATE] route 2 spacing: 0.2090 mm at request 0.2109 (ratio 0.9911) and 0.1042 mm at request 0.1054 (ratio 0.9885) PASS
[VALIDATE] route 2 cover: random surface points to the nearest cloud point median=0.1115 (0.529 s) p99=0.2079 (0.986 s) max=0.2476 mm (accept median<=0.80 s, p99<=2.50 s) PASS
[VALIDATE] route 2 surface: 6259 points to the original triangles median=0.00114 (0.005 s) p99=0.02800 (0.133 s) p99.9=0.04991 max=0.14001 mm (0.664 s) [7 points past 0.5 s re-measured over every triangle; their incident-set maximum was 0.89927 mm] (accept median<=0.25 s, p99<=1.00 s) PASS
[VALIDATE] Juglet_Piece_9 mesh v=2094 f=4184 area=373.7574 mm2  edge_median=0.3146 edge_cv=0.919 angle_median=55.6 deg angle_min=0.0 deg frac(tri min angle<20 deg)=0.105
[VALIDATE] shipped cloud: points=2094 median_nn=0.2034 p10=0.1599 p90=0.3950 mm density_index=0.232 (points*s^2/area)
[VALIDATE] route 1 literal: sampled at 0.2034 mm -> points=5257 median_nn=0.2015 p10=0.1630 p90=0.2580 mm (voxel 0.3113 mm, 2 merge iterations) | count_ratio=2.5105 spacing_ratio=0.9906 (accept 0.95-1.05)
[VALIDATE] route 1 context: a uniform covering of 373.7574 mm2 at that spacing carries 9033 points = 4.31x the shipped count, so the literal count comparison cannot hold on this input
[VALIDATE] route 2 spacing: 0.2015 mm at request 0.2034 (ratio 0.9906) and 0.1011 mm at request 0.1017 (ratio 0.9942) PASS
[VALIDATE] route 2 cover: random surface points to the nearest cloud point median=0.1071 (0.527 s) p99=0.2014 (0.990 s) max=0.2442 mm (accept median<=0.80 s, p99<=2.50 s) PASS
[VALIDATE] route 2 surface: 5257 points to the original triangles median=0.00088 (0.004 s) p99=0.02638 (0.130 s) p99.9=0.05486 max=0.08530 mm (0.419 s) [3 points past 0.5 s re-measured over every triangle; their incident-set maximum was 0.18714 mm] (accept median<=0.25 s, p99<=1.00 s) PASS
[VALIDATE] gate_route=instrument-validated-disclosed literal=FAIL route2=PASS
```

The brief's literal test — "sampling the ORIGINAL mesh at its own spacing must reproduce the shipped cloud's
point count and median NN to 5 %" — **fails on the count by construction, and the failure is a property of the
input, not of the sampler**: each Juglet cloud *is* its mesh's vertex set (2565 and 2094 points), so its
`density_index` `points*s^2/area` is 0.232, while any uniform covering carries 3.94 points per `s^2`
(`1/cos30` per triangle lattice + voxel merge). A uniform sampler therefore gives 2.44x / 2.51x the count at
`spacing_ratio` 0.9911 / 0.9906 — the shipped cloud is an under-dense draw of the same surface (spacing p10
0.1609 / p90 0.4131 mm on piece 2). Route 2 is what every synthetic cloud in this ticket is gated on instead:
**spacing** ratio 0.9885-0.9942 at two requests per piece, **cover** median 0.529 s / 0.527 s and p99
0.986 s / 0.990 s of random surface points, **surface** median 0.00114 / 0.00088 mm, p99 0.02800 / 0.02638 mm,
max 0.14001 / 0.08530 mm exhaustively. Both pieces are written up in
`out/SAMPLER-GATE-DISCLOSURE_Juglet_Piece_{2,9}.txt`, and stage38 is **not a replica of the shipped clouds** —
it is a uniform sampler at the shipped spacing. Every table repeats the achieved spacing beside the request.

## 2. Achieved spacing beside requested, per (piece, level)

```
piece  level  requested mm  achieved mm  ratio   points   voxel mm  merges
P2     x1     0.210896      0.209043     0.9912   6 259    0.3213    2
P2     x2     0.105448      0.104191     0.9881   25 240   0.1605    2
P2     x4     0.052724      0.052051     0.9872   102 166  0.0800    2
P2     x10    0.021090      0.020800     0.9863   649 067  0.0319    2
P9     x1     0.203415      0.201511     0.9906   5 257    0.3113    2
P9     x2     0.101708      0.101015     0.9932   21 315   0.1548    2
P9     x4     0.050854      0.050435     0.9918   86 329   0.0773    2
P9     x10    0.020342      0.020165     0.9913   547 195  0.0308    2
```

`x10` stayed under the ticket's 1.2 M-point cap on both pieces (649 067 and 547 195), so no level fell back to
"the finest spacing the mesh supports".

**Lattice-floor control (the ticket worried that x10 would just put one point per sub-triangle).** The level-L
mesh was *also* sampled at `s0/L` (a level-10 mesh sampled at 0.021 mm; the one-point-per-triangle floor would
be 0.034 mm > `s0/10` on piece 2):

```
P2 from x2 mesh at 0.10545 mm -> 25 181 points (the original mesh at the same request gave 25 240, -0.2 %)
P2 from x4 mesh at 0.05272 mm -> 102 111 points (102 166, -0.1 %)
P2 from x10 mesh at 0.02089 mm -> 645 180 points (649 067, -0.6 %)
P9 from x2/x4/x10 -> 21 302 / 85 872 / 542 164 points (21 315 / 86 329 / 547 195, -0.1 / -0.5 / -0.9 %)
```

The floor does not bite at these levels: subdividing and re-sampling reproduces the same count to within 1 %.

## 3. Max displacement of each subdivided surface — measured, and what the number actually is

```
piece  level  verts             faces             disp max mm  disp mean mm  sub-vertex spacing mm
P2     x2     2 565 -> 10 254   5 126 -> 20 504   1.809259    0.008309      0.10959
P2     x4     2 565 -> 41 010   5 126 -> 82 016   1.811170    0.006426      0.05729
P2     x10    2 565 -> 256 302  5 126 -> 512 600  1.814676    0.006312      0.02378
P9     x2     2 094 -> 8 370    4 184 -> 16 736   1.124688    0.004371      0.10493
P9     x4     2 094 -> 33 474   4 184 -> 66 944   1.129993    0.002903      0.05471
P9     x10    2 094 -> 209 202  4 184 -> 418 400  1.150416    0.002865      0.02270
```

**These maxima are a measurement artefact and must not be quoted as displacement.** The instrument measured them
with `dist_to_mesh`, whose candidate set is the triangles incident to the 3 nearest original vertices; on this
mesh 11 % of triangles have a minimum angle under 20 deg, so a subdivided vertex inside a sliver is scored against
a *neighbouring* triangle and the max becomes a triangle size. The same artefact is visible and quantified in
item 1: 7 points of 6259 scored 0.89927 mm against the incident set and 0.14001 mm exhaustively (3 of 5257:
0.18714 vs 0.08530 mm).

What is actually known about displacement, exactly:
- midpoint/lattice subdivision places every new vertex on an affine combination of its parent triangle's corners,
  so the subdivided surface is the original surface; the instrument's own self-test asserts this and fails at
  `max |off-parent| = 2.776e-17 mm` (L=10, one triangle), and asserts the midpoint and lattice routes agree
  exactly at L=4;
- the only real perturbation is the 1e-6 rounding of the merged shared midpoints, i.e. **<= 1e-6 mm**;
- an exact per-parent measurement (distance of each new vertex to *its own* parent triangle, which `subdivide`
  does not currently return) is the fix, and it is NOT in the run of record. Listed under item 10.

Sutures of the original meshes, measured (these, not the displacement, set how much fold per step a given spacing
sees — sagitta = (edge/2)·tan(fold/2)):

```
P2  edges 7 689  edge_median 0.3387 mm  fold_median 8.259 deg  fold_p99 110.031 deg  sag_median 0.01349 mm  sag_p99 1.25396 mm
P9  edges 6 276  edge_median 0.3146 mm  fold_median 9.015 deg  fold_p99 102.926 deg  sag_median 0.01395 mm  sag_p99 0.72254 mm
```

(`sag_max` 382.83 / 590.24 mm is a degenerate near-180 deg fold, not a physical sagitta; only median and p99 are
meaningful. `edge_cv` is 1.107 / 0.919 — the edge lengths are far from uniform.)

## 4. Full pre-floor distribution (3.4 deg gate, floor 50), per (piece, level, arm)

All rows at `theta=3.4 deg`, `kappa=3.4`, `nb=30`, `curvature_k=clamp(n/300,10,50)`; `share` = largest/points;
`fail_angle/pt` = angle refusals per point; `depth` = growth-tree depth of the largest region.

**`x1` is not today's cloud, and `level` is not `density`.** Today's cloud *is* the mesh's vertex set (2 565 /
2 094 points); `x1` is a uniform covering at the same median spacing (6 259 / 5 257 points). The two have the same
`median_nn` (0.2109 against 0.2090 mm on piece 2, 0.2034 against 0.2015 on piece 9) — and yet the largest region
goes **46 -> 873** on piece 2 and **16 -> 1 410** on piece 9, at 2.44x / 2.51x the point count (`density_index`
0.232 against ~3.94 points per s^2). So part of what this ladder measures is **coverage at a given median spacing**,
not median spacing itself: the shipped draw leaves gaps the 3.4 deg gate reads as buried surface, and a covering of
the same surface at the same spacing does not. Every arm and every level below is a *covering*; the `scan` /
`scan37` rows are the only ones grown on a shipped cloud, and they are labelled as such in every table.

```
piece  lvl arm   points   req mm   ach mm   regions  largest  share   ge10 ge20 ge30 ge50  pct1 pct5 pct10  fail_angle/pt  depth
P2     x1  A      6 259  0.21090  0.20904   2 000     873   0.1395   45   27   17    9     7    3    2      3.128775     54
P2     x1  F      6 259  0.21090  0.20904   2 045     684   0.1093   52   30   19   10     8    3    2      3.190925     48
P2     x1  scan   2 565  0.21090  0.21090   1 906      46   0.0179    9    3    2    0     2    0    0      5.069006      7
P2     x1  scan37 2 399  0.22172  0.22172   1 765      45   0.0188    9    3    2    0     3    0    0      5.032097      7
P2     x2  A     25 240  0.10545  0.10419   4 539   6 088   0.2412  167   82   60   35     6    3    2      2.270365    172
P2     x2  F     25 240  0.10545  0.10419   4 630   4 709   0.1866  196  103   73   44     9    3    2      2.319374    172
P2     x4  A    102 166  0.05272  0.05205   8 430  27 522   0.2694  493  234  156   93     9    2    2      1.451246    178
P2     x4  B    102 166  0.05272  0.05205   6 641  39 947   0.3910  155   61   45   32     6    3    2      1.197355    296
P2     x4  F    102 166  0.05272  0.05205   8 578  23 715   0.2321  548  278  195  123    10    2    2      1.486326    153
P2     x10 A    649 067  0.02109  0.02080  19 313 190 064   0.2928 1 259  989  714  444     7    4    2      0.689955    592
P2     x10 B    649 067  0.02109  0.02080  20 335 328 220   0.5057   327  149  103   66     2    2    2      0.617167    673
P2     x10 F    649 067  0.02109  0.02080  19 565 163 518   0.2519 1 330 1053  777  497    11    4    2      0.705630    531
P9     x1  A      5 257  0.20342  0.20342   1 575   1 410   0.2682   39   25   13    8     8    2    1      2.951113     43
P9     x1  F      5 257  0.20342  0.20151   1 623     739   0.1406   45   28   17    9     9    2    2      3.028914     31
P9     x1  scan   2 094  0.20342  0.20342   1 562      16   0.0076   10    0    0    0     0    0    0      5.167144      7
P9     x1  scan37 1 972  0.21069  0.21069   1 465      16   0.0081    9    0    0    0     0    0    0      5.148073      7
P9     x2  A     21 315  0.10171  0.10102   3 539   6 012   0.2821  128   63   40   25     9    3    2      2.109219     73
P9     x2  F     21 315  0.10171  0.10102   3 633   3 071   0.1441  148   76   49   32    12    3    2      2.172555     56
P9     x4  A     86 329  0.05085  0.05044   6 570  25 021   0.2898  401  192  131   82     6    3    2      1.324862    153
P9     x4  B     86 329  0.05085  0.05044   5 234  19 496   0.2258  110   42   33   17     6    4    4      1.122056    148
P9     x4  F     86 329  0.05085  0.05044   6 749  13 156   0.1524  445  225  152   97     9    5    3      1.370999    153
P9     x10 A    547 195  0.02034  0.02017  13 791 177 914   0.3251 1 261 1060  691  406     5    3    2      0.618376    722
P9     x10 B    547 195  0.02034  0.02017  12 859 264 761   0.4839   329  181  131   77     2    2    2      0.548620    658
P9     x10 F    547 195  0.02034  0.02017  14 187  88 137   0.1611 1 348 1134  750  454     8    6    4      0.637329    230
```

`scan` is the pipeline's own arrangement (the scan's normals at native spacing — the row that fails, and the
row that reproduces ticket 37: piece 2 1 906 regions / largest 46 against 1 765 / 45, piece 9 1 562 / 16 against
1 465 / 16; `scan37` re-grows ticket 37's own pre-floor clouds, 2 399 points at 0.22172 mm and 1 972 at
0.21069 mm, and returns the same 46 / 16). Arm `A` is analytic face normals as the pipeline writes them,
`F` the same normals flipped towards viewpoint (0,0,0) as PCL's `flipNormalTowardsViewpoint` does, `B` the
pipeline's own PCA re-estimation at `k=max(5,min(20,n/1000))` (k=6 at 6 259 points, k=20 at x4 and x10).

Controls (phase 2, pieces 3, 5, 7 — "always works" reference), arm A at native spacing, from `out/phase2.log`:

```
piece lvl arm  points   req mm   ach mm   regions  largest  share   ge50  fail_angle/pt  depth  cov2mm  fold deg
P3    x1  scan   3 493  0.21531  0.21531   2 400      350  0.1002     1        4.919      33   0.6304   0.466
P3    x1  A      9 613  0.21531  0.21612   2 548    3 383  0.3519     9        2.620      74   0.7547   2.086
P3    x2  A     39 605  0.10765  0.10684   5 656   14 327  0.3617    32        1.847     136   0.7681   2.283
P3    x4  A    161 173  0.05383  0.05339  10 618   59 840  0.3713   115        1.163     295   0.7893   2.402
P5    x1  scan   6 211  0.23858  0.23858   3 750      713  0.1148     3        4.558      41   0.3257   0.389
P5    x1  A     15 095  0.23858  0.23812   3 646    6 232  0.4129    16        2.608      96   0.5110   2.054
P5    x2  A     60 812  0.11929  0.11885   7 047   25 791  0.4241    77        1.761     153   0.5395   2.328
P5    x4  A    246 575  0.05964  0.05943  12 171  105 677  0.4286   163        1.062     364   0.5439   2.461
P7    x1  scan  17 698  0.25801  0.25801   4 169    6 809  0.3847    26        2.797     110   0.4897   2.259
P7    x1  A     17 698  0.25801  0.25464   4 169    6 809  0.3847    26        2.797     110   0.4897   2.259
P7    x2  A     71 219  0.12900  0.12807   7 994   30 515  0.4285    76        1.876     257   0.5313   2.757
P7    x4  A    287 814  0.06450  0.06390  13 665  125 923  0.4375   163        1.117     266   0.5389   2.970
```

(`P7 x1 scan` and `P7 x1 A` are the same row because at native spacing arm A grows on the scan's own cloud —
17 698 points, its vertex-spacing draw — so both lines repeat.)

## 5. Largest region against the ORIGINAL mesh

`extent` = diagonal of the largest region's axis-aligned box (mm); `cov2mm` = fraction of the ORIGINAL cloud's
points within 2 mm of the largest region; `fold` = median angle between the largest region's fitted plane and the
ORIGINAL mesh's normals.

```
piece  lvl arm   largest  share   extent mm  cov2mm  fold_med deg
P2     x1  A        873  0.1395   20.4757   0.4581   3.199
P2     x1  F        684  0.1093   17.0466   0.3559   2.882
P2     x1  scan      46  0.0179    8.3805   0.2047   0.431
P2     x1  scan37    45  0.0188    8.3219   0.2043   0.425
P2     x2  A      6 088  0.2412   24.2641   0.7290   3.554
P2     x2  F      4 709  0.1866   22.6128   0.6386   3.475
P2     x4  A     27 522  0.2694   27.6747   0.7201   3.611
P2     x4  B     39 947  0.3910   27.6278   0.7696   3.819
P2     x4  F     23 715  0.2321   25.9085   0.6203   3.643
P2     x10 A    190 064  0.2928   27.7416   0.7388   3.957
P2     x10 B    328 220  0.5057   27.8544   0.9041   4.721
P2     x10 F    163 518  0.2519   26.0343   0.6289   3.985
P9     x1  A      1 410  0.2682   18.7329   0.5564   2.851
P9     x1  F        739  0.1406   14.2299   0.3458   2.590
P9     x1  scan      16  0.0076    4.1089   0.0664   0.806
P9     x1  scan37    16  0.0081    4.1089   0.0664   0.806
P9     x2  A      6 012  0.2821   19.4471   0.5922   3.100
P9     x2  F      3 071  0.1441   14.2683   0.3500   2.828
P9     x4  A     25 021  0.2898   19.9611   0.6237   3.289
P9     x4  B     19 496  0.2258   20.5653   0.7335   3.437
P9     x4  F     13 156  0.1524   16.4024   0.4059   2.965
P9     x10 A    177 914  0.3251   21.9314   0.8486   4.564
P9     x10 B    264 761  0.4839   23.0099   0.9436   3.920
P9     x10 F     88 137  0.1611   17.2743   0.4126   3.229
```

## 6. Pair statistic, wherever two regions reach 50 points

**Corrected, and the earlier columns are VOID.** `measure34.pair_stats` took the absolute projection of the step
on Surface_0's normal and rebuilt the perpendicular part from that scalar, so wherever the step ran against the
normal the reported `across` came out as `sqrt(across^2 + 4t^2)` instead of the perpendicular residual — up to
twice `med_nn`. Fixed (signed `t`, `along = |t|`, `across = |v - t a|`), self-tested on a synthetic
anti-parallel pair (nn 2.2000 / along 2.2000 / across 0.0000) and a parallel one, and every row of
`results/pair38.tsv` re-derived from the regenerated regions — no `across` column was carried forward.
`med_nn`, `med_along`, `p90_along` and `coin` were correct as printed and are unchanged.

41 rows (pieces 2 and 9, controls 3, 5, 7, and Pot_A 07). `med_nn` = nearest Surface_0 point to each Surface_1
point; `med_along` = that step measured along Surface_0's own normal there; `med_across` = the part of the step
perpendicular to that normal (the residual, i.e. how far off-parallel the two sheets are);
`med_angle_deg` = folded angle between the two normals at that nearest point; `coin` = fraction coincident
within 1 micron; `min_slack` = the smallest per-point `nn - across` (0 = tangent). mm.

Arm A (analytic face normals) on the target pieces, every level (`results/pair38.tsv`):

```
piece lvl   |S0|     |S1|     med_nn   med_along  med_across  med_angle  min_slack  coin
P2    x1         873      722  2.18482   2.17139    0.16143    9.702     0.86414   0.0
P2    x2       6 088    3 427  2.15571   2.12676    0.08751   11.232     0.59549   0.0
P2    x4      27 522   26 983  2.28343   2.27144    0.04359   12.633     0.83401   0.0
P2    x10    190 064  184 688  2.28375   2.26684    0.02084   14.008     0.66736   0.0
P9    x1       1 410      277  2.18787   2.18016    0.11676   14.258     1.34433   0.0
P9    x2       6 012    2 292  2.19913   2.19262    0.06023   12.782     1.19270   0.0
P9    x4      25 021   21 353  2.19229   2.18326    0.03362   13.069     0.63319   0.0
P9    x10    177 914  166 389  2.12195   2.11247    0.03119   15.505     0.00820   0.0
PotA  x1      13 131   12 042  3.92787   3.92247    0.11657    4.172     1.36374   0.0   (scan37 row, its own cloud)
```

Arm B (the pipeline's own PCA normals at `pipeline_k`, with the viewpoint flip):

```
P2 x4  B   39 947 /  32 293   2.16853 / 2.01298 / 0.46441 / 27.724   slack 0.000003
P2 x10 B  328 220 / 254 407   0.97886 / 0.22576 / 0.66628 / 19.178
P9 x4  B   19 496 /  18 187   1.34053 / 0.43098 / 0.90630 / 35.695
P9 x10 B  264 761 / 235 216   1.04764 / 0.32650 / 0.53465 / 22.887
```

Controls (arm A at x1): P3 1.97199 / 1.96323 / 0.11448 / 9.803; P5 2.58583 / 2.58289 / 0.10108 / 12.348;
P7 3.35995 / 3.34192 / 0.15140 / 19.324. The `scan` rows on the shipped clouds: P5 (713 / 83)
4.32313 / 0.70142 / 4.26585 / 18.283 and P7 (1 040 / 112) 5.64742 / 1.16699 / 5.50842 / 22.078.

**Wall thickness from ticket 35's ray measurements: Juglet 2 = 2.693 mm, Juglet 9 = 2.595 mm, Pot A 07 =
4.056 mm.** Arm A's `med_along` on both target pieces sits at 2.11-2.29 mm with a perpendicular residual of
0.02-0.16 mm and 9.7-15.5 deg between the normals: the second-largest region is a sheet offset by roughly one
wall thickness and essentially parallel to the first. Arm B collapses `med_along` to 0.23-0.43 mm while the
residual rises to 0.47-0.91 mm — not a parallel offset. On the shipped-cloud `scan` rows of P5 and P7 the step is
mostly perpendicular (along 0.70 and 1.17 mm against `nn` 4.32 and 5.65 mm). No pair anywhere is coincident at
1 micron (coin 0.000000 on all 41 rows), and `nn - across` never goes negative.

## 7. The real pipeline cells

Five cells were planned for the last job (33892259, run `20261028-0414_2a34d86`); **three ran**. Each staged its
cloud inside the run directory, built the pipeline's own binary from commit `2a34d86`, ran it with
`SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10`, and counted its geometry before
deleting it.

```
cell                  cloud                                  points   median mm  clusters  outcome   |S0|    |S1|
Juglet_Piece_2  x1    SYNTHETIC (uniform covering)            6 259   0.20904       8       two    4 155   3 979
Juglet_Piece_9  x1    SYNTHETIC (uniform covering)            5 257   0.20151       7       two    2 229   3 512
Pot_A_Piece_07  real  the released cloud (1 000 000 points)  34 608   0.12307       7       two   24 636  26 741
```

The pipeline's own lines (`results/cells-pipeline/<cell>/logs/lines38.log` in the run directory):

```
Juglet_Piece_2   [SPACING-22] policy=piece diagMM=28.2305 s0MM=0.209045 samples=200 rawMM=0.141153 S=0.209045
                 Number of clusters is equal to 8
                 [RETRY-23] retry=1 npts=6259 clusters_pre=8 clusters=4 sizes=1684,1620,62,52 minCluster=50
                 [STATUS-23] outcome=two retries=1 clusters=4 sizes=1684,1620,62,52 npts=6259 floor=50
                             floor_from=50 capped=no surf0_points=4155 surf1_points=3979 reason=two surfaces written
Juglet_Piece_9   [SPACING-22] policy=piece diagMM=23.3454 s0MM=0.201486 samples=200 rawMM=0.116727 S=0.201486
                 Number of clusters is equal to 7
                 [RETRY-23] retry=1 npts=5256 clusters_pre=7 clusters=6 sizes=589,1497,327,166,158,89 minCluster=50
                 [STATUS-23] outcome=two retries=1 clusters=6 sizes=589,1497,327,166,158,89 npts=5256 floor=50
                             floor_from=50 capped=no surf0_points=2229 surf1_points=3512 reason=two surfaces written
Pot_A_Piece_07   [SPACING-22] policy=piece diagMM=58.5761 s0MM=0.021169 samples=200 rawMM=0.292881 S=0.292881
                 Number of clusters is equal to 7
                 [RETRY-23] retry=1 npts=34608 clusters_pre=7 clusters=7 sizes=11815,12888,2722,1059,1018,234,216
                             minCluster=69 minClusterFrom=69
                 [STATUS-23] outcome=two retries=1 clusters=7 sizes=11815,12888,2722,1059,1018,234,216 npts=34608
                             floor=69 floor_from=69 capped=no surf0_points=24636 surf1_points=26741 reason=two surfaces written
```

Rung-2 (pre-merge) dumps: P2 9 clusters largest 2 841 `[2841,1549,1212,264,144,74,62,61,52]`; P9 8 clusters
largest 2 430 `[2430,1497,538,327,166,158,89,51]`; Pot_A 8 clusters largest 12 888
`[12888,11815,4656,2722,1059,1018,234,216]`. SampledWithNormals spacing after the pipeline's own downsampling:
0.20892 / 0.20154 / 0.12307 mm (Pot_A: the pipeline cut the 1 000 000-point release to 34 608 points).

**The per-surface measurement did not run in any of the three.** `run_cell38.sh` picked the surface file with
`for ext in ply xyz; do [ -f ... ] && F=...; done`, which keeps the LAST existing extension; the pipeline writes
both `<piece>_Surface_<k>.ply` and `<piece>_Surface_<k>.xyz`
(`.scratch/pota-repro/ticket278_files/mesh_processing_headless.cpp:2197-2211`), so `F` ended on the `.xyz` and
the measurement was skipped:

```
[PIPELINE] surface 0 is xyz, not a ply: cannot measure normals, kept as written
```

Fixed after the run (prefer `.ply`) and **not exercised**. So the pipeline's own `surf0_points` / `surf1_points`
are reported above, but extent, 2 mm coverage of the ORIGINAL cloud and folded angle to the ORIGINAL mesh for
those two written surfaces do not exist.

**Both x10 cells are missing.** Juglet_Piece_2 x10 sampled inside the job (649 067 points at 0.02080 mm, 153.2 s,
md5 `ce37ceaf6cea4f70489e9202ba86e435`), staged, and its pipeline was started; the job hit its 40-minute wall
during it (`sacct`: 33892259 TIMEOUT 00:40:11). Juglet_Piece_9 x10 never started. The driver's wall-clock guard
did not protect them: `squeue -h -j $JOBID -o %L` answered with a day-scale counter from inside the step
(89 572 / 89 328 / 89 084 / 88 474 s at the four cell boundaries), never below `MIN_LEFT_S=420`, so no cell was
skipped. Item 7 asked for the finest level that reaches 50 points — that is x10, and it is not delivered; x1 is
the coarsest level that clears the floor and is what ran.

## 8. Part E redraws — fractions measured from the new PNGs

Two renders per piece: a replay of the ticket-37 drawing (`*_t37style_replay.png`, through the same instrument
path) to show the measurement reproduces ticket 37's numbers, and the redraw (`*_partE_ranked_fullopacity.png`,
tail at full opacity, marker one step larger, continuous rank palette). Ink = fraction of panel pixels with any
channel < 245; grey = ink pixels whose channel spread is <= 12; colour = ink pixels with a wider spread.
Whole-panel box for the replay, axes-box panels for the redraw.

```
piece            render              ink (panels)              grey_share_of_ink  colour (panels)
Juglet_Piece_9   replay (t37 style)  0.0898                    0.8267             0.0156
Juglet_Piece_9   redraw              0.1849 0.2795 0.3778      0.0937 (mean)      0.1640 0.2579 0.3436
Pot_A_Piece_07   replay (t37 style)  0.1265                    0.2859             0.0904
Pot_A_Piece_07   redraw              0.3330 0.2495 0.2632      0.0560 (mean)      0.3206 0.2371 0.2418
```

Ticket 37's own figure measured 10.6 / 13.9 / 16.0 % ink with 82-83 % pale grey on piece 9, and 17.5 / 14.0 /
12.5 % with 26-31 % on Pot A 07. The replay lands at 9.0 % ink / 82.7 % grey on piece 9 and 12.7 % / 28.6 % on
Pot A 07. On the redraw the pale-grey share of ink drops from 0.83 to 0.09 (piece 9) and from 0.29 to 0.06
(Pot A 07); the plot-interior variant gives the same picture (piece 9 mean ink 0.2727, grey share 0.0292;
Pot A 07 0.2769, 0.0170). PNG sizes: piece 9 replay 195 664 B, redraw 212 477 B; Pot A 07 replay 371 084 B,
redraw 431 964 B.

## 9. Corpus, pristine, deletion, jobs, branch

- **Corpus and frozen inputs unchanged in both closed runs**: `out/corpus.diff` 0 bytes, `out/inputs.diff` 0
  bytes, 215 md5 rows in `out/inputs_before.md5` and 215 in `out/inputs_after.md5`.
- **`/opt/sfs-pristine`: ABSENT** on the compute node, recorded in `out/pristine.txt` (197 B; not created).
- **Geometry deleted, counted first.** Run 5 (`out/geometry_counts_phase1-2-3.tsv`, then
  `out/GEOMETRY_DELETED_phase1-2-3.txt`):

  ```
  ext   files  bytes
  obj       3  1 407 940
  pcd      22  183 320 145
  ply     108  889 808 135
  xyz       9  83 627 271
  TOTAL   142  1 158 163 491      after deletion: 0 files (out/ 6.0 MB of tables, logs, jsons)
  ```

  Run 4 (`20261027-1615_92d6871`) had recorded 112 files / 672 680 485 B (obj 2 / 1 248 259, pcd 20 /
  143 952 030, ply 90 / 527 480 196) and the aborted first run 401 files / 103 262 155 B; both deleted.
  Tables, logs, sources and figures survive; the PLY/PCD/OBJ geometry does not.
- **Run 5 was closed by hand** (the batch script was killed mid phase 3 and never reached its own closing block:
  bash defers a `trap` until the foreground child returns and Slurm's 15 s kill window cut it off first). The
  `corpus_tree`/`pristine_record`/`md5_corpus`/`geom_record`/`geom_delete` function bodies were lifted verbatim
  out of that run's own `submit.sbatch` and executed on the login node — bookkeeping only, no compute — and
  `out/CLOSED-BY-HAND.txt`, `out/run-meta_phase1-2-3.txt` (`phase_rc=timeout`, `closed_by=hand`) and the index
  row were written.
- **Jobs and states** (`sacct -X`):

  ```
  33888878  t38-targets  FAILED   00:00:18  ExitCode 7:0   2026-10-28T02:38:54 -> 02:39:12
  33889190  t38-targets  FAILED   00:00:11  ExitCode 7:0   2026-10-28T02:47:38 -> 02:47:49
  33889547  t38-targets  FAILED   00:00:14  ExitCode 7:0   2026-10-28T02:55:52 -> 02:56:06
  33890365  t38-all      FAILED   00:15:16  ExitCode 1:0   2026-10-28T03:15:30 -> 03:30:46
  33892259  t38-cell5    TIMEOUT  00:40:11  ExitCode 0:15   2026-10-28T04:15:12 -> 04:55:23
  ```

  Budget: 5 of 5 used (the fifth was authorised as the last). Index rows appended for every run with `verdict`
  and `human_note` left empty; the last is
  `20261028-0414_2a34d86_t38-resolution<TAB>33892259<TAB>2a34d86a54467ac1f0238eed214bc11bdf7be208<TAB>t38-resolution<TAB><TAB>`.
- **Branch** `38-does-more-resolution-give-the-silent-sherds-a-face`, pushed; the head this report is built on is
  `2a34d86a54467ac1f0238eed214bc11bdf7be208` (the commit that built run 5's binary and the instruments it ran),
  with this report's own commit on top.

## 10. Not done, with the exact failing command

1. **Item 7 at the finest floor-clearing level (x10)** — the pipeline was started on the P2 x10 cloud and killed by
   the wall clock; P9 x10 never started. `logs/slurm-33892259.err`:
   `error: *** JOB 33892259 ON spartan-bm149 CANCELLED AT 2026-10-25T04:55:23 DUE TO TIME LIMIT ***`.
   The guard meant to prevent this read a day-scale counter (`[PIPELINE] wall clock left: 88474s`) and never
   skipped a cell.
2. **Per-surface extent / 2 mm coverage / folded angle for the three cells that ran** — skipped by the extension
   loop quoted in item 7. The fix is in `run_cell38.sh` (prefer `.ply`) and was not exercised (no job left).
3. **Item 3's exact displacement** — not implemented. The run measured the incident-candidate value
   (1.809-1.815 mm on piece 2, 1.125-1.150 mm on piece 9), which section 3 shows is an artefact of candidate-triangle
   selection, not displacement; the analytic bound is <= 1e-6 mm. The exact figure needs `subdivide` /
   `subdivide_lattice` to return each new vertex's parent face.
4. **`cloud_points` is blank for the Pot_A cell** in `results/cells-pipeline/pipeline_cells.tsv`:
   `pcd_points() { grep -m1 "^POINTS" "$1" | awk '{print $2}'; }` and GNU grep answers `Binary file ... matches`
   for a binary PCD (reproduced: `grep -m1 "^POINTS" b.pcd` -> `Binary file b.pcd matches`, awk field `file`).
   The header reads `POINTS 1000000` (`head -c 320 ... | strings`) and the pipeline's own line says
   `npts=34608`; the released cloud is 1 000 000 points, 28 000 229 B, `DATA binary`.
5. **No sixth job**: budget spent, the fifth ran to TIMEOUT.
6. **The ladder plots show arm A only** (`arm=A` in the PNG); arms B and F exist in the tables but not in a figure.
7. **The phase-1/2 numbers in sections 1-5 come from run 4** (`20261027-1615_92d6871`), not run 5. Run 5 repeated
   phase 1 and 2 and reproduced them (anchors 1 765 / 1 906 regions and 1 465 / 1 562; `floor_reached_at` now the
   coarsest clearing level, x1 = 873 and 1 410 points), but the tables quoted in sections 1-5 were not re-copied
   from run 5's `out/` where they agree and were re-rendered where they did not (the two PNGs and
   `figure_*.json` in `results/` are run 5's).

## Where the surviving numbers live

```
stage38/results/regions38.tsv                    run 5: one row per (piece, level, arm), item 4's columns, 46 rows
stage38/results/largest38.tsv                    run 5: item 5's columns + ext_x/y/z, diag, fold, normal source
stage38/results/pair38.tsv                       run 5: item 6, corrected, 41 rows
stage38/results/pair38_NOTE.txt                  run 5: what each pair column means, and the VOID declaration
stage38/results/ticket37_compare.json            the ticket-37 anchor comparison
stage38/results/figure_Juglet_Piece_{2,9}.json   run 5: the figure's own record (mm/px, sizes, rows, floor_reached_at)
stage38/results/Juglet_Piece_{2,9}_resolution_by_density.png        run 5 figures (label and floor fixes applied)
stage38/results/Juglet_Piece_9_{partE_ranked_fullopacity,t37style_replay}.png   item 8, piece 9
stage38/results/Pot_A_Piece_07_{partE_ranked_fullopacity,t37style_replay}.png   item 8, Pot A 07
stage38/results/cells-pipeline/                  item 7: pipeline_cells.tsv + each cell's cell.tsv, measure jsons, logs
stage38/results/sample_*.json, subdiv_*.json     run 5: achieved spacing per (piece, level), subdivision counts
stage38/results/sampler_validate_*.json          run 5: the sampler proof, five pieces
stage38/results/SAMPLER-GATE-DISCLOSURE_*.txt    item 1 in long form
stage38/results/geometry_counts_phase1-2-3.tsv   item 9's counts (run 5)
stage38/results/GEOMETRY_DELETED_phase1-2-3.txt  the deletion record written before the delete
stage38/results/run5_CLOSED-BY-HAND.txt          why run 5's record was closed by hand, and how
stage38/results/run5_meta.txt                    run 5's own run-meta line
stage38/run-20261028-0414_2a34d86/               the whole run-5 record: out/, run.json, submit.sbatch, instruments/, logs/
stage38/run-20261027-1615_92d6871/               the run-4 record, kept: every per-cell json, phase logs, md5s
stage38/instruments/                             the sources (md5 equal to the run directories' copies)
```
