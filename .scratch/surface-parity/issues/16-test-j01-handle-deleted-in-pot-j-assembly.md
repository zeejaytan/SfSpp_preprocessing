# 16 — Test J01 handle-deleted surfaces in Pot J end-to-end assembly

**Answers:** E2
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-27)
**Branch:** 16-test-j01-handle-deleted-in-pot-j-assembly, in /c/PR/worktrees/sfs/16
**Worker:** DeepSeek

## Context

[Ticket 13](13-diagnose-pot-j-t09-drop-and-j01-surface-factors.md) showed that `t09`'s canonical Pot J axes (`J02..J12`) are healthy: swapping **only** `Pot_J_Piece_01`'s axis back to `AUTHOR` (`T09_WITH_AUTHOR_J01`) jumps Pot J from `6/21` joins (`T09_ALL`) to `17/21` (`[16, 17]`), beating the Authors' full-pot control (`MOR_CTL`, `16/21`).

[Ticket 14](14-diagnose-j01-s1-lobe-and-voxel-selector-split.md) showed *why* `J01` fails on our own walls:
1. Our `Surface_1` (`OWN_T09.S1`) grew onto an attached handle stub (`17,795` points, `42.2%`, curving `48.5 mm` off the body wall), whereas the Authors' `AUTHOR.S1` stopped at the body wall (`63.1%` vs `85.1%` mesh coverage).
2. Even after deleting the handle points (`OWN_SHARED_1MM` and `OWN_VOXEL_1MM`), the frozen `SHIP` selector (`select_joint_lines`) drops the good donor-close backup line because `select_joint_lines` only keeps `thickness_arm`'s rank-0 line (`73°–78°` off) and discards its `kept=True` secondary lines (`6.60°` at `1.173x` on `OWN_SHARED_1MM`, and `8.68°` at `1.168x` on `OWN_VOXEL_1MM`). Meanwhile `OWN_SHARED_1MM` through the unchanged `SHIP` selector reaches `27.11°` from donor (vs `58.58°` with the handle).

This ticket answers the conservator's direct question: **if we delete the handle on our own `J01` surface, does our Pot J match or beat the Authors' `16/21` control?** It runs five `J01` axis arms inside the exact pinned `Hierarchy-T13` Pot J assembler (with byte-identical `J02..J12` `t09` axes and `t09` breaklines, 2 repeats per arm).

## Exact Inputs & Environment (Spartan compute node only)

- **Saved `t13` `J01` walls (read-only):**
  `/data/gpfs/projects/punim2657/SfSpp/runs/20261126-1500_cf88609_t13-diagnose/j01/walls/`
  (`AUTHOR`, `OWN_T09`, `OWN_SHARED_1MM`, `OWN_VOXEL_1MM`, `.S0.xyz` and `.S1.xyz`)
- **Pinned `Hierarchy-T13` binary, Pot J `t09` axes/breaklines, and `t13` cell/scorer setup (read-only):**
  `/data/gpfs/projects/punim2657/SfSpp/runs/20261126-1500_cf88609_t13-diagnose/`
  Reuse the exact compiled `Hierarchy-T13` executable, `t09` `J02..J12` axis files, `t09` breaklines, and Ticket 13 scoring recipe (`t13` scripts / `score305` / `acc_*.tsv`). Zero recompilation and zero changes to `J02..J12`.
- **Frozen `SHIP` selector & corpus loader (read-only):**
  `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship/work`
  (`t03_lib.py`, `t03_extract.py`, `impl_t03/sfs_axes/joint.py`, `impl_t03/sfs_axes/select.py`)
- **Donor reference (evaluation only; never fed to selector):**
  `DONOR_DIR = [0.992676, 0.042854, 0.112950]` (unit), `DONOR_PT = [-53.313366, -28.804402, 479.479140]`, `CENTROID = [30.107, 12.692, 452.566]`, plus `t03_lib.gt_axis("Pot_J_Piece_01")`.
- **Spartan run directory:**
  `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t16-j01-handle-deleted`

## Deliverables

Create all new scripts under `.scratch/surface-parity/t16/` in `worktrees/sfs/16`:

