# Ticket 36 — adaptive spacing with the honest normals: evidence from the two jobs

Evidence only. No verdict, no interpretation — the lead judges. Every number below was read out of the
run directories named in section 1; the same tables are committed beside this file in `results/`.

## 1. Jobs and run directories

| # | run directory | job id | state | elapsed | node | cells | valid for the ticket |
|---|---|---|---|---|---|---|---|
| 1 | `/data/gpfs/projects/punim2657/SfSpp/runs/20261028-0004_fe5b17f_t36-adaptive-spacing` | 33880164 | COMPLETED, ExitCode 0:0 | 00:03:26 | spartan-bm076 | 70/70 | **no** — arms B and C ran with empty switch strings (§2) |
| 2 | `/data/gpfs/projects/punim2657/SfSpp/runs/20261028-0013_0a53dee_t36-adaptive-spacing-r2` | 33880555 | COMPLETED, ExitCode 0:0 | 00:03:59 | spartan-bm174 | 70/70 | yes — this is the grid |

Both run dirs hold `run.json`, `submit.sbatch`, `logs/`, `out/`; run 2 additionally holds `instruments/` (9 files,
proved LF by `out/instruments_lf.md5`). Sizes: run 2 497M, run 1 444M. Job budget: two allowed, two used.
Walltime requested 01:30:00; `--partition=sapphire --cpus-per-task=8 --mem=64G --nodes=1 --ntasks=1`.

## 2. The switches that actually ran (out/ARMCHECK.txt, run 2)

    # ticket 36 arm check -- read from each arm's own per-piece mesh logs
    # arm cells spacing_piece normal_set single_write verdict
    A 14 0/0 0/0 0/0 ok
    A2 14 0/0 0/0 0/0 ok
    B 14 14/14 0/0 0/0 ok
    C 14 14/14 14/14 0/0 ok
    D 14 14/14 14/14 14/14 ok
    # the pipeline's own first line of each kind, arm by arm
    # A [SPACING-22] policy=fixed S=0.6
    # A normalSource=reestimate normalSourceSet=no minPairs=3
    # A [SWITCH-23] singleCluster=off floorCeiling=off countScaleAuto=no
    # A2 [SPACING-22] policy=fixed S=0.6
    # A2 normalSource=reestimate normalSourceSet=no minPairs=3
    # A2 [SWITCH-23] singleCluster=off floorCeiling=off countScaleAuto=no
    # B [SPACING-22] policy=piece diagMM=63.0542 s0MM=0.338049 samples=200 rawMM=0.315271 S=0.338049
    # B normalSource=reestimate normalSourceSet=no minPairs=3
    # B [SWITCH-23] singleCluster=off floorCeiling=off countScaleAuto=no
    # C [SPACING-22] policy=piece diagMM=63.0542 s0MM=0.338049 samples=200 rawMM=0.315271 S=0.338049
    # C normalSource=input normalSourceSet=yes minPairs=3
    # C [SWITCH-23] singleCluster=off floorCeiling=off countScaleAuto=no
    # D [SPACING-22] policy=piece diagMM=63.0542 s0MM=0.338049 samples=200 rawMM=0.315271 S=0.338049
    # D normalSource=input normalSourceSet=yes minPairs=3
    # D [SWITCH-23] singleCluster=write floorCeiling=off countScaleAuto=no

Job 1's defect, in its own cells: every arm B and C `logs/mesh.log` carried `[SPACING-22] policy=fixed S=0.6`
and `normalSourceSet=no`; the `envs` column of run 1's `out/cells36.tsv` reads `none` for B and a single space for C.
Cause: `SPACING=`/`CARRY=` were unexported shell variables referenced inside `export -f run_cell_one`.
Fixed in commit 0a53dee by writing the switch strings literally; run 1's run dir records this in
`NOTE-arms-B-and-C-ran-as-A.md`.

## 3. Every cell: sampling step, points into clustering, clusters, floor, outcome

`S` is the step from `[SPACING-22] ... S=`, `npts` the points entering clustering, `pre->post` the cluster count
before and after merge, `floor(from)` the `[STATUS-23]` floor and its source, `s0pts`/`s1pts` the exported surface
point counts (`-1` = no such surface). `SFS_COUNT_SCALE` was unset in all 70 cells.

