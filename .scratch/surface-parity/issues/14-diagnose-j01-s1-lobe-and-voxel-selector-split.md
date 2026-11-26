# 14 — Diagnose J01 face-1 3D lobe and selector voxel split

**Answers:** E2
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-27)
**Branch:** 14-diagnose-j01-s1-lobe-and-voxel-selector-split, in /c/PR/worktrees/sfs/14
**Worker:** DeepSeek

## Context

[Ticket 13](13-diagnose-pot-j-t09-drop-and-j01-surface-factors.md) established that `Pot_J_Piece_01` (`J01`) is the master lever in Pot J's `t09` drop (`T09_ALL` `6/21` vs `T09_WITH_AUTHOR_J01` `17/21`, beating `MOR_CTL` `16/21`), and that on `J01` face 0 agrees with the Authors (`99.97%` within `1 mm`, `nn_p90 = 0.48 mm`) while face 1 (`S1`) has `42.2%` of its points (`17,795` of `42,153`) off the Authors' outer wall (`nn_p90 = 24.64 mm`). It also uncovered a surprise: `OWN_VOXEL_1MM` and `AUTHOR_VOXEL_1MM` share identical `13,022` 1 mm voxels (`6,372` on `S0` + `6,650` on `S1`), yet `OWN_VOXEL_1MM` emits `k = 1` (`77.92°` from the Ticket 13 donor line) whereas `AUTHOR_VOXEL_1MM` emits `k = 3` (`3.73° / 5.39 mm` from the donor line at candidate rank 1).

Read-only follow-up checks established two facts before writing this ticket:
1. **`o1_off` is real pottery mesh, not noise:** All `17,795` off-wall points (`> 1 mm` from `AUTHOR.S1`, median `16.60 mm`, p90 `35.88 mm`, max `48.52 mm`, `0.0%` within `1 mm` of `AUTHOR.S0`) sit in bounding box `[4.1, -36.6, 425.8]..[85.4, 52.9, 463.6]` on the real `Pot_J_Piece_01_Mesh_DS.obj` (`5,524` vertices, bbox `[-15.4, -41.3, 423.7]..[85.4, 53.5, 514.9]`). On a `2 mm` voxel grid, the Authors' `a0 | a1` covers `63.1%` of the mesh vertices while `t09`'s `o0 | o1` covers `85.1%`. In `mesh.log`, `[WINDOW-26-FINAL]` printed `surface=1 admitted_own=111 admitted_other=39730 other_copied_over=yes final_points=42153`.
2. **`OWN_VOXEL_1MM` vs `AUTHOR_VOXEL_1MM` have zero normal flips:** Across all `6,372 + 6,650 = 13,022` common `1 mm` voxels in identical order (`100.00%` matching `floor(xyz)` keys), `dp_med = 0.340 mm` (`S0`) / `0.348 mm` (`S1`), signed normal angle median is `0.98°` (`S0`) / `0.93°` (`S1`), and `neg_dot = 0 (0.0%)`. Rank `[0]` is nearly identical across all arms (`dir ≈ [-0.26..-0.28, -0.68..-0.69, 0.67..0.68]`), while the donor axis sits at rank `[1]` on `AUTHOR_VOXEL_1MM` and `OWN_SHARED_1MM` (at `k = 2`), and vanishes on `OWN_VOXEL_1MM` (`k = 1`).

This diagnostic ticket answers both questions cleanly without altering any production pipeline code:
- **Part A (`j01_lobe14.py`):** Render `Pot_J_Piece_01_Mesh_DS.obj` together with `o0`, `o1_on`, and `o1_off` in 3D/orthogonal views so we can visually see the extra `42.2%` lobe on `J01`, and scan all `143` released `Pot A..J` pieces (`286` faces) to find whether any other piece has a large off-author-wall lobe.
- **Part B (`j01_selector_trace14.py`):** Instrument the frozen `SHIP` selector (`select_joint_lines`, `normal_arm`, `thickness_arm`, `select_union_lines(..., tri_select=False)`, and `keep_lines`) on the 6 saved `t13` walls plus the 2 voxel cross-swaps (`VOXEL_OWN_XYZ_AUTH_N`, `VOXEL_AUTH_XYZ_OWN_N`) to pinpoint the exact stage and threshold where the donor line disappears on `OWN_VOXEL_1MM` (and on `OWN_T09`, `OWN_SHARED_1MM`).

## Exact Inputs & Environment (Spartan compute node only)

- **Saved `t13` J01 walls:** `/data/gpfs/projects/punim2657/SfSpp/runs/20261126-1500_cf88609_t13-diagnose/j01/walls/`
  (`AUTHOR`, `OWN_T09`, `OWN_SHARED_1MM`, `AUTHOR_SHARED_1MM`, `OWN_VOXEL_1MM`, `AUTHOR_VOXEL_1MM`, `.S0.xyz` and `.S1.xyz` each)
