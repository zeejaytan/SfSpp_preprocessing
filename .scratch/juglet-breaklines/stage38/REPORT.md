# Ticket 38 — does more resolution give the silent sherds a face?

Numbers only, from the runs; no verdict on what they mean (the ticket's Status and `intent/` are untouched).

Run of record: `/data/gpfs/projects/punim2657/SfSpp/runs/20261027-1615_92d6871_t38-resolution/`
(job 33890365, commit `92d6871022fdf75f63170a5af65b30e31c9e843a`, built on `spartan-bm174.hpc.unimelb.edu.au`,
`[JOB] instruments match commit 92d6871022fdf75f63170a5af65b30e31c9e843a (12 files)`).
Everything below that survived is copied into `stage38/results/` and `stage38/run-20261027-1615_92d6871/`;
the geometry those runs made was deleted on the cluster with counts recorded first (item 9).

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

20 of 24 (piece, level, arm) cells have two regions at or over 50 — the exceptions are the four `scan`/`scan37`
rows, where nothing reaches 50. `med_nn` = nearest distance from each Surface_1 (second) point to Surface_0;
`along` = that displacement projected on Surface_0's normal at the nearest point; `across` = the component
perpendicular to it; `coin` = fraction of pairs coincident within 1 micron. mm.

```
piece lvl arm  |S0|    |S1|    med_nn   med_along  p90_along  med_across  p90_across  coin
P2    x1  A      873     722   2.18482   2.17138    2.51699    4.35093     5.07731   0.0000
P2    x1  F      684     653   2.57304   2.42535    3.45468    4.98169     9.18776   0.0000
P2    x2  A    6 088   3 427   2.15570   2.12676    2.39685    4.26837     4.79501   0.0000
P2    x2  F    4 709   3 242   2.25157   2.14841    2.51854    0.14264     1.24151   0.0000
P2    x4  A   27 522  26 983   2.28343   2.27144    2.56101    4.54712     5.15222   0.0000
P2    x4  B   39 947  32 293   2.16853   2.01298    2.55516    4.10249     5.11719   0.0000
P2    x4  F   23 715  20 883   2.31313   2.27768    2.61413    4.57646     5.30181   0.0000
P2    x10 A  190 064 184 688   2.28374   2.26684    2.56496    4.54278     5.14802   0.0000
P2    x10 B  328 220 254 407   0.97885   0.22575    1.44159    1.16185     3.07841   0.0000
P2    x10 F  163 518 112 518   2.37570   2.33978    2.68854    4.70318     5.42948   0.0000
P9    x1  A    1 410     277   2.18787   2.18015    2.42220    4.36254     4.84646   0.0000
P9    x1  F      739     586   2.24925   0.15532    0.59881    2.29572     4.08046   0.0000
P9    x2  A    6 012   2 292   2.19913   2.19262    2.41400    4.39219     4.82942   0.0000
P9    x2  F    3 071   2 643   2.32267   0.18012    0.63482    2.36218     4.22026   0.0000
P9    x4  A   25 021  21 353   2.19229   2.18326    2.43032    4.37702     4.89180   0.0000
P9    x4  B   19 496  18 187   1.34052   0.43098    1.51816    1.80290     3.61994   0.0000
P9    x4  F   13 156  10 511   2.06784   0.14175    0.46648    2.08544     3.87292   0.0000
P9    x10 A  177 914 166 389   2.12194   2.11246    2.34059    4.22991     4.68368   0.0000
P9    x10 B  264 761 235 216   1.04764   0.32650    2.16710    1.36003     4.34780   0.0000
P9    x10 F   88 137  74 293   1.95841   0.13561    0.50367    1.97098     3.93734   0.0000
```

**No pair is coincident at 1 micron anywhere** (coin 0.0000 in all 20 rows). On arm A the two largest regions sit
4.23-4.58 mm apart *across* Surface_0's normal and 2.11-2.28 mm *along* it at every level and on both pieces —
i.e. on the two faces of the wall, not on a duplicate of one face.

## 7. The real pipeline cell — NOT RUN

No level was attempted: phase 3 died before it started.

```
out/phase3.log:
/data/gpfs/projects/punim2657/SfSpp/runs/20261027-1615_92d6871_t38-resolution/build/src/.scratch/juglet-breaklines/stage38/instruments/run_cell38.sh: line 15: STAGER: parameter null or not set
```

The driver requires `STAGER` (the synthetic staging script) and `submit38.sbatch.tmpl` never exported it; the
job's own log says `[JOB] WARN phase 3 driver failed rc=1 (see out/phase3.log); continuing`. Fixed after the run
(`STAGER=$INSTR/stage_synth_p38.sh` + `export ... STAGER`), **not exercised**.

Every level that reaches the 50-point floor is known from item 4 — piece 2: x1 already (873 points), so the
"finest level that reaches 50" is any level; piece 9: x1 (1 410). The ticket's intent (run the pipeline where the
floor is first met) therefore points at **x1** for both pieces, not x10 — but the cell was specified at the finest
level and x10 is also floor-clearing, so either is available for the next job.

## 8. Part E redraws — NOT RUN

Phase 2 aborted at the Pot_A anchor, before `parte38.py`, so neither redraw exists and no ink/grey/colour fraction
was measured on a new PNG.

```
out/phase2.log:
  File ".../instruments/grow38.py", line 94, in cmd_cell
    orig_xyz, _orig_n = S.read_pcd_xyz(a.orig_cloud)
  File ".../instruments/mesh38.py", line 342, in read_pcd_xyz
    raise ValueError("%s: only ascii clouds here" % path)
ValueError: /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Point/Pot_A/Pot_A_Piece_07_Point.pcd: only ascii clouds here
```

