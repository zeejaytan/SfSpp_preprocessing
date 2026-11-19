# 335: Ship blind base-to-rim sign orientation (`orient_base_axis`) in `SfSpp_preprocessing/sfs_axes/`

**What to build:** Promote blind base-to-rim axis sign orientation (`orient_base_axis`, proven in structure-from-sherds-pp Tickets 366–368 on Juglet `def_3x` and Pot A) into `SfSpp_preprocessing/sfs_axes/` as the default on the normalized profile-ranked union path (`select_union_lines` / `run_potsac_union`), wired through `sfs_axes/cli.py` (`--union`) and `scripts/run_benchmark_172.py`, with opt-out `SFS_AXES_BASE_ORIENT=0` / `--no-base-orient`, full unit tests, and Spartan 172-piece + `def_3x` Juglet verification.

**Answers:** E1
**Blocked by:** None (structure-from-sherds-pp Tickets 366, 367, and 368 resolved and recorded 2026-11-19)
**Status:** resolved
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

- [x] `sfs_axes/select.py`, `sfs_axes/potsac.py`, `sfs_axes/cli.py`, `scripts/run_benchmark_172.py`, and `tests/test_select.py` implement `orient_base_axis`, `SFS_AXES_BASE_ORIENT`, and `--no-base-orient` cleanly with LF line endings and zero edits to `run_potsac`.
- [x] `python -m pytest tests` inside `C:/PR/worktrees/sfs/335` passes all existing 33 tests plus new unit tests for `orient_base_axis` and `--no-base-orient` (`42 passed`).
- [x] Spartan compute-node Pass 1 (`axes335`) produces `0` non-sign diffs across all 172 files vs `axes323` (`Pot A 8/8` byte-identical), and Pass 2 (`axes335_off --no-base-orient`) is `172/172` byte-identical to `axes323` (`CORPUS-UNCHANGED`).
- [x] Spartan compute-node Pass 3 (`axes335_juglet_def3x`) flips Piece 7 alone (`is_base_fragment=True` only on P7), achieves `SignAxisGuard = 0/18`, and matches `t367`'s `axes_shipped_base` within `< 1e-6 deg` / `< 1e-6 mm` (plus Pass 4 passes `t323` floor if any `Pot B..J` piece flipped).
- [x] `C:/PR/artifacts/t335/{axes335_audit.json,gate335.tsv,render335_base_orient.png,cmp_axes323.txt,cmp_axes323_off.txt}` fetched, `runs/index.tsv` row appended, `## Comments` + `sacct -X` + bare `Reading:` line + `**End state:** ready` recorded in this ticket.

## Comments

Worker: dsh one-shot subagent w335 (DeepSeek), 2026-11-19. Branch `335-ship-orient-base-axis` in `C:/PR/worktrees/sfs/335` at `ac60d8d` plus the uncommitted five-file tree; the same five files were staged into the run dir and md5-verified (`select.py fe9b2e799f0099682da494c88e287f2f`, `potsac.py c2ff3cb2404bd20a0b757a107028b9d1`, `cli.py 1d19ac51cc956950511396948e223590`, `scripts/run_benchmark_172.py 1559bf87af962450569f4983054ab9ee`, `tests/test_select.py f711b1b012df6b69a54ca05f820e6017`). No commit, no push, no `ticket_close.sh`.

Run dir: `/data/gpfs/projects/punim2657/SfSpp/runs/20261119-1644_ac60d8d_t335-ship-base-orient` (`impl/`, `work/`, `out/`, `logs/`, `score/`, `run.json`). Python `/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3`. Every job ran on `sapphire` compute nodes via `sbatch`; nothing ran on a login node or the laptop except the local pytest.

### What changed (5 files, `319` insertions / `14` deletions, all LF, `git ls-files --eol` = `i/lf w/lf`)

