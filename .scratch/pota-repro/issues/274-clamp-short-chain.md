# 274 — Short chains crash the splitter: clamp the k=20 neighbour loop

Answers: E1
Status: results-in
Working in: C:/PR/worktrees/sfs/273 (worktree at e060f87); main read-only, NO main commits
Needs-eye: no

## Why

Ticket 273 step A named the Pot_C_01 segfault: SIGSEGV at `edgeline_extraction_headless.cpp:2257`
inside `detectSeparateLineSegments(std::string, int)`, reached from `processFragmentData`
(:3377) and `main` (:3700). The faulting read is
`rawBreaklinePts->points[nn_indicesAll[i]].x` with a garbage index, and the garbage index comes
from an **out-of-range read of the neighbour arrays**, not from a null cloud.

Mechanism: `:2239` calls `tree_->nearestKSearch(pt, 20, nn_indices, nn_dists)` on a cloud that may
hold fewer than 20 points. PCL 1.9 `kdtree_flann.hpp:139-143` clamps `k` and **resizes both
vectors down** to the cloud size, but the loop at `:2240` still reads slots `11..19`
(`operator[]` is unchecked). A garbage float <= 1.8 in that heap tail is pushed into
`nn_indicesAll`, and `:2257` then indexes the point cloud with it.

