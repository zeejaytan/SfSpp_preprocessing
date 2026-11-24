# 05: Test whether duplicates, coverage, sampling, or stride explain the Pot E candidate-count gap

**What to build:** Test on Pot E sherds 27 and 28 whether exact duplicate points, 1 mm exclusive-fringe coverage, spatial sampling/density, or the frozen estimator's `n < 5000` stride-1 switch explain why our wall clouds emit 1 candidate axis on sherd 28 vs 2 on the authors' (and 3 vs 2 on sherd 27), while keeping every retained point's own original normal untouched.

**Answers:** E2

**Blocked by:** None. Surface Parity 04 is resolved on main and showed wall normals alone shift axis angles/positions while candidate count `k` stays tied to point coordinates.

**Status:** resolved
**Branch:** 05-test-sampling-and-coverage-at-fixed-normals, in /c/PR/worktrees/sfs/05
**Worker:** dsh-surface-parity-05


**Budget:** medium 5

**Hand-over:** DeepSeek V4.1 Flash via DSH Baton. Lead verification is outside the worker's worktree.
**DSH cost:** session-71ce176e-623f-4b2c-89eb-acdc30d6ccc9 (dsh-opencode-go/deepseek-v4.1-flash, flat-rate)

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

- [x] `inputs.tsv` has 40 rows (2 sherds × 10 arms × 2 faces) with exact header `sherd,arm,face,native_points,points,duplicate_xyz,retained_fraction,xyz_sha256,normals_sha256,source_sha256`. Hash the in-order little-endian contiguous float64 `Nx3` XYZ and normal matrices separately. Verify `duplicate_xyz == 0` on `OWN_DEDUP`, `OWN_DEDUP_STRIDE1`, `OWN_MATCHED_TO_AUTHOR`, `OWN_COMMON_VOXEL`, and `AUTHOR_COMMON_VOXEL`, and identical `points` between `OWN_COMMON_VOXEL` and `AUTHOR_COMMON_VOXEL` on every `(sherd, face)`. Keep full retained index maps under `evidence/indices/*.npz` on Spartan; fetch only short tables, summary, and renders. Record `sources.tsv` with wall, GT, archive, `t03_*`/`impl_t03`, and `t05` code hashes.
- [x] `runs.tsv` has 20 rows (2 sherds × 10 arms) with exact header `sherd,arm,status,k,axes_sha256,archive_ok,requested_step,effective_stride,drawn_points,basins,reason` (plus optional numeric columns `archived_sha256`, `archive_rank_count_agree`, `archive_max_abs`, `secs`). Set `archive_ok` to `1` or `0` for `OWN` and `AUTHOR`, and leave it blank for all other arms. Record `axes.tsv` with exact header `sherd,arm,rank,oriented_deg,line_deg,anchor_mm,pos_x,pos_y,pos_z,dir_x,dir_y,dir_z,cost` (rank starts at 1; `oriented_deg` in `0–180`, `line_deg` in `0–90`, `anchor_mm` from the pose-derived reference anchor). Record `changes.tsv` (16 rows, non-native arms vs parent `OWN` or `AUTHOR`) with exact header `sherd,arm,parent_arm,k_parent,k_arm,axes_bytes_identical,best_ref_line_deg_parent,best_ref_line_deg_arm,best_ref_anchor_mm_parent,best_ref_anchor_mm_arm,max_rank_line_delta_deg,max_rank_anchor_delta_mm`, defining `max_rank_line_delta_deg` strictly as the sign-independent 3D line angle `arccos(|dot|)` in `0–90°`.
- [x] `fixtures.tsv` has exact header `fixture,status,detail` and records `PASS` for all 8 named fixtures run on Spartan: `dedup_first_order`, `shared_inclusive_cut`, `shared_same_face`, `matched_unique_order`, `voxel_shared_center_tie`, `voxel_negative_coords`, `normals_verbatim`, and `stride_override`.
- [x] `renders.tsv` has exact header `sherd,path,scale_bar_mm` (`path` relative to run root, e.g. `renders/Pot_E_Piece_27.png`, `scale_bar_mm` = `20`). Produce one locked multi-panel comparison PNG per sherd with a `20 mm` scale bar showing both wall faces and ranked candidate axes for `OWN` vs `OWN_MATCHED_TO_AUTHOR` and `OWN_COMMON_VOXEL` vs `AUTHOR_COMMON_VOXEL`. Inspect both figures by eye.
- [x] `jobs.tsv` has exact header `job_id,state,exit_code` and records every submitted Slurm ID, terminal state, and exit code (`check05.py --expect-terminal` passes after polling). Leave `verdict` and `human_note` empty in `runs/index.tsv`. Write a `## Write-back` with facts only, budget used, one end state, a per-requirement compliance table, and a separate read-only DeepSeek review that checks the tables and opens both figures. Leave interpretation, commits, and closure to the lead.

