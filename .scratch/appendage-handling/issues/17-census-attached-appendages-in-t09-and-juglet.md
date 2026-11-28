# 17 — Census attached appendages in t09 and Juglet

**Answers:** E3
**Type:** prototype
**Blocked by:** None
**Status:** in-progress
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
