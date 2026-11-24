# 05: Test whether duplicates, coverage, sampling, or stride explain the Pot E candidate-count gap

**What to build:** Test on Pot E sherds 27 and 28 whether exact duplicate points, 1 mm exclusive-fringe coverage, spatial sampling/density, or the frozen estimator's `n < 5000` stride-1 switch explain why our wall clouds emit 1 candidate axis on sherd 28 vs 2 on the authors' (and 3 vs 2 on sherd 27), while keeping every retained point's own original normal untouched.

**Answers:** E2

**Blocked by:** None. Surface Parity 04 is resolved on main and showed wall normals alone shift axis angles/positions while candidate count `k` stays tied to point coordinates.

**Status:** ready-for-agent

**Worker:** unassigned

**Budget:** medium 5

**Hand-over:** DeepSeek V4.1 Flash via DSH Baton. Lead verification is outside the worker's worktree.

## Frozen estimator and scope

Use the two saved inner and outer wall arrays of E27 and E28 loaded by `t03_lib.walls(stem, surfaces=own/authors)` from the archived run `/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship` (SHIP). Use the archived TORA Python `/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3` and `SFS_IMPL=$SHIP/work/impl_t03`. Reuse `t03_lib.draw_pool(C, seeds=10, step=step)`, `t03_extract.select_lines(..., 6, None)`, and `t03_extract.write_lines` on the frozen shipped joint-selector path with its original environment. Form `C` by concatenating face 0 then face 1. Reference axes (`t03_lib.gt_axis(stem)`) are for readout only.

Changes are limited to this ticket (in worktree `C:/PR/worktrees/sfs/05`) and four new files under `.scratch/surface-parity/t05/`: `sampling05.py` (deduplication, coverage filtering, matching, shared voxel resampling, and small fixtures), `extract05.py` (worker wrapper, tables, and rendering), `submit.sbatch` (Spartan compute job), and `check05.py` (public evidence validation, including `--expect-terminal` for post-poll verification). Use a fresh run directory and existing Slurm polling (`scripts/slurm_poll.sh <JOBID>`). Preserve all source, frozen inputs, estimator (`potsac.py`, `profile.py`, `select.py`), configured seed list (`seeds=10`), selector, candidate cap (`6`), and assembly inputs. Do not transfer or re-estimate normals, do not run the assembler, and do not change extraction defaults in this ticket.

## Ten arms per sherd (20 extraction runs total)

Run all ten arms on both Pot E sherd 27 and Pot E sherd 28. In every arm, every retained point MUST keep its exact original 6-vector `(x, y, z, nx, ny, nz)` verbatim from its own native wall—no coordinate averaging, normal re-estimation, normalization, or normal flipping.

1. `OWN`: native OWN walls, `step=10`.
2. `AUTHOR`: native AUTHOR walls, `step=10`.
3. `OWN_DEDUP`: per face, remove exact duplicate float64 `(x, y, z)` rows keeping the first occurrence in archive order; `step=10`.
4. `OWN_STRIDE1`: native OWN walls passed to `draw_pool(C, seeds=10, step=1)` (isolates the `ADAPTIVE_UNDER_5K` `n < 5000` stride-1 switch).
5. `OWN_DEDUP_STRIDE1`: `OWN_DEDUP` walls passed to `draw_pool(C, seeds=10, step=1)`.
6. `OWN_SHARED_1MM`: per face, keep OWN rows whose nearest AUTHOR point on the same face lies within `1.000 mm` inclusive Euclidean distance (preserve original OWN row order and duplicates); `step=10`.
7. `AUTHOR_SHARED_1MM`: per face, keep AUTHOR rows whose nearest OWN point on the same face lies within `1.000 mm` inclusive Euclidean distance (preserve original AUTHOR row order); `step=10`.
8. `OWN_MATCHED_TO_AUTHOR`: per face, starting from `OWN_DEDUP`, for each AUTHOR point find its nearest `OWN_DEDUP` point on the same face within `1.000 mm` inclusive (ties to first `OWN_DEDUP` row in archive order), deduplicate the matched `OWN_DEDUP` indices, and emit in `OWN_DEDUP` archive order; `step=10`.
9. `OWN_COMMON_VOXEL`: per face, map points to integer 1.000 mm voxel keys `(i, j, k) = np.floor(xyz / 1.0).astype(np.int64)` (origin `(0, 0, 0)`). Keep only voxel keys occupied by **both** OWN and AUTHOR on that face. In each shared voxel, keep the single OWN point closest in Euclidean distance to the voxel center `(i + 0.5, j + 0.5, k + 0.5)` (ties to first OWN row in archive order). Emit rows sorted lexicographically by `(i, j, k)`; `step=10`.
10. `AUTHOR_COMMON_VOXEL`: same shared 1.000 mm voxels per face as `OWN_COMMON_VOXEL`, keeping the single AUTHOR point closest to `(i + 0.5, j + 0.5, k + 0.5)` (ties to first AUTHOR row in archive order), sorted lexicographically by `(i, j, k)`; `step=10`.