Named checks: `python -m py_compile` on the three Python files under `.scratch/surface-parity/t05/`, `bash -n .scratch/surface-parity/t05/submit.sbatch`, run fixtures and `check05.py` on the compute node (and `check05.py --expect-terminal` after polling), and `git diff --check` scoped to the ticket.

## Write-back

Facts only. Interpretation, commits and closure stay with the lead.

**Run under acceptance:** `/data/gpfs/projects/punim2657/SfSpp/runs/20261125-0017_57a4da7_t05-sampling-coverage` (git7 `57a4da7`, tag `t05-sampling-coverage`), job `35624709`, `sacct` terminal `COMPLETED|0:0|2026-11-25T00:44:38`, 15 min wall. Submitted with `sbatch --parsable` from the run directory, polled with `scripts/slurm_poll.sh 35624709 30` to the terminal state.
**Earlier attempt (kept as its own run directory, not reused):** `20261125-0013_57a4da7_t05-sampling-coverage`, job `35624000`, `FAILED|1:0` after 2 s. Cause: my own `normals_verbatim` fixture placed the duplicate row before the row carrying the unnormalized normal, so the assertion read the wrong column; 7/8 fixtures passed and the run stopped before extraction. The transform was not at fault. The fixture wall was reordered, then 8/8 passed.
**Budget:** medium 5 — **1 of 5 tries used** (the failed first submission; the one-sherd pre-flight and a deliberate partial-run gate were diagnostics, not acceptance checks).

**Frozen inputs, untouched:** SHIP `20261121-1319_2e951d9_t03-ship` (`work/t03_lib.py`, `work/t03_extract.py`, `work/impl_t03/sfs_axes/*`), archive control `20261124-0443_21446b8_t19-decisions`, TORA `/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3`. No file under SHIP, the corpus or the estimator was written; no normal transferred or re-estimated; assembler not run; `seeds=10`, cap 6 and the joint selector unchanged; `SFS_AXES_ADAPTIVE_UNDER_5K` left at its frozen default.

**Gates**
- In-job gate: `SUMMARY checks=980 failures=0` (`evidence/check.txt`).
- Post-poll gate: `SUMMARY checks=989 failures=0` with `--expect-terminal` (`evidence/check_postpoll.txt`), re-run after the earlier attempt's terminal row was appended.
- Named static checks on a compute node: `python -m py_compile sampling05.py extract05.py check05.py` rc 0, `bash -n submit.sbatch` rc 0, and `ls -1` showing exactly the four ticket files (`evidence/check_static.txt`, host `spartan-bm065`, 2026-11-25T01:08:34).
- Fixtures on the compute node: 8/8 `PASS` (`evidence/fixtures.tsv`).
- Archive control: `archive_ok=1` on the four OWN/AUTHOR rows; in each, `axes_sha256 == archived_sha256` (byte identical), `archive_rank_count_agree=1`, `archive_max_abs=0` — E27 OWN k=3, E27 AUTHOR k=2, E28 OWN k=1, E28 AUTHOR k=2.
- `sources.tsv`: 40 rows (3 `root`, 8 `input_wall`, 2 `reference`, 4 `archive_axis`, 23 `code`); `sources_hashes` re-hashes every listed file and passes.
- Index maps: 40 `evidence/indices/*.npz` on Spartan (`npz` and `indices_count` checks pass); only short tables, the gate logs and the two PNGs were fetched to `artifacts/surface-parity-05/evidence/`.

