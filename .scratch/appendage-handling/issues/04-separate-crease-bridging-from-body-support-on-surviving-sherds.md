# 04 — Separate crease bridging from body support on surviving sherds

**Answers:** E3
**Type:** research
**Blocked by:** 17
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-29)
**Branch:** 04-separate-crease-bridging-from-body-support-on-surviving-sherds, in /c/PR/worktrees/sfs/04
**Worker:** DeepSeek
**Hand-over:** DeepSeek (DSH Baton in worktree `C:/PR/worktrees/sfs/04`)

## Question

[Census attached appendages in t09 and Juglet](17-census-attached-appendages-in-t09-and-juglet.md) established that `Juglet_Piece_1` absorbed its loop handle (`7,658` pts, `10.5%` of `S1`) into `Surface_1` yet its estimated axis shifted only `0.023° / 0.17 mm` thanks to `359.0°` neck wrap — whereas `Pot_J_Piece_01` absorbed a `36.8%–42.2%` spout on a `135.0°` partial side wall and collapsed (`69.97°` best / `88.56°` rank-0 GT error), while `Pot_J_Piece_03`'s `11,511`-pt 3rd cluster is a sharp flat-base crease cut (`1.87°` GT), and `Pot_J_Piece_02` shattered its lug across small clusters (`0.0%` off-author, `6.82°` GT).

Across all `157` `t09` + `Juglet` pieces, with deep-dive instrumentation on `Pot_J_Piece_01`, `Pot_J_Piece_02`, `Pot_J_Piece_03`, and `Juglet_Piece_1`:
1. **Factor separation across `157` pieces:** Using thickness-relative protrusion (`d(S1,S0) - med_thick_mm > 4.0 mm` and `> 1.5x med_thick_mm`) alongside `S0` angular wrap (`wrap_deg`), how cleanly do `wrap_deg` and `S1` protrusion fraction separate broken axis failures from surviving sherds (including the `7` `s1_lobe` pieces)?
2. **Pre-merge (`r2`) vs post-merge (`r3`) crease bridging:** On `Pot_J_Piece_01`, `Pot_J_Piece_02`, `Pot_J_Piece_03`, and `Juglet_Piece_1`, did bridging across the appendage/base crease already happen during region growing (`growPaper234`, Ticket 25 rung `r2_clusters_premerge`) or during Appendix-A cluster merging (`mergePaper234`, `r3`), and how do tighter `theta` (`2.5`, `2.0`) or `SFS_MERGE_CLUSTER_DOT` (`0.887`, `0.95`) affect `r2` vs `r3`?
3. **Controlled azimuthal-wrap threshold (`Juglet_Piece_1`):** As we crop `Juglet_Piece_1`'s circular collar from `360°` down through `270° -> 180° -> 135° -> 90°` centered on its handle (`> 4.0 mm`), at what wrap angle does the absorbed loop handle break `sfs_axes` relative to the `NO_HANDLE` slice?

## Related tickets

- Blocked by [Census attached appendages in t09 and Juglet](17-census-attached-appendages-in-t09-and-juglet.md); unblocks [Decide appendage guard location and scope](05-decide-appendage-guard-location-and-scope.md).

---

## Execution Spec

### 1. Paths, pins, and strict read-only rule

- **Read-only upstream paths on Spartan** (never write into these):
  - `CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp`
  - `RUN09=/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1340_a50f8cc_t09-own-surfaces`
  - `SHIP=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship`
  - `T331=/data/gpfs/projects/punim2657/SfSpp/runs/20261112-0218_b1e1580_t331-large`
  - `SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif`
  - `APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer`
  - `PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3`
