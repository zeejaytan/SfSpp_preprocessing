# 02: Swap test (laptop-only cross-pair)

**What to build:** a laptop-only test that settles whether the +Z shift is an interior/exterior Surface_0↔Surface_1 swap, using only the existing xyz samples — no sbatch, no rebuilds.

**Answers:** E1

**Blocked by:** None (can start immediately).

**Status:** results-in — swap confirmed 2–8, p1 control; E1 write-back still to do

**Working in:** `%TEMP%\swaptest\` (32 xyz + `swaptest.py`; outside repo, kept for re-run)

- [x] Spike: read `mesh_processing_headless.cpp:1680,1704,1755-1769,2073-2087` assignment path and state the swap mechanism in ticket
- [x] Cross-pair at GT with existing samples: fresh-S1 vs ORIG-S0 and fresh-S0 vs ORIG-S1, `task3_persherd.py` median metric + normal-sign check, pieces 2–8
- [x] Swap confirmed iff crossed ≈0.5mm / straight ≈3.5mm; else H2 wins — then compare per-piece driver centroids (Mesh OBJ vs PCD driver)
- [x] Result written into ticket Comments with numbers; E1 `Where it stands` untouched by worker (lead owns intent/)

## Comments (worker pota-swap-tester, 2026-10-15)

**Verdict: H1 SWAP CONFIRMED on pieces 2–8. Piece 1 is the unswapped control. H2 not needed (no centroid comparison run).**

### Assignment path (spike)
- `mesh_processing_headless.cpp:1680` — clusters sorted by size descending (`myobject3`, `:217-219`).
- `:1704` — `mergeClusters` runs before assignment.
- `:1755-1769` — `clusters[0]` (largest) → `Cluster1`, `clusters[1]` → `Cluster2`; `:1798-1799` → `tmpSurfaceCluster_Improved_0/1.ply`; `:2073-2087` → `_Surface_0/_Surface_1.xyz`.
- `:1733` `checkNormalsIntersection` only flips ALL normals globally, never swaps the assignment.
- Mechanism: Surface_0/Surface_1 labels derive purely from cluster-size rank — no interior/exterior classification anywhere on the path. When the opposite wall wins the size race, the labels come out swapped. Piece-dependent (piece 1 kept authors' labelling), not a systematic flip.

### Cross-pair numbers (laptop-only, at GT from `artifacts/untouched_pota_verify_20261015/task3_gt/`)
Fresh = untouched d5ee6865 run (`.../sfs_preprocessing/untouched_pota_verify_20261015/Dataset/Surfaces/Pot_A/`, fetched to `%TEMP%\swaptest\fresh\`); ORIG = authors' sample (`.../sfs_main/original_samples/SfS_pp/Surfaces/`, fetched to `%TEMP%\swaptest\orig\`). Metric = task3_persherd-style median fresh→ORIG NN displacement + median offset xyz + normal-sign check (median cos of GT-rotated matched normals, % cos>0). Script: `%TEMP%\swaptest\swaptest.py` (numpy/scipy, conda python).

| piece | straight S0-S0 med (mm) | straight S1-S1 med (mm) | straight normal sign | crossed S1-S0 med (mm) | crossed S0-S1 med (mm) | crossed normal sign |
|---|---|---|---|---|---|---|
| 1 (control) | 0.30 | 0.30 | agree (+1.000, 100%) | 7.09 | 7.80 | oppose (−0.98, 0%) |
| 2 | 3.65 | 3.65 | oppose (−0.998, 0%) | 0.30 | 0.29 | agree (+1.000, 100%) |
| 3 | 3.69 | 3.68 | oppose (−0.998, 0%) | 0.29 | 0.29 | agree (+1.000, 100%) |
| 4 | 3.67 | 3.67 | oppose (−0.999, 0%) | 0.30 | 0.30 | agree (+1.000, 100%) |
| 5 | 3.78 | 3.78 | oppose (−0.998, 0%) | 0.30 | 0.30 | agree (+1.000, 100%) |
| 6 | 3.57 | 3.57 | oppose (−0.998, 0%) | 0.30 | 0.30 | agree (+1.000, 100%) |
| 7 | 3.97 | 3.93 | oppose (−0.998, 0%) | 0.30 | 0.30 | agree (+1.000, 100%) |
| 8 | 3.63 | 3.63 | oppose (−0.998, 0%) | 0.31 | 0.31 | agree (+1.000, 100%) |

Median offsets on straight pairings carry the known +Z signature (e.g. p2 S0-S0 dz +2.65, p7 dz +3.66); crossed offsets are 0.00 mm on all axes. Fresh clouds ~3.3× denser than ORIG (e.g. p1 64661 vs 19463 pts) — density differs, geometry matches.

Reading: on pieces 2–8 the crossed pairing sits at 0.29–0.31 mm with normals agreeing everywhere, while straight sits at ~3.6–4.0 mm with normals opposing everywhere — fresh Surface_0 IS the authors' Surface_1 and vice versa. Piece 1 is the mirror image (straight 0.30 mm, crossed ~7–8 mm wall-to-wall), proving the metric discriminates and the swap is piece-dependent, not a global flip.

No geometry was moved and nothing was rendered (comparison-only; AGENTS.md render rule applies to geometry-changing ops).