**Candidate counts returned (`k`, from `runs.tsv`; all `status=ok`, `reason` empty, none `no_axis`)**

| arm | E27 | E28 | E27 stride / drawn | E28 stride / drawn |
|---|---|---|---|---|
| OWN | 3 | 1 | 10 / 1814 | 10 / 1554 |
| AUTHOR | 2 | 2 | 10 / 526 | 1 / 4480 |
| OWN_DEDUP | 2 | 2 | 10 / 957 | 10 / 828 |
| OWN_STRIDE1 | 2 | 1 | 1 / 18137 | 1 / 15539 |
| OWN_DEDUP_STRIDE1 | 3 | 3 | 1 / 9570 | 1 / 8279 |
| OWN_SHARED_1MM | 3 | 1 | 10 / 1813 | 10 / 1554 |
| AUTHOR_SHARED_1MM | 2 | 1 | 10 / 524 | 1 / 4479 |
| OWN_MATCHED_TO_AUTHOR | 3 | 2 | 1 / 4105 | 1 / 3658 |
| OWN_COMMON_VOXEL | 3 | 2 | 1 / 2340 | 1 / 1965 |
| AUTHOR_COMMON_VOXEL | 3 | 2 | 1 / 2340 | 1 / 1965 |

`effective_stride=1` on an arm comes either from the frozen `n<5000` rule (AUTHOR 28: 4480; AUTHOR_SHARED_1MM 28: 4479) or from the explicit `step=1` of arms 4 and 5 or from the arm's own cloud being under 5000 points (MATCHED 27 4105 / 28 3658, OWN_COMMON_VOXEL 27 2340 / 28 1965, AUTHOR_COMMON_VOXEL 27 2340 / 28 1965); `requested_step` is recorded separately and `check05.py` recomputes both columns from `potsac.effective_step`.

**Point counts (`inputs.tsv`)**

| sherd | OWN native / exact duplicates | AUTHOR native / duplicates | OWN_DEDUP kept | MATCHED kept | COMMON_VOXEL kept (each side) |
|---|---|---|---|---|---|
| 27 | 18137 / 8567 | 5255 / 0 | 9570 | 4105 | 2340 |
| 28 | 15539 / 7260 | 4480 / 0 | 8279 | 3658 | 1965 |

`duplicate_xyz == 0` holds on `OWN_DEDUP`, `OWN_DEDUP_STRIDE1`, `OWN_MATCHED_TO_AUTHOR`, `OWN_COMMON_VOXEL` and `AUTHOR_COMMON_VOXEL`; `points` agree between the two voxel arms on every `(sherd, face)`.

**Figures, opened by eye** (`artifacts/surface-parity-05/evidence/renders/`, 2250×2250 px, 20 mm bar drawn in all four panels):
- `Pot_E_Piece_27.png`: 2250×2250, 2×2; titles `view 1, face-0 side` / `view 2, face-1 side`; a 20 mm bar in all four panels. Row 1 grey = the native OWN walls, two thin sheets at z ≈ 424–443 (denser band 433–443, thinner band 424–433), spanning x ≈ −10…55, y ≈ −5…45; navy `s1 47 mm`, `s2 76 mm`, `s3 74 mm`; pink dashed `c1 9 mm`, `c2 71 mm`, `c3 76 mm` (offset = closest pass of that line to the sherd centre). Row 2 grey = the 2340 OWN_COMMON_VOXEL points, green = the 2340 AUTHOR_COMMON_VOXEL points, same two layers; navy `s1 32 mm`, `s2 63 mm`, `s3 70 mm`; pink `c1 10 mm`, `c2 73 mm`, `c3 73 mm`. No empty or blank panel. The `s2`/`s3` labels overprint each other in panel 1 and `c2` sits under `s3` — readable in the second view, crowded in the first.
- `Pot_E_Piece_28.png`: same layout and bars. Row 1 grey = native OWN walls, one sheet at z ≈ 418–443 (dense band 430–443, thinner 418–431); navy `s1 67 mm`; pink `c1 63 mm`, `c2 69 mm`. Row 2 grey = the 1965 OWN_COMMON_VOXEL points, green = the 1965 AUTHOR_COMMON_VOXEL points; navy `s1 55 mm`, `s2 69 mm`; pink `c1 62 mm`, `c2 69 mm`. In row 2 panel 1 the `c1` and `s1` labels collide (`c1 62 … s1 55`) — readable but crowded; nothing else is mislabelled or missing.

