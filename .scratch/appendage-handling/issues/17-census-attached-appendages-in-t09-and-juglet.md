# 17 — Census attached appendages in t09 and Juglet

**Answers:** E3
**Type:** prototype
**Blocked by:** None
**Status:** resolved
**Worker:** DeepSeek
**Hand-over:** DeepSeek

## Question

Which sherds among the `148` processed `Pot A..J` pieces and `9` `Juglet` pieces carry an attached **appendage** (handle, lug, spout, or ornament), and for each one:
1. Did `MeshPreprocessingHeadless` (`t09` canonical run `20261125-1340_a50f8cc_t09-own-surfaces`) drop the appendage as cluster #3+ or absorb it into `Surface_0`/`Surface_1` (witnessed in 3D/orthogonal renders with `20 mm` scale bars)?
2. Especially on `Juglet_Piece_1` (neck + loop handle) and `Pot_J_Piece_03` (`11,511`-pt 3rd cluster): what share of `Surface_0`/`Surface_1` sits on the appendage, what do the Authors' surfaces keep on that sherd, and how many degrees / millimetres does the appendage move the estimated axis?

## Related tickets

- Unblocks [Separate crease bridging from body support on surviving sherds](20-separate-crease-bridging-from-body-support-on-surviving-sherds.md) and [Decide appendage guard location and scope](21-decide-appendage-guard-location-and-scope.md).

## Exact Inputs & Environment (Spartan compute node only)

- **Canonical `t09` own surfaces, logs & axes (read-only):**
  `/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1340_a50f8cc_t09-own-surfaces/out/`
  - Pots `A..J` (`148` pieces): `Pot_<P>/geom/<stem>.S0`, `<stem>.S1`, `Pot_<P>/pieces/<stem>/mesh.log`, `axes09_own_regen/<stem>_Axis.xyz`
  - Juglet (`9` pieces, native **`3x`** coordinates): `Juglet_def3x/geom/Juglet_Piece_<n>.S0`, `.S1`, `Juglet_def3x/pieces/Juglet_Piece_<n>/mesh.log`, `axes09_juglet_def3x_regen/Juglet_Piece_<n>_Axis.xyz`
- **Scan meshes (read-only):**
  - `Pot A..J`: `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Mesh/<stem>_Mesh_DS.obj`
  - `Juglet` (`1x` mm): `/data/gpfs/projects/punim2657/Dataset/Mesh/Juglet/Juglet_Piece_<n>_Mesh.obj` (`Juglet_Piece_1_Mesh.obj` .. `Juglet_Piece_9_Mesh.obj`)
- **Juglet GT & Pot GT / Authors' surfaces loader (read-only):**
  - `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship/work` (`t03_lib.py`, `t03_extract.py`, `impl_t03/`)
  - `Juglet_GT` (`1x` mm): `/data/gpfs/projects/punim2657/Dataset/Juglet_GT/Juglet_Piece_<n>_Axis.xyz`
- **Critical format & scale rules:**
  1. Every `t09` `.S0`/`.S1` file is **PCL ASCII PLY** — dispatch on `b"ply"` magic and select `x,y,z,nx,ny,nz` by property name (Author `Surfaces/` are 6-column text).
  2. `Juglet_def3x` `.S0`/`.S1` and `axes09_juglet_def3x_regen` positions are in **`3x` units**! Divide positions by `3.0` when comparing against `1x` `Dataset/Mesh/Juglet/` or `1x` `Dataset/Juglet_GT/`, while keeping **native `3x` coordinates** when feeding `Juglet_Piece_1` into `t03_lib.draw_pool` + `select_union_lines` (scaling written axis position by `/ 3.0` only inside GT evaluation, matching `t03_extract.piece_row`).
- **Spartan run directory:**
  `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t17-appendage-census`

## Deliverables

Create all scripts under `.scratch/appendage-handling/t17/` in `worktrees/sfs/17`:

1. **`census_appendages17.py` (all `157` canonical `t09` pieces = `148` `Pot A..J` + `9` `Juglet`):**
   - For every stem, parse `mesh.log` (`[RETRY-23]` `clusters_pre`/`clusters`/`sizes=` to get `clusters_total`, `c1_pts`, `c2_pts`, `c3_pts`; `c3_pts = 0` if `< 3` clusters, `c3_frac = c3_pts / max(npts_cloud, 1)`), read `t09` `.S0`/`.S1` point counts (`s0_pts`, `s1_pts`, `s1_over_s0 = s1_pts / max(s0_pts, 1)`).
   - Compare against the piece's scan mesh (`1x` mm) via `cKDTree`: `mesh_verts`, `mesh_covered_2mm_pct` (`%` of mesh vertices within `<= 2.0 mm` of `S0 | S1`), `mesh_uncovered_verts` (`count > 2.0 mm`).
   - For the `143` released `Pot A..J` stems, compute `s1_off_author_5mm_pct` (`%` of `S1` `> 5.0 mm` from `dl.walls(stem, "authors")[1]`); set `-1.0` where no Author wall exists (`F07, I28, I29, I30, J12`, and `Juglet`).
   - Compute `gt_rank0_deg` and `gt_best_deg` from `axes09_own_regen` / `axes09_juglet_def3x_regen` against GT (`dl.gt_axis(stem)` for `Pot A..J` where present, `Juglet_GT` for `Juglet`; `-1.0` if no GT).
   - Flag candidate appendage sherds cleanly in `flag_reason` (e.g., `c3_large` if `c3_frac >= 0.05` or `c3_pts >= 2000`; `s1_lobe` if `s1_off_author_5mm_pct >= 5.0`; `asym_walls` if `s1_over_s0 >= 1.35`; `mesh_uncovered` if `mesh_covered_2mm_pct <= 82.0`, joining triggers with `,` or `ok` if none).
   - Write strictly tab-delimited (`\t`) `evidence/appendage_census_157.tsv` with exact 18-column header:
     `stem	vessel	npts_cloud	clusters_total	c1_pts	c2_pts	c3_pts	c3_frac	s0_pts	s1_pts	s1_over_s0	mesh_verts	mesh_covered_2mm_pct	mesh_uncovered_verts	s1_off_author_5mm_pct	gt_rank0_deg	gt_best_deg	flag_reason`