- **Frame rule (matches `.scratch/appendage-handling/t17/t17_common.py`):** Pot `A..J` surfaces, clouds, and axes are `1x mm`. `Juglet_def3x` clouds/surfaces/axes (`t09` and `t331`) are `3x` tree units — divide positions by `3.0` before computing millimetre distances/thicknesses or comparing against `1x` `Dataset/Juglet_GT` axes, and run frozen `t03_lib` `sfs_axes` in the native `3x` frame (converting `p_est / 3.0` for `d_gt_mm`).
- **Spartan run directory (all heavy compute via `sbatch` on `sapphire`, `8` CPUs, `32G`, `01:30:00`):**
  `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t04-crease-vs-wrap` (`work/`, `logs/`, `out/`, `evidence/`, `renders/`).
- **Allowed tracked files to add/edit in this worktree ONLY:**
  - `.scratch/appendage-handling/t04/*`
  - `.scratch/appendage-handling/issues/04-separate-crease-bridging-from-body-support-on-surviving-sherds.md`
  - **Zero edits** to `mesh_processing_headless.cpp`, `sfs_axes/`, `.scratch/appendage-handling/t17/`, or any files outside those two paths. (You may import helpers from `t17/t17_common.py` read-only or write standalone readers in `t04/`.)

### 2. Three quantitative experiments + three renders on Spartan (`run04.sbatch`)

1. **Part A — Corpus-wide `157`-piece protrusion vs wrap factor table (`evidence/factor_table_157.tsv`):**
   - For all `157` `t09` stems (`148` `Pot A..J` + `9` `Juglet_def3x`):
     - Compute `wrap_deg` (`0..360°`) of `S0` around the piece's GT axis when available (`wrap_axis_src=gt`), else around `axes09_own_regen` (`wrap_axis_src=est`).
     - Compute per-point nearest-neighbor distance from `S1` to `S0` in 1x mm (`cKDTree(P0).query(P1)`), `med_thick_mm = median(d)`, and thickness-relative protrusion metrics:
       - `off_s0_frac_4mm`: fraction of `S1` points with `(d - med_thick_mm) > 4.0`
       - `off_s0_frac_1p5x`: fraction of `S1` points with `d > 1.5 * med_thick_mm` and `d > 2.0`
       - `off_s0_p95_mm`: 95th percentile of `max(d - med_thick_mm, 0.0)`
       - `off_s0_max_mm`: max of `max(d - med_thick_mm, 0.0)`
     - Include `s0_pts`, `s1_pts`, `s1_over_s0`, `c3_frac`, `s1_off_author_5mm_pct` (`-1.0` where no author wall exists, e.g. 5 derived + Juglet), `gt_rank0_deg`, `gt_best_deg` (`-1.0` where no GT axis exists), and `flag_reason` (matching `t17` rules).