**Work-tree state:** no commit, no push, HEAD still `57a4da7`. `git status --porcelain` shows only `.scratch/surface-parity/t05/` (four new files) and this ticket. `git diff --check` scoped to the ticket returns 0.

### Per-requirement compliance

| # | Requirement | Met | Evidence |
|---|---|---|---|
| R1 | Ten arms, exactly as specified, on both sherds (20 runs) | yes | `runs.tsv` 20 rows with the ten arm names; `extract05.py` `ARM_SPEC`; `sampling05.py` `dedup_indices`/`shared_indices`/`matched_indices`/`common_voxel_indices`; `check05.py` recomputes every arm's index map independently (`arm_*` 40 checks pass) |
| R2 | Every retained point keeps its exact original 6-vector | yes | `check05.py` `verbatim_*` 40 checks: `np.array_equal(wall, native[:, idx])` on all 40 `(sherd, arm, face)`; fixture `normals_verbatim` PASS |
| R3 | Archive control gate on OWN and AUTHOR, both sherds | yes | `runs.tsv` `archive_ok=1`, `axes_sha256 == archived_sha256`, `archive_max_abs=0` on all four rows; `archive_gate` in `extract05.py` |
| R4 | `no_axis` + `k=0` + stage/reason when an arm cannot return finite rows, no invented distances | yes (not triggered) | `run_arm` empty-pool/exception/non-finite branches; `runs_status` checks require `ok ⇒ k≥1`; all 20 rows are `ok` |
| R5 | `inputs.tsv` 40 rows, exact header, LE float64 XYZ and normal hashes separately, duplicates 0 on five arms, voxel `points` identical | yes | `inputs_rows` (40, exact grid), `hash` 120 checks, `duplicate_zero` 60, `points` 40; `matrix_sha` in `sampling05.py` |
| R6 | `sources.tsv` wall / GT / archive / `t03_*` / `impl_t03` / `t05` code hashes | yes | `sources.tsv` 40 rows in five kinds; `sources_hashes` re-hashes every path; `sources_code` requires all 12 basenames |
| R7 | `runs.tsv` 20 rows, exact header, `archive_ok` only on OWN/AUTHOR | yes | `runs_header`, `runs_rows`, `runs_archive_blank_*`; the four gate rows carry 1, the other 16 are blank |
| R8 | `axes.tsv` exact header, ranks from 1, `oriented_deg` 0–180, `line_deg` 0–90, `anchor_mm` | yes | 43 axis rows; `axes_ranks`, `axes_ranges`, `axes_recompute` (1e-5) pass |
| R9 | `changes.tsv` 16 rows, exact header, parent OWN/AUTHOR, sign-independent `max_rank_line_delta_deg` = `arccos(\|dot\|)` in 0–90 | yes | `changes_rows` (16), `changes_parent`, `changes_max_rank` (recomputed 1e-6), `changes_line_range` 0–90; `max_rank_line_delta_deg` in `extract05.py` uses `np.abs(np.dot(...))` |
| R10 | `fixtures.tsv` exact header, 8/8 PASS on Spartan | yes | `fixtures.tsv` eight `PASS` rows; `fixtures_pass` (3 checks) |
| R11 | `renders.tsv` exact header, path relative to run root, 20 mm bar, both faces, four arms, inspected by eye | yes | `renders.tsv` `renders/Pot_E_Piece_27.png` / `_28`, `20`; `renders_relative`, `renders_png`, `renders_scale`; both figures opened (see above) |
| R12 | `jobs.tsv` exact header with every submitted job's terminal state and exit code; `--expect-terminal` passes; `verdict`/`human_note` empty | yes | `jobs.tsv` `35624709 SUBMITTED`, `35624709 COMPLETED 0:0`, `35624000 FAILED 1:0` — both submitted IDs terminal; `jobs_terminal_rows`, `jobs_terminal_code_35624000`, `jobs_completed`, `index_verdict_empty`, `index_human_note_empty`, `index_columns` (6); index row has two trailing tabs |
| R13 | Write-back facts only, budget, one end state, compliance table, separate read-only review | yes | this section; end state below; review section below |
| R14 | Named checks: `py_compile` ×3, `bash -n`, fixtures + `check05.py` on a compute node, `--expect-terminal` after polling, `git diff --check` | yes | `check_static.txt` (both commands rc 0, four files listed), `check.txt` (980/0), `check_postpoll.txt` (989/0), fixtures 8/8, `git diff --check` rc 0 |
| R15 | Frozen estimator/inputs preserved; no normal transfer or re-estimation; no assembler; no default changes | yes | `sources.tsv` hashes of SHIP `t03_lib.py`, `t03_extract.py`, `impl_t03/sfs_axes/*`; code paths only read; `draw_pool(C, seeds=10, step=…)`, `select_lines(..., 6, None)`, `write_lines` used as shipped |
| R16 | Edit only the ticket and four files under `.scratch/surface-parity/t05/`; no commit, no push | yes | `git status --porcelain` → `?? .scratch/surface-parity/t05/` + this ticket only; HEAD `57a4da7` |
| R17 | Full index maps stay on Spartan; only short tables, summary and renders fetched | yes | 40 `.npz` under `evidence/indices/` on Spartan; `artifacts/surface-parity-05/evidence/` holds the eight tables, `check.txt`, `check_postpoll.txt`, `check_static.txt` and the two PNGs (byte-identical to the Spartan originals, sha256 `a10dd97e…` / `437f605b…`) |
| R18 | Fresh run directory, polled with `scripts/slurm_poll.sh`, terminal `sacct` recorded | yes | run directory `20261125-0017_…`; poll log; `COMPLETED|0:0|2026-11-25T00:44:38` |