- **Canonical `t09` own surfaces:** `/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1340_a50f8cc_t09-own-surfaces/out/Pot_<P>/geom/`
- **J01 triangle mesh:** `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Mesh/Pot_J_Piece_01_Mesh_DS.obj`
- **Frozen `SHIP` selector & corpus loader:**
  `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship/work`
  (`t03_lib.py`, `t03_extract.py`, `impl_t03/sfs_axes/joint.py`, `impl_t03/sfs_axes/select.py`)
- **Python environment on Spartan:** Use the same Conda/Python environment used in `t03-ship` / `t13-diagnose` (which has `numpy`, `scipy`, `matplotlib`). Submit via `sbatch` and poll to a final state (`COMPLETED 0:0`) with `scripts/slurm_poll.sh <JOBID>`.
- **Spartan run directory:** `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t14-j01-lobe-trace`
- **Donor reference (evaluation only; never fed to the selector):**
  `DONOR_DIR = [0.992676, 0.042854, 0.112950]` (normalized), `DONOR_PT = [-53.313366, -28.804402, 479.479140]`.
  Use `sfs_axes.io_axes.direction_angle_deg` and symmetric/axial midpoint distance to the line `(DONOR_DIR, DONOR_PT)` anchored near `CENTROID = [30.107, 12.692, 452.566]` (matching `t13/j01_factors13.py`), and `t03_lib.gt_axis("Pot_J_Piece_01")` for GT angle.

## Deliverables

Create all new scripts under `.scratch/surface-parity/t14/` in `worktrees/sfs/14`:

1. **`j01_lobe14.py`:**
   - **J01 mesh & lobe figure:** Partition `OWN_T09.S1` by 1-NN Euclidean distance to `AUTHOR.S1` into `o1_on` (`<= 1.0 mm`) and `o1_off` (`> 1.0 mm`). Load `Pot_J_Piece_01_Mesh_DS.obj` vertices (and triangles if helpful for light grey wireframe/points) and classify each mesh vertex (`<= 2.0 mm` to `a0|a1` vs `o1_off`-only vs uncovered). Render `renders/J01_mesh_and_s1_lobe_3d.png` at `180+ dpi`: a 2×2 panel figure with XY, XZ, YZ orthographic views (each with equal aspect ratio and a drawn `20 mm` physical scale bar) plus 1 oblique 3D view (`view_init(elev=25, azim=-55)` or similar clear angle). Colour legend: mesh vertices in light grey (`#cccccc`), `AUTHOR.S0` (`a0`) in muted blue (`#4c72b0`), `o1_on` in teal (`#1b9e77`), and `o1_off` in bright orange-red (`#d95f02`), with `AUTHOR` donor line overlaid as dashed green and GT axis in black if clear. Title with exact point counts and off-wall fraction.
   - **143-piece corpus wall comparison:** Iterate over the `143` released `Pot A..J` stems (matching `dl.walls(stem, "authors")` and `t09` canonical walls at `/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1340_a50f8cc_t09-own-surfaces/out/Pot_<P>/geom/`), handling both face `0` and face `1` (`286` rows total). For each `(stem, face)`, measure 1-NN distance from every own point to the author face wall (noting that `t09` matches `S0`/`S1` indexing to authors as classified). Compute `pct_within_1mm`, `pct_over_5mm`, `nn_p90_mm`, `nn_max_mm`. Write **strictly tab-delimited** (`\t`) `evidence/corpus_offwall_143.tsv` with header:
     `stem	pot	face	own_points	author_points	pct_within_1mm	pct_over_5mm	nn_p90_mm	nn_max_mm`

