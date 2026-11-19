# 335: Ship blind base-to-rim sign orientation (`orient_base_axis`) in `SfSpp_preprocessing/sfs_axes/`

**What to build:** Promote blind base-to-rim axis sign orientation (`orient_base_axis`, proven in structure-from-sherds-pp Tickets 366–368 on Juglet `def_3x` and Pot A) into `SfSpp_preprocessing/sfs_axes/` as the default on the normalized profile-ranked union path (`select_union_lines` / `run_potsac_union`), wired through `sfs_axes/cli.py` (`--union`) and `scripts/run_benchmark_172.py`, with opt-out `SFS_AXES_BASE_ORIENT=0` / `--no-base-orient`, full unit tests, and Spartan 172-piece + `def_3x` Juglet verification.

**Answers:** E1
**Blocked by:** None (structure-from-sherds-pp Tickets 366, 367, and 368 resolved and recorded 2026-11-19)
**Status:** in-progress
**Working in:** DSH Baton w335 (2026-11-19) (2026-11-19)
**Branch:** 335-ship-orient-base-axis, in /c/PR/worktrees/sfs/335
**Worker:** dsh one-shot subagent w335
**Budget:** medium 5
**Hand-over:** DeepSeek — C:/PR/artifacts/dsh-handover/335/accept.py

---

## Why this ticket exists (proven in `structure-from-sherds-pp` Tickets 366–368)

1. `sfs_axes.normalized.is_base_fragment(X, vt)` already detects genuine base sherds blindly (e.g. `Pot_A_Piece_01` and `Juglet_Piece_7` alone on Juglet). However, PotSAC (`pottmann.py`) returns an undirected line (`+a` and `-a` have identical normal and profile cost), and `run_benchmark_172.py` canonicalized every direction to `dir_z >= 0`. Whenever a base scan sits inverted in its frame (`Juglet_Piece_7`: `GT dir_z = -0.670 < 0`), canonicalizing `dir_z >= 0` leaves the written axis pointing rim-to-base (`175.31 deg` off), triggering `SignAxisGuard` (`4/18 = 22.22%`) and causing `SFS_AXIS_SIGN=1` to drop all upright Piece 7 joins.
2. Tickets 366–367 showed that applying blind `orient_base_axis` on top of shipped `sfs_axes` (`shipped_base`) leaves **Pot A `8/8` byte-identical (`cmp`)** to `axes323` (`8/8, 15/15` at `2.02–2.06 mm`), while flipping only Piece 7 on `def_3x` Juglet (`SignAxisGuard 0/18`) and closing Juglet `9/9` sherds in one upright vessel (`0.466–0.476 mm` vertex-centroid Kabsch, `18/18` centroid-gauge joins `<= 1.73 deg / 0.86 mm`, `4/4` Piece 7 joins).
3. Tickets 367–368 also tested `4-DoF c_in` and `6°`-guarded `4-DoF c_ref` variants and found both regress `Pot_A_Piece_08` to `7/8, 13/15`. Therefore we ship `orient_base_axis` alone first (zero non-sign change to `axes323`) before validating `a1_k0` across all 10 pots in a separate ticket.

## Exact implementation specification (preserve LF line endings in all edited files)

Edit ONLY inside this ticket's worktree (`C:/PR/worktrees/sfs/335`):