2. **Part B — C++ pre-merge (`r2`) vs post-merge (`r3`) & parameter sweep (`evidence/crease_sweep_4pieces.tsv`):**
   - Inspect `$RUN09/work/t09/regen09.sbatch`, `$RUN09/build/src/.scratch/juglet-breaklines/stage66/run_cell66.sh`, and `mesh_processing_headless.cpp` lines around `SFS_DUMP_STAGE` (`~1696-1915`, `5660-5745`) before writing scripts so CLI args and `r2_clusters_premerge` / `r3` dump filenames are exact.
   - Run unmodified `$RUN09/bin-MeshPreprocessingHeadless` inside `$SIF` across the `4` pieces `Pot_J_Piece_01`, `Pot_J_Piece_02`, `Pot_J_Piece_03` (on their `$CORP/Point/Pot_J/<stem>_Point.pcd` + `$CORP/Axes/<stem>_Axis.xyz` with `SHIPPED` base env), and `Juglet_Piece_1` (on `$T331/cloud_mesh/Juglet_Piece_1_Point.pcd` + `$T331` / `ENV3` base env) with Ticket 25 dump armed: `SFS_DUMP_STAGE=<RUN>/work/dump25/<arm>/<stem>` and `SFS_DUMP_PIECES=<stem>` (`SFS_DEDUPE` unset, `SFS_WALL_PAIR_FILTER` unset).
   - Run `5` env arms per piece (`20` runs total):
     1. `baseline_t09`: Pot J = `SHIPPED` (`theta=3.4`); Juglet_Piece_1 = `ENV3` (`SFS_MERGE_CLUSTER_DOT=0.887`, `theta=3.4`)
     2. `theta_2p5`: base + `SFS_PAPER_THETA=2.5 SFS_SMOOTHNESS_DEG=2.5`
     3. `theta_2p0`: base + `SFS_PAPER_THETA=2.0 SFS_SMOOTHNESS_DEG=2.0`
     4. `merge_dot_887` (for Pot J = base + `SFS_MERGE_CLUSTER_DOT=0.887`; for Juglet_Piece_1 use `merge_dot_off` with `SFS_MERGE_CLUSTER_DOT=0.0` so Juglet tests both dot-off and baseline `0.887`!)
     5. `merge_dot_95`: base + `SFS_MERGE_CLUSTER_DOT=0.95`
   - Parse each run's `r2_clusters_premerge` JSON/PLY, stdout `mesh.log` (`merge`, `PAPER-234` / `SFS-74`), and output `.S0`/`.S1` PLYs to record exact `env_override`, `r2_n_clusters`, `r2_c1_pts`, `r2_c2_pts`, `r2_c3_pts`, `merge_fired_count` (count of accepted merges logged between `r2` and `r3`, plus check `r2_clusters_premerge` vs `r3` sizes), `r3_s0_pts`, `r3_s1_pts`, `s1_protrusion_pts` (points on `r3 S1` with `d(S1,S0) - med_thick_mm > 4.0 mm` computed against baseline `med_thick_mm` or that arm's `med_thick_mm` — document which consistently), and deterministic `bridged_stage` enum (`growth_r2 | merge_r3 | split_clean | shattered` based on whether protrusion/creased band already fused into `r2_c1/c2` vs merged in `r3` vs stayed split out in `c3+` / small clusters).