1. **`prep_j01_axes16.py` (run on Spartan compute node, NOT login node):**
   Build 5 `Pot_J_Piece_01_Axis.xyz` files (exact `[position, direction]` format matching `t03_extract.write_lines`, unscaled):
   - **`CTL_T09_WITH_AUTHOR_J01`:** copy the exact `t13` `AUTHOR` `J01` axis (positive control).
   - **`OWN_NO_HANDLE_SHIP`:** `OWN_SHARED_1MM` through the unchanged frozen `SHIP` `select_joint_lines` (`dl.draw_pool(C, seeds=10, step=10)`).
   - **`OWN_NO_HANDLE_THICKSEC`:** `OWN_SHARED_1MM` through the exact same `normal_arm`, `thickness_arm`, `select_union_lines(..., tri_select=False)` calls, then merge in a helper `merge_with_thick_secondaries` that takes `normal rank-0`, `thickness rank-0`, `shipped rank-0`, then **`res_thickness[:, 1:]` in rank order BEFORE `res_shipped[:, 1:]` in rank order** (each subject to `direction_angle_deg >= 10.0` from kept lines and `kmax = 3`), followed by `orient_merged(..., C, base_orient=True)`. Keep `sfs_axes/` unmodified; define the 10-line merge helper cleanly inside `prep_j01_axes16.py`.
   - **`OWN_VOXEL_THICKSEC`:** `OWN_VOXEL_1MM` through the exact same `merge_with_thick_secondaries` rule (expected to admit `thickness_arm` rank 1 at `8.68°`).
   - **`OWN_S0_ONLY_SHIP`:** `OWN_T09.S0` alone (`C0 = S0, C1 = S0, C = S0`) through the unchanged frozen `SHIP` `select_joint_lines` (checks whether inner wall alone avoids the handle-bearing outer wall).
   - Write strictly tab-delimited (`\t`) `evidence/j01_axes16.tsv` with header:
     `arm	k	best_donor_deg	best_donor_mm	best_gt_deg	axes_sha256`

2. **`run_potj16.sbatch` (Slurm array job, `10` cells = 5 arms × 2 repeats, using `Hierarchy-T13`):**
   - For each `(arm, rep)` cell (`rep` in `1, 2`), verify before running that `Pot_J_Piece_{02..12}_Axis.xyz` and all `Breakline_0` files are byte-identical to Ticket 13 `T09_ALL`, and ONLY `Pot_J_Piece_01_Axis.xyz` is substituted.
   - Run `Hierarchy-T13` cleanly, score with the exact Ticket 13 `score305` / seam scorer, poll all jobs via `scripts/slurm_poll.sh`, and append the verbatim `sacct` output for all jobs to `logs/run_status.txt`.
   - Write strictly tab-delimited (`\t`) `evidence/potj_assembly16.tsv` with exact header:
     `arm	rep	sherds_ok	sherds_total	joins_ok	joins_total	j01_joins_ok	j01_joins_total	non_j01_joins_ok	non_j01_joins_total	jobid	state	exit_code`
     (`sherds_total = 11`, `joins_total = 21`, `j01_joins_total` = J01's GT edges out of 21, `non_j01_joins_total = 21 - j01_joins_total`, `state = COMPLETED`, `exit_code = 0:0`).

3. **`render_potj16.py` (run on Spartan compute node):**
   - Render `renders/Pot_J_handle_deleted_comparison.png` (`180+ dpi`, 1×5 or 2×3 locked-camera mesh layout of the best repeat of each arm with a `20 mm` scale bar in every panel, `Pot_J_Piece_01` highlighted, showing exact `X/21` joins and `J01`'s `Y/Z` seams per panel).
   - Write strictly tab-delimited (`\t`) `evidence/renders.tsv` listing the relative path `renders/Pot_J_handle_deleted_comparison.png`.

4. **Stage & write-back:**
   - Stage `evidence/` (`j01_axes16.tsv`, `potj_assembly16.tsv`, `renders.tsv`), `renders/Pot_J_handle_deleted_comparison.png`, and `logs/run_status.txt` into `C:/PR/worktrees/sfs/16/artifacts/surface-parity-16/`.
   - Write back the concise results (best-of-2 AND per-repeat `X/21` joins, `J01` seams vs non-`J01` seams, axis table, exact Spartan run dir + `sacct` State/ExitCode, and compliance table) into `.scratch/surface-parity/issues/16-test-j01-handle-deleted-in-pot-j-assembly.md`, set `Status: ready-for-review`, and **stop** (do not merge, edit `main`, or close the worktree).

## Must Not Change

- Do NOT modify `sfs_axes/`, `mesh_processing_headless.cpp`, `Data/`, `intent/`, `scripts/`, or any existing ticket/script outside `.scratch/surface-parity/t16/`, `.scratch/surface-parity/issues/16-test-j01-handle-deleted-in-pot-j-assembly.md`, and the worktree's gitignored `artifacts/surface-parity-16/` folder.
- All `.tsv` files MUST use literal `\t` tabs (never commas) and finite numbers; `renders.tsv` MUST use the relative path `renders/Pot_J_handle_deleted_comparison.png`.
- All heavy compute (`prep_j01_axes16.py`, `Hierarchy-T13` assembly cells, scoring, rendering) MUST run via `sbatch` on Spartan compute nodes, never on the laptop or Spartan login node.
