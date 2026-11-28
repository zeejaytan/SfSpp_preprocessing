# 02 — Probe the 20 author-excluded special-part meshes

**Answers:** E3
**Type:** task
**Blocked by:** None
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-29)
**Branch:** 02-probe-the-20-author-excluded-special-part-meshes, in /c/PR/worktrees/sfs/02
**Worker:** DeepSeek
**Hand-over:** DeepSeek (DSH Baton in worktree `C:/PR/worktrees/sfs/02`)

## Question

What are all `21` non-released meshes in the Spartan corpus (`/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Mesh/`: the `20` special-part fragments excluded from the authors' released `Point/` benchmark across Pots C, D, E, F, I, and J — `5` already processed via `derived` clouds in `t09` plus `15` unprocessed special parts — along with mesh-only `Pot_C_Piece_07`), and what does our **unmodified** pipeline (`cc_mesh_to_pcd.sh` -> `MeshPreprocessingHeadless` -> `sfs_axes`) do when fed them directly?

Specifically:
1. Measure geometry (vertex count, `bbox_diag_mm`, principal extents `L1xL2xL3` in mm), CloudCompare conversion (`cc_rc`, `npts_cloud`), `MeshPreprocessingHeadless` segmentation (`mesh_rc`, `clusters_total`, `c1..c3`, `s0_pts`, `s1_pts`, `mesh_covered_2mm_pct`), and frozen `t03-ship` `sfs_axes` output (`k_axes`, `rank0_vs_auth_deg`, `best_vs_auth_deg`, `outcome`).
2. Render all `21` meshes alongside their extracted `S0`/`S1` surfaces and rank-0 axis lines in 3D/orthogonal views with `20 mm` scale bars so a conservator can see which pieces are standalone handles/noses/ornaments vs tiny wall fragments, and where the unmodified pipeline succeeds, mis-segments, or fails cleanly.

## Related tickets

- Independent of [Census attached appendages in t09 and Juglet](17-census-attached-appendages-in-t09-and-juglet.md); unblocks [Decide appendage guard location and scope](05-decide-appendage-guard-location-and-scope.md).

---

## Execution Spec

### 1. Paths, pins, and strict read-only rule

- **Read-only upstream paths on Spartan** (never write into these):
  - `CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp`
  - `RUN09=/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1340_a50f8cc_t09-own-surfaces`
  - `SHIP=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship`
  - `CC_SCRIPT=/data/gpfs/projects/punim2657/sfs_preprocessing/cc_mesh_to_pcd.sh`
  - `SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif`
  - `APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer`
  - `PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3`
- **Spartan run directory (all heavy compute via `sbatch` on `sapphire`, `8` CPUs, `32G`, `02:00:00`):**
  `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t02-excluded-special-parts` (`work/`, `logs/`, `out/`, `evidence/`, `renders/`).
- **Allowed tracked files to add/edit in this worktree ONLY:**
  - `.scratch/appendage-handling/t02/*`
  - `.scratch/appendage-handling/issues/02-probe-the-20-author-excluded-special-part-meshes.md`
  - **Zero edits** to `mesh_processing_headless.cpp`, `sfs_axes/`, or any files outside those two paths.
  - Before final commit/push, remove any `artifacts/` or `__pycache__` inside tracked `.scratch/` if staging clean (note: keep fetched deliverables in `<worktree>/artifacts/appendage-handling-02/` which is gitignored; delete `.pyc` / `__pycache__` under `.scratch/appendage-handling/t02/`).

### 2. Exact `21` target stems

Determine dynamically or verify exact match against `sorted(mesh_stems - released_stems)`:
- **`5` already processed in `t09` (`source = t09_derived`):**
  `Pot_F_Piece_07`, `Pot_I_Piece_28`, `Pot_I_Piece_29`, `Pot_I_Piece_30`, `Pot_J_Piece_12`.
- **`16` unprocessed meshes (`source = fresh_probe`):**
  `Pot_C_Piece_05`, `Pot_C_Piece_06`, `Pot_C_Piece_07` (note: `Pot_C_Piece_07` has no `$CORP/Axes/Pot_C_Piece_07_Axis.xyz`), `Pot_D_Piece_30`, `Pot_D_Piece_31`, `Pot_D_Piece_32`, `Pot_E_Piece_32`, `Pot_E_Piece_33`, `Pot_E_Piece_34`, `Pot_J_Piece_13`, `Pot_J_Piece_14`, `Pot_J_Piece_15`, `Pot_J_Piece_16`, `Pot_J_Piece_17`, `Pot_J_Piece_18`, `Pot_J_Piece_19`.

### 3. Pipeline steps on Spartan compute node (`run02.sbatch`)

1. **Unprocessed `16` meshes (`fresh_probe`):**
   - For each mesh (`_Mesh_DS.obj` or `_Mesh.obj`), isolate each piece into its own staging dir under `$RUN/work/pieces/<stem>/`:
   - Step A (`CloudCompare` sampling -> PCD): copy/symlink the OBJ and run `bash "$CC_SCRIPT" -i <mesh> -o <cloud_dir> -f` (inspect `cc_mesh_to_pcd.sh` first to verify exact CLI flags, module load, and output filename `<stem>_Point.pcd`). Wrap each piece with `set +e` so if CloudCompare exits non-zero (e.g. too few points / small-fragment SOR guard), capture `cc_rc`, log it, and continue to the remaining pieces.
   - Step B (`MeshPreprocessingHeadless` segmentation): inspect `$RUN09/build/src/.scratch/juglet-breaklines/stage66/run_cell66.sh` and `$RUN09/bin-MeshPreprocessingHeadless` CLI args first! Stage each piece whose `cc_rc == 0` and run `$RUN09/bin-MeshPreprocessingHeadless` inside `$APT exec --bind /data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657 "$SIF"` with the exact `t09` `SHIPPED` env (`SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0`, leaving `SFS_DEDUPE` and `SFS_WALL_PAIR_FILTER` unset), saving full stdout/stderr to `$RUN/work/pieces/<stem>/mesh.log` and recording `mesh_rc`. For `Pot_C_Piece_07` (no author axis file), pass a dummy axis file (`0 0 0 0 0 1`) only if the binary/stager requires an axis argument.
2. **`5` `t09_derived` pieces:** Read existing `$RUN09/out/Pot_<P>/geom/<stem>.{S0,S1}` and `$RUN09/out/Pot_<P>/pieces/<stem>/mesh.log` (`cc_rc=0`, `mesh_rc=0`, `npts_cloud` from `Total points:` in `mesh.log`).
3. **Axis extraction (`sfs_axes`) & metrics across all `21` pieces:**
   - Reuse the loader pattern in `.scratch/appendage-handling/t17/t17_common.py` and the `t03_lib` selector (`draw_pool(C, seeds=10, step=10)` -> `select_union_lines(reps, sizes, C0, C1, C, 6, tri_select=None)` in `.scratch/appendage-handling/t17/juglet1_ablation17.py`).
   - Run `sfs_axes` on every piece with non-empty `S0` and `S1` (wrapping in `try/except` so degenerate small walls record `k_axes=0` cleanly without aborting).
   - Compare estimated axes (`rank0_vs_auth_deg`, `best_vs_auth_deg` across up to 3 lines) against `$CORP/Axes/<stem>_Axis.xyz` (use `-1.0` where no author axis exists, i.e., `Pot_C_Piece_07`, or when `k_axes == 0`). Compute `mesh_verts`, `bbox_diag_mm`, `extents_mm` (`L1xL2xL3` sorted descending SVD/PCA extents in mm formatted e.g. `42.1x21.4x11.2`), `clusters_total`, `c1_pts`, `c2_pts`, `c3_pts`, `s0_pts`, `s1_pts`, `s1_over_s0` (`0.0` if `s0_pts == 0`), `mesh_covered_2mm_pct` (fraction of mesh vertices within `2.0 mm` of `S0 union S1`), and deterministic `outcome`:
     - `cc_failed` if `cc_rc != 0`
     - `mesh_failed` if `cc_rc == 0` and (`mesh_rc != 0` or `s0_pts == 0` or `s1_pts == 0`)
     - `walls_only` if `s0_pts > 0` and `s1_pts > 0` and `k_axes == 0`
     - `walls_and_axes` if `s0_pts > 0` and `s1_pts > 0` and `k_axes >= 1`

### 4. Deliverables & Verification Gates

Fetch all deliverables into `<worktree>/artifacts/appendage-handling-02/`:
1. `evidence/excluded_21_probe.tsv`: `22` lines (header + `21` pieces sorted by stem), exact `21` tab-separated columns:
   `stem`, `vessel`, `source`, `mesh_verts`, `bbox_diag_mm`, `extents_mm`, `cc_rc`, `npts_cloud`, `mesh_rc`, `clusters_total`, `c1_pts`, `c2_pts`, `c3_pts`, `s0_pts`, `s1_pts`, `s1_over_s0`, `mesh_covered_2mm_pct`, `k_axes`, `rank0_vs_auth_deg`, `best_vs_auth_deg`, `outcome`. All numeric columns finite (zero `NaN`/`inf`, using `-1.0` / `-1` sentinel where unavailable).
2. `renders/Excluded_21_meshes_and_walls_gallery.png` (`>=150 DPI`, `> 20 KB`): grid showing all `21` pieces (`OBJ` mesh vertices light gray, `S0` blue, `S1` orange), `20 mm` scale bar in every panel, annotated with `<stem>`, `extents_mm`, `S0/S1` counts, `k_axes`, and `outcome`.
3. `renders/Pot_J_excluded_13_to_19_detail.png` (`>=150 DPI`, `> 20 KB`): detailed `3D / XY / XZ` views of `Pot_J_Piece_13..19` showing mesh, `S0`, `S1`, estimated rank-0 axis line (if `k >= 1`), and author axis line with `20 mm` scale bars.
4. `evidence/renders.tsv`: exact `3` lines (`name\tpath\tdescription` + the `2` PNG rows with relative `renders/*.png` paths).
5. `logs/run_status.txt`: `sacct -j <JOBID> -X --format=JobID,JobName%20,Partition,AllocCPUS,State,ExitCode,Elapsed --parsable2` proving `COMPLETED` with `ExitCode 0:0`.
6. Visually inspect both PNGs with `read_file` before finishing.
7. Assert all deliverable files, row counts, column headers, and PNG sizes in `run02.sbatch` before exit 0.

### 5. Mandatory In-DSH Read-Only Audit & Hand-Back

Before finishing:
1. Spawn a **read-only sub-agent** (`t02-auditor`, read-only tools only) inside this DSH session to independently audit every item in the spec (git diff scope, `sbatch` + `sacct` `COMPLETED 0:0`, all `21` stems present & finite in `excluded_21_probe.tsv`, `renders.tsv` + both PNG renders, visual correctness of renders, and write-back compliance).
2. Fix any defects raised by `t02-auditor` and re-verify affected checks.
3. Update this ticket file with:
   - `**Status:** ready-for-review`
   - Findings summary + physical classification of the `21` pieces (handles/spouts/ornaments vs flat sherds/bases) + self-check compliance table + `t02-auditor` audit summary + `**End state:** ready`.
4. Commit all work under `.scratch/appendage-handling/{t02/,issues/02-probe-the-20-author-excluded-special-part-meshes.md}` with a `Worker:` trailer, remove any stray `__pycache__/`, push `origin HEAD`, and verify `git status --short` is clean (`artifacts/` is gitignored).