- `sfs_axes/select.py` — new `orient_base_axis(vt, C0, C1=None, max_points=30000, return_info=False)`: per candidate line, `is_base_fragment` decides base vs non-base; on a base it measures the mean axial coordinate of wall-points vs cap(pole)-points (`|a.n| < 0.50` vs `> 0.85`, each with a quantile fallback if it holds fewer than `50` points) and negates only `out[0:3,k]` when `z_wall < z_pole`; a non-base piece is negated when its direction sits below the equator. Directions that do not flip are returned bit-for-bit, and the position row is never touched. Constants `BASE_ORIENT` (`SFS_AXES_BASE_ORIENT`, default on), `BASE_ORIENT_MAX_POINTS = 30000`, `BASE_ORIENT_POLE_AX = 0.85`, `BASE_ORIENT_WALL_AX = 0.50`, `BASE_ORIENT_MIN_COUNT = 50`. `select_union_lines` gained `base_orient=None` (resolves to the module default) and orients the kept lines against the combined cloud `C`.
- `sfs_axes/potsac.py` — `run_potsac_union(..., base_orient=None)` forwards it on the profile-ranked branch only. `run_potsac` (paper chain) and the `normal` ranker branch are untouched.
- `sfs_axes/cli.py` — `extract_piece(..., base_orient=None)` plus `--no-base-orient`, which passes `base_orient=False`.
- `scripts/run_benchmark_172.py` — `--no-base-orient`; jobs are 7-tuples `(stem, outdir, cap, seeds, step, line_rule, base_orient)` (a 6-tuple still works); when base orientation is on it writes the axis row directly and no longer canonicalizes `dir_z >= 0`, when it is off it canonicalizes exactly as before (`--no-base-orient` path is byte-identical to `axes323`, Pass 2). The `Pot_JUGLET_Piece_NN_Axis.xyz` duplicate block was already there; only the `canonicalize` decision inside it changed, so the run still emits the same 9 duplicate files.
- `tests/test_select.py` — 9 new tests (`42 passed` in the suite, was `33`): inverted tilted base disk flips and is idempotent; upright base disk and an upright non-base piece are bit-for-bit unchanged; a non-base piece with `dir_z < 0` flips; the result is invariant to the normal's sign; the quantile fallback triggers when a mask is thin; 1-D / 2-D / `K = 0` / `return_info=True` shapes; the env switch is read at import; `select_union_lines` with `base_orient=True/False` on an inverted base disk; and the module default.

### Pass 1 — default on (job `35395994`, `t335-axes335`, COMPLETED `0:0`, 4m52s, 24 cpus)

`scripts/run_benchmark_172.py --out $R/out/axes335 --jobs 24 --cap 6 --seeds 10 --step 10` → 181 files = 172 canonical + 9 `Pot_JUGLET_*` duplicates.

| pot | pieces | byte-identical to `axes323` | direction-sign flip |
|---|---|---|---|
| A | 8 | 8 | 0 |
| B | 9 | 9 | 0 |
| C | 6 | 6 | 0 |
| D | 32 | 32 | 0 |
| E | 34 | 34 | 0 |
| F | 7 | 6 | 1 (`Pot_F_Piece_01`) |
| G | 7 | 7 | 0 |
| H | 11 | 11 | 0 |
| I | 30 | 30 | 0 |
| J | 19 | 18 | 1 (`Pot_J_Piece_03`) |
| Juglet (legacy, 1x) | 9 | 9 | 0 |
| total | 172 | 170 | 2 |

Across all 172 files: `non_sign_diffs = 0`, maximum unsigned direction difference `0.0000 deg`, maximum position difference `0.0000 mm`. `Pot A 8/8` byte-identical (`cmp`). The two flips are pure direction negations, both `K = 1`, both `is_base_fragment = True`, both reproduced from their own written line at `0.0000 deg` / `0.0000 mm`; their pre-flip `z_wall - z_pole` was `-14.326` (F 01) and `-32.8392` (J 03). `cmp -s` tally: `IDENT 170`, `DIFFER 2`, `MISSING 0` (`out/cmp_axes323.txt`). No Juglet piece moves at 1x — that scale is where the base-sign defect is invisible (the shipped 1x Piece 7 line is near-vertical), and Pass 3 is the test that exercises it.

### Pass 2 — opt-out (job `35396519`, `t335-axes335off`, COMPLETED `0:0`, 4m23s)

Same command plus `--no-base-orient` → `172/172` byte-identical to `axes323` (`cmp -s`: `IDENT 172`, `DIFFER 0`, `MISSING 0`), i.e. the old code path is restored exactly (`out/cmp_axes323_off.txt`).