| arm | piece | S mm | npts | pre->post | cluster sizes after merge | floor(from) | capped | outcome | s0pts | s1pts |
|---|---|---|---|---|---|---|---|---|---|---|
| A | J1 | 0.6 | 14546 | 22->18 | 626,3489,429,411,349,284,228,143,106,103,86,84,81,80,58,57,53,50 | 50(50) | no | two | 3580 | 12092 |
| A | J2 | 0.6 | 1031 | 0->0 | none | 50(50) | no | none | -1 | -1 |
| A | J3 | 0.6 | 1467 | 2->1 | 268 | 50(50) | no | none | -1 | -1 |
| A | J5 | 0.6 | 3021 | 1->1 | 679 | 50(50) | no | none | -1 | -1 |
| A | J7 | 0.6 | 4254 | 5->4 | 403,263,68,65 | 50(50) | no | two | 1012 | 829 |
| A | J9 | 0.6 | 787 | 0->0 | none | 50(50) | no | none | -1 | -1 |
| A | A01 | 0.6 | 85136 | 12->11 | 32775,27551,3803,3375,900,815,730,570,379,285,173 | 170(170) | no | two | 66760 | 57287 |
| A | A02 | 0.6 | 49528 | 5->3 | 20628,22543,1183 | 99(99) | no | two | 42197 | 46324 |
| A | A03 | 0.6 | 46784 | 5->4 | 19382,21172,929,156 | 93(93) | no | two | 39771 | 43572 |
| A | A04 | 0.6 | 38901 | 5->5 | 15932,17374,770,164,124 | 77(77) | no | two | 32683 | 35790 |
| A | A05 | 0.6 | 38074 | 5->5 | 15256,16570,588,304,281 | 76(76) | no | two | 31576 | 34136 |
| A | A06 | 0.6 | 27944 | 6->6 | 10739,11984,195,140,117,76 | 55(55) | no | two | 22575 | 24919 |
| A | A07 | 0.6 | 8598 | 8->7 | 2850,3093,203,191,170,144,73 | 50(50) | no | two | 6066 | 6437 |
| A | A08 | 0.6 | 7682 | 5->4 | 2611,2832,284,265 | 50(50) | no | two | 5528 | 6097 |
| A2 | J1 | 0.6 | 14546 | 22->18 | 626,3489,429,411,349,284,228,143,106,103,86,84,81,80,58,57,53,50 | 50(50) | no | two | 3580 | 12092 |
| A2 | J2 | 0.6 | 1031 | 0->0 | none | 50(50) | no | none | -1 | -1 |
| A2 | J3 | 0.6 | 1467 | 2->1 | 268 | 50(50) | no | none | -1 | -1 |
| A2 | J5 | 0.6 | 3021 | 1->1 | 679 | 50(50) | no | none | -1 | -1 |
| A2 | J7 | 0.6 | 4254 | 5->4 | 403,263,68,65 | 50(50) | no | two | 1012 | 829 |
| A2 | J9 | 0.6 | 787 | 0->0 | none | 50(50) | no | none | -1 | -1 |
| A2 | A01 | 0.6 | 85136 | 12->11 | 32775,27551,3803,3375,900,815,730,570,379,285,173 | 170(170) | no | two | 66762 | 57287 |
| A2 | A02 | 0.6 | 49528 | 5->3 | 20628,22543,1183 | 99(99) | no | two | 42202 | 46324 |
| A2 | A03 | 0.6 | 46784 | 5->4 | 19382,21172,929,156 | 93(93) | no | two | 39774 | 43576 |
| A2 | A04 | 0.6 | 38901 | 5->5 | 15932,17374,770,164,124 | 77(77) | no | two | 32683 | 35790 |
| A2 | A05 | 0.6 | 38074 | 5->5 | 15256,16570,588,304,281 | 76(76) | no | two | 31574 | 34138 |
| A2 | A06 | 0.6 | 27944 | 6->6 | 10739,11984,195,140,117,76 | 55(55) | no | two | 22574 | 24919 |
| A2 | A07 | 0.6 | 8598 | 8->7 | 2850,3093,203,191,170,144,73 | 50(50) | no | two | 6066 | 6437 |
| A2 | A08 | 0.6 | 7682 | 5->4 | 2611,2832,284,265 | 50(50) | no | two | 5528 | 6097 |
| B | J1 | 0.338 | 23077 | 13->7 | 4812,9032,752,373,338,205,59 | 50(50) | no | two | 10800 | 15780 |
| B | J2 | 0.211 | 2397 | 0->0 | none | 50(50) | no | none | -1 | -1 |
| B | J3 | 0.215 | 3252 | 1->1 | 289 | 50(50) | no | none | -1 | -1 |
| B | J5 | 0.239 | 5668 | 3->2 | 51,740 | 50(50) | no | two | 229 | 2317 |
| B | J7 | 0.258 | 7471 | 5->4 | 609,648,93,57 | 50(50) | no | two | 1753 | 1997 |
| B | J9 | 0.203 | 1971 | 0->0 | none | 50(50) | no | none | -1 | -1 |
| B | A01 | 0.600 | 85136 | 12->11 | 32775,27551,3803,3375,900,815,730,570,379,285,173 | 170(170) | no | two | 66763 | 57297 |
| B | A02 | 0.600 | 49528 | 5->3 | 20628,22543,1183 | 99(99) | no | two | 42201 | 46334 |
| B | A03 | 0.600 | 46784 | 5->4 | 19382,21172,929,156 | 93(93) | no | two | 39777 | 43575 |
| B | A04 | 0.582 | 41296 | 5->5 | 16955,18456,857,205,147 | 82(82) | no | two | 34731 | 38007 |
| B | A05 | 0.600 | 38074 | 5->5 | 15256,16570,588,304,281 | 76(76) | no | two | 31576 | 34140 |
| B | A06 | 0.600 | 27944 | 6->6 | 10739,11984,195,140,117,76 | 55(55) | no | two | 22573 | 24919 |
| B | A07 | 0.293 | 34608 | 7->7 | 11815,12888,2722,1059,1018,234,216 | 69(69) | no | two | 24637 | 26740 |
| B | A08 | 0.270 | 36097 | 7->7 | 12817,14141,1899,1499,222,106,97 | 72(72) | no | two | 26777 | 29285 |
| C | J1 | 0.338 | 23077 | 26->14 | 2254,5864,1328,655,607,540,499,80,77,76,58,55,51,50 | 50(50) | no | two | 8026 | 13532 |
| C | J2 | 0.211 | 2399 | 0->0 | none | 50(50) | no | none | -1 | -1 |
| C | J3 | 0.215 | 3253 | 1->1 | 350 | 50(50) | no | none | -1 | -1 |
| C | J5 | 0.239 | 5668 | 3->3 | 84,716,64 | 50(50) | no | two | 320 | 2178 |
| C | J7 | 0.258 | 7471 | 5->5 | 136,1035,88,85,82 | 50(50) | no | two | 564 | 3219 |
| C | J9 | 0.203 | 1972 | 0->0 | none | 50(50) | no | none | -1 | -1 |
| C | A01 | 0.600 | 85136 | 11->11 | 32206,28179,3743,3401,891,757,486,336,304,291,240 | 170(170) | no | two | 66265 | 58048 |
| C | A02 | 0.600 | 49528 | 7->6 | 20705,22696,686,385,245,184 | 99(99) | no | two | 42263 | 46490 |
| C | A03 | 0.600 | 46784 | 5->5 | 19526,21518,916,135,128 | 93(93) | no | two | 39988 | 43936 |
| C | A04 | 0.582 | 41296 | 9->7 | 17251,18904,575,516,251,240,120 | 82(82) | no | two | 35030 | 38547 |
| C | A05 | 0.600 | 38074 | 7->6 | 15594,17028,713,462,429,129 | 76(76) | no | two | 32003 | 34636 |
| C | A06 | 0.600 | 27944 | 9->7 | 11196,12418,393,316,219,104,62 | 55(55) | no | two | 23118 | 25463 |
| C | A07 | 0.293 | 34608 | 10->8 | 12042,13131,2870,1127,1052,255,183,103 | 69(69) | no | two | 24910 | 27029 |
| C | A08 | 0.270 | 36097 | 7->7 | 13092,14298,2084,1639,262,207,72 | 72(72) | no | two | 27295 | 29508 |
| D | J1 | 0.338 | 23077 | 26->14 | 2254,5864,1328,655,607,540,499,80,77,76,58,55,51,50 | 50(50) | no | two | 8026 | 13532 |
| D | J2 | 0.211 | 2399 | 0->0 | none | 50(50) | no | none | -1 | -1 |
| D | J3 | 0.215 | 3253 | 1->1 | 350 | 50(50) | no | one | 1223 | -1 |
| D | J5 | 0.239 | 5668 | 3->3 | 84,716,64 | 50(50) | no | two | 320 | 2178 |
| D | J7 | 0.258 | 7471 | 5->5 | 136,1035,88,85,82 | 50(50) | no | two | 564 | 3219 |
| D | J9 | 0.203 | 1972 | 0->0 | none | 50(50) | no | none | -1 | -1 |
| D | A01 | 0.600 | 85136 | 11->11 | 32206,28179,3743,3401,891,757,486,336,304,291,240 | 170(170) | no | two | 66262 | 58048 |
| D | A02 | 0.600 | 49528 | 7->6 | 20705,22696,686,385,245,184 | 99(99) | no | two | 42263 | 46491 |
| D | A03 | 0.600 | 46784 | 5->5 | 19526,21518,916,135,128 | 93(93) | no | two | 39993 | 43937 |
| D | A04 | 0.582 | 41296 | 9->7 | 17251,18904,575,516,251,240,120 | 82(82) | no | two | 35031 | 38547 |
| D | A05 | 0.600 | 38074 | 7->6 | 15594,17028,713,462,429,129 | 76(76) | no | two | 32005 | 34638 |
| D | A06 | 0.600 | 27944 | 9->7 | 11196,12418,393,316,219,104,62 | 55(55) | no | two | 23119 | 25464 |
| D | A07 | 0.293 | 34608 | 10->8 | 12042,13131,2870,1127,1052,255,183,103 | 69(69) | no | two | 24910 | 27029 |
| D | A08 | 0.270 | 36097 | 7->7 | 13092,14298,2084,1639,262,207,72 | 72(72) | no | two | 27295 | 29515 |