1. **`sfs_axes/select.py`** (must remain LF `\n`, zero `\r\n`):
   - Import `is_base_fragment` from `.normalized` (alongside `refine_axis_normalized`).
   - Add module-level constants:
     - `BASE_ORIENT = os.environ.get("SFS_AXES_BASE_ORIENT", "1") not in ("", "0")`
     - `BASE_ORIENT_MAX_POINTS = 30000`
     - `BASE_ORIENT_POLE_AX = 0.85`
     - `BASE_ORIENT_WALL_AX = 0.50`
     - `BASE_ORIENT_MIN_COUNT = 50`
   - Implement `orient_base_axis(vt, C0, C1=None, max_points=BASE_ORIENT_MAX_POINTS, return_info=False)`:
     - Accept 1D `(6,)` or 2D `(6, K)` `vt`. Preserve input dimensionality (`(6,)` -> `(6,)`, `(6, K)` -> `(6, K)`). Handle `K == 0` or empty point cloud safely (`out = vt.copy()`, return empty `info=[]` if `return_info=True`).
     - Concatenate walls: `C_all = np.asarray(C0, dtype=float)` if `C1 is None` else `np.concatenate([np.asarray(C0, dtype=float), np.asarray(C1, dtype=float)], axis=1)`.
     - Deterministic stride via `stride(C_all, n=max_points)` (from `.profile`).
     - Precompute unit normals locally on `C_all`: `n_norm = np.linalg.norm(C_all[3:6, :], axis=0)`, `N_unit = C_all[3:6, :] / np.maximum(n_norm, 1e-12)`.
     - Start from `out = vt2d.copy()`. **Strict bit-for-bit invariance rule:** NEVER renormalize `out[0:3, k]` and NEVER overwrite `out[3:6, k]` unless flipping is not needed — even when flipping, ONLY negate `out[0:3, k] = -out[0:3, k]` (leaving `out[3:6, k]` untouched). When no flip occurs, `out[:, k]` is left byte-identical to `vt2d[:, k]`.
     - For each column `k`:
       - Compute local unit direction `norm_d = float(np.linalg.norm(out[0:3, k]))`. If `norm_d < 1e-12`, record `flipped=False` and continue.
       - `a = out[0:3, k] / norm_d`; `p0 = out[3:6, k] - float(out[3:6, k] @ a) * a`; `line = np.r_[a, p0]`.
       - Record dict `rec = dict(cand=k, base=False, flipped=False, z_wall=None, z_pole=None, z_wall_minus_z_pole=None, n_pole=0, n_wall=0)`.
       - If `C_all.shape[1] > 0` and `is_base_fragment(C_all, line)`:
         - `z = a @ (C_all[0:3, :] - p0[:, None])`
         - `n_ax = np.abs(a @ N_unit)`
         - `pole = n_ax > BASE_ORIENT_POLE_AX`; if `int(pole.sum()) < BASE_ORIENT_MIN_COUNT`: `pole = n_ax >= np.quantile(n_ax, 0.90)`
         - `wall = n_ax < BASE_ORIENT_WALL_AX`; if `int(wall.sum()) < BASE_ORIENT_MIN_COUNT`: `wall = n_ax <= np.quantile(n_ax, 0.50)`
         - `z_wall = float(z[wall].mean())`, `z_pole = float(z[pole].mean())`
         - Update `rec`: `base=True, z_wall=round(z_wall, 4), z_pole=round(z_pole, 4), z_wall_minus_z_pole=round(z_wall - z_pole, 4), n_pole=int(pole.sum()), n_wall=int(wall.sum())`.
         - If `z_wall < z_pole`: negate `out[0:3, k] = -out[0:3, k]`, set `rec["flipped"] = True`.
       - Else (non-base):
         - If `out[2, k] < 0`: negate `out[0:3, k] = -out[0:3, k]`, set `rec["flipped"] = True`.
     - Return `(out_shaped, info)` if `return_info` else `out_shaped`.
   - Update `select_union_lines(reps, sizes, C0, C1, C, max_candidates, line_rule=None, tau=LINE_RULE_TAU, kmax=LINE_RULE_KMAX, base_orient=None, verbose=False)`:
     - Resolve `if base_orient is None: base_orient = BASE_ORIENT`.
     - After `keep_lines`, if `base_orient`: `vt = orient_base_axis(vt, C)` (pass combined cloud `C`, not both `C0` and `C1`).

2. **`sfs_axes/potsac.py`** (must remain LF `\n`, zero `\r\n`):
   - Update `run_potsac_union(..., line_rule=None, base_orient=None)` to forward `base_orient=base_orient` into `select_union_lines(...)`.
   - **Do NOT touch `run_potsac` (paper chain) or the legacy `UNION_RANKER == "normal"` branch.**