2. **`j01_selector_trace14.py`:**
   - Load the 6 `t13` wall pairs (`AUTHOR`, `OWN_T09`, `OWN_SHARED_1MM`, `AUTHOR_SHARED_1MM`, `OWN_VOXEL_1MM`, `AUTHOR_VOXEL_1MM`) and build the 2 matched-voxel cross-swap pairs (on `OWN_VOXEL_1MM` vs `AUTHOR_VOXEL_1MM`, already aligned 1-to-1 by `common_voxel`):
     - `VOXEL_OWN_XYZ_AUTH_N`: xyz from `OWN_VOXEL_1MM`, normals from `AUTHOR_VOXEL_1MM`
     - `VOXEL_AUTH_XYZ_OWN_N`: xyz from `AUTHOR_VOXEL_1MM`, normals from `OWN_VOXEL_1MM`
   - For all **8 arms**, run the frozen `SHIP` draw (`dl.draw_pool(C, seeds=10, step=10)`) cleanly without modifying any repo files (import `impl_t03/sfs_axes/joint.py`, `select.py`, `meridian.py`, `profile.py` in read-only mode) and replicate/instrument each stage with identical constants:
     - Pool stage: min angle to `DONOR_DIR` across all `reps` (`pool_min_donor_deg`) and across the top-60 most-drawn basins (`top60_min_donor_deg`), plus `n_basins`.
     - For each of `normal_arm`, `thickness_arm`, and `shipped` (`select_union_lines(..., tri_select=False)`):
       - Inspect the distinct refined candidate lines **before** `keep_lines` is applied! Record:
         - `<arm>_r0_donor_deg`: donor angle of the cheapest refined candidate (rank 0)
         - `<arm>_pre_tau_donor_deg`: minimum donor angle among all distinct refined candidates (up to 6 / 8) *before* the `tau = 1.2` `keep_lines` cut
         - `<arm>_pre_tau_ratio`: the `cost / cost[0]` ratio of that best-donor candidate before `keep_lines`
         - `<arm>_k`: count surviving `keep_lines(tau=1.2, kmax=3)` (`normal_k`, `thick_k`, `ship_k`)
     - Also capture the full per-candidate trace (candidate index, cost, `cost/c0`, donor angle, GT angle) to a log/JSON under the Spartan run dir (`logs/j01_selector_trace_detail.json`) so we can inspect exact costs.
     - Final merged stage (`select_union_lines(..., tri_select=True)` with `write_lines` scaling = 1.0): record `k_final`, `final_best_donor_deg`, `final_best_donor_mm`, `final_best_gt_deg`.
   - Write **strictly tab-delimited** (`\t`) `evidence/j01_arm_trace.tsv` with exact header:
     `arm	n_basins	pool_min_donor_deg	top60_min_donor_deg	normal_k	normal_r0_donor_deg	normal_pre_tau_donor_deg	normal_pre_tau_ratio	thick_k	thick_r0_donor_deg	thick_pre_tau_donor_deg	thick_pre_tau_ratio	ship_k	ship_r0_donor_deg	ship_pre_tau_donor_deg	ship_pre_tau_ratio	k_final	final_best_donor_deg	final_best_donor_mm	final_best_gt_deg`
   - Render `renders/J01_selector_trace.png`: a clear 2-panel diagnostic plot showing (left) minimum donor angle at each stage (`pool`, `top60`, `normal pre-tau`, `thick pre-tau`, `ship pre-tau`, `final`) for the 8 arms, and (right) `cost / cost[0]` ratio of the best-donor refined candidate vs the `tau = 1.2` cutoff line in `thickness_arm`, `normal_arm`, and `shipped_arm`.

3. **Slurm execution & staging (`run14.sbatch`):**
   - Run both scripts inside a single Slurm batch job on Spartan, poll with `scripts/slurm_poll.sh`, and record final `sacct` `State` and `ExitCode` into `logs/run_status.txt`.
   - Stage into the **worktree** `C:/PR/worktrees/sfs/14/artifacts/surface-parity-14/`:
     - `evidence/corpus_offwall_143.tsv` (tab-delimited, `286` data rows)
     - `evidence/j01_arm_trace.tsv` (tab-delimited, `8` data rows)
     - `evidence/renders.tsv` (tab-delimited, columns `name	path	description` or similar with **relative** paths `renders/J01_mesh_and_s1_lobe_3d.png` and `renders/J01_selector_trace.png`)
     - `renders/J01_mesh_and_s1_lobe_3d.png`
     - `renders/J01_selector_trace.png`
     - `logs/run_status.txt`

4. **Write-back:**
   - Update this ticket (`.scratch/surface-parity/issues/14-diagnose-j01-s1-lobe-and-voxel-selector-split.md`) with a concise summary of Part A (is `J01` unique among the `143` pieces or do others have `> 10%` off-author-wall lobes?), Part B (which arm and exact `cost/c0` ratio or basin drop causes `OWN_VOXEL_1MM` vs `AUTHOR_VOXEL_1MM` to split between `k=1` and `k=3`), exact Spartan run path + `sacct` State/ExitCode, and the compliance table. Set `Status: ready-for-review` and **stop** (do not merge, commit to `main`, or close the worktree).

## Must Not Change

- Do NOT modify `sfs_axes/`, `mesh_processing_headless.cpp`, `Data/`, `intent/`, `scripts/`, or any existing ticket/script outside `.scratch/surface-parity/t14/` and `.scratch/surface-parity/issues/14-diagnose-j01-s1-lobe-and-voxel-selector-split.md` (plus the gitignored `artifacts/surface-parity-14/` staging folder in the worktree).
- All `.tsv` files MUST use literal `\t` tab delimiters (never commas) and finite numeric values; `renders.tsv` MUST use relative paths `renders/J01_mesh_and_s1_lobe_3d.png` and `renders/J01_selector_trace.png`.
- All compute-heavy Python runs (KD-trees over 143 pieces, PotSAC selector sweeps, matplotlib renders) MUST run on a Spartan compute node via `sbatch`, never on the laptop or Spartan login node.