Retry ladders (`[RETRY-23]`, one line per attempt). Every cell in this grid that reached a cluster set stopped
after **one** attempt; only the two cells that found **zero** clusters retried, and they retried 21 times:

```
A  J1 retry=1 npts=14546 clusters_pre=22 clusters=18 sizes=626,3489,429,411,349,284,228,143,106,103,86,84,81,80,58,57,53,50 minCluster=50 from=50
B  J1 retry=1 npts=23077 clusters_pre=13 clusters=7  sizes=4812,9032,752,373,338,205,59 minCluster=50 from=50
C  J1 retry=1 npts=23077 clusters_pre=26 clusters=14 sizes=2254,5864,1328,655,607,540,499,80,77,76,58,55,51,50 minCluster=50 from=50
A  J3 retry=1 npts=1467  clusters_pre=2 clusters=1 sizes=268 minCluster=50 from=50   outcome=none
B  J3 retry=1 npts=3252  clusters_pre=1 clusters=1 sizes=289 minCluster=50 from=50   outcome=none
C  J3 retry=1 npts=3253  clusters_pre=1 clusters=1 sizes=350 minCluster=50 from=50   outcome=none
D  J3 retry=1 npts=3253  clusters_pre=1 clusters=1 sizes=350 minCluster=50 from=50   outcome=one surf0_points=1223
A  J5 retry=1 npts=3021  clusters_pre=1 clusters=1 sizes=679 minCluster=50 from=50   outcome=none
B  J5 retry=1 npts=5668  clusters_pre=3 clusters=2 sizes=51,740 minCluster=50 from=50  outcome=two
C  J5 retry=1 npts=5668  clusters_pre=3 clusters=3 sizes=84,716,64 minCluster=50 from=50 outcome=two
A  J7 retry=1 npts=4254  clusters_pre=5 clusters=4 sizes=403,263,68,65 minCluster=50 from=50 outcome=two
B  J7 retry=1 npts=7471  clusters_pre=5 clusters=4 sizes=609,648,93,57 minCluster=50 from=50 outcome=two
C  J7 retry=1 npts=7471  clusters_pre=5 clusters=5 sizes=136,1035,88,85,82 minCluster=50 from=50 outcome=two
A  J2 retries=21 clusters=0 sizes=none npts=1031 floor=50 from=50 outcome=none reason=no temp surface
B  J2 retries=21 clusters=0 sizes=none npts=2397 floor=50 from=50 outcome=none
C  J2 retries=21 clusters=0 sizes=none npts=2399 floor=50 from=50 outcome=none
D  J2 retries=21 clusters=0 sizes=none npts=2399 floor=50 from=50 outcome=none
A  J9 retries=21 clusters=0 sizes=none npts=787  floor=50 from=50 outcome=none
B  J9 retries=21 clusters=0 sizes=none npts=1971 floor=50 from=50 outcome=none
C  J9 retries=21 clusters=0 sizes=none npts=1972 floor=50 from=50 outcome=none
D  J9 retries=21 clusters=0 sizes=none npts=1972 floor=50 from=50 outcome=none
A  A04 retry=1 npts=38901 clusters_pre=5 clusters=5 sizes=15932,17374,770,164,124 minCluster=77 from=77
B  A04 retry=1 npts=41296 clusters_pre=5 clusters=5 sizes=16955,18456,857,205,147  minCluster=82 from=82
B  A07 retry=1 npts=34608 clusters_pre=7 clusters=7 sizes=11815,12888,2722,1059,1018,234,216 minCluster=69 from=69
B  A08 retry=1 npts=36097 clusters_pre=7 clusters=7 sizes=12817,14141,1899,1499,222,106,97 minCluster=72 from=72
```

[FLOOR-23] is silent in all 70 cells. That is what the source does when `SFS_COUNT_SCALE` is unset:
mesh_processing_headless.cpp:3625 prints it only when `g_floorCeilingOn && g_countScaleAuto`. The floor and its
source are still on [STATUS-23]/[RETRY-23], and are the `floor(from)` column above.

## 4. Geometry of every exported surface

`ext` is the bounding box in mm, `diag` its diagonal, `cov` the 2 mm coverage fraction, `fold` the folded angle
between the surface and the mesh in degrees, `nsrc` the normal source the pipeline recorded.