This is **pre-existing released code**, not something the recent strip touched: the same failure was
already recorded in ticket 216 (2026-10, "walk collapses to 10-pt CompleteBreakline, then segfault in
segment handling") and again as the "KDF-only single occurrence" in ticket 248. It stayed latent
because a short chain used to be rare. The stop-at-the-weld rule makes short chains ordinary, so it
now fires on Pot_C_01 every time (4/4 reproductions on one frozen sheet pair).

## Goal

Clamp the neighbour loops to the count the search actually returned, so a short chain cannot read
past the end of the arrays. Then prove the change is invisible on healthy clouds.

## Boundary

- `edgeline_extraction_headless.cpp` only, in the 273 worktree. No mesh-stage change, no theta
  change, no RNG change.
- **No env switch.** Reading uninitialised slots is undefined behaviour, not a feature: when the
  cloud holds >= k points the clamped loop is identical, so there is nothing to preserve. The
  justification belongs in the commit message, not behind a flag.
- Sweep for every other hard-coded-k read of the same shape (`for (size_t i = 0; i < 20; i++)` over
  `nn_indices`/`nn_dists` after a `nearestKSearch`) and fix them together, or state why a site is
  safe.

## Acceptance

1. Pot_C_01 on the frozen pair (Surface_0 md5 5c012f0bb17bc620fc39ce7525dcd9bb, Surface_1 md5
   d50d499de4e6e2a19a4fdc230a471350, SampledWithNormals.ply md5 8fdc8afdc9215b42491aea0febe33691)
   runs to completion, writes breakline files, exit 0 — instead of exit 139.
2. **Bit-identity gate:** on the six guard lanes (P03 Bl0/Bl1, P22 Bl0/Bl1, P01 Bl0/Bl1) the fixed
   binary produces the same breakline positions as the shipped one (`max|dxyz| = 0`, same n).
3. Every edited site quoted with its line number, and the sweep result (count of remaining
   hard-coded-k reads, and why each is safe).
4. No change to any score on any lane that already ran.

## Evidence to report

The diff; the Pot_C_01 run log showing exit 0 and the breakline point count; the six-lane identity
table; job ids with sacct State/ExitCode.

## Results (2026-10-24)

Status: results-in. Fix is in the 273 worktree, uncommitted, `edgeline_extraction_headless.cpp` only,
9 insertions / 5 deletions. No env switch, no theta change, no RNG change, no mesh-stage change.

### The fix

The crash site (`:2237-2250`, indentation as in the file):

```diff
@@ -2236,14 +2236,18 @@ void detectSeparateLineSegments(string b1_FilePath, int len = 10)
 		for (size_t i = 1; i < smoothedSegment->points.size() - 1; i++)
 		{
-			tree_->nearestKSearch(smoothedSegment->points[i], 20, nn_indices, nn_dists);
-			for (size_t i = 0; i < 20; i++)
+			// POTA-274: nearestKSearch clamps k to the cloud size and shrinks both
+			// result vectors (PCL 1.9 kdtree_flann.hpp:139-143). Walk only what came
+			// back: reading the k=20 slots regardless indexed a short chain's heap
+			// tail and segfaulted at :2257 (garbage dist <= 1.8 -> garbage index).
+			const int nnFound274 = tree_->nearestKSearch(smoothedSegment->points[i], 20, nn_indices, nn_dists);
+			for (int j = 0; j < nnFound274; j++)
 			{
-				if (nn_dists[i] <= 1.8)
+				if (nn_dists[j] <= 1.8)
 				{
-					nn_indicesAll.push_back(nn_indices[i]);
+					nn_indicesAll.push_back(nn_indices[j]);
 				}
-				//rawBreaklinePtsInSegment->points.push_back(rawBreaklinePts->points[nn_indices[i]]);
+				//rawBreaklinePtsInSegment->points.push_back(rawBreaklinePts->points[nn_indices[j]]);
 			}
 		}
```

Note the loop variable is now `j`: the inner `i` shadowed the outer point index, so `nn_dists[i]`
was indexed by the *neighbour* slot only by accident of the shadowing. Bounding by `nnFound274`
makes the shadow irrelevant.

### Sweep: every other kdtree result read in this file

`grep -n 'nearestKSearch\|radiusSearch' edgeline_extraction_headless.cpp` (fixed file) returns nine
sites. Eight are already bounded by the count the search returned:

| site | call | loop bound | verdict |
|---|---|---|---|
| :592 | `radiusSearch(pt, COMP_GAP_MM, nb, nd)` | `k < nn` | safe |
| :649 | `nearestKSearch(pt, 50, idx, dist)` | `k < found` (heading branch and exhaustive fallback) | safe |
| :896 | `nearestKSearch(currentPoint, K, ...)` | `k < found` | safe |
| :980 | `radiusSearch(bag->points[cur], CGAP, nbr, dist) > 0` | `k < nbr.size()` | safe |
| :1142 | `nearestKSearch(pt, K218, aIdx218, aDist218)` | `kk < aFound218` | safe |
| :1189 | `nearestKSearch(pt, K218, cIdx218, cDist218)` | `kk < cFound218` | safe |
| :1271 | `nearestKSearch(searchPoint, K, ...) > 0` | `j < pointIdxNKNSearch.size()` | safe |
| :2998, :3255 | `radiusSearch(searchPoint, radius, ...) > 0` | `i < pointIdxRadiusSearch.size()` | safe |
| :2243 | `nearestKSearch(..., 20, ...)` | `j < nnFound274` | **this fix** |

`grep -n 'i < 20' edgeline_extraction_headless.cpp` is now empty: no hard-coded-k read remains.

Residual, **not touched** (different shape, no index read): `:2237`
`for (size_t i = 1; i < smoothedSegment->points.size() - 1; i++)` underflows when the segment cloud is
**empty** (`size() - 1` wraps to `SIZE_MAX`), which would walk off the end. A one-point cloud is fine
(`0`, no iterations). Worth a follow-up only if an empty segment is reachable; the clamp does not
affect it either way.

### Evidence 1 — Pot_C_01 runs to completion (was exit 139, 4/4 reproductions)

Frozen pair, as named in Acceptance: `Temp/Data/Pot_C/Pot_C_Piece_01_Surface_0.xyz` md5
`5c012f0bb17bc620fc39ce7525dcd9bb`, `..._Surface_1.xyz` md5 `d50d499de4e6e2a19a4fdc230a471350`,
`..._SampledWithNormals.ply` md5 `8fdc8afdc9215b42491aea0febe33691`. Shipped defaults, no behaviour env.

```
EXIT=0                       (shipped binary: EXIT=139, zero breakline files, 4/4)
Pot_C_Piece_01_Breakline_0.pcd: POINTS 11      11 rows in Breakline_0.xyz, stepring 0 rows
Pot_C_Piece_01_Breakline_1.pcd: POINTS 82      82 rows in Breakline_1.xyz, stepring 0 rows
[VOTE-247] ON (paper CCW vote-order)
[FULL-263] no-discard kept 1000/1000 (4 comps @ 5mm)
[STOP-267] CHAIN-END step=88 of 1000: nearest fresh dot 12.6104mm > R=12mm ; refusing it ; left=911 dots unvisited
[FULL-263] chain=89 maxjump=10.4107mm
[FULL-263] kept chain order n=89 (clock sort skipped)
[VOTE-247] chain=89 turnSum=-1.57241 CW-reversed-to-CCW
[VOTE-247] resampled=14 (L=25.7448mm) corners=0 thr=11.1077 med=3.70257 idx=[]
```

The 11/82 is the walk's own output for this piece under the stopped chain (14 resampled dots on
Breakline_0); it is not a healthy count and is not claimed to be one — 274 only has to stop the crash.