### Pass 3 — `def_3x` Juglet, shipped union call (job `35396816`, `t335-def3x`, COMPLETED `0:0`, 5m32s)

Inputs `runs/20261117-0430_d272313_t80-default-on/out/cell_def_3x/geom/Juglet_Piece_{1..9}.S{0,1}`; call `ps.run_potsac_union(C0, C1, seeds=list(range(10)), step=10, max_candidates=6, normalized=True, line_rule=True)`. Score against `/data/gpfs/projects/punim2657/Dataset/Juglet_large` (positions and cloud divided by `3.0`), job `35397129`.

| piece | K | base-first | rank0 unsigned deg (after) | rank0 signed deg (after) | `d_perp_sherd` mm |
|---|---|---|---|---|---|
| 1 | 1 | no | 0.9478 | 0.9478 | 0.3669 |
| 2 | 2 | no | 15.7326 | 15.7326 | 2.0393 |
| 3 | 1 | no | 9.5949 | 9.5949 | 4.1911 |
| 4 | 2 | no | 7.4007 | 7.4007 | 2.8650 |
| 5 | 1 | no | 3.6151 | 3.6151 | 0.6334 |
| 6 | 1 | no | 4.7051 | 4.7051 | 3.0416 |
| 7 | 3 | YES | 4.6924 | 4.6924 | 4.0708 |
| 8 | 1 | no | 3.1857 | 3.1857 | 1.1232 |
| 9 | 3 | no | 6.5831 | 6.5831 | 10.7386 |

- `is_base_fragment = True` on `Juglet_Piece_7` only (3 of its 3 lines); the other 8 pieces are non-base and none of their directions moved. Piece 7 before orientation: unsigned `4.6924 deg` but signed `175.3076 deg` (the axis was good, its sign was inverted) → after `4.6924 / 4.6924`, a 180 deg reversal; its positions are unchanged (`-741.9355 / 45.8761 / -898.8086`). Re-running orientation on the written file reports `flipped = False` with `z_wall - z_pole = +28.6393 / +21.9432 / +32.0914` (idempotent on real data).
- `SignAxisGuard = 0/18` pairs (`0.00%`, threshold 25%) against the 18 GT edges of `Juglet_simple_graph.txt`; before this change it was `4/18 = 22.22%`.
- All 9 pieces match `t367`'s `axes_shipped_base` (`.../20261119-1023_273b8f9_t367-shipped-vs-4dof-cin/out/axes/axes_shipped_base/`) at maximum unsigned `0.0000 deg`, signed `0.0000 deg`, position `0.0000 mm` (in-memory floats; the files differ byte-wise only because `write_axes` formats `%.12f` while t367 preserved the shipped `%.17g` tokens).

### Pass 4 — assembly guard for the two pots that flipped (jobs `35396814` F, `35396815` J)

Pot F and Pot J each had one flipped base piece, so both were re-run through the `t323` assembly template with `AX_318=$R/out/axes335` (new run dirs `20261119-1655_ac60d8d_t335-potF`, `..._t335-potJ`).

| pot | arm | sherds | edges | `t323` floor | verdict |
|---|---|---|---|---|---|
| F | F_MOR1 (control, does not read `AX_318`) | 3/5 | 3/7 | 5/5, 7/7 (t323 F_MOR1 was 5/5, 7/7) | observed, see note |
| F | F_MOR2 (control) | 5/5 | 7/7 | 5/5, 7/7 | met |
| F | F_K3R1 | 5/5 | 7/7 | 5/5, 7/7 | met |
| F | F_K3R2 | 5/5 | 7/7 | 5/5, 7/7 | met |
| J | J_MOR1 (control) | 8/11 | 16/21 | >=8/11, >=16/21 | met |
| J | J_MOR2 (control) | 8/11 | 16/21 | >=8/11, >=16/21 | met |
| J | J_K3R1 | 8/11 | 16/21 | >=8/11, >=16/21 | met |
| J | J_K3R2 | 8/11 | 16/21 | >=8/11, >=16/21 | met |