| arm | piece | surface | points | ext x | ext y | ext z | diag | cov 2mm | fold deg | nsrc |
|---|---|---|---|---|---|---|---|---|---|---|
| A | J1 | 0 | 3580 | 17.57 | 27.09 | 23.02 | 39.65 | 0.274 | 1.78 | ply |
| A | J1 | 1 | 12092 | 32.16 | 36.05 | 25.02 | 54.40 | 0.710 | 1.91 | ply |
| A | J7 | 0 | 1012 | 14.66 | 7.26 | 22.08 | 27.48 | 0.197 | 1.12 | ply |
| A | J7 | 1 | 829 | 15.66 | 20.43 | 11.61 | 28.24 | 0.168 | 1.16 | ply |
| A | A01 | 0 | 66760 | 103.16 | 115.29 | 56.35 | 164.65 | 0.434 | 0.73 | ply |
| A | A01 | 1 | 57287 | 105.92 | 118.43 | 58.35 | 169.26 | 0.395 | 0.83 | ply |
| A | A02 | 0 | 42197 | 56.61 | 107.37 | 49.08 | 130.93 | 0.479 | 0.83 | ply |
| A | A02 | 1 | 46324 | 59.01 | 110.64 | 52.13 | 135.80 | 0.524 | 0.93 | ply |
| A | A03 | 0 | 39771 | 52.95 | 84.70 | 77.89 | 126.66 | 0.487 | 0.61 | ply |
| A | A03 | 1 | 43572 | 56.30 | 86.32 | 78.01 | 129.26 | 0.519 | 0.71 | ply |
| A | A04 | 0 | 32683 | 57.82 | 85.03 | 42.27 | 111.18 | 0.482 | 0.57 | ply |
| A | A04 | 1 | 35790 | 60.37 | 86.50 | 43.66 | 114.16 | 0.522 | 0.55 | ply |
| A | A05 | 0 | 31576 | 54.09 | 94.67 | 35.18 | 114.57 | 0.482 | 0.65 | ply |
| A | A05 | 1 | 34136 | 57.14 | 97.64 | 36.19 | 118.77 | 0.522 | 0.59 | ply |
| A | A06 | 0 | 22575 | 37.35 | 115.19 | 38.43 | 127.04 | 0.501 | 0.62 | ply |
| A | A06 | 1 | 24919 | 38.76 | 118.30 | 39.42 | 130.58 | 0.532 | 0.60 | ply |
| A | A07 | 0 | 6066 | 25.80 | 39.83 | 25.73 | 53.98 | 0.486 | 0.57 | ply |
| A | A07 | 1 | 6437 | 26.88 | 40.56 | 26.40 | 55.36 | 0.523 | 0.48 | ply |
| A | A08 | 0 | 5528 | 33.14 | 27.25 | 23.04 | 48.70 | 0.502 | 0.70 | ply |
| A | A08 | 1 | 6097 | 35.73 | 28.47 | 24.45 | 51.81 | 0.545 | 0.64 | ply |
| A2 | J1 | 0 | 3580 | 17.57 | 27.09 | 23.02 | 39.65 | 0.274 | 1.78 | ply |
| A2 | J1 | 1 | 12092 | 32.16 | 36.05 | 25.02 | 54.40 | 0.710 | 1.91 | ply |
| A2 | J7 | 0 | 1012 | 14.66 | 7.26 | 22.08 | 27.48 | 0.197 | 1.12 | ply |
| A2 | J7 | 1 | 829 | 15.66 | 20.43 | 11.61 | 28.24 | 0.168 | 1.16 | ply |
| A2 | A01 | 0 | 66762 | 103.16 | 115.29 | 56.35 | 164.65 | 0.434 | 0.73 | ply |
| A2 | A01 | 1 | 57287 | 105.92 | 118.43 | 58.35 | 169.26 | 0.395 | 0.83 | ply |
| A2 | A02 | 0 | 42202 | 56.61 | 107.37 | 49.08 | 130.93 | 0.479 | 0.83 | ply |
| A2 | A02 | 1 | 46324 | 59.01 | 110.64 | 52.13 | 135.80 | 0.524 | 0.93 | ply |
| A2 | A03 | 0 | 39774 | 52.95 | 84.70 | 77.89 | 126.66 | 0.487 | 0.61 | ply |
| A2 | A03 | 1 | 43576 | 56.30 | 86.32 | 78.01 | 129.26 | 0.519 | 0.71 | ply |
| A2 | A04 | 0 | 32683 | 57.82 | 85.03 | 42.27 | 111.18 | 0.482 | 0.57 | ply |
| A2 | A04 | 1 | 35790 | 60.37 | 86.50 | 43.66 | 114.16 | 0.522 | 0.55 | ply |
| A2 | A05 | 0 | 31574 | 54.09 | 94.67 | 35.18 | 114.57 | 0.482 | 0.65 | ply |
| A2 | A05 | 1 | 34138 | 57.14 | 97.64 | 36.19 | 118.77 | 0.522 | 0.59 | ply |
| A2 | A06 | 0 | 22574 | 37.35 | 115.19 | 38.43 | 127.04 | 0.501 | 0.62 | ply |
| A2 | A06 | 1 | 24919 | 38.76 | 118.30 | 39.42 | 130.58 | 0.532 | 0.60 | ply |
| A2 | A07 | 0 | 6066 | 25.80 | 39.83 | 25.73 | 53.98 | 0.486 | 0.57 | ply |
| A2 | A07 | 1 | 6437 | 26.88 | 40.56 | 26.40 | 55.36 | 0.523 | 0.48 | ply |
| A2 | A08 | 0 | 5528 | 33.14 | 27.25 | 23.04 | 48.70 | 0.502 | 0.70 | ply |
| A2 | A08 | 1 | 6097 | 35.73 | 28.47 | 24.45 | 51.81 | 0.545 | 0.64 | ply |
| B | J1 | 0 | 10800 | 30.17 | 30.92 | 33.07 | 54.41 | 0.660 | 1.63 | ply |
| B | J1 | 1 | 15780 | 33.74 | 37.12 | 35.85 | 61.66 | 0.779 | 1.61 | ply |
| B | J5 | 0 | 229 | 8.39 | 10.58 | 7.75 | 15.57 | 0.087 | 1.18 | ply |
| B | J5 | 1 | 2317 | 22.33 | 27.40 | 19.95 | 40.59 | 0.872 | 2.11 | ply |
| B | J7 | 0 | 1753 | 19.15 | 20.04 | 21.29 | 34.95 | 0.285 | 1.27 | ply |
| B | J7 | 1 | 1997 | 21.01 | 24.37 | 14.19 | 35.17 | 0.313 | 1.35 | ply |
| B | A01 | 0 | 66763 | 103.16 | 115.29 | 56.35 | 164.65 | 0.434 | 0.73 | ply |
| B | A01 | 1 | 57297 | 105.92 | 118.43 | 58.35 | 169.26 | 0.395 | 0.83 | ply |
| B | A02 | 0 | 42201 | 56.61 | 107.37 | 49.08 | 130.93 | 0.479 | 0.83 | ply |
| B | A02 | 1 | 46334 | 59.28 | 110.64 | 52.13 | 135.92 | 0.524 | 0.93 | ply |
| B | A03 | 0 | 39777 | 52.95 | 84.70 | 77.89 | 126.66 | 0.487 | 0.61 | ply |
| B | A03 | 1 | 43575 | 56.30 | 86.32 | 78.01 | 129.26 | 0.519 | 0.71 | ply |
| B | A04 | 0 | 34731 | 57.65 | 84.68 | 41.90 | 110.68 | 0.483 | 0.56 | ply |
| B | A04 | 1 | 38007 | 60.24 | 86.63 | 43.63 | 114.18 | 0.522 | 0.54 | ply |
| B | A05 | 0 | 31576 | 54.08 | 94.67 | 35.18 | 114.57 | 0.482 | 0.65 | ply |
| B | A05 | 1 | 34140 | 57.14 | 97.64 | 36.19 | 118.77 | 0.522 | 0.59 | ply |
| B | A06 | 0 | 22573 | 37.35 | 115.19 | 38.43 | 127.04 | 0.501 | 0.62 | ply |
| B | A06 | 1 | 24919 | 38.76 | 118.30 | 39.42 | 130.58 | 0.532 | 0.60 | ply |
| B | A07 | 0 | 24637 | 24.76 | 39.95 | 25.77 | 53.61 | 0.485 | 0.56 | ply |
| B | A07 | 1 | 26740 | 27.22 | 41.06 | 26.09 | 55.75 | 0.530 | 0.51 | ply |
| B | A08 | 0 | 26777 | 33.81 | 27.62 | 23.86 | 49.75 | 0.513 | 0.59 | ply |
| B | A08 | 1 | 29285 | 35.98 | 28.56 | 24.82 | 52.22 | 0.547 | 0.60 | ply |
| C | J1 | 0 | 8026 | 31.01 | 29.31 | 32.19 | 53.45 | 0.537 | 0.28 | ply |
| C | J1 | 1 | 13532 | 32.30 | 36.07 | 27.35 | 55.61 | 0.585 | 0.27 | ply |
| C | J5 | 0 | 320 | 5.45 | 10.91 | 11.08 | 16.47 | 0.123 | 0.56 | ply |
| C | J5 | 1 | 2178 | 22.45 | 21.81 | 19.39 | 36.82 | 0.729 | 0.80 | ply |
| C | J7 | 0 | 564 | 10.92 | 19.28 | 13.34 | 25.86 | 0.135 | 0.79 | ply |
| C | J7 | 1 | 3219 | 21.84 | 26.89 | 26.04 | 43.34 | 0.485 | 0.55 | ply |
| C | A01 | 0 | 66265 | 103.20 | 115.29 | 56.35 | 164.67 | 0.435 | 0.48 | ply |
| C | A01 | 1 | 58048 | 106.14 | 118.66 | 58.35 | 169.56 | 0.396 | 0.51 | ply |
| C | A02 | 0 | 42263 | 56.59 | 107.36 | 49.08 | 130.92 | 0.478 | 0.51 | ply |
| C | A02 | 1 | 46490 | 59.32 | 110.53 | 52.17 | 135.86 | 0.524 | 0.56 | ply |
| C | A03 | 0 | 39988 | 53.09 | 84.59 | 78.03 | 126.74 | 0.488 | 0.46 | ply |
| C | A03 | 1 | 43936 | 56.30 | 86.06 | 78.01 | 129.08 | 0.519 | 0.49 | ply |
| C | A04 | 0 | 35030 | 58.00 | 84.91 | 41.90 | 111.04 | 0.483 | 0.41 | ply |
| C | A04 | 1 | 38547 | 60.36 | 86.84 | 43.81 | 114.48 | 0.523 | 0.42 | ply |
| C | A05 | 0 | 32003 | 53.84 | 94.63 | 35.18 | 114.42 | 0.483 | 0.46 | ply |
| C | A05 | 1 | 34636 | 57.32 | 98.44 | 36.79 | 119.71 | 0.522 | 0.42 | ply |
| C | A06 | 0 | 23118 | 37.30 | 115.83 | 38.50 | 127.64 | 0.504 | 0.42 | ply |
| C | A06 | 1 | 25463 | 38.76 | 118.42 | 39.42 | 130.69 | 0.535 | 0.43 | ply |
| C | A07 | 0 | 24910 | 24.87 | 39.95 | 25.84 | 53.69 | 0.485 | 0.47 | ply |
| C | A07 | 1 | 27029 | 27.27 | 41.44 | 26.19 | 56.10 | 0.531 | 0.40 | ply |
| C | A08 | 0 | 27295 | 33.81 | 28.18 | 23.68 | 49.98 | 0.524 | 0.53 | ply |
| C | A08 | 1 | 29508 | 35.96 | 28.70 | 24.88 | 52.30 | 0.547 | 0.49 | ply |
| D | J1 | 0 | 8026 | 31.01 | 29.31 | 32.19 | 53.45 | 0.537 | 0.28 | ply |
| D | J1 | 1 | 13532 | 32.30 | 36.07 | 27.35 | 55.61 | 0.585 | 0.27 | ply |
| D | J3 | 0 | 1223 | 18.48 | 22.02 | 13.89 | 31.92 | 0.929 | 1.10 | ply |
| D | J5 | 0 | 320 | 5.45 | 10.91 | 11.08 | 16.47 | 0.123 | 0.56 | ply |
| D | J5 | 1 | 2178 | 22.45 | 21.81 | 19.39 | 36.82 | 0.729 | 0.80 | ply |
| D | J7 | 0 | 564 | 10.92 | 19.28 | 13.34 | 25.86 | 0.135 | 0.79 | ply |
| D | J7 | 1 | 3219 | 21.84 | 26.89 | 26.04 | 43.34 | 0.485 | 0.55 | ply |
| D | A01 | 0 | 66262 | 103.20 | 115.29 | 56.35 | 164.67 | 0.435 | 0.48 | ply |
| D | A01 | 1 | 58048 | 106.14 | 118.66 | 58.35 | 169.56 | 0.396 | 0.51 | ply |
| D | A02 | 0 | 42263 | 56.59 | 107.36 | 49.08 | 130.92 | 0.478 | 0.51 | ply |
| D | A02 | 1 | 46491 | 59.32 | 110.53 | 52.17 | 135.86 | 0.524 | 0.56 | ply |
| D | A03 | 0 | 39993 | 53.09 | 84.59 | 78.03 | 126.74 | 0.489 | 0.46 | ply |
| D | A03 | 1 | 43937 | 56.30 | 86.06 | 78.01 | 129.08 | 0.519 | 0.49 | ply |
| D | A04 | 0 | 35031 | 58.00 | 84.91 | 41.90 | 111.04 | 0.483 | 0.41 | ply |
| D | A04 | 1 | 38547 | 60.36 | 86.84 | 43.81 | 114.48 | 0.523 | 0.42 | ply |
| D | A05 | 0 | 32005 | 53.84 | 94.63 | 35.18 | 114.42 | 0.483 | 0.46 | ply |
| D | A05 | 1 | 34638 | 57.32 | 98.44 | 36.79 | 119.71 | 0.522 | 0.42 | ply |
| D | A06 | 0 | 23119 | 37.30 | 115.83 | 38.50 | 127.64 | 0.504 | 0.42 | ply |
| D | A06 | 1 | 25464 | 38.76 | 118.42 | 39.42 | 130.69 | 0.535 | 0.43 | ply |
| D | A07 | 0 | 24910 | 24.87 | 39.95 | 25.84 | 53.69 | 0.485 | 0.47 | ply |
| D | A07 | 1 | 27029 | 27.27 | 41.44 | 26.19 | 56.10 | 0.531 | 0.40 | ply |
| D | A08 | 0 | 27295 | 33.81 | 28.18 | 23.68 | 49.98 | 0.524 | 0.53 | ply |
| D | A08 | 1 | 29515 | 35.96 | 28.70 | 24.88 | 52.30 | 0.547 | 0.49 | ply |