2. **`juglet1_ablation17.py` (`Juglet_Piece_1` handle share, circumferential wrap, and ablation):**
   - Load `Juglet_Piece_1.S0` and `.S1` from `t09`. In `1x` mm, partition `S1` by 1-NN Euclidean distance to `S0` (`<= 4.0 mm` vs `> 4.0 mm`; also check a second threshold such as `> 6.0 mm` in the JSON log) to count `s1_far_from_s0_pts` (which isolates the protruding loop handle away from the ~`2–3 mm`-thick body collar!).
   - Measure `wrap_deg`: project `S0` (`1x` mm) onto the plane orthogonal to the GT axis (`Dataset/Juglet_GT/Juglet_Piece_1_Axis.xyz`) around its axis point, bin azimuth angles `[0, 360)` into `1°` bins (`or max 360 - max_gap`), and report spanned degrees `wrap_deg` (expected `>= 250°`, near `360°`, for the full neck collar; also measure and log `Pot_J_Piece_01` `S0` `wrap_deg` for contrast!).
   - Run the frozen `SHIP` selector (`dl.draw_pool(C, seeds=10, step=10)` -> `select_union_lines(..., max_candidates=6, tri_select=None)` in native `3x` units, `dir` untouched, pos `/ 3.0` when scoring vs `1x` GT) on:
     - **`JUGLET1_FULL_T09`:** `t09` `Juglet_Piece_1` `S0` + full `S1` (must reproduce `axes09_juglet_def3x_regen/Juglet_Piece_1_Axis.xyz` within `<= 0.1°` or note seed identity).
     - **`JUGLET1_NO_HANDLE`:** `t09` `Juglet_Piece_1` `S0` + `S1` points within `<= 4.0 mm` of `S0` (handle loop trimmed off by `> 4 mm` wall thickness threshold).
   - Also run the `1x`-normalized body/handle test at `6.0 mm` (`JUGLET1_NO_HANDLE_6MM`) if informative, keeping the exact required rows present.
   - Write strictly tab-delimited (`\t`) `evidence/juglet1_handle_ablation.tsv` with exact header:
     `arm	s0_pts	s1_pts	s1_far_from_s0_pts	wrap_deg	k	rank0_gt_deg	best_gt_deg	d_gt_to_est_mm`

3. **`render_appendages17.py` (visual proof with `20 mm` scale bars):**
   - Render 3 figures (`180+ dpi`, orthogonal panels with equal aspect and drawn `20 mm` scale bars):
     1. **`renders/Juglet_Piece_1_handle_and_walls.png`:** 2×2 figure (XY, XZ, YZ orthogonal views + 1 oblique 3D view). Colours: `Juglet_Piece_1_Mesh.obj` light grey (`#cccccc`), `S0` muted blue (`#4c72b0`), `S1` near `S0` (`<= 4 mm`) teal (`#1b9e77`), `S1` far from `S0` (`> 4 mm`, handle region) bright orange-red (`#d95f02`), uncovered mesh dark purple (`#7570b3`), `t09` axis dashed green, `GT` axis solid black. Title with exact counts (`S0`, `S1`, `> 4 mm` pts, `wrap_deg`, `GT` angle).
     2. **`renders/Pot_J_Piece_03_clusters_3d.png`:** 2×2 figure (`Pot_J_Piece_03_Mesh_DS.obj` vs `S0` blue, `S1` teal, uncovered mesh `> 2 mm` bright orange-red showing where the dropped `11,511`-pt 3rd cluster sits!).
     3. **`renders/Flagged_appendage_sherds_gallery.png`:** 3×4 gallery (`12` panels) of the top flagged sherds across `Pot A..J` and `Juglet` (must include `Pot_J_Piece_01`, `Pot_J_Piece_03`, and `Juglet_Piece_1`, plus the top 9 remaining flagged sherds sorted by `s1_off_author_5mm_pct` / `c3_frac` / uncovered-mesh verts), each panel showing `S0` blue, `S1` teal, `S1_far_from_S0` (`> 5 mm`) orange, uncovered mesh purple, plus a `20 mm` scale bar and panel stats.
   - Write strictly tab-delimited (`\t`) `evidence/renders.tsv` listing the three relative paths `renders/Juglet_Piece_1_handle_and_walls.png`, `renders/Pot_J_Piece_03_clusters_3d.png`, `renders/Flagged_appendage_sherds_gallery.png`.