### Read-only review (separate session, no writes)

A second DeepSeek session (`t05review`, read-only) read this ticket, the four `t05/` files, the eight fetched tables, both PNGs at full size and 2× crops, and re-hashed frozen files on Spartan. It changed nothing. Its first 24-row table marked 22 requirements met, one not met (`jobs.tsv`) and one partly unverifiable (the `py_compile`/`bash -n` artefact), with two prose slips under the write-back row:

- **Not met — `jobs.tsv` job coverage.** The file held only `35624709`; no `jobs.tsv` anywhere carried job `35624000`'s terminal state (the failed attempt's own file still said `SUBMITTED`). Fix: `35624000 FAILED 1:0` appended to both run directories' `jobs.tsv`, then `check05.py --expect-terminal` re-run — `SUMMARY checks=989 failures=0` (`jobs_terminal_rows`, `jobs_terminal_code_35624000`, `jobs_completed` all pass; the gate requires a terminal row for every listed ID and the first ID to end `COMPLETED 0:0`).
- **Corroboration it supplied:** re-hashing on Spartan matched `sources.tsv` for `t03_lib.py` (`7c738d9a…`), `t03_extract.py` (`46b24bee…`), `potsac.py` (`45150a90…`), `profile.py` (`40fa509e…`), `select.py` (`b72ccdd8…`), `joint.py` (`881ce410…`), `io_axes.py` (`c6f167c7…`) and `run_benchmark_172.py` (`dc3928a2…`); all 16 `changes.tsv` rows and all 40 `retained_fraction` values recomputed from the tables with 0 mismatches (worst residual 4.5e-7); every `line_deg == min(oriented_deg, 180−oriented_deg)`.
- **Prose slips it caught in this write-back, all corrected above:** the E27 lower sheet's z range (both sheets are z ≈ 424–443, not 385–405), E27 row-2 pink offsets (`c2 73`/`c3 73`, not 78/79), E28 row-1 pink `c1 63` (not 69), and "seven tables" (there are eight).
- **Its factual caveat:** eight of the 20 rows were produced with `requested_step=10` but `effective_stride=1` — 27 `OWN_MATCHED_TO_AUTHOR` (4105 points), 27 `OWN_COMMON_VOXEL` (2340), 27 `AUTHOR_COMMON_VOXEL` (2340), 28 `OWN_MATCHED_TO_AUTHOR` (3658), 28 `OWN_COMMON_VOXEL` (1965), 28 `AUTHOR_COMMON_VOXEL` (1965), plus 28 `AUTHOR` (4480) and 28 `AUTHOR_SHARED_1MM` (4479) through the frozen `n<5000` rule — so those arms did not run at stride 10, which matters when their `k` is compared with the native stride-10 arms. Both columns are in `runs.tsv` and recomputed by `check05.py`.
- **Extra disk the lead should know about before closing:** the failed attempt's run directory `20261125-0013_57a4da7_t05-sampling-coverage` (its own `evidence/`, `out/`, `renders/`) and `work/preflight/` inside the accepted run (a one-sherd diagnostic tree). Neither is a ticket violation; neither is deleted.