## 5. Ticket 30 ruler, every cell

| arm | pot | piece | status | n0 | n1 | med_nn | med_along | p90_along | max_along | med_across | p90_across | max_across | coincidence 1um |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | Juglet | J1 | ok | 3580 | 12092 | 4.347 | 0.368 | 6.067 | 14.724 | 4.199 | 13.665 | 19.424 | 0.325 |
| A | Juglet | J2 | no_pair |  |  | - | - | - | - | - | - | - | - |
| A | Juglet | J3 | no_pair |  |  | - | - | - | - | - | - | - | - |
| A | Juglet | J5 | no_pair |  |  | - | - | - | - | - | - | - | - |
| A | Juglet | J7 | ok | 1012 | 829 | 4.339 | 0.643 | 4.001 | 8.127 | 4.295 | 10.693 | 14.039 | 0.263 |
| A | Juglet | J9 | no_pair |  |  | - | - | - | - | - | - | - | - |
| A | Pot_A | A01 | ok | 66760 | 57287 | 7.095 | 7.089 | 9.944 | 12.955 | 0.271 | 0.544 | 4.474 | 0.000 |
| A | Pot_A | A02 | ok | 42197 | 46324 | 3.646 | 3.632 | 4.458 | 6.353 | 0.251 | 0.447 | 3.722 | 0.000 |
| A | Pot_A | A03 | ok | 39771 | 43572 | 3.683 | 3.671 | 4.410 | 5.567 | 0.244 | 0.424 | 3.539 | 0.000 |
| A | Pot_A | A04 | ok | 32683 | 35790 | 3.669 | 3.657 | 4.147 | 5.054 | 0.237 | 0.415 | 3.007 | 0.000 |
| A | Pot_A | A05 | ok | 31576 | 34136 | 3.779 | 3.767 | 4.354 | 5.319 | 0.251 | 0.433 | 3.160 | 0.000 |
| A | Pot_A | A06 | ok | 22575 | 24919 | 3.563 | 3.547 | 3.745 | 4.229 | 0.256 | 0.723 | 2.900 | 0.000 |
| A | Pot_A | A07 | ok | 6066 | 6437 | 3.961 | 3.920 | 4.297 | 4.596 | 0.249 | 0.468 | 3.556 | 0.000 |
| A | Pot_A | A08 | ok | 5528 | 6097 | 3.619 | 3.604 | 3.817 | 4.000 | 0.250 | 1.202 | 2.891 | 0.000 |
| A2 | Juglet | J1 | ok | 3580 | 12092 | 4.347 | 0.368 | 6.067 | 14.724 | 4.199 | 13.665 | 19.424 | 0.325 |
| A2 | Juglet | J2 | no_pair |  |  | - | - | - | - | - | - | - | - |
| A2 | Juglet | J3 | no_pair |  |  | - | - | - | - | - | - | - | - |
| A2 | Juglet | J5 | no_pair |  |  | - | - | - | - | - | - | - | - |
| A2 | Juglet | J7 | ok | 1012 | 829 | 4.339 | 0.643 | 4.001 | 8.127 | 4.295 | 10.693 | 14.039 | 0.263 |
| A2 | Juglet | J9 | no_pair |  |  | - | - | - | - | - | - | - | - |
| A2 | Pot_A | A01 | ok | 66762 | 57287 | 7.095 | 7.089 | 9.944 | 12.955 | 0.271 | 0.544 | 4.474 | 0.000 |
| A2 | Pot_A | A02 | ok | 42202 | 46324 | 3.646 | 3.632 | 4.458 | 6.353 | 0.251 | 0.447 | 3.722 | 0.000 |
| A2 | Pot_A | A03 | ok | 39774 | 43576 | 3.683 | 3.671 | 4.409 | 5.567 | 0.244 | 0.424 | 3.630 | 0.000 |
| A2 | Pot_A | A04 | ok | 32683 | 35790 | 3.669 | 3.657 | 4.147 | 5.054 | 0.237 | 0.415 | 3.007 | 0.000 |
| A2 | Pot_A | A05 | ok | 31574 | 34138 | 3.779 | 3.767 | 4.354 | 5.319 | 0.251 | 0.433 | 3.160 | 0.000 |
| A2 | Pot_A | A06 | ok | 22574 | 24919 | 3.563 | 3.547 | 3.745 | 4.229 | 0.256 | 0.723 | 2.900 | 0.000 |
| A2 | Pot_A | A07 | ok | 6066 | 6437 | 3.961 | 3.920 | 4.297 | 4.596 | 0.249 | 0.468 | 3.556 | 0.000 |
| A2 | Pot_A | A08 | ok | 5528 | 6097 | 3.619 | 3.604 | 3.817 | 4.000 | 0.250 | 1.202 | 2.891 | 0.000 |
| B | Juglet | J1 | ok | 10800 | 15780 | 0.472 | 0.007 | 0.911 | 4.432 | 0.387 | 5.045 | 11.373 | 0.460 |
| B | Juglet | J2 | no_pair |  |  | - | - | - | - | - | - | - | - |
| B | Juglet | J3 | no_pair |  |  | - | - | - | - | - | - | - | - |
| B | Juglet | J5 | ok | 229 | 2317 | 11.628 | 5.187 | 11.787 | 17.566 | 10.270 | 17.107 | 20.451 | 0.015 |
| B | Juglet | J7 | ok | 1753 | 1997 | 5.217 | 0.732 | 4.777 | 9.495 | 5.127 | 12.267 | 15.887 | 0.232 |
| B | Juglet | J9 | no_pair |  |  | - | - | - | - | - | - | - | - |
| B | Pot_A | A01 | ok | 66763 | 57297 | 7.095 | 7.089 | 9.944 | 12.955 | 0.271 | 0.544 | 4.665 | 0.000 |
| B | Pot_A | A02 | ok | 42201 | 46334 | 3.646 | 3.632 | 4.458 | 6.353 | 0.251 | 0.447 | 3.722 | 0.000 |
| B | Pot_A | A03 | ok | 39777 | 43575 | 3.683 | 3.671 | 4.410 | 5.567 | 0.244 | 0.424 | 3.539 | 0.000 |
| B | Pot_A | A04 | ok | 34731 | 38007 | 3.669 | 3.658 | 4.146 | 5.024 | 0.233 | 0.403 | 3.090 | 0.000 |
| B | Pot_A | A05 | ok | 31576 | 34140 | 3.779 | 3.767 | 4.354 | 5.319 | 0.251 | 0.433 | 3.160 | 0.000 |
| B | Pot_A | A06 | ok | 22573 | 24919 | 3.563 | 3.547 | 3.745 | 4.229 | 0.256 | 0.723 | 2.900 | 0.000 |
| B | Pot_A | A07 | ok | 24637 | 26740 | 3.959 | 3.902 | 4.279 | 4.618 | 0.126 | 1.295 | 3.814 | 0.000 |
| B | Pot_A | A08 | ok | 26777 | 29285 | 3.604 | 3.593 | 3.816 | 3.990 | 0.129 | 1.540 | 3.009 | 0.000 |
| C | Juglet | J1 | ok | 8026 | 13532 | 0.000 | 0.000 | 0.685 | 5.960 | 0.000 | 6.971 | 14.859 | 0.531 |
| C | Juglet | J2 | no_pair |  |  | - | - | - | - | - | - | - | - |
| C | Juglet | J3 | no_pair |  |  | - | - | - | - | - | - | - | - |
| C | Juglet | J5 | ok | 320 | 2178 | 13.442 | 6.827 | 14.664 | 20.694 | 11.520 | 16.473 | 19.527 | 0.018 |
| C | Juglet | J7 | ok | 564 | 3219 | 9.006 | 2.688 | 12.701 | 21.452 | 7.755 | 15.389 | 17.513 | 0.116 |
| C | Juglet | J9 | no_pair |  |  | - | - | - | - | - | - | - | - |
| C | Pot_A | A01 | ok | 66265 | 58048 | 7.075 | 7.070 | 9.960 | 13.332 | 0.266 | 0.553 | 4.928 | 0.000 |
| C | Pot_A | A02 | ok | 42263 | 46490 | 3.646 | 3.633 | 4.488 | 6.394 | 0.247 | 0.435 | 3.645 | 0.000 |
| C | Pot_A | A03 | ok | 39988 | 43936 | 3.684 | 3.672 | 4.422 | 5.597 | 0.243 | 0.421 | 3.528 | 0.000 |
| C | Pot_A | A04 | ok | 35030 | 38547 | 3.670 | 3.659 | 4.156 | 5.039 | 0.231 | 0.398 | 3.039 | 0.000 |
| C | Pot_A | A05 | ok | 32003 | 34636 | 3.779 | 3.765 | 4.357 | 5.322 | 0.249 | 0.439 | 3.315 | 0.000 |
| C | Pot_A | A06 | ok | 23118 | 25463 | 3.562 | 3.548 | 3.745 | 4.229 | 0.253 | 0.677 | 2.985 | 0.000 |
| C | Pot_A | A07 | ok | 24910 | 27029 | 3.958 | 3.890 | 4.270 | 4.626 | 0.131 | 1.478 | 3.854 | 0.000 |
| C | Pot_A | A08 | ok | 27295 | 29508 | 3.602 | 3.590 | 3.815 | 3.989 | 0.135 | 1.504 | 2.696 | 0.000 |
| D | Juglet | J1 | ok | 8026 | 13532 | 0.000 | 0.000 | 0.685 | 5.960 | 0.000 | 6.971 | 14.859 | 0.531 |
| D | Juglet | J2 | no_pair |  |  | - | - | - | - | - | - | - | - |
| D | Juglet | J3 | no_pair |  |  | - | - | - | - | - | - | - | - |
| D | Juglet | J5 | ok | 320 | 2178 | 13.442 | 6.827 | 14.664 | 20.694 | 11.520 | 16.473 | 19.527 | 0.018 |
| D | Juglet | J7 | ok | 564 | 3219 | 9.006 | 2.688 | 12.701 | 21.452 | 7.755 | 15.389 | 17.513 | 0.116 |
| D | Juglet | J9 | no_pair |  |  | - | - | - | - | - | - | - | - |
| D | Pot_A | A01 | ok | 66262 | 58048 | 7.075 | 7.070 | 9.960 | 13.332 | 0.266 | 0.553 | 4.928 | 0.000 |
| D | Pot_A | A02 | ok | 42263 | 46491 | 3.646 | 3.633 | 4.488 | 6.394 | 0.247 | 0.435 | 3.645 | 0.000 |
| D | Pot_A | A03 | ok | 39993 | 43937 | 3.684 | 3.672 | 4.421 | 5.597 | 0.243 | 0.421 | 3.738 | 0.000 |
| D | Pot_A | A04 | ok | 35031 | 38547 | 3.670 | 3.659 | 4.156 | 5.039 | 0.231 | 0.398 | 3.039 | 0.000 |
| D | Pot_A | A05 | ok | 32005 | 34638 | 3.779 | 3.765 | 4.357 | 5.322 | 0.249 | 0.439 | 3.315 | 0.000 |
| D | Pot_A | A06 | ok | 23119 | 25464 | 3.561 | 3.548 | 3.745 | 4.229 | 0.253 | 0.680 | 2.985 | 0.000 |
| D | Pot_A | A07 | ok | 24910 | 27029 | 3.958 | 3.890 | 4.270 | 4.626 | 0.131 | 1.478 | 3.854 | 0.000 |
| D | Pot_A | A08 | ok | 27295 | 29515 | 3.602 | 3.590 | 3.815 | 3.989 | 0.135 | 1.504 | 2.696 | 0.000 |