Compare `OWN` and `AUTHOR` outputs on both sherds against the archived Ticket 19 axis pack `20261124-0443_21446b8_t19-decisions`. Accept the archived-control gate only when bytes match, or when candidate counts and ranks agree and every ordered serialized component agrees within absolute `1e-9` and zero relative tolerance. A failed gate is an inconclusive experiment: preserve its evidence and stop interpreting the arms. If any arm cannot return finite candidate rows, record status `no_axis`, `k=0`, and the stage and reason explicitly without inventing geometric distances.

## Evidence and acceptance

- [ ] `inputs.tsv` has 40 rows (2 sherds × 10 arms × 2 faces) with exact header `sherd,arm,face,native_points,points,duplicate_xyz,retained_fraction,xyz_sha256,normals_sha256,source_sha256`. Hash the in-order little-endian contiguous float64 `Nx3` XYZ and normal matrices separately. Verify `duplicate_xyz == 0` on `OWN_DEDUP`, `OWN_DEDUP_STRIDE1`, `OWN_MATCHED_TO_AUTHOR`, `OWN_COMMON_VOXEL`, and `AUTHOR_COMMON_VOXEL`, and identical `points` between `OWN_COMMON_VOXEL` and `AUTHOR_COMMON_VOXEL` on every `(sherd, face)`. Keep full retained index maps under `evidence/indices/*.npz` on Spartan; fetch only short tables, summary, and renders. Record `sources.tsv` with wall, GT, archive, `t03_*`/`impl_t03`, and `t05` code hashes.
- [ ] `runs.tsv` has 20 rows (2 sherds × 10 arms) with exact header `sherd,arm,status,k,axes_sha256,archive_ok,requested_step,effective_stride,drawn_points,basins,reason` (plus optional numeric columns `archived_sha256`, `archive_rank_count_agree`, `archive_max_abs`, `secs`). Set `archive_ok` to `1` or `0` for `OWN` and `AUTHOR`, and leave it blank for all other arms. Record `axes.tsv` with exact header `sherd,arm,rank,oriented_deg,line_deg,anchor_mm,pos_x,pos_y,pos_z,dir_x,dir_y,dir_z,cost` (rank starts at 1; `oriented_deg` in `0–180`, `line_deg` in `0–90`, `anchor_mm` from the pose-derived reference anchor). Record `changes.tsv` (16 rows, non-native arms vs parent `OWN` or `AUTHOR`) with exact header `sherd,arm,parent_arm,k_parent,k_arm,axes_bytes_identical,best_ref_line_deg_parent,best_ref_line_deg_arm,best_ref_anchor_mm_parent,best_ref_anchor_mm_arm,max_rank_line_delta_deg,max_rank_anchor_delta_mm`, defining `max_rank_line_delta_deg` strictly as the sign-independent 3D line angle `arccos(|dot|)` in `0–90°`.
- [ ] `fixtures.tsv` has exact header `fixture,status,detail` and records `PASS` for all 8 named fixtures run on Spartan: `dedup_first_order`, `shared_inclusive_cut`, `shared_same_face`, `matched_unique_order`, `voxel_shared_center_tie`, `voxel_negative_coords`, `normals_verbatim`, and `stride_override`.
- [ ] `renders.tsv` has exact header `sherd,path,scale_bar_mm` (`path` relative to run root, e.g. `renders/Pot_E_Piece_27.png`, `scale_bar_mm` = `20`). Produce one locked multi-panel comparison PNG per sherd with a `20 mm` scale bar showing both wall faces and ranked candidate axes for `OWN` vs `OWN_MATCHED_TO_AUTHOR` and `OWN_COMMON_VOXEL` vs `AUTHOR_COMMON_VOXEL`. Inspect both figures by eye.
- [ ] `jobs.tsv` has exact header `job_id,state,exit_code` and records every submitted Slurm ID, terminal state, and exit code (`check05.py --expect-terminal` passes after polling). Leave `verdict` and `human_note` empty in `runs/index.tsv`. Write a `## Write-back` with facts only, budget used, one end state, a per-requirement compliance table, and a separate read-only DeepSeek review that checks the tables and opens both figures. Leave interpretation, commits, and closure to the lead.

Named checks: `python -m py_compile` on the three Python files under `.scratch/surface-parity/t05/`, `bash -n .scratch/surface-parity/t05/submit.sbatch`, run fixtures and `check05.py` on the compute node (and `check05.py --expect-terminal` after polling), and `git diff --check` scoped to the ticket.