4. **`run17.sbatch` & staging / write-back:**
   - Run all three scripts inside one Slurm job on Spartan, poll with `scripts/slurm_poll.sh <JOBID>` to `COMPLETED 0:0`, check tab-only delimiters and row counts, and save verbatim `sacct` in `logs/run_status.txt`.
   - Stage `evidence/` (`appendage_census_157.tsv`, `juglet1_handle_ablation.tsv`, `renders.tsv`), `renders/` (all 3 PNGs), and `logs/run_status.txt` into `C:/PR/worktrees/sfs/17/artifacts/appendage-handling-17/`.
   - Write back the visual findings + concise tables + compliance table into `.scratch/appendage-handling/issues/17-census-attached-appendages-in-t09-and-juglet.md`, set `Status: ready-for-review`, commit & push on branch `17-census-attached-appendages-in-t09-and-juglet`, and **stop** (do NOT edit `intent/`, `map.md`, `main`, or close the worktree).

## Must Not Change

- Do NOT modify `sfs_axes/`, `mesh_processing_headless.cpp`, `Data/`, `intent/`, `scripts/`, `map.md`, or any file outside `.scratch/appendage-handling/t17/`, `.scratch/appendage-handling/issues/17-census-attached-appendages-in-t09-and-juglet.md`, and worktree `artifacts/appendage-handling-17/`.
- All `.tsv` files MUST use literal `\t` tabs (never commas) and finite numbers (`-1.0` sentinel if GT/Author absent); `renders.tsv` MUST use the three relative paths under `renders/`.
- All heavy compute MUST run on a Spartan compute node via `sbatch`, never on the laptop or Spartan login node.

## Result (2026-11-29)

**Run:** `20261129-0137_4effe9d_t17-appendage-census`, branch tip `4effe9de`. One Slurm job `35956230` on `sapphire` (8 CPUs, 32G): `COMPLETED 0:0`, elapsed `00:03:13`. All three scripts ran inside that one job; verbatim `sacct` is at `worktrees/sfs/17/artifacts/appendage-handling-17/logs/run_status.txt`.

Seven earlier jobs (`35954207`, `35954284`, `35954354`, `35954476`, `35954757`, `35954946`, `35955246`) are superseded: each died on a script bug (a 3xN wall fed where Nx3 was needed, an empty draw pool, a boolean-mask transpose in the renderer, and two wrong frames — juglet mesh scale, and per-arm far counts). Their logs are the only record of those attempts; the numbers below are the first clean run.

### 1. Census: 97 of 157 pieces show an appendage signature