## 6. Arm A against the shipped default, and A against A2

| piece | shipped default (ticket) | arm A this grid | arm A2 |
|---|---|---|---|
| Juglet 1 | 3580 / 12092 | 3580 / 12092 | 3580 / 12092 |
| Juglet 7 | 1012 / 829 | 1012 / 829 | 1012 / 829 |
| Juglet 4 | 182 / 732 | not in this grid | not in this grid |
| Juglet 6 | 608 / 1016 | not in this grid | not in this grid |

A against A2 — independent check, parsing the x y z of each ASCII PLY and comparing sorted multisets
(the `sorted_identical`/`max_abs_diff` columns of `compare36.py` disagree with this check; see §10):

```
Juglet_Piece_1  Surface_0  3580 / 3580    sorted point sets exactly equal, max |d| 0.000e+00
Juglet_Piece_1  Surface_1 12092 /12092    sorted point sets exactly equal, max |d| 0.000e+00
Juglet_Piece_7  Surface_0  1012 / 1012    sorted point sets exactly equal, max |d| 0.000e+00
Juglet_Piece_7  Surface_1   829 /  829    sorted point sets exactly equal, max |d| 0.000e+00
Pot_A_Piece_07  Surface_0  6066 / 6066    sorted point sets exactly equal, max |d| 0.000e+00
Pot_A_Piece_07  Surface_1  6437 / 6437    sorted point sets exactly equal, max |d| 0.000e+00
Pot_A_Piece_01  Surface_0 66760 /66762    point sets differ (2 points), max |d| over sorted pairs 2.160e-01
Pot_A_Piece_01  Surface_1 57287 /57287    sorted point sets exactly equal, max |d| 0.000e+00
```