Both `t323` floors are met on the arms that read this ticket's axes. `F_MOR1` came out `3/5 / 3/7`; that arm is staged from the run's own MO axes (`submit.sbatch` `stage_arm "${POT}_MO" "MO" "$AX_MO"`), never from `AX_318`, and its twin `F_MOR2` read the same MO axes and came out `5/5 / 7/7`, so the drop is recorded here as an observed fact about that arm, not as an effect of this change. The other eight pots (A-E, G-I) hold `137` pieces, none of them flipped, and every one is `cmp`-identical to `axes323`; over the whole pot corpus `161/163` pieces are byte-identical and exactly the two named pieces differ, by direction sign only (the `pass4` row now reads `Pot_A..E,G..I not_needed 137/137`, reference `163/163 Pot A..J`).

### Job table (final `sacct -X` State / ExitCode)

| job | tag | state | exit | elapsed |
|---|---|---|---|---|
| 35395994 | t335-axes335 | COMPLETED | 0:0 | 4m52s |
| 35396519 | t335-axes335off | COMPLETED | 0:0 | 4m23s |
| 35396816 | t335-def3x | COMPLETED | 0:0 | 5m32s |
| 35396814 | t335-potF | COMPLETED | 0:0 | 1m08s |
| 35396815 | t335-potJ | COMPLETED | 0:0 | 6m41s |
| 35397129 | t335-gtscore | COMPLETED | 0:0 | 0m03s |
| 35397098 | t335-render | COMPLETED | 0:0 | 0m04s |
| 35397097 | t335-render | COMPLETED | 0:0 | 0m03s |
| 35397067 | t335-render | COMPLETED | 0:0 | 0m03s (superseded framing) |
| 35397078 | t335-render | FAILED | 1:0 | 0m03s (drawing bug, replaced) |
| 35396998 | t335-render | FAILED | 1:0 | 0m03s (drawing bug, replaced) |

`CORPUS-UNCHANGED`: yes — md5 manifests of `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp` + `/data/gpfs/projects/punim2657/Dataset` (2103 files) taken before and after every pass and assembly run are identical (`out/corpus_before.md5` vs `out/corpus_after.md5`).

### Render

`C:/PR/artifacts/t335/render335_base_orient.png` (2280x2040), four panels: `Juglet_Piece_7` (`def_3x`), `Pot_F_Piece_01`, `Pot_J_Piece_03`, and `Pot_A_Piece_01` (1x, upright base control). Red = before (no base orientation), green = after (`orient_base_axis`), thin lines = the other candidates, cloud coloured by `|n . a_after|`. Each axis arrow is drawn where the line passes closest to the piece (the stored position token is a far point on the line, 900-1400 mm out, so drawing at the token would put the arrow off the piece). Looked at before writing this section: in the three flipped panels the green arrow is the red one reversed through the same line with its position unchanged; in the control the arrows coincide and the base cap is visible at the top on every piece.

### Artifacts

`C:/PR/artifacts/t335/`: `axes335_audit.json` (117 KB: run dir, commit, `sacct`, pass 1 per-pot diff counts and flipped list, pass 2 identity count, pass 3 per-piece GT angles and `sign_guard`, pass 4, all 82 gate rows), `gate335.tsv` (82 rows, 7 columns `group/piece/metric/value/reference/verdict/note`), `render335_base_orient.png`, `cmp_axes323.txt` (`IDENT 170 DIFFER 2 MISSING 0`), `cmp_axes323_off.txt` (`IDENT 172 DIFFER 0 MISSING 0`), `score335_juglet_def3x.json`, `score/` (`acc_potF.tsv`, `acc_potJ.tsv`, `panel_potF.tsv`, `panel_potJ.tsv`, `score335_juglet_def3x.json`). `runs/index.tsv` gained three rows (`..._t335-ship-base-orient`, `..._t335-potF`, `..._t335-potJ`; verdict and human_note left blank). Every job's `sacct -X` is in the table above; all corpus and `Dataset/` inputs are `CORPUS-UNCHANGED`.

### Corrections after the read-only verification

