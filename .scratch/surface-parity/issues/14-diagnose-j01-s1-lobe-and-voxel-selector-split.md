# 14 — Diagnose J01 face-1 3D lobe and selector voxel split

**Answers:** E2
**Status:** ready-for-review
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

## Outcome (2026-11-27)

Run `/data/gpfs/projects/punim2657/SfSpp/runs/20261127-1052_78a40f5_t14-j01-lobe-trace`, job **35842878** `COMPLETED 0:0` in `00:02:33` (Start `2026-11-27T10:54:46`, End `2026-11-27T10:57:19`, sapphire, 8 CPUs). One `sbatch` job ran both scripts, as required; the first attempt **35842705** `FAILED 1:0` in `00:00:09` because the `t09` own surfaces are PCL ASCII PLY while the Authors' `Surfaces/*.xyz` are six-column text — both scripts now dispatch on the file magic and pick `x,y,z,nx,ny,nz` by property name. Both attempts are in `logs/run_status.txt` with the full `sacct` block.

### Part A — is `J01` unique among the 143 pieces?

Not the only face with points far outside the Authors' wall, but the only one where a **seated** wall carries a **genuine extra lobe**.

`evidence/corpus_offwall_143.tsv`: 143 stems x 2 faces = **286 rows**, median `pct_within_1mm = 99.9829`, median `pct_over_5mm = 0`. Within 1 mm: **240** faces >= 99.9 %, **20** faces < 99 %, **13** < 90 %, **7** < 1 %. Beyond 5 mm: **19** faces carry any such point, **12** exceed 5 %, and **9** exceed 10 % — across 6 stems:

| stem | face | own points | within 1 mm % | over 5 mm % | nn_p90 mm | nn_max mm | what it is |
|---|---|---|---|---|---|---|---|
| `Pot_I_Piece_25` | 0 | 2,636 | 0.00 | 100.00 | 7.42 | 7.57 | whole small wall displaced 7.4 mm |
| `Pot_I_Piece_25` | 1 | 3,472 | 0.00 | 100.00 | 7.42 | 7.65 | same, 7.4 mm |
| `Pot_J_Piece_08` | 0 | 2,545 | 0.00 | 100.00 | 12.42 | 13.20 | whole small wall displaced 12.4 mm |
| `Pot_J_Piece_08` | 1 | 3,648 | 0.00 | 100.00 | 15.82 | 26.89 | same, 15.8 mm, tail to 26.9 mm |
| `Pot_C_Piece_03` | 1 | 21,019 | 0.07 | 83.33 | 34.49 | 57.28 | known corpus caveat (wrong reference) |
| `Pot_D_Piece_28` | 0 | 2,429 | 0.04 | 72.17 | 6.52 | 7.71 | whole small wall displaced 6.5 mm |
| `Pot_D_Piece_28` | 1 | 2,605 | 0.00 | 68.14 | 6.49 | 6.62 | same, 6.5 mm |
| `Pot_J_Piece_01` | 1 | 42,153 | **57.78** | **36.81** | **24.64** | **48.52** | **this ticket: 57.8 % seated + a lobe** |
| `Pot_D_Piece_27` | 1 | 2,914 | 68.94 | 18.15 | 8.41 | 15.79 | partial: 31 % off, 8.4 mm, one-sixth J01's points |

Reading: six of the seven faces under 1 % within 1 mm are a **whole own wall sitting 6–16 mm away from the Authors' wall** (I25 7.4 mm, J08 12.4–15.8 mm with a tail to 26.9 mm, D28 6.5 mm; 2.4k–3.6k points each, `own_points` is the entire face) — a registration/extent difference, not an extra surface. The seventh is `Pot_C_Piece_03` face 1, and with `Pot_J_Piece_09` it is already recorded as a corpus caveat in `SfSpp_preprocessing/AGENTS.md` (wrong reference), so those numbers are reported for completeness and say nothing new about the method. That leaves `J01` face 1 as the only case of a large own wall that agrees with the Authors over most of its area and then adds a coherent extra sheet up to 48.5 mm outside it — visible in `renders/J01_mesh_and_s1_lobe_3d.png` as a smooth closed band standing off the teal on-wall region, over real mesh (1,000 of the 5,524 mesh vertices are `o1_off`-only, 769 uncovered). `Pot_D_Piece_27` face 1 is the only smaller analogue (18.2 % beyond 5 mm, max 15.8 mm).

