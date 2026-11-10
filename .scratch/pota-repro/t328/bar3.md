
### Bar 3 — the correspondence bar. First measurement FAILS, and it convicts the bar-2 estimator, not the filing

Run **34700288** (`20261110-2235_123f2ca_t328-harness-after`) **COMPLETED 0:0**, 00:00:18. It clones t325's
`trees/juglet_GT_r1`, regenerates `Surfaces/*.xyz` from the cured `geom`, replaces `Breaklines/*.pcd` with the
cured `Bl0`/`Bl1`, hardlinks 326's pristine objects (`34671027`) and runs `diag326.sh jug_cured /inc 20
-DJUGLET_ORIG` in `sfs_main/sfs_pristine_assembly.sif`. Its before table is 326's own `out/diag_jug_GT.txt`.

`dot_med_d3` = median over the harness's correspondences of `n_A·n_B` (both normals are the exported PCD
normals); `inl` = the strict gate's `n_inl15_15deg`. **Before** = shipped t66 bundle; **after** = this cure.

| pair | before dot_med_d3 | before inl | after dot_med_d3 | after inl | after n_d3 (neg) |
|---|---|---|---|---|---|
| 1-2 | −0.896 | 11 | **+0.311** | 0 | 13 (0) |
| 1-4 | +0.786 | 4 | **+0.469** | 0 | 9 (0) |
| 1-8 | +0.971 | 22 | **+0.741** | 0 | 19 (0) |
| 1-9 | −0.945 | 0 | **−0.408** | 0 | 7 (6) |
| 2-5 | −0.991 | 0 | **+0.642** | 0 | 1 (0) |
| 2-9 | +0.991 | 8 | **+0.693** | 0 | 4 (0) |
| 3-5 | +0.987 | 6 | **+0.674** | 0 | 3 (0) |
| 6-7 | +0.106 | 0 | **−0.786** | 0 | 15 (12) |
| 7-9 | −0.674 | 0 | **+0.287** | 0 | 3 (0) |

One pair of nine clears +0.7 (1-8) and the strict gate is empty on all nine: **bar 3 fails as implemented**. The
cured tree is a fresh draw (the mesh stage's 30 unseeded ray-cast points), so `gap_min` moved too — 1-2
1.103→0.514, 1-9 2.124→0.998, 6-7 0.357→0.809 mm — and the before/after columns are two draws of the same
pipeline, not the same draw.

**Why it fails, measured rather than guessed.** `.scratch/pota-repro/t328/mutualpair2.py` is an exact local
replica of the harness's pair statistic (GTRel on the 4×4 `T` matrices, mutual nearest, |Δp| < 3 mm, dot of the
PCD normals, median). It reproduces both trees to three decimals *and* reproduces 327's swap table exactly
(1-2 +0.704, 1-4 +0.786, 1-8 +0.971, 1-9 −0.039, 2-5 +0.948, 2-9 +0.967, 3-5 +0.987, 6-7 −0.183, 7-9 +0.708),
so the statistic is trustworthy. On **that** bundle, with the filing already correct, four normal estimators:

| pair | fitted (327 swap) | fitted, sign per point from wall | wall k=5 mean | wall nearest-1 | 3 mm wall plane |
|---|---|---|---|---|---|
| 1-2 | +0.704 | +0.704 | +0.311 | +0.278 | **+0.926** |
| 1-4 | +0.786 | +0.786 | +0.469 | +0.199 | **+0.874** |
| 1-8 | +0.971 | +0.971 | +0.741 | +0.605 | **+0.984** |
| 1-9 | −0.039 | −0.039 | −0.408 | −0.808 | **+0.652** |
| 2-5 | +0.948 | +0.948 | +0.642 | +0.608 | **+0.953** |
| 2-9 | +0.967 | +0.967 | +0.688 | +0.400 | **+0.959** |
| 3-5 | +0.987 | +0.987 | +0.674 | +0.636 | **+0.989** |
| 6-7 | −0.183 | −0.177 | −0.609 | −0.499 | **+0.372** |
| 7-9 | +0.708 | +0.708 | +0.287 | +0.126 | **+0.797** |

- The **k=5 mean of the wall's own vertex normals** — what bar 2 shipped — is worse than the fitted normal on
  every one of the nine pairs, including the seven that were already passing. The wall's per-vertex normals right
  at a break edge are contaminated by the break face and by the last jagged triangle row, so the mean is pulled
  tens of degrees off the wall; the fitted B-spline normal is a smooth field over the whole fragment and does not
  suffer that.
- **Signing the fitted normal per point from the wall changes nothing** (−0.039 → −0.039, −0.183 → −0.177). The
  fitted normal already agrees in sign with the local wall, so 327's reading — that 1-9 and 6-7's residual is a
  per-point sign defect — is **not supported**: those correspondences are between surfaces that genuinely differ
  in orientation, not between a normal and its negation.
- A **3 mm disc of the wall, fitted as a plane** (smallest principal direction, sign from the fitted normal) is
  best of all: it beats the fitted normal on six of nine pairs and recovers 1-9 and 6-7 from −0.039/−0.183 to
  +0.652/+0.372 on this bundle. On the cured geometry it predicts 7/9 at bar (1-2 +0.926, 1-4 +0.874, 1-8 +0.984,
  2-5 +0.953, 2-9 +0.959, 3-5 +0.989, 7-9 +0.797) with 1-9 +0.652 and 6-7 +0.285 still short.

So the bar-2 code is being changed from the k=5 mean to the 3 mm plane fit (`edgeline_extraction_headless.cpp`,
the block after `fitBSplineSurfaceAndGetNormalsOnProjectedPoints`), and bars 1-3 are re-measured on the rebuild:
**34702694** (run dir `20261110-2252_123f2ca_t328-planenorm`), which also carries one fresh pot cell pair so the
filing change stays visible on the pots. Bar 5's byte-identity test is **34702695** in the same run directory.