`<piece>_SampledWithNormals.ply` is byte-identical between A and A2 for all 14 pieces (md5 equal), i.e. the
sampling stage reproduces exactly. Pot A surface point counts differ between A and A2 on 01 (+2), 02 (+5),
03 (+3), 05 (-2/-2) and 06 (-1); they are identical on 04, 07, 08. The mesh stage draws 30 random ray-cast
points from an unseeded generator (mesh_processing_headless.cpp:1526-1527), which is the only unseeded step
between two runs of the same bytes.

## 7. Inputs, corpus, pristine

```
out/inputs_before.md5  222 lines   out/inputs_after.md5  222 lines   cmp: IDENTICAL
out/corpus_before.txt vs out/corpus_after.txt (1803 lines incl the /opt/sfs-pristine line)  cmp: IDENTICAL
first input rows: 74086636b14717695cf12330c702bfca  107  .../SfS_pp/Axes/Pot_A_Piece_01_Axis.xyz
                  c7edaa769cefbd0006d010239c6f5ace  107  .../SfS_pp/Axes/Pot_A_Piece_02_Axis.xyz
out/pristine.txt  status ABSENT  ('ls: cannot access /opt/sfs-pristine: No such file or directory',
                  'stat: cannot statx /opt/sfs-pristine: No such file or directory', recorded on the compute node)
```