### Part B — which arm and which ratio splits `k=1` from `k=3`

All 8 arms, frozen `SHIP` selector, `seeds=10, step=10` (identical sampled indices in every arm); full 20-column table in `evidence/j01_arm_trace.tsv`, per-candidate costs in `logs/j01_selector_trace_detail.json`:

| arm | basins | pool min deg | top-60 min deg | ship k | ship pre-tau donor deg | cost/c0 | k_final | final best donor deg | mm |
|---|---|---|---|---|---|---|---|---|---|
| `AUTHOR` | 131 | 6.64 | 10.06 | 3 | 0.00 | 1.133 | 3 | 0.00 | 0.00 |
| `OWN_T09` | 124 | 3.40 | 20.25 | 3 | 35.21 | 1.109 | 3 | 58.58 | 203.81 |
| `OWN_SHARED_1MM` | 136 | 2.10 | 9.61 | 2 | 27.11 | 1.177 | 2 | 27.11 | 97.17 |
| `AUTHOR_SHARED_1MM` | 124 | 6.27 | 9.30 | 3 | 7.26 | 1.131 | 3 | 7.26 | 13.48 |
| **`OWN_VOXEL_1MM`** | 130 | **2.82** | **9.84** | **1** | **37.90** | **1.2695** | **1** | **77.92** | **337.23** |
| **`AUTHOR_VOXEL_1MM`** | 130 | **6.69** | **6.69** | **3** | **3.73** | **1.1525** | **3** | **3.73** | **5.39** |
| `VOXEL_OWN_XYZ_AUTH_N` | 130 | 6.78 | 6.78 | 3 | 6.63 | 1.1254 | 3 | 6.63 | 1.37 |
| `VOXEL_AUTH_XYZ_OWN_N` | 134 | 7.86 | 7.86 | 2 | 25.62 | 1.1858 | 2 | 25.62 | 38.20 |

Two discrete gates in series, in this order:

1. **The 60-basin cut decides whether a donor-like line is ever refined.** `OWN_VOXEL_1MM`'s draw pool *does* contain a `2.82 deg` basin, but its 60 largest basins bottom out at `9.84 deg` (its three donor-close basins sit at 9.84, 10.22, 14.73 deg), so no donor-like basin reaches `rank_by_profile` and the best refined candidate is `37.90 deg`, and the axis the arm does ship is the one every arm ranks first (~78 deg from the donor, 89.4 deg off GT). `AUTHOR_VOXEL_1MM` carries a `6.69 deg` basin inside its top 60 (`pool_min == top60_min == 6.69`), and refining it lands on `3.73 deg`.
2. **`keep_lines(tau=1.2, kmax=3)` then decides whether that line survives.** AUTHOR's best-donor candidate costs `cost/c0 = 1.1525 <= 1.2`, so `ship_k = 3`; rank 0 is still the 78.22 deg axis, and the 3.73 deg line enters the merged axis as a *secondary* — `k_final = 3`, best 3.73 deg / 5.39 mm. OWN's best-donor candidate costs `1.2695 > 1.2`, so `ship_k = 1` and nothing donor-like can reach `merge_lines`; the merged axis is the single rank-0 line at **77.92 deg / 337.23 mm** (89.42 deg off GT).

So the answer is not "one arm wins": the `k` and the angle both come from the basin cut, and the tau cut is the second lock — **raising tau alone would not rescue `OWN_VOXEL_1MM`**, because the best donor-like candidate it can offer is already 37.90 deg. The *same shape* of failure is present in `OWN_SHARED_1MM` (2.10 deg in the pool, 9.61 deg top-60, ship 27.11 deg at 1.177 — admitted, so `k=2`) and `OWN_T09` (3.40 -> 20.25 deg, so 58.58 deg).

### Why two walls holding the same voxels behave differently

The two voxel walls contain the same `13,022` points in matched order; measured per arm in `logs/j01_selector_trace_detail.json`, they differ by at most `0.893 mm` (S0) / `0.948 mm` (S1) in position and `0.765` / `0.530` in normal component. The cross-swaps place that difference:

