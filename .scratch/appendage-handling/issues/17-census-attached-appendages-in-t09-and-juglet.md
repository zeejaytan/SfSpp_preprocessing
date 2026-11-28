# 17 — Census attached appendages in t09 and Juglet

**Answers:** E3
**Type:** prototype
**Blocked by:** None
**Status:** ready-for-review
**Working in:** chat on Thinkbook16 (2026-11-29)
**Branch:** 17-census-attached-appendages-in-t09-and-juglet, in /c/PR/worktrees/sfs/17
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

Spot check against the mesh log, `Pot_D_Piece_03`: row is npts 158221, clusters 8, c1 51743, c2 50069, c3 30189, s0 51584, s1 52905; the log line reads `clusters=8 sizes=51743,50069,30189,6609,2883,2333,2310,885 npts=158221 ... surf0_points=51584 surf1_points=52905`. (The emitted tag is `[STATUS-23]`, not the `[RETRY-23]` named in the ticket; the parser matches the tag as written by the pipeline.)

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
| 2 | Cluster counts parsed from the per-piece mesh log (`clusters=`, `sizes=`) | met | `t17_common.py` `mesh_log()` parses the emitted `[STATUS-23]` line; spot-checked `Pot_D_Piece_03` against the raw log line |
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
| 18 | `renders.tsv` exactly three relative paths, tab-separated | met | `renders/Juglet_Piece_1_handle_and_walls.png`, `renders/Pot_J_Piece_03_clusters_3d.png`, `renders/Flagged_appendage_sherds_gallery.png`, no header |
| 19 | One Slurm job; poll to `COMPLETED 0:0`; `sacct` saved verbatim | met | job 35956230, `scripts/slurm_poll.sh 35956230` returned `COMPLETED 0:0`; `logs/run_status.txt` is the raw `sacct` output |
| 20 | Everything staged under `artifacts/appendage-handling-17/` (`evidence/`, `renders/`, `logs/`) | met | 3 TSVs, 3 PNGs, `logs/run_status.txt` plus the job's stdout/stderr |
| 21 | No edits to `sfs_axes/`, `mesh_processing_headless.cpp`, `Data/`, `intent/`, `map.md`, `scripts/` | met | `git diff --name-only origin/main...HEAD` lists only the ticket and the five files under `.scratch/appendage-handling/t17/` |
| 22 | Ticket written back, `Status: ready-for-review`, committed and pushed on the branch, not merged | met | this section; branch `17-census-attached-appendages-in-t09-and-juglet` |

### 6. Deviations, and what a reader should not over-read

- The census reads the pipeline's `[STATUS-23]` line; the ticket calls it `[RETRY-23]`. Same line: `piece=`, `outcome=`, `clusters=`, `sizes=`, `npts=`, `surf0_points=`, `surf1_points=`.
- Orthogonal panels are world-axis projections (XY, XZ, YZ), not PCA planes, because the panel labels name world axes.
- Units: walls and axes are 3x for `Juglet_def3x`/`axes09_juglet_def3x_regen`; the Juglet *mesh* in `Dataset/Mesh/Juglet` is already 1x mm (34 × 37.6 × 37.4 mm, matching walls/3), so it is used as-is — dividing it by 3 draws a speck and reports 0% coverage.
- `Juglet_Piece_1` is `ok` by the flag rules; its interest is the handle ablation, not a trigger.
- Coverage is a nearest-vertex distance to a point cloud, so it under-reports when the mesh is dense and the walls sparse; comparisons across pieces hold, absolute percentages are approximate.
- Nothing here decides whether dropping third clusters is *right*; it measures where they are and how big.

### 7. Open questions this raises

- 89 pieces carry a large third cluster. If those clusters are outer walls or handles, the two-surface model is discarding a third of the evidence on more than half the corpus — worth deciding per-vessel-class before tuning anything else.
- `Pot_J_Piece_01` is the mirror case of the juglet: S0 wraps 135°, S1 is 1.8x S0, 36.8% of S1 is off the author wall, and its axis is 88.6° from GT — a large lobe that the axis follows. That piece, not the juglet, is where an appendage-aware selector could gain.