## 8. Deletion record

`out/GEOMETRY_DELETED.txt` (3903 lines, 316320 bytes) was written before anything was removed. Its tail:

```
# ticket 36 -- geometry written by this run, recorded BEFORE the delete.
# The binary stays at out/bin-new; everything below is reproducible from 0a53dee287fd577643bae3fe57e52527e3b2864b and the
# corpus by out/commands.txt.
key	ext	files	bytes
ext	.1	1	108287
...
# <piece>/{cell.tsv,logs/,surfaces/,measure/}, logs/
#
# deleted at 2026-10-27T13:18:36Z: 3831 files, 193057045 bytes (the build tree)
# after the delete: 0 files remain, build/ is gone
# per-cell stage and rung-dump counts: out/cells/<tag>/<pot>/<piece>/logs/geometry_counts.tsv
```

Per-cell counted totals live in `out/cells/<tag>/<pot>/<piece>/logs/geometry_counts.tsv`; one example
(arm A, Juglet 1) verbatim:

```
path	ext	files	bytes
A/Juglet/Juglet_Piece_1/stage	other	3	492
A/Juglet/Juglet_Piece_1/stage	obj	1	1655590
A/Juglet/Juglet_Piece_1/stage	pcd	3	1971974
A/Juglet/Juglet_Piece_1/stage	ply	8	6287342
A/Juglet/Juglet_Piece_1/stage	xyz	5	2866050
A/Juglet/Juglet_Piece_1/dump	json	5	4522
A/Juglet/Juglet_Piece_1/dump	ply	5	4726314
# counted above, then deleted: 12855360 bytes of stage, 4739028 bytes of rung dump
after: stage present=no dump present=no
```

`out/GEOMETRY_KEPT.txt`: `count 0` — no cell was kept, every measurement exited 0 (all 70 `meas_exit=0`,
all 70 `mesh_exit=0`, all 70 `kept=no`). Kept for the lead: every cell's `surfaces/` (Surface_0/1 .ply and
.xyz plus SampledWithNormals.ply), `logs/`, `measure/` and `cell.tsv`, and the run dir's `out/` tables.

## 9. Index rows and git

```
307:20261028-0004_fe5b17f_t36-adaptive-spacing^I33880164^Ife5b17f1dbab527df2ddbb33e0a6342c5f9bef0c^It36-adaptive-spacing^I^I$
308:20261028-0013_0a53dee_t36-adaptive-spacing-r2^I33880555^I0a53dee287fd577643bae3fe57e52527e3b2864b^It36-adaptive-spacing^I^I$
```
Six fields each, tabs as shown by `cat -A`, field 5 (verdict) and field 6 (human_note) empty.

Pushed branch head at the time the grid ran: `0a53dee287fd577643bae3fe57e52527e3b2864b` on
`origin/36-adaptive-spacing-with-the-honest-normals` (`git cat-file -e` passes in the canonical checkout).
`git diff --stat main...HEAD`: 11 files, all inside `.scratch/juglet-breaklines/` — the ticket file's 4 changed
lines from `ticket_start.sh` plus the 10 files of `stage36/`. No tracked source file changed: this grid runs
main's own switches.

## 10. What was not done, and the caveats that belong to these numbers

- **Job 1 is invalid and stays in the record as invalid.** Its 70 cells exist and its index row exists, but its
  arms B and C are reruns of A. Nothing in run 1 answers the ticket; run 2 is the grid.
- **`compare36.py`'s `sorted_identical` and `max_abs_diff` columns are not usable for the `.ply` surfaces.**
  It reports `sorted_identical=0` even where a direct parse of the same two files gives exactly equal sorted
  x y z multisets, and `max_abs_diff` values of 2.5e24 / 3.4e35 / 1.1e36, which are not coordinates. Its
  `md5_equal` column is usable (it is a plain file hash). §6 gives the independent check.
- **`md5_equal=0` on the surface `.ply` files does not mean the geometry differs** — the vertex order in the
  exported file differs between two runs of identical geometry (Juglet 1 and 7: same points, different order).
- **[FLOOR-23] does not appear in any of the 70 cells** (see §3). The floor ceiling cannot fire with
  `SFS_COUNT_SCALE` unset, which is what the ticket specified.
- **Pot A 04, 07, 08 are the only Pot A pieces whose step moved.** Their `rawMM` is below 0.6 and above `s0`
  (0.581739 / 0.292881 / 0.270368), so `S` follows them down; 01, 02, 03, 05, 06 have `rawMM >= 0.6` and keep
  S=0.6; every Juglet piece has `rawMM < s0`, so `S = s0` there.
- **Pieces 4 and 6 are not in this grid** (the ticket's 14 pieces are Juglet 1, 2, 3, 5, 7, 9 and Pot A 01-08),
  so two of the four shipped-default counts cannot be checked here.
- **`/opt/sfs-pristine` is absent on this host and was not created.**
- Nothing else was left undone: 70 cells attempted in each job, all `mesh_exit=0`, all measured, all logged.