- `VOXEL_OWN_XYZ_AUTH_N` (OWN positions, AUTHOR normals): `6.63 deg` at `1.1254`, `k_final = 3`, final **1.37 mm** — the donor is recovered.
- `VOXEL_AUTH_XYZ_OWN_N` (AUTHOR positions, OWN normals): `25.62 deg` at `1.1858`, `k_final = 2`, final **38.20 mm** — the donor is lost.

Neither positions alone nor normals alone decide it: both walls sit inside the selector's unstable zone, where the size rank of one Hough basin among 130–136 decides whether it is refined at all. Because every arm shares seeds and stride, this is not draw noise — it is the wall data. At 1 mm voxels the own and Authors' walls are the same pottery to within a millimetre, and the frozen selector can still land on a 78 deg axis instead of the 3.7 deg one.

### Evidence, checks, figures

- Scripts (worktree = what ran, `sha256` equals `evidence/sources.tsv`): `j01_lobe14.py` 475 lines `6bb0c7e5...`, `j01_selector_trace14.py` 547 lines `dab98c6f...`, `run14.sbatch` 98 lines `40f0bc11...`.
- **Reproduction fidelity:** each stage is a line-for-line copy of the frozen `jt.normal_arm` / `jt.thickness_arm` / `sel.select_union_lines(..., tri_select=False)` / `keep_lines`; the job compares its kept lines with the frozen functions and exits non-zero unless `max|diff| <= 1e-9`. All 8 arms: `normal_maxdiff = thick_maxdiff = ship_maxdiff = 0` (the trace is evidence about the frozen selector, not about a transcription).
- `evidence/counts.tsv` asserts `286` and `8` data rows in-job; the job refuses any comma in the TSVs and any header that does not start with the specified columns. `evidence/renders.tsv`: name / relative path / description, both paths relative.
- Figures: `renders/J01_mesh_and_s1_lobe_3d.png` 3800x3600 px (`figsize 19x18 in, dpi 200`) — XY/XZ/YZ orthographic with equal aspect and a drawn 20 mm bar each, plus an oblique 3D view `view_init(25, -55)`, title carrying 5,524 / 17,795 / 42.2 % / covered 3,755 (68.0 %) / `o1_off`-only 1,000 (18.1 %) / uncovered 769 (13.9 %). `renders/J01_selector_trace.png` 3060x1548 px (`17x8.6 in, dpi 180`) — left: minimum donor angle at pool / top-60 / normal pre-tau / thickness pre-tau / ship pre-tau / final for the 8 arms; right: `cost/c0` of the best-donor refined candidate against the `tau = 1.2` line in `normal_arm`, `thickness_arm` and `shipped`. Both opened and read by eye: the left panel shows `OWN_VOXEL_1MM` climbing 2.8 -> 9.8 -> 19.4 -> 8.7 -> 37.9 -> 77.9 while `AUTHOR_VOXEL_1MM` goes 6.7 -> 6.7 -> 17.1 -> 8.3 -> 3.7 -> 3.7, which is this section at a glance.
- Cost: 2 `sbatch` submissions, `00:02:33` of node time, 8 CPUs.

### Compliance