3. **`sfs_axes/cli.py`** (must remain LF `\n`, zero `\r\n`):
   - Update `extract_piece(..., line_rule=None, base_orient=None)` to forward `base_orient=base_orient` into `run_potsac_union(...)`.
   - Add `--no-base-orient` CLI option passing `base_orient=False if args.no_base_orient else None`.

4. **`scripts/run_benchmark_172.py`** (must remain LF `\n`, zero `\r\n`):
   - Add `--no-base-orient` CLI option.
   - Forward `base_orient = False if a.no_base_orient else None` into `one(job)` -> `ps.run_potsac_union(..., base_orient=base_orient)`.
   - Import `select` (`import sfs_axes.select as sel`) and resolve `use_base_orient = sel.BASE_ORIENT if base_orient is None else bool(base_orient)`.
   - **CRITICAL:** When writing `.xyz` files (`outpath` and `alt_path`), if `use_base_orient` is `True`, write `v = vt[:, k]` **WITHOUT calling `canonicalize(vt[:, k])`** (calling `canonicalize` would flip `dir_z < 0` back to `dir_z >= 0` and undo `orient_base_axis` on inverted bases!). Only call `canonicalize` when `use_base_orient` is `False` (restoring exact `axes323` bytes when `--no-base-orient` or `SFS_AXES_BASE_ORIENT=0`).

5. **`tests/test_select.py`** (must remain LF `\n`, zero `\r\n`):
   - Keep all 10 existing tests untouched and passing.
   - Add comprehensive unit tests covering:
     - Inverted base disk (`z_wall < z_pole`) flipped to base->rim (`dot > 0.99`) and **idempotent** on a 2nd call (`flipped=False`, `np.array_equal`).
     - Upright base disk (`z_wall > z_pole`, including non-unit perturbation norm `1.0 + 1e-13`) NOT flipped and **bit-for-bit `np.array_equal`**.
     - Tilted base disk whose true base->rim direction has `z < 0` (`(-0.3, 0.2, -0.9)`): starting with `dir_z > 0` flips to `dir_z < 0` cleanly.
     - Non-base sherd: `v[2] < 0` flips to `v[2] >= 0`; `v[2] >= 0` stays bit-for-bit `np.array_equal`.
     - Normal-sign invariance: flipping all input wall normals `N -> -N` produces the identical `orient_base_axis` result.
     - Quantile fallback when `< 50` pole or `< 50` wall points satisfy strict thresholds.
     - `1D (6,)` vs `2D (6, K)` shapes, `K=0` / empty cloud safety, and `return_info=True`.
     - `select_union_lines(..., base_orient=True)` vs `base_orient=False` vs `SFS_AXES_BASE_ORIENT=0` env switch on a tilted negative-z base disk.

## Spartan verification ladder (compute nodes only)

1. Run local unit tests inside `C:/PR/worktrees/sfs/335`: `python -m pytest tests` (all existing 33 + new tests must pass).
2. Create run directory on Spartan:
   `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t335-ship-base-orient/`
   Stage the worktree's `sfs_axes/` and `scripts/run_benchmark_172.py` into `<run>/impl/`. Check corpus md5/timestamps before & after (`CORPUS-UNCHANGED`). Append one row to `SfSpp/runs/index.tsv` (`verdict` and `human_note` blank).
