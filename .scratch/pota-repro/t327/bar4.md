

### Bar 4 — causality proof on copies: the swap moves three of five, not five

**Setup.** Run dir `/data/gpfs/projects/punim2657/SfSpp/runs/20261110-2028_1b131dc_t327-swap`, job
**34687732** (partition sapphire, 24 cpus, 64G, COMPLETED 0:0, 44 s). `work/trees/juglet_GT_ctrl` is a
byte-identical copy of the 326 Juglet GT tree (`20261110-1640_22151d0_t325-juglet/work/trees/juglet_GT_r1`);
`juglet_SWAP` differs from it in **exactly 12 files** — `Surface_0`/`Surface_1`/`Breakline_0`/`Breakline_1`
for pieces 2, 6, 9 — with `Surface_0<->Surface_1` swapped and `Breakline_0` replaced by the t66 `Bl1` (the walk
on the other wall). Source tree untouched (`Surfaces+Breaklines` md5 `2c0c39c37d3311e97d9bb79c08c4c7de` =
ctrl copy; swap tree `4fd20b5ea6babe5aa8eaad6ffe08e682`). Harness shipped byte-identical to what 326 ran
(`diag326_pairs.cpp` `4486b2d31b0194b5f0d3555fd73cfbdd`, `diag326.sh` `fb48c6ef741dacc853827136a4a0e299`),
same SIF (`63a532b9732f84e59e7b1349065f1323`), 20 mm floor, `-DJUGLET_ORIG`, three labels: `jug_GTctrl`,
`jug_SWAPr1`, `jug_SWAPr2` (the last two are the same tree twice — they returned **identical** numbers, so the
harness is deterministic here). Outputs in `artifacts/pota327/swap/`, parser `.scratch/pota-repro/t327/parse_bar4.py`
-> `artifacts/pota327/swap/bar4_pairs.json`.

**The five formerly-failing pairs at GT** (`dot_med_d3` = median n·n over the strict-gate correspondence set,
+1 = the two walls agree; n = that set's size):

| pair | gap mm | ctrl dot / n (neg) | swap dot / n (neg) | strict n_dot07 | verdict |
|---|---|---|---|---|---|
| 1-2 | 1.1030 | −0.896 / 10 (10) | **+0.704 / 13** (0) | 7 | PASS |
| 1-9 | 2.1244 | −0.945 / 8 (8) | **−0.039 / 7** (4) | 0 | **FAIL** |
| 2-5 | 2.9096 | −0.991 / 1 (1) | **+0.948 / 1** (0) | 1 | PASS |
| 6-7 | 0.3570 | +0.106 / 16 (6) | **−0.183 / 15** (10) | 0 | **FAIL** |
| 7-9 | 1.7941 | −0.674 / 4 (4) | **+0.708 / 3** (0) | 2 | PASS |

Same-wall reference pairs, which the swap must not touch: 1-4 +0.786 -> +0.786, 1-8 +0.971 -> +0.971,
2-9 +0.991 -> +0.971, 3-5 +0.987 -> +0.987. Pairs with no correspondence are unchanged (−1.000/0): 1-5, 1-6,
3-7, 4-5, 4-6, 5-9, 7-8, 8-9; the only other move is 6-8, which gains one inlier (−1.000/0 -> +0.637/1).

**The bar is met on 3 of 5, and fails on 1-9 and 6-7.** Bar 4's criterion is all five at ≥ +0.7 with strict-gate
inliers > 0; 1-9 lands at −0.039 with four of seven correspondences negative and no strict inlier, 6-7 at
−0.183 with ten of fifteen negative and no strict inlier. Both are much closer to zero than the control, and
both gaps shrank (1-9 2.124 -> 0.998 mm, 6-7 0.357 -> 0.809 mm), so the swap is doing something on all five —
it is not sufficient on two.

**The swap really took effect (the harness's own per-piece rows, not my bookkeeping).** Columns `bl_r_med`
(radius of the loaded `Breakline_0` about the piece's own aligned axis), `n_radial_pos_frac`, `d_sur0_med`,
`r_sur0_med`, `r_sur1_med`:

| piece | ctrl `bl_r_med / frac / d_sur0 / r_sur0 / r_sur1` | swap |
|---|---|---|
| 2 | 16.777 / 1.00 / 0.329 / 16.897 / 15.184 | 15.253 / 0.00 / 0.313 / 14.992 / 16.957 |
| 6 | 16.654 / 1.00 / 0.294 / 16.795 / 14.531 | 14.506 / 0.00 / 0.314 / 14.498 / 16.846 |
| 9 | 16.798 / 1.00 / 0.289 / 16.858 / 15.230 | 14.905 / 0.17 / 0.302 / 14.778 / 16.919 |

The line moved to the other wall, stayed on its own surface (d_sur0 stays ~0.3 mm), and the loaded line's
radial sign flipped. Untouched pieces 1/5/7 have identical rows in ctrl and swap.

**Why two pairs still fail — the wall side is no longer the residual; the stored normal sign is.**
`.scratch/pota-repro/t327/blnormals327.py` reads the sign of every exported line's stored normals against the GT
radial direction (fraction outward, mean n·r̂): `Bl0` **is exactly the wall side** on 9/9 (all three offenders'
`Bl0` mean n·r̂ = +0.987 P2, +0.973 P6, +0.989 P9 — outward, because they ride the outer wall), but the two walks
do **not** share a per-piece sign convention: `Bl1` is inward on 1, 2, 6, 9 and **outward on 3, 4, 5, 7, 8**
(P7: frac 0.983 outward). The two-walk writer stores whatever sign its surface carried; nothing normalises it
to a slot-0 (interior) convention. A slot swap therefore moves the geometry but cannot guarantee that the two
lines' stored normals agree at every pairing. Locally (`pairprobe327.py`, placement convention verified to
reproduce the harness `gap_min` exactly as `inv(T_y) T_x`): after the swap, piece 1's matched points are clean
inward (−0.93..−1.00) and piece 9's swapped-in line runs −0.74..+0.07 (mixed), while piece 6's matched points
are clean inward and **piece 7's untouched line** swings −0.80..+0.61 across zero at both ends of the matched
run — i.e. in both failing pairs the mixed-sign line is the partner, not the piece I swapped.
Bar 4b tests that directly.