### Evidence 2 — bit-identity gate on the six guard lanes: PASS

Same trees, same frozen sheets, shipped `db7cebb78ed9fc1d69d3622a7fc1ce17` vs fixed
`d20d2a6a75285913fdb8cd5fd9f995bc`. `max|dxyz|` computed both pointwise (same order) and over the
sorted point sets:

| piece | lane | n shipped | n fixed | max\|dxyz\| pointwise | max\|dxyz\| sorted | verdict |
|---|---|---|---|---|---|---|
| P03 | Bl0 | 216 | 216 | 0.000000 | 0.000000 | IDENTICAL |
| P03 | Bl1 | 339 | 339 | 0.000000 | 0.000000 | IDENTICAL |
| P22 | Bl0 | 131 | 131 | 0.000000 | 0.000000 | IDENTICAL |
| P22 | Bl1 | 143 | 143 | 0.000000 | 0.000000 | IDENTICAL |
| P01 | Bl0 | 334 | 334 | 0.000000 | 0.000000 | IDENTICAL |
| P01 | Bl1 | 346 | 346 | 0.000000 | 0.000000 | IDENTICAL |

`IDENTITY GATE: PASS (all six guard lanes identical)`. P22's 131/143 differ from the 271 table only
because 271's accepted run was a different mesh draw; both binaries here saw the same sheets.

### Build and jobs

- Fixed source: `src274fix` = the 67ff3d7 sources plus this diff, `edgeline_extraction_headless.cpp`
  md5 `8264da3647d048e67d983edfe810b59d` (LF). Built Release in
  `build-67ff3d7/fix274` inside `pcl_191_nurbs.sif`; binary md5 `d20d2a6a75285913fdb8cd5fd9f995bc`.
  The shipped build directory was not touched.
- `33732190` p273A1 COMPLETED 0:0 — crash reproduction, shipped binary, 4/4.
- `33732191` p273Abuild COMPLETED 0:0 — `-g` build used for the readable backtrace.
- `33732230` p273A2 COMPLETED 0:0, `33732255` p273A3 COMPLETED 0:0 — same PC both builds, fault at
  `:2257`, index 12 of 11 valid slots.
- `33732363` p273gate2 COMPLETED 0:0 — this run: C01 exit 0 plus the six-lane identity gate.

### Not done here

The fix is **not in any shipped binary** and is not committed. It is validated as `67ff3d7 + clamp`;
the attribution matrix for ticket 273 runs on that binary and says so in its table.


## Lead verdict (2026-10-24) — accepted and landed

The defect is real and pre-existing. `nearestKSearch(smoothedSegment->points[i], 20, nn_indices, nn_dists)`
clamps k to the cloud size and shrinks both vectors (PCL 1.9 `kdtree_flann.hpp:139-143`), while the loop walked
all 20 slots regardless. On an 11-dot breakline the slots past 11 held heap tail; one stale distance passed the
1.8 mm test and the stale index faulted at `:2257`.

The clamp is the whole fix, and it is narrow: when the chain holds >= 20 dots the loop body is unchanged
(slot i still reads `nn_dists[i]` / `nn_indices[i]`), which is why the six guard lanes come back pointwise
identical rather than merely close. Below 20 it now walks what the search actually wrote. Pot_C_01 exits 0
instead of 139.

Residual noted, deliberately untouched: `:2237` `i < points.size() - 1` underflows on a one-dot chain. It is
not reachable from the pipeline today (the shortest chain observed is 11 dots) and is recorded here rather than
patched blind.

Landed with ticket 273 in the commit that ships the clamp.