3. Submit compute-node job (`sbatch`, sapphire partition, e.g. 24 CPUs / 48G):
   - **Pass 1 (default ON):**
     `python run_benchmark_172.py --out <run>/out/axes335 --jobs 24 --cap 6 --seeds 10 --step 10`
     Compare all `172` files (`163` corpus pieces `Pot A..J` + `9` legacy `Juglet` from `t66`) against `axes323` (`/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-axes/out/axes323`) -> save full report in `<run>/out/cmp_axes323.txt` and `axes335_audit.json`:
     - **Pot A (`8/8`) MUST be `8/8` byte-identical (`cmp -s`).**
     - **ZERO non-sign differences allowed across all 172 files:** every differing file MUST have identical line count `K`, max position diff `< 1e-12 mm`, max unsigned direction angle diff `< 1e-12 deg`, exact sign reversal `d_new == -d_old` (`signed_diff_deg ~ 180 deg`), `is_base_fragment == True`, and `z_wall < z_pole`. Report separately which of `Pot A..J` (`163` pieces) vs legacy `Juglet` (`9` pieces) flipped!
   - **Pass 2 (`--no-base-orient` switch OFF):**
     `python run_benchmark_172.py --out <run>/out/axes335_off --jobs 24 --cap 6 --seeds 10 --step 10 --no-base-orient`
     Compare all `172` files against `axes323` -> **MUST be `172/172` byte-identical (`cmp -s`, `DIFFER 0`, `MISSING 0`)**.
   - **Pass 3 (`def_3x` Juglet using shipped `sfs_axes`):**
     Load the 9 clean `t80` `def_3x` Juglet walls (`/data/gpfs/projects/punim2657/SfSpp/runs/20261117-0430_d272313_t80-default-on/out/cell_def_3x/geom/Juglet_Piece_{1..9}.S{0,1}`, PLY format via `run_benchmark_172.load_wall`), call shipped `run_potsac_union(C0, C1, seeds=list(range(10)), step=10, max_candidates=6, normalized=True, line_rule=True)` (default `base_orient=True`), write `<run>/out/axes335_juglet_def3x/Juglet_Piece_{1..9}_Axis.xyz` with `write_axes`, and verify:
     - `is_base_fragment == True` on **Piece 7 ONLY** (Piece 7 flipped `3/3` lines, `1..6, 8, 9` unflipped),
     - `SignAxisGuard` against `Dataset/Juglet_large` (`scale=3.0`) = **`0/18 (0.00%)`**,
     - All 9 pieces match `t367`'s `axes_shipped_base` (`/data/gpfs/projects/punim2657/SfSpp/runs/20261119-1023_273b8f9_t367-shipped-vs-4dof-cin/out/axes/axes_shipped_base/`) within `< 1e-6 deg` (both signed and unsigned) and `< 1e-6 mm` position.
   - **Pass 4 (conditional Pot B..J end-to-end assembly guard):**
     If **ANY** file in `Pot B..J` flipped in Pass 1 (`cmp` differed from `axes323`), run that pot through the `t323` assembly template (`/data/gpfs/projects/punim2657/SfSpp/runs/20261109-1426_ecd5bb8_t319-pot<P>`, `${P}_MOR1`, `${P}_MOR2`, `${P}_K3R1`, `${P}_K3R2`) using `AX_318=<run>/out/axes335` and confirm it meets/exceeds the `t323` floor (`B 9/9 15/15`, `C 4/4 5/5`, `D >=23/28 >=55/69`, `E >=29/31 >=57/62`, `F 5/5 7/7`, `G 7/7 10/10`, `H 11/11 17/17`, `I >=25/26 >=59/62`, `J >=8/11 >=16/21`). Note any `Pot_X` that had `>= 1` flipped piece! (If `0` files in `Pot B..J` flipped and all `163/163` pot files are `cmp`-identical to `axes323`, record `pass4: not needed (163/163 Pot A..J byte-identical to axes323)` in `axes335_audit.json`.)

## Deliverables to fetch to `C:/PR/artifacts/t335/`