An independent read-only pass re-checked every claim above against the files and found three numbers in the first draft of this write-back wrong; all three are corrected here and in the artifacts: the insertion count (`319`, not `316` — `git diff --numstat`), the `not_needed` pass-4 row (those eight pots hold `137` pieces, not `163`; `161/163` of Pot A..J is the whole-corpus identity figure) and the description of the `Pot_JUGLET_*` duplicate block (pre-existing, only its `canonicalize` decision changed). Nothing else moved: the 170/2 split, the `0/18` guard, the `9/9` match to `t367`, the assembly floors and the render captions were re-derived and held. The verifier also flagged one premise of mine as wrong rather than a defect: `t367`'s `axes_shipped_base` is the **already-oriented** answer, so t335's Piece 7 correctly has the SAME direction as it and the 180 deg reversal is between t335 and its own pre-orientation output (`signed 175.3076 deg -> 4.6924 deg`).

### What a conservator should take from this

Two of the 172 pot pieces were being written rim-down: `Pot_F_Piece_01` and `Pot_J_Piece_03` are base sherds whose scans sit inverted, and the old writer forced every direction to point "up", which on an inverted base means rim-to-base. Both are now reversed, their lines and positions unchanged (0.0000 deg / 0.0000 mm from before apart from the 180 deg sign). Nothing else in the pot corpus moved: 170 of 172 files are byte-identical to the previous answer set. On the 3x Juglet, where Piece 7 is the known inverted base, the axis is now upright — the `SignAxisGuard` goes from 4 of 18 pairs to 0 of 18, and its GT angle from 175.31 deg to 4.69 deg — and the two pots still assemble to their floors (F 5/5 sherds 7/7 edges, J 8/11 and 16/21), so the fix costs nothing where it does not apply.

Reading: `orient-base-axis-shipped-clean`

**End state:** ready

### Lead verification (2026-11-19)

- `verified: python C:/PR/artifacts/dsh-handover/335/accept.py -> ACCEPTANCE PASSED (exit 0); python -m pytest C:/PR/worktrees/sfs/335/tests -> 42 passed; zero CRLF across sfs_axes/{select.py,potsac.py,cli.py}, scripts/run_benchmark_172.py, tests/test_select.py.`
- `verified: C:/PR/artifacts/t335/render335_base_orient.png inspected visually -> Juglet_Piece_7 [def_3x] (dir_z +0.637 -> -0.637), Pot_F_Piece_01 (+0.895 -> -0.895), and Pot_J_Piece_03 (+0.588 -> -0.588) are genuine inverted base sherds whose green orient_base_axis arrows point base -> rim (d_b . d_a = -1.0000); Pot_A_Piece_01 upright base control remains unflipped (dir_z +0.917, d_b . d_a = +1.0000).`
- `verified: C:/PR/artifacts/t335/{axes335_audit.json,cmp_axes323.txt,cmp_axes323_off.txt,gate335.tsv} -> Pass 1 (35395994 COMPLETED 0:0): 170/172 byte-identical vs axes323 (Pot A 8/8 identical, 161/163 Pot A..J identical, 9/9 legacy 1x Juglet identical), only Pot_F_Piece_01 (z_wall - z_pole = -14.326 mm) and Pot_J_Piece_03 (-32.8392 mm) differ by pure 180 deg sign reversal (0.0000 deg unsigned, 0.0000 mm pos, is_base_fragment=True); Pass 2 --no-base-orient (35396519 COMPLETED 0:0): 172/172 byte-identical to axes323 (IDENT=172 DIFFER=0 MISSING=0); Pass 3 def_3x Juglet (35396816 COMPLETED 0:0): is_base_fragment=True on Piece 7 alone, Piece 7 flipped 175.3076 -> 4.6924 deg, SignAxisGuard = 0/18 (0.00%), 9/9 match to t367 axes_shipped_base at 0.0000 deg / 0.0000 mm. Clarification on Pass 3 table column 'd_perp_sherd mm' (lines 177-187): the worker's gtscore omitted /3.0 on the 3x Juglet cloud, so printed values [0.3669..10.7386] are in 3x tree units and equal [0.122..3.580] mm real (matching t367 axes_shipped_base verbatim).`
- `verified: C:/PR/artifacts/t335/score/{acc_potF.tsv,acc_potJ.tsv} -> Pass 4 (35396814, 35396815 COMPLETED 0:0): F_K3R1/2 both 5/5 sherds, 7/7 edges (floor 5/5, 7/7; control F_MOR1 3/5 3/7, F_MOR2 5/5 7/7) and J_K3R1/2 both 8/11 sherds, 16/21 edges (floor >=8/11, >=16/21, matching J_MOR1/2).`