| Requirement | Status | Where it can be re-read |
|---|---|---|
| Only `.scratch/surface-parity/t14/`, this ticket and the gitignored `artifacts/surface-parity-14/` touched; no `sfs_axes/`, `mesh_processing_headless.cpp`, `Data/`, `intent/`, `scripts/` or other ticket | met | `git status --porcelain` (one new dir + this file), `git diff --check` |
| Part A figure: 2x2 with XY/XZ/YZ orthographic + 1 oblique 3D, 180+ dpi, 20 mm bar each, mesh / a0 / o1_on / o1_off colours, donor + GT overlay, counts in the title | met | `renders/J01_mesh_and_s1_lobe_3d.png` (3800x3600, dpi 200), eye-checked |
| Corpus scan over 143 released stems x 2 faces, 1-NN to the author face wall, `pct_within_1mm` / `pct_over_5mm` / `nn_p90_mm` / `nn_max_mm` | met | `evidence/corpus_offwall_143.tsv` 286 rows, exact 9-column header, tab-delimited |
| Part B: 8 arms through the frozen draw `draw_pool(C, seeds=10, step=10)`, both cross-swap arms built from the matched voxel pair | met | `evidence/j01_arm_trace.tsv` 8 rows, exact 20-column header; `logs/j01_selector_trace_detail.json` per-candidate costs |
| Pool, per-arm pre-tau (`r0`, min donor, ratio, `k`) and final merged stage recorded | met | the 20 columns; detail JSON per candidate |
| Reproduction of the frozen selector, not a re-implementation | met | in-job `maxdiff = 0` against `jt.normal_arm`, `jt.thickness_arm`, `sel.select_union_lines(tri_select=False)`; job exits non-zero on > `1e-9` |
| Both scripts in ONE `sbatch` job; polled; final `sacct` State/ExitCode in `logs/run_status.txt` | met | `logs/run_status.txt` (both jobs, verbatim `sacct`), job 35842878 `COMPLETED 0:0` |
| Staged artefacts: both TSVs, `renders.tsv` with relative paths, both PNGs, `logs/run_status.txt` | met | `artifacts/surface-parity-14/{evidence,renders,logs}` |
| Tab-only delimiters, finite numbers, exact inline headers | met | in-job check: any comma is FATAL; row counts 286 / 8 asserted |
| Compute on a Spartan node via `sbatch`, never the laptop or login node | met | job 35842878 on `sapphire`; only file transfer, `sacct` and reading ran on the laptop/login node |
| Write-back with Part A, Part B, run path + `sacct`, compliance table; `Status: ready-for-review`; nothing merged, `main` untouched, worktree open | met | this section; `git log` on the ticket branch only |

### Known limits

1. **One draw per arm** (`seeds=10, step=10` -> 1,303 sampled points of the 13,022, as the ticket specifies), and the arms share seeds rather than being independent repetitions. Each row is one realisation of a stochastic draw; a distribution over draws (basin size rank of the donor-like axis across, say, 20 seeds) is what a claim about *probability* would need. The cross-swap pair is the independent check, and it moves the answer from 6.63 deg to 25.62 deg.
2. `Pot_C_Piece_03` face 1 and `Pot_J_Piece_09` are the known wrong-reference corpus caveats (`SfSpp_preprocessing/AGENTS.md`); their rows are reported for completeness and are not evidence about the method. `Pot_C_Piece_01` / `Pot_J_Piece_01` interior Bl0 edgelines measure the input; nothing here scores them.
3. Part A's off-wall criterion is 1-NN distance to the Authors' face wall, so a whole displaced wall and a genuine extra lobe both score high. The classes in the table were assigned by reading each face's distribution (within-1 mm fraction, p90 against max, and `own_points`), not by a second independent measurement.
4. The lobe figure's light grey mesh is largely buried under the denser walls and is visible only as speckle inside the orange band; the counts in the title carry the mesh coverage exactly.

**End state:** ready — Part A: of 286 faces, 9 exceed 10 % beyond 5 mm, but `J01` face 1 is the only one where a wall that seats on the Authors' surface (57.8 % within 1 mm) adds a coherent extra sheet 24–49 mm outside it (17,795 points, 1,000 mesh vertices) — the other eight are whole small walls displaced as a unit (I25 7.4 mm, J08 12–16 mm, D28 6.5 mm), the known wrong-reference caveat (C03 f1), or the one small partial analogue (D27 f1, 18.2 %). Part B: the split is the 60-basin draw cut, then `keep_lines(tau=1.2)` as the second lock — `OWN_VOXEL_1MM` has a 2.82 deg basin in its pool but not in its 60 largest (floor 9.84 deg), so its best refined donor-like candidate is 37.90 deg at `cost/c0 = 1.2695 > 1.2` and it ships `k = 1` at 77.92 deg / 337.23 mm, while `AUTHOR_VOXEL_1MM` refines a 6.69 deg basin to 3.73 deg at `1.1525 <= 1.2` and ships `k = 3` (final 3.73 deg / 5.39 mm); the xyz/normal cross-swaps move the outcome between 6.63 deg and 25.62 deg, so the selector is unstable at the sub-millimetre wall difference rather than at one bad arm. Nothing merged, `main` untouched, worktree open.