3. **Part C — Controlled `Juglet_Piece_1` azimuthal-wrap ablation (`evidence/juglet1_wrap_ablation.tsv`):**
   - Load `t09` `Juglet_Piece_1.S0` and `.S1` (`6xN` walls with normals in native 3x units) and GT axis (`Dataset/Juglet_GT`).
   - Identify handle points on `S1` where `d(S1, S0) > 4.0 mm` (1x mm, matching Ticket 17's `7,658`-pt handle). Find the handle's azimuthal centroid `phi0` around the GT axis.
   - For each target angular span `span in [360, 270, 180, 135, 90]`, keep all points in `S0` and `S1` whose wrapped angular offset `|atan2_diff(phi, phi0)| <= span / 2` (so at smaller spans, the slice stays **centered on the handle**, progressively removing opposite-side circular rim support; at `360` keep full walls).
   - Produce `2` arms per span: `FULL` (sliced `S0` + sliced `S1` including handle) and `NO_HANDLE` (sliced `S0` + sliced `S1` minus handle points `> 4.0 mm`), giving `10` runs total.
   - Run frozen `t03_lib` `sfs_axes` (`draw_pool(C, seeds=10, step=10)` -> `select_union_lines`) on each of the `10` cases, measuring `actual_wrap_deg` of sliced `S0`, `s0_pts`, `s1_pts`, `handle_pts` (handle points in that arm), `handle_frac_s1`, `k_axes`, `gt_rank0_deg`, `gt_best_deg`, `d_gt_mm` (`radial_axial_errors` using `/ 3.0`).
4. **Part D — Visual renders (`>=150 DPI`, `> 20 KB`, `20 mm` scale bars on every 3D panel):**
   - `renders/Focal_10_protrusion_and_wrap_gallery.png`: `2x5` 3D gallery of `Pot_C_Piece_03`, `Pot_D_Piece_27`, `Pot_D_Piece_28`, `Pot_I_Piece_25`, `Pot_J_Piece_01`, `Pot_J_Piece_08`, `Pot_J_Piece_09`, `Juglet_Piece_1`, `Pot_J_Piece_02`, `Pot_J_Piece_03` showing `S0` (blue), `S1` body (teal), `S1` thickness-relative protrusion (`(d - med_thick_mm) > 4.0 mm`, bright orange-red), annotated with `wrap_deg`, `off_s0_frac_4mm`, `gt_best_deg`, `20 mm` scale bars.
   - `renders/Factor_separation_and_juglet_wrap_ablation.png`: Two-panel summary figure — (Left) scatter of `wrap_deg` vs `off_s0_frac_4mm` across all GT-scored pieces (`gt_best_deg <= 10°` pass vs `> 10°` fail) with the focal pieces labeled; (Right) `Juglet_Piece_1` azimuthal-wrap sweep (`360° -> 90°`) plotting `gt_rank0_deg` and `gt_best_deg` for `FULL` vs `NO_HANDLE` with `10°` failure threshold line.
   - `renders/Crease_bridging_rung2_vs_rung3_4pieces.png`: `4x2` grid (`4` focal pieces × [Pre-merge `r2_clusters_premerge` `c1/c2/c3+` | Post-merge baseline `S0/S1`]), each panel with a `20 mm` scale bar showing cleanly whether the crease bridged before `r2` or during `r3`.

### 3. Deliverables & Verification Gates

Fetch all deliverables into `<worktree>/artifacts/appendage-handling-04/`:
1. `evidence/factor_table_157.tsv` (`158` lines, `17` columns: `stem`, `vessel`, `wrap_axis_src`, `wrap_deg`, `med_thick_mm`, `off_s0_frac_4mm`, `off_s0_frac_1p5x`, `off_s0_p95_mm`, `off_s0_max_mm`, `s0_pts`, `s1_pts`, `s1_over_s0`, `c3_frac`, `s1_off_author_5mm_pct`, `gt_rank0_deg`, `gt_best_deg`, `flag_reason`).
2. `evidence/juglet1_wrap_ablation.tsv` (`11` lines, `11` columns: `target_span_deg`, `arm`, `actual_wrap_deg`, `s0_pts`, `s1_pts`, `handle_pts`, `handle_frac_s1`, `k_axes`, `gt_rank0_deg`, `gt_best_deg`, `d_gt_mm`).
3. `evidence/crease_sweep_4pieces.tsv` (`21` lines, `12` columns: `stem`, `arm`, `env_override`, `r2_n_clusters`, `r2_c1_pts`, `r2_c2_pts`, `r2_c3_pts`, `merge_fired_count`, `r3_s0_pts`, `r3_s1_pts`, `s1_protrusion_pts`, `bridged_stage`).
4. `evidence/renders.tsv` (`4` lines: `name\tpath\tdescription` + `3` `renders/*.png` rows).
5. All `3` PNGs under `renders/` (`> 20 KB` each), visually inspected via `read_file`.
6. `logs/run_status.txt` (`sacct` showing `COMPLETED 0:0`).

### 4. Mandatory In-DSH Read-Only Audit & Hand-Back

Before finishing:
1. Spawn a **read-only sub-agent** (`t04-auditor`, read-only tools only) inside this DSH session to independently audit every item in the spec against the actual TSVs, `run04.sbatch`, `sacct` status, renders, and git status.
2. Fix any defects raised by `t04-auditor` and re-verify affected checks.
3. Update this ticket file with `**Status:** ready-for-review`, clear quantitative answers to all 3 sub-questions, self-check compliance table, `t04-auditor` summary, and `**End state:** ready`.
4. Commit all work under `.scratch/appendage-handling/{t04/,issues/04-separate-crease-bridging-from-body-support-on-surviving-sherds.md}` with a `Worker:` trailer, remove any stray `__pycache__/`, push `origin HEAD`, and verify `git status --short` is clean (`artifacts/` is gitignored).