- `C:/PR/artifacts/t335/axes335_audit.json` — structured JSON containing `run_dir`, `commit`, `sacct` job info, `pass1` (`163` pots + `9` legacy Juglet diff counts, exact list of flipped files, max `unsigned_diff_deg`, max `pos_diff_mm`, `non_sign_diffs == 0`), `pass2` (`172/172` byte-identical count vs `axes323`), `pass3` (`juglet_def3x` per-piece `unsigned_deg`, `signed_deg`, `d_perp_sherd_mm`, `is_base_fragment`, `sign_guard`, max diff vs `t367 axes_shipped_base`), and `pass4` (assembly scores if any pot B..J flipped, or explicit `163/163` byte-identical note).
- `C:/PR/artifacts/t335/gate335.tsv` — exact 7-column header `group\tpiece\tmetric\tvalue\treference\tverdict\tnote`.
- `C:/PR/artifacts/t335/render335_base_orient.png` — multi-panel figure showing before (`--no-base-orient`, red axis arrow) vs after (`orient_base_axis`, green axis arrow) overlaid on the sherd point clouds for Juglet Piece 7 (`def_3x`), every flipped `Pot A..J` base piece (plus `Pot_A_Piece_01` upright base control), rendered at a close-up scale resolving orientation direction clearly.
- `C:/PR/artifacts/t335/cmp_axes323.txt` and `C:/PR/artifacts/t335/cmp_axes323_off.txt` (and `C:/PR/artifacts/t335/score/` if Pass 4 ran).
- Update `## Comments` in this ticket with Slurm job IDs + `sacct -X`, Pass 1/2/3/(4) tables, `CORPUS-UNCHANGED` confirmation, one bare `Reading:` line, and `**End state:** ready`.

## Readings (pick one verbatim on a bare `Reading:` line)

- `orient-base-axis-shipped-clean` — all unit tests pass (`0` CRLF), Pass 1 (`172` pieces) has `0` non-sign diffs and `Pot A 8/8` byte-identical (`axes323`), Pass 2 (`--no-base-orient`) is `172/172` byte-identical to `axes323`, Pass 3 (`def_3x` Juglet) achieves `0/18 SignAxisGuard` matching `t367 axes_shipped_base`, and any Pass 4 assembly passes its `t323` floor.
- `orient-base-axis-regresses-corpus-pot` — Pass 1 introduces an unintended non-sign diff or Pass 4 fails a `t323` pot floor.
- `blocked: control-or-input-failed` — Pass 2 fails `172/172` identity or a required Spartan input/script is missing.

## Out of scope

- Changing `run_potsac` (paper chain), changing 4-DoF polish or `select_union_lines` ranking (that is evaluated in Ticket 336), committing, pushing, merging, or running `ticket_close.sh`.

## Acceptance

- [ ] `sfs_axes/select.py`, `sfs_axes/potsac.py`, `sfs_axes/cli.py`, `scripts/run_benchmark_172.py`, and `tests/test_select.py` implement `orient_base_axis`, `SFS_AXES_BASE_ORIENT`, and `--no-base-orient` cleanly with LF line endings and zero edits to `run_potsac`.
- [ ] `python -m pytest tests` inside `C:/PR/worktrees/sfs/335` passes all existing 33 tests plus new unit tests for `orient_base_axis` and `--no-base-orient`.
- [ ] Spartan compute-node Pass 1 (`axes335`) produces `0` non-sign diffs across all 172 files vs `axes323` (`Pot A 8/8` byte-identical), and Pass 2 (`axes335_off --no-base-orient`) is `172/172` byte-identical to `axes323` (`CORPUS-UNCHANGED`).
- [ ] Spartan compute-node Pass 3 (`axes335_juglet_def3x`) flips Piece 7 alone (`is_base_fragment=True` only on P7), achieves `SignAxisGuard = 0/18`, and matches `t367`'s `axes_shipped_base` within `< 1e-6 deg` / `< 1e-6 mm` (plus Pass 4 passes `t323` floor if any `Pot B..J` piece flipped).
- [ ] `C:/PR/artifacts/t335/{axes335_audit.json,gate335.tsv,render335_base_orient.png,cmp_axes323.txt,cmp_axes323_off.txt}` fetched, `runs/index.tsv` row appended, `## Comments` + `sacct -X` + bare `Reading:` line + `**End state:** ready` recorded in this ticket.

## Comments