`mesh38.read_pcd_xyz` refused the released Pot A cloud because it is binary, not text. Fixed after the run (a
binary body is handed to `measure34.read_pcd`, which parses both layouts) and **not exercised**. The pieces 3/5/7
controls above ran in the same phase before the anchor and are valid.

## 9. Corpus, pristine, deletion, jobs, branch

- **Corpus and frozen inputs unchanged**: `out/corpus.diff` 0 bytes and `out/inputs.diff` 0 bytes; 215 md5 rows in
  `out/inputs_before.md5` and 215 in `out/inputs_after.md5`; the job's own line `[JOB] corpus and frozen inputs unchanged`.
- **`/opt/sfs-pristine`: ABSENT** on the compute node, recorded in `out/pristine.txt` (not created).
- **Geometry deleted, counted first** (`out/geometry_counts_phase1-2-3.tsv`, then
  `out/GEOMETRY_DELETED_phase1-2-3.txt`):

  ```
  ext   files  bytes
  obj       2  1 248 259
  pcd      20  143 952 030
  ply      90  527 480 196
  TOTAL   112  672 680 485     after deletion: 0 files
  ```

  The first, aborted run (`20261027-1538_55477bf`) recorded 401 files / 103 262 155 bytes (pcd 99 / xyz 300 / ply 1)
  and deleted them too. Tables, logs, sources, figures and the PLYs' numbers survive; the PLYs themselves do not.
- **Jobs and states** (`sacct -X`):

  ```
  33888878  t38-targets  FAILED  00:00:18  ExitCode 7:0   2026-10-28T02:38:54 -> 02:39:12
  33889190  t38-targets  FAILED  00:00:11  ExitCode 7:0   2026-10-28T02:47:38 -> 02:47:49
  33889547  t38-targets  FAILED  00:00:14  ExitCode 7:0   2026-10-28T02:55:52 -> 02:56:06
  33890365  t38-all      FAILED  00:15:16  ExitCode 1:0   2026-10-28T03:15:30 -> 03:30:46
  ```

  Budget: 4 of 4 used. Index rows appended for each run with `verdict` and `human_note` left empty; the last row is
  `20261027-1615_92d6871_t38-resolution<TAB>33890365<TAB>92d6871022fdf75f63170a5af65b30e31c9e843a<TAB>t38-resolution<TAB><TAB>`.

## 10. Not done, with the exact failing command

1. **Item 7 (the real pipeline cell)** — not run.
   `out/phase3.log: .../run_cell38.sh: line 15: STAGER: parameter null or not set`.
2. **Item 8 (Part E redraws + measured ink/grey/colour)** — not run.
   `ValueError: .../Pot_A_Piece_07_Point.pcd: only ascii clouds here` (grow38.py:94 -> mesh38.py:342).
3. **Item 3's exact displacement** — the run measured the incident-candidate value (1.809-1.815 mm on piece 2,
   1.125-1.150 mm on piece 9), which item 3 above shows is an artefact, not displacement. The exact measurement
   needs `subdivide`/`subdivide_lattice` to return each new vertex's parent face and the distance to be taken
   against that one triangle. Not implemented; the analytic value is <= 1e-6 mm.
4. **The delivered figures carry two defects** (`results/*.png`), both fixed in the instrument after the run and
   **not re-rendered** (denied the job budget):
   - the per-row label block overprints the first panel's y tick labels (real tick labels are 6 characters wide
     against the toy's 2; `wspace` 0.22 -> 0.62, label column 0.17 -> 0.21, label x 0.98 -> 0.94);
   - the ladder title said `largest region reaches the floor at x10` when the floor is cleared at the **coarsest**
     level (`floor_reached_at` kept the level with the biggest region instead of the coarsest level that clears
     the floor; piece 2 x1 = 873 points, piece 9 x1 = 1 410). `figure_*.json` in `results/` inherits the wrong
     `floor_reached_at` field for that reason.
5. **The phase-2 aggregate and the controls' tables** never ran, so `regions38.tsv`/`largest38.tsv` cover pieces 2
   and 9 only; pieces 3, 5, 7 exist as `[CELL]` lines in `out/phase2.log` and as jsons under `out/cells/`.
6. **The figure ladder plots arm A only** (`arm=A` chosen for the PNG); arms F and B exist in the tables but not in
   a picture.

## Where the surviving numbers live

```
stage38/results/regions38.tsv                    one row per (piece, level, arm): item 4's columns
stage38/results/largest38.tsv                    item 5's columns + ext_x/y/z, diag, fold, normal source
stage38/results/pair38.tsv                       item 6, 20 rows
stage38/results/ticket37_compare.json            the ticket-37 anchor comparison
stage38/results/figure_Juglet_Piece_{2,9}.json   the figure's own record (mm/px, sizes, rows, floor_reached_at)
stage38/results/Juglet_Piece_{2,9}_resolution_by_density.png   the two figures (defects in item 10.4)
stage38/results/SAMPLER-GATE-DISCLOSURE_*.txt    item 1 in long form
stage38/results/geometry_counts_phase1-2-3.tsv   item 9's counts
stage38/results/GEOMETRY_DELETED_phase1-2-3.txt  the deletion record written before the delete
stage38/results/phase_failures.tsv               phase -> rc (2->6, 3->1)
stage38/run-20261027-1615_92d6871/out/*.json     every per-cell json, phase logs, corpus/inputs md5, run meta
stage38/run-20261027-1615_92d6871/instruments/   the exact bytes the job ran (md5 equal to commit 92d6871)
```