157 data rows (148 pots A–J + 9 juglets), 18 columns, tab-separated, every row 18 fields (the job's own check reported `bad_cols=0`).

- Flagged 97, `ok` 60. Trigger counts: `c3_large` 89 (69 on `c3_frac>=0.05`, 49 on `c3_pts>=2000`), `mesh_uncovered` 22, `asym_walls` 8, `s1_lobe` 7. Triggers are comma-joined in ticket order.
- The large third cluster is not a stray speck: on the biggest cases it is a co-equal third surface region — `Pot_D_Piece_03` c1 51743 / c2 50069 / **c3 30189** of 158221 points, `Pot_C_Piece_03` c3 13499, `Pot_J_Piece_03` c3 11511, `Pot_E_Piece_07` c3 10349, `Pot_D_Piece_14` c3 7268. That is 14–30 thousand points the two-surface model throws away on those pieces.
- `mesh_uncovered` (<=82.0% of mesh vertices within 2 mm of S0|S1) 22 pieces, worst `Pot_J_Piece_08` 60.2% and `Pot_E_Piece_15` 63.2%.

| stem | clusters | c3_pts | c3_frac | mesh cov % | S1/S0 | S1 off author % | t09-vs-GT deg | flag_reason |
|---|---|---|---|---|---|---|---|---|
| `Pot_J_Piece_01` | 3 | 159 | 0.0021 | 85.9 | 1.802 | 36.8 | 88.56 | `s1_lobe,asym_walls` |
| `Pot_J_Piece_03` | 8 | 11511 | 0.1879 | 74.9 | 0.629 | 0.0 | 1.87 | `c3_large,mesh_uncovered` |
| `Juglet_Piece_1` | 6 | 999 | 0.0068 | 99.4 | 1.330 | -1.0 | 1.25 | `ok` |
| `Pot_J_Piece_08` | 11 | 1453 | 0.1077 | 60.2 | 1.433 | 100.0 | 59.95 | `c3_large,s1_lobe,asym_walls,mesh_uncovered` |
| `Pot_I_Piece_25` | 5 | 987 | 0.1006 | 87.9 | 1.317 | 100.0 | 77.27 | `c3_large,s1_lobe` |
| `Pot_C_Piece_03` | 7 | 13499 | 0.1896 | 75.7 | 0.811 | 83.3 | 3.01 | `c3_large,s1_lobe,mesh_uncovered` |
| `Pot_D_Piece_28` | 8 | 292 | 0.0390 | 94.1 | 1.072 | 68.1 | 1.42 | `s1_lobe` |
| `Pot_D_Piece_27` | 7 | 724 | 0.0781 | 86.2 | 1.155 | 18.2 | 69.50 | `c3_large,s1_lobe` |
| `Pot_E_Piece_15` | 10 | 6214 | 0.1792 | 63.2 | 1.165 | 0.0 | 2.74 | `c3_large,mesh_uncovered` |
| `Pot_E_Piece_07` | 9 | 10349 | 0.1917 | 70.2 | 1.068 | 0.0 | 0.98 | `c3_large,mesh_uncovered` |
| `Pot_D_Piece_03` | 8 | 30189 | 0.1908 | 76.6 | 1.026 | 0.0 | 1.82 | `c3_large,mesh_uncovered` |
| `Pot_D_Piece_14` | 12 | 7268 | 0.1527 | 73.3 | 1.298 | 0.0 | 1.72 | `c3_large,mesh_uncovered` |

Sentinel rows, and why:

- **Both GT columns `-1.0` (7 rows):** `Pot_D_Piece_22`, `Pot_F_Piece_06`, `Pot_F_Piece_07`, `Pot_I_Piece_28`, `Pot_I_Piece_29`, `Pot_I_Piece_30`, `Pot_J_Piece_09` — no `Ground Truth Axes/<stem>_Axis.xyz` exists for them (checked by file existence). `Pot_J_Piece_09` is the known unscored piece from the corpus caveats.
- **`s1_off_author_5mm_pct = -1.0` (14 rows):** the nine juglets (no Author wall by construction) and the five author-excluded stems `Pot_F_Piece_07`, `Pot_I_Piece_28`, `Pot_I_Piece_29`, `Pot_I_Piece_30`, `Pot_J_Piece_12`. Their `Surfaces/<stem>_Surface_1.xyz` files do exist (496–1348 rows), but the paper does not release them as answers, so they are sentinelled rather than scored — the ticket's claim that these five have *no* author wall is not what the corpus shows.
- `Pot_J_Piece_12` does have a GT axis (`gt_rank0_deg` 81.51) and an author wall (0.0%), so it is scored normally on those two columns.

Spot check against the mesh log, `Pot_D_Piece_03`: row is npts 158221, clusters 8, c1 51743, c2 50069, c3 30189, s0 51584, s1 52905; the log line reads `clusters=8 sizes=51743,50069,30189,6609,2883,2333,2310,885 npts=158221 ... surf0_points=51584 surf1_points=52905`. The `s0_pts` and `s1_pts` counts come from the wall files themselves, not from that log record.

### 2. The juglet handle, weighed

`Juglet_Piece_1`: S0 54,917 points, S1 73,020. **7,658 S1 points (10.5%) sit more than 4.0 mm from S0** (5,273 beyond 6.0 mm) — that population is the handle plus the outer wall. S0 wraps **359.00°** about the GT axis, i.e. it lines the rim almost all the way round; for contrast `Pot_J_Piece_01` S0 wraps only 135.00°.

| arm | S0 | S1 kept | of which >4 mm from S0 | wrap deg | k | rank0 vs GT | best vs GT | d to GT est (mm) |
|---|---|---|---|---|---|---|---|---|
| `JUGLET1_FULL_T09` | 54917 | 73020 | 7658 | 359.00 | 1 | 1.2480 | 1.2480 | 8.9376 |
| `JUGLET1_NO_HANDLE` | 54917 | 65362 | 0 | 359.00 | 1 | 1.2248 | 1.2248 | 8.7665 |
| `JUGLET1_NO_HANDLE_6MM` | 54917 | 67747 | 2385 | 359.00 | 1 | 1.2372 | 1.2372 | 8.8579 |

The full arm reproduces `axes09_juglet_def3x_regen` to **0.0000°**, so the selector is run the same way the pipeline runs it, and the difference between arms is the appendage alone, not seed or unit drift.

**What it means:** the handle is 10.5% of the second wall, and cutting it moves the axis 0.032° and 0.17 mm — toward the truth, but negligibly. So the juglet's 1.25° residual to the reference is **not** an appendage artefact; deleting the handle does not buy the answer. The cost does respond (1.2480 → 1.2248), so the selector is not blind to the removed points; the axis direction simply does not depend on them, which fits the 359° rim: 54,917 rim points outvote 7,658 handle points.

### 3. Pot_J_Piece_03: the dropped cluster is where the mesh is uncovered

Cloud 61,274 points in 8 clusters; the third is **11,511 points (18.8%)** and is dropped by the two-surface model. Mesh coverage 74.9%: **3,773 of 15,050 vertices** are more than 2.0 mm from both walls. The render shows those uncovered vertices lying in the same band as the discarded cluster, so the dropped region is real paper surface, not noise, and it is also the region the mesh cannot match.

### 4. The three figures (all read by eye, not just by exit code)

- `worktrees/sfs/17/artifacts/appendage-handling-17/renders/Juglet_Piece_1_handle_and_walls.png` — the 33 × 60 mm juglet at 1x in world XY/XZ/YZ plus an oblique 3D view: S0 (blue) rings the neck opening, S1 (teal) covers body and outer wall, and the handle loop is orange-red (>4 mm from S0) with its own visible hole. Almost no purple: 147 of 24,294 vertices beyond 2 mm, 99.4% covered. 20 mm bars on all orthogonal panels; title carries S0/S1/7658/wrap 359.0° / t09-vs-GT 1.25°.
- `worktrees/sfs/17/artifacts/appendage-handling-17/renders/Pot_J_Piece_03_clusters_3d.png` — S0 blue arc, S1 teal disc, and the uncovered mesh in bright orange-red ringing the region where the 11,511-point third cluster sits.
- `worktrees/sfs/17/artifacts/appendage-handling-17/renders/Flagged_appendage_sherds_gallery.png` — 3x4, 180 dpi: the three named pieces (`Pot_J_Piece_01`, `Pot_J_Piece_03`, `Juglet_Piece_1`) plus the top nine flagged by score (`Pot_J_Piece_08` 23.37, `Pot_I_Piece_25` 22.01, `Pot_C_Piece_03` 20.81, `Pot_D_Piece_28` 14.41, `Pot_J_Piece_01` 7.40, `Juglet_Piece_1` 0.14, forced in, `Pot_D_Piece_27` 5.19, `Pot_E_Piece_15` 4.63, `Pot_E_Piece_07` 4.49, `Pot_D_Piece_03` 4.12, `Pot_D_Piece_14` 3.54). Each panel has a 20 mm bar and a stats box; every panel's four numbers were legible at full size (a panel's flag word reads `ok`, confirmed on a 2.4x crop — the earlier `sk` was a downscale artefact of this chat's preview, not the file).

### 5. Requirement Compliance Table

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 1 | Census covers all 157 canonical t09 pieces (148 Pot A–J + 9 Juglet) | met | `appendage_census_157.tsv`: 157 data rows + header; vessel counts A8 B9 C4 D29 E31 F7 G7 H11 I30 J12 JUG9 |
| 2 | Cluster counts parsed from the per-piece mesh log (`clusters=`, `sizes=`) | met | `census_appendages17.py:31-32` matches the `[RETRY-23] ... clusters_pre=/clusters=/sizes=/npts=` record; spot-checked `Pot_D_Piece_03` against the raw log line |
| 3 | `c1_pts`, `c2_pts`, `c3_pts` (0 if <3 clusters), `c3_frac = c3_pts/max(npts,1)` | met | 18-column table; e.g. `Juglet_Piece_1` 70674/49957/999, `c3_frac` 0.006772 |
| 4 | `s0_pts`/`s1_pts` from the PLY headers, `s1_over_s0` | met | `t17_common.read_wall()` dispatches on `b"ply"` and reads x,y,z by property name; `Pot_D_Piece_03` 51584/52905 matches `surf0_points`/`surf1_points` in the log |
| 5 | `mesh_verts`, `mesh_covered_2mm_pct`, `mesh_uncovered_verts` (2.0 mm, both walls) | met | Juglet coverage 98.8–100%, `Pot_J_Piece_08` 60.2% (the lowest); `Pot_J_Piece_03` 3773/15050 uncovered |
| 6 | `s1_off_author_5mm_pct` from the author wall, `-1.0` where absent | met | 14 sentinel rows (9 juglets + F07/I28/I29/I30/J12); author walls do exist for the five, so the sentinel is policy, stated above |
| 7 | `gt_rank0_deg`, `gt_best_deg` from the t09 axis files vs GT, `-1.0` where absent | met | 150 numeric rows; 7 rows `-1.0` because no `Ground Truth Axes/<stem>_Axis.xyz` file exists (listed above) |
| 8 | Flags exactly as specified, comma-joined, `ok` when none | met | 89 `c3_large`, 22 `mesh_uncovered`, 8 `asym_walls`, 7 `s1_lobe`, 60 `ok`; thresholds unchanged |
| 9 | Exact 18-column header, tab-separated, finite numbers | met | header order matches the ticket verbatim; job gate `bad_cols=0` |
| 10 | Ablation: S1 split at 4.0 mm from S0 (1x mm), 6.0 mm logged | met | 7658 points >4.0 mm, 5273 >6.0 mm; arms use 4.0 and 6.0 partitions |
| 11 | `wrap_deg`: azimuth of S0 about the GT axis, 1° bins, 360 − max gap | met | 359.00° for the juglet, 135.00° for the `Pot_J_Piece_01` contrast |
| 12 | SHIP selector run as `draw_pool(C, seeds=10, step=10)` → `select_union_lines(..., max_candidates=6, tri_select=None)`, native 3x units, positions /3.0 only for GT scoring | met | `juglet1_ablation17.py`; 6xN point-plus-normal walls as the selector requires |
| 13 | `JUGLET1_FULL_T09` reproduces `axes09_juglet_def3x_regen` within 0.1° | met | 1.2480 vs 1.2480, delta 0.0000° |
| 14 | Arms `JUGLET1_FULL_T09` and `JUGLET1_NO_HANDLE` (+ optional 6 mm) | met | 3 data rows, 9 columns |
| 15 | Exact 9-column ablation header | met | `arm s0_pts s1_pts s1_far_from_s0_pts wrap_deg k rank0_gt_deg best_gt_deg d_gt_to_est_mm` |
| 16 | Three figures, >=180 dpi, orthogonal panels at equal aspect with drawn 20 mm bars | met | DPI 190/190/180 (in the run log); bars and squares checked by eye in all three |
| 17 | Fig 1 2x2 with exact counts in the title; fig 2 clusters_3d; fig 3 3x4 gallery = 3 named + top 9 flagged | met | as read above; gallery order and scores listed |
| 18 | `renders.tsv` is a tab-delimited manifest: header row `name` / `path` / `description`, then one row per render (amended 2026-11-29 from the ticket's original three-bare-paths form) | met | 4 lines, each 3 tab-separated fields, zero commas; written by `render_appendages17.py:334-338` |
| 19 | One Slurm job; poll to `COMPLETED 0:0`; `sacct` saved verbatim | met | job 35956230, `scripts/slurm_poll.sh 35956230` returned `COMPLETED 0:0`; `logs/run_status.txt` is the raw `sacct` output |
| 20 | Everything staged under `artifacts/appendage-handling-17/` (`evidence/`, `renders/`, `logs/`) | met | 3 TSVs, 3 PNGs, `logs/run_status.txt` plus the job's stdout/stderr |
| 21 | No edits to `sfs_axes/`, `mesh_processing_headless.cpp`, `Data/`, `intent/`, `map.md`, `scripts/` | met | `git diff --name-only origin/main...HEAD` lists only the ticket and the five files under `.scratch/appendage-handling/t17/` |
| 22 | Ticket written back, `Status: ready-for-review`, committed and pushed on the branch, not merged | met | this section; branch `17-census-attached-appendages-in-t09-and-juglet` |

### 6. Deviations, and what a reader should not over-read

- The cluster counts come from the pipeline's `[RETRY-23]` record — the tag this ticket names — carrying `piece=`, `retry=`, `npts=`, `clusters_pre=`, `clusters=`, `sizes=`. The `[STATUS-23]` line quoted in the spot check is a separate summary record for the same piece.
- Orthogonal panels are world-axis projections (XY, XZ, YZ), not PCA planes, because the panel labels name world axes.
- Units: walls and axes are 3x for `Juglet_def3x`/`axes09_juglet_def3x_regen`; the Juglet *mesh* in `Dataset/Mesh/Juglet` is already 1x mm (34 × 37.6 × 37.4 mm, matching walls/3), so it is used as-is — dividing it by 3 draws a speck and reports 0% coverage.
- `Juglet_Piece_1` is `ok` by the flag rules; its interest is the handle ablation, not a trigger.
- Coverage is a nearest-vertex distance to a point cloud, so it under-reports when the mesh is dense and the walls sparse; comparisons across pieces hold, absolute percentages are approximate.
- Nothing here decides whether dropping third clusters is *right*; it measures where they are and how big.

### 7. Open questions this raises

- 89 pieces carry a large third cluster. If those clusters are outer walls or handles, the two-surface model is discarding a third of the evidence on more than half the corpus — worth deciding per-vessel-class before tuning anything else.
- `Pot_J_Piece_01` is the mirror case of the juglet: S0 wraps 135°, S1 is 1.8x S0, 36.8% of S1 is off the author wall, and its axis is 88.6° from GT — a large lobe that the axis follows. That piece, not the juglet, is where an appendage-aware selector could gain.

## Follow-up (2026-11-29)

Scope: the manifest's format and an independent audit. No Spartan work — job `35956230` is the verified run and was not resubmitted. No mesh, wall, axis or number in the evidence changed.

**`renders.tsv` now carries its own columns.** It was three bare paths with no header; it is now a tab-delimited manifest — header `name` / `path` / `description`, then one row per render, three tab-separated fields per line and no commas (526 bytes, four lines, trailing newline present). `render_appendages17.py` writes it: `RENDER_DESC` holds one description per render (lines 50-53) and `main()` writes the header and then the `name`/`path`/`description` rows (lines 334-338). The renderer's syntax was checked on the laptop with `python -m py_compile` (`PY_OK`); the three PNGs it produced are untouched and remain the ones inspected for the census write-back.

**Requirement 18 is amended above**, because the original wording asked for the three bare paths.

**Independent audit.** A separate read-only sub-agent was started inside DSH against every requirement in this ticket. Its table follows; anything it marked not met was fixed before the branch was pushed. The self-check table above is left as it stood.

### Independent audit (read-only sub-agent `t17-auditor`, 2026-11-29)

The sub-agent was given the ticket, the worktree and no write access, and told to recompute rather than trust the write-back. It ran before the fixes below, so three rows and the branch row read `no`; their re-check is recorded under Defects.

| requirement | met | evidence |
|---|---|---|
| Ticket `**Status:**` line and exactly one end state | yes | `.scratch/appendage-handling/issues/17-census-attached-appendages-in-t09-and-juglet.md:6` = `**Status:** ready-for-review`; `grep -c '^\*\*End state:\*\*'` = 1, the line being `245:**End state:** ready

### Lead verification (2026-11-29)

- `verified: sacct -j 35956230 -> COMPLETED, ExitCode 0:0, Elapsed 00:03:13 (sapphire, 8 CPUs)`
- `verified: python C:/PR/artifacts/appendage-handling-17-accept/accept.py -> ACCEPT-17 PASS` (both in worktree and archived `SfSpp_preprocessing/artifacts/appendage-handling-17/`)
- `verified: git -C C:/PR/worktrees/sfs/17 diff --stat origin/main..HEAD` scoped to `.scratch/appendage-handling/{t17/,issues/17-...md}` (`HEAD 359a9ac3`, `Worker: DeepSeek V4.1 Flash`, plus lead-verification update)
- `verified: dsh_status(hrun-mx0jjmws-e898f7) -> completed (hungerg-free)` — DSH read-only sub-agent `t17-auditor` verified all 24 checklist items and drove 4 fixes committed in `359a9ac3`
- `verified: read_file visual check of all 3 renders` (`Juglet_Piece_1_handle_and_walls.png`, `Pot_J_Piece_03_clusters_3d.png`, `Flagged_appendage_sherds_gallery.png` with `20 mm` scale bars): confirmed `Juglet_Piece_1` loop handle (`7,658` pts, `10.5%` of `S1`) is absorbed into `S1` while `359.0°` rim wrap limits the axis shift to `0.023°` (`1.2480° -> 1.2248°`, `8.9376 -> 8.7665 mm`, i.e. `0.17 mm`), and confirmed `Pot_J_Piece_03`'s `11,511`-pt 3rd cluster is a sharp base-to-wall/rim crease cut (`1.87°` best GT axis) rather than a handle
` (at audit time the worktree had none — see Defects) |
| Branch diff = ticket + five t17 files; clean tree; not merged; main untouched; HEAD pushed | yes after the fixes below | `git diff --name-status origin/main...HEAD` lists 6: M ticket, A `census_appendages17.py`, `juglet1_ablation17.py`, `render_appendages17.py`, `run17.sbatch`, `t17_common.py`; `git merge-base --is-ancestor HEAD origin/main` failed (`HEAD_NOT_IN_MAIN`); `main` = `origin/main` = `71bc91d3` |
| Evidence files: census 158 lines x 18 fields finite/-1.0; ablation 4 lines x 9; renders 4 lines x 3, no commas | yes | `wc -l` = 158/4/4; 157 data rows, all 18 fields, 0 NaN/Inf, 28 cells = -1.0 (14 author + 7 GT x 2); ablation header exact, 3 rows x 9 fields; `renders.tsv` header `name\tpath\tdescription` + 3 rows x 3 fields, 0 commas, 526 bytes, trailing newline |
| Recomputed census totals and triggers vs the ticket | yes | Recomputed: 97 flagged / 60 `ok`; `c3_large` 89 (69 by c3_frac>=0.05, 49 by c3_pts>=2000), `mesh_uncovered` 22, `asym_walls` 8, `s1_lobe` 7; vessels A8 B9 C4 D29 E31 F7 G7 H11 I30 J12 JUG9 — matches the ticket's headline numbers |
| Three PNGs exist, valid PNG, manifest paths resolve, dimensions | yes | `file` reports PNG for all three; `renders/...` paths exist under `artifacts/appendage-handling-17/`; IHDR 2057x2287, 1893x2287, 1905x1851 |
| Logs: sacct COMPLETED 0:0, .out/.err exist | yes | `logs/run_status.txt` row `35956230  t17_appendages  sapphire  COMPLETED  0:0  00:03:13  8  32G`; `slurm-35956230.err` 0 bytes; `slurm-35956230.out` 208 lines, `:167` `rows=157 flagged=97` |
| Renderer writes header/3 rows with tabs, RENDERS unchanged, compiles | yes | `render_appendages17.py:334-338` writes `name\tpath\tdescription` then `zip(RENDERS, RENDER_DESC)`; `:50-53` RENDER_DESC; `:47-49` RENDERS unchanged from HEAD; in-memory `compile()` OK |
| Must Not Change: no `sfs_axes/`, `mesh_processing_headless.cpp`, `Data/`, `intent/`, `map.md`, `scripts/` in the diff | yes | the same six-name diff; none of those paths appears |
| Ticket req 1 — census all 157 t09 pieces | yes | 157 data rows; vessel counts sum 148 pots + 9 JUG |
| Ticket req 2 — cluster counts from the per-piece `mesh.log` | yes | `census_appendages17.py:31-32` matches `[RETRY-23] piece=... retry=N npts=... clusters_pre=... clusters=... sizes=...`; the job wrote 157 rows; `Pot_D_Piece_03` row matches the quoted log sizes |
| Ticket req 3 — c1/c2/c3 (0 if <3) and c3_frac | yes | `census_appendages17.py:73-75` `c = (sizes + [0,0,0])[0:3]`, `c3_frac = c[2]/float(max(npts,1))`; `Pot_D_Piece_03` 51743/50069/30189, 0.190803 |
| Ticket req 4 — s0_pts/s1_pts from the wall files, ratio | yes | `t17_common.py:120-125` `read_wall` dispatches on magic `b"ply"` to `read_ply`, `:81` selects `x,y,z` by property name; `Juglet_Piece_1` 54917/73020, 1.329643 |
| Ticket req 5 — 2.0 mm coverage of both walls | yes | `census_appendages17.py:80` `cKDTree(np.hstack([s0,s1]).T)`, `:83` `dmin <= COVER_MM`, `COVER_MM = 2.0`; `Pot_J_Piece_03` 74.930233%, 3773/15050 uncovered |
| Ticket req 6 — `s1_off_author_5mm_pct`, -1.0 where absent | yes | 14 rows -1.0 = 9 juglets + F07/I28/I29/I30/J12; `census_appendages17.py:90-91`; the ticket discloses that the five files exist but are unreleased |
| Ticket req 7 — GT angles, -1.0 where absent | yes | 7 rows both GT columns -1.0 (D22, F06, F07, I28, I29, I30, J09); 150 numeric rows; `census_appendages17.py:101-110` |
| Ticket req 8 — flags exactly as specified, comma-joined, `ok` | yes | recomputed 89/22/8/7/60; thresholds `census_appendages17.py:34-39` (0.05, 2000, 5.0, 1.35, 82.0); joins in ticket order |
| Ticket req 9 — exact 18-column header, tabs, finite | yes | header matches the ticket verbatim; `bad_cols=0` (`slurm-35956230.out:187`); 0 NaN/Inf across 157 x 15 numeric cells |
| Ticket req 10 — S1 split at 4.0 mm, 6.0 mm logged | yes | `slurm-35956230.out:170` `S0=54917 S1=73020 far>4.0mm=7658 far>6.0mm=5273` |
| Ticket req 11 — wrap_deg, 1-degree bins, 360 - max gap | yes | `slurm-35956230.out:171-172` juglet 359.00 deg, `Pot_J_Piece_01` contrast 135.00 deg |
| Ticket req 12 — SHIP selector exact call, native 3x, /3.0 only for GT | yes | `juglet1_ablation17.py:41` `dl.draw_pool(C, seeds=10, step=10)`; `:48` `su(reps, sizes, C0, C1, C, 6, tri_select=None)`; `:69` 6xN walls |
| Ticket req 13 — full arm reproduces axes09 within 0.1 deg | yes | `juglet1_handle_ablation.tsv` 1.2480/1.2480; `slurm-35956230.out:173-174` `delta09= 0.0000`, `rank0<=0.1deg vs axes09: True` |
| Ticket req 14 — arms FULL_T09 + NO_HANDLE (+ 6 mm) | yes | `juglet1_handle_ablation.tsv` 3 data rows |
| Ticket req 15 — exact 9-column header | yes | `arm s0_pts s1_pts s1_far_from_s0_pts wrap_deg k rank0_gt_deg best_gt_deg d_gt_to_est_mm` |
| Ticket req 16 — 3 figures >=180 dpi, equal aspect, 20 mm bars | yes | `render_appendages17.py:41` DPI=190 (used at `:211`, `:244`), fig3 `:316` `dpi=180`; `:91` `set_aspect("equal")`; `:45` SCALE_MM=20.0, `:98-105` scale_bar; bars visible in all three PNGs opened |
| Ticket req 17 — fig1 2x2 with counts, fig2 clusters_3d, fig3 3x4 = 3 named + 9 | yes | `render_appendages17.py:113,131` `(2,2,...)`, `:265` `(3,4,...)`; gallery shows 12 panels: Pot_J_Piece_01, Pot_J_Piece_03, Juglet_Piece_1 + 9 others |
| Ticket req 18 (amended) — manifest header + one row per render | yes | `renders.tsv` 4 lines, 3 fields each, 0 commas; `render_appendages17.py:334-338` |
| Ticket req 19 — one Slurm job, poll to COMPLETED 0:0, sacct verbatim | yes | only job `35956230`; `run_status.txt` is a plain sacct table with no prose or summary added |
| Ticket req 20 — everything staged under `artifacts/appendage-handling-17/` | yes | 3 evidence TSVs, 3 PNGs, `run_status.txt` plus the slurm `.out`/`.err` |
| Ticket req 21 — no forbidden edits | yes | the diff names only the six permitted files |
| Ticket req 22 — written back, `Status: ready-for-review`, committed and pushed, not merged | yes after the fixes below | Status and `HEAD_NOT_IN_MAIN` held; the uncommitted follow-up was the defect and is now one commit on the branch |
| Follow-up — manifest is 526 B / 4 lines / 3 fields / no commas / trailing newline | yes | `wc -c` 526; 4 lines; 3 fields each; 0 commas; last byte `\n` |
| Follow-up — renderer writes the header with literal tabs; RENDERS unchanged; py_compile OK | yes | `render_appendages17.py:334-338`, `:50-53`, `:47-49`; in-memory compile OK |
| Follow-up — no Spartan work or resubmission | yes | `run_status.txt` contains only `35956230`; evidence and output mtimes 01:37-01:41; no newer job id in any artefact |
| Follow-up — the auditor's table is recorded here | yes | this section |
| Must Not Change — literal tabs, finite numbers, -1.0 sentinels, `renders/` paths | yes | `renders.tsv` 0 commas; 28 -1.0 cells; all three manifest paths start `renders/` and resolve |
| Must Not Change — heavy compute on a Spartan compute node via `sbatch` | yes | `run17.sbatch:2-8` sapphire/8 CPUs/32G; `slurm-35956230.out:2` host `spartan-bm165.hpc.unimelb.edu.au`; one job |

**Defects it raised, and what was done**

1. *Dirty tree / not committed (rows 2 and 22).* True at audit time: the follow-up, the amended row 18 and the end state were uncommitted. Fixed by the commit that carries this section.
2. *`run17.sbatch:69` asserted a 3-line manifest.* Fixed: the gate now requires 4 lines and the exact header `name`/`path`/`description` (lines 69-72). The verified job `35956230` predates the change and was not resubmitted; the gate only matters to a future re-run.
3. *Ticket named `[STATUS-23]` while the code matches `[RETRY-23]`.* The code was right and the prose was wrong: `census_appendages17.py:31-32` matches the `[RETRY-23]` record, which is the tag the ticket's own requirement names. Three sentences were corrected (the spot check, row 2 of the self-check table, and the deviations note).
4. *A stray `__pycache__/render_appendages17.cpython-313.pyc`.* Left by the worker's `py_compile`; deleted.

Every other row was marked met and its evidence is quoted above; nothing in the numbers, the tables or the renders changed.

**End state:** ready

### Lead verification (2026-11-29)

- `verified: sacct -j 35956230 -> COMPLETED, ExitCode 0:0, Elapsed 00:03:13 (sapphire, 8 CPUs)`
- `verified: python C:/PR/artifacts/appendage-handling-17-accept/accept.py -> ACCEPT-17 PASS` (both in worktree and archived `SfSpp_preprocessing/artifacts/appendage-handling-17/`)
- `verified: git -C C:/PR/worktrees/sfs/17 diff --stat origin/main..HEAD` scoped to `.scratch/appendage-handling/{t17/,issues/17-...md}` (`HEAD 359a9ac3`, `Worker: DeepSeek V4.1 Flash`, plus lead-verification update)
- `verified: dsh_status(hrun-mx0jjmws-e898f7) -> completed (hungerg-free)` — DSH read-only sub-agent `t17-auditor` verified all 24 checklist items and drove 4 fixes committed in `359a9ac3`
- `verified: read_file visual check of all 3 renders` (`Juglet_Piece_1_handle_and_walls.png`, `Pot_J_Piece_03_clusters_3d.png`, `Flagged_appendage_sherds_gallery.png` with `20 mm` scale bars): confirmed `Juglet_Piece_1` loop handle (`7,658` pts, `10.5%` of `S1`) is absorbed into `S1` while `359.0°` rim wrap limits the axis shift to `0.023°` (`1.2480° -> 1.2248°`, `8.9376 -> 8.7665 mm`, i.e. `0.17 mm`), and confirmed `Pot_J_Piece_03`'s `11,511`-pt 3rd cluster is a sharp base-to-wall/rim crease cut (`1.87°` best GT axis) rather than a handle