**End state:** ready

---

## Comments

### Lead verification and closure (2026-11-25)

Worker end state: `ready` (DSH session `session-71ce176e-623f-4b2c-89eb-acdc30d6ccc9`, run `20261125-0017_57a4da7_t05-sampling-coverage`, job `35624709`; earlier fixture-fail attempt `35624000` recorded). Accepted and closed.

Private acceptance check note (`C:/PR/artifacts/dsh-handover/surface-parity-05/accept.py`): `dsh_status` `evidence.changes` and `git status` confirmed zero files changed outside `sfs/05` (the `snapshots()` difference was an unrelated parallel worktree `C:/PR/worktrees/pr-workspace/02` from run `hrun-mwus0r9e-2a98fd`); `renders/` was fetched inside `evidence/` rather than its parent; all 40 `inputs.tsv`, 20 `runs.tsv`, 43 `axes.tsv`, 16 `changes.tsv`, 8 `fixtures.tsv`, 4 archive pins, `sources.tsv` local code hashes, renders, and write-back checks passed.

Minor record notes: (1) `runs.tsv` `basins` column logged `10000` (candidate draws) rather than clustered basin count (`reps.shape[1]`), with no effect on axes; (2) local archived `jobs.tsv` was refreshed from Spartan so `35624000 FAILED 1:0` is present locally.

- `verified: accept.py data/code/hash/render assertions + independent recompute of changes.tsv (16 rows, max_err=4.54e-07 deg) -> PASS`
- `verified: ssh spartan sacct -j 35624709,35624000 -> 35624709 COMPLETED 0:0 (00:15:15), 35624000 FAILED 1:0 (00:00:05)`
- `verified: visual inspection of Pot_E_Piece_27.png and Pot_E_Piece_28.png -> 2250x2250 2x2 locked views, 20 mm bar in all 4 panels, both wall faces, axis counts match runs.tsv k (27: 3/3/3/3, 28: 1/2/2/2)`

**Lead verdict:** Removing exact duplicate XYZ rows alone (`OWN_DEDUP`, still at stride 10, 828/957 drawn points, unchanged normals) accounts for the candidate-count gap on both sherds: E28 flips from `k=1` (11.28 deg / 69.9 mm) to `k=2` with rank 2 at 4.03 deg / 25.6 mm (near AUTHOR's 3.60 deg / 22.0 mm), and E27 drops from `k=3` (7.35 deg / 5.9 mm) to `k=2` with rank 2 at 3.86 deg / 2.9 mm (near AUTHOR's 2.87 deg / 2.0 mm). By contrast, forcing stride 1 (`OWN_STRIDE1`) or 1 mm coverage filtering (`OWN_SHARED_1MM`) while keeping ~47% duplicates leaves E28 stuck at `k=1` (11.28-11.37 deg). Common 1 mm voxels yield identical `k` on both sides (`3/3` on E27, `2/2` on E28). Caveat: `AUTHOR_SHARED_1MM` on E28 dropped from `k=2` to `k=1` after dropping 1 point, showing threshold sensitivity near `keep_lines`. Evidence preserved in `SfSpp_preprocessing/artifacts/surface-parity-05/evidence/`.
