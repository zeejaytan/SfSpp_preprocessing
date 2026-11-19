# 336: Validate 2-DoF tilt-only `a1_k0` + landed `orient_base_axis` across all 10 paper pots (`Pot A..J`) and `def_3x` Juglet

**What to build:** A **measurement and 10-pot validation run** (ZERO edits to tracked `SfSpp_preprocessing/sfs_axes/`, `scripts/`, `tests/`, `structure-from-sherds-pp/class/`, or `Dataset/`; all prototype `a1_k0` code lives strictly inside the Spartan run directory's `<run>/work/impl_a1_k0/`) evaluating Ticket 365's 2-DoF tilt-only `a1_k0` ranking rule layered on top of Ticket 335's landed `orient_base_axis` (`commit 9e0fe6a`) across **all 10 paper pots (`Pot A..J`, 163 corpus pieces, 2 repeats each)** and **`def_3x` Juglet (`9` pieces, 2 repeats)** before deciding whether to promote `a1_k0` over shipped 4-DoF `c_ref`.

**Answers:** E1
**Blocked by:** None (Ticket 335 resolved and landed on `SfSpp_preprocessing` `main` at `9e0fe6a`)
**Status:** in-progress
**Working in:** DSH Baton w336 (2026-11-19) (2026-11-19)
**Branch:** 336-validate-a1-k0-ten-pots, in /c/PR/worktrees/sfs/336
**Worker:** dsh one-shot subagent w336
**Budget:** medium 5
**Hand-over:** DeepSeek — C:/PR/artifacts/dsh-handover/336/accept.py

---

## Why this ticket exists (from Tickets 366–368 and Ticket 335)

1. Ticket 335 landed blind `orient_base_axis` cleanly on top of shipped `sfs_axes` (`9e0fe6a`): `170/172` byte-identical to `axes323` (`Pot_F_Piece_01` and `Pot_J_Piece_03` pure base-sign flips passing `F 5/5, 7/7` and `J 8/11, 16/21`), `0/18 SignAxisGuard` on `def_3x` Juglet, and closed `9/9` Juglet vessel (`0.466–0.476 mm` vertex cluster, `6/9 <= 4.596 mm` / `5.56 mm` origin gauge).
2. Tickets 366–367 also established that `a1_k0 + orient_base_axis` (`axes_a1_base`: `2-DoF` direction-tilt-only profile polish holding `p0 = foot` fixed + pre-polish `c_in` order preserved + `5.0 deg` dedup + `keep_lines(c_in, tau=1.2, kmax=3)` + `orient_base_axis`) tightens Juglet further (`juglet_a1_base_r2`: `9/9` sherds, **`11/18` stock edges vs `8/18`**, **`8/9 <= 4.596 mm` / `4.653 mm` origin gauge vs `6/9` / `5.56 mm`**, `0.482 mm` vertex cluster) while holding `Pot A` at `8/8, 15/15` (`2.011 mm`). Meanwhile, Tickets 367–368 ruled out `4-DoF c_in` and `6 deg`-guarded `4-DoF c_ref` because both regress `Pot_A_Piece_08` to `7/8, 13/15`.
3. Before deciding whether to promote `2-DoF a1_k0` into `SfSpp_preprocessing/sfs_axes/`, we must test whether `a1_k0 + orient_base_axis` holds across **all 10 paper pots (`Pot A..J`, especially hard pots `D`, `E`, `G`, `H`, `I`, `J`)** against the Ticket 323 (`axes323`) benchmark and `t323` floors.

## Prototype rules (ZERO edits to tracked repo files)

1. Create run directory on Spartan:
   `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t336-a1-k0-ten-pots/`
2. Copy Ticket 335's landed `sfs_axes/` (`commit 9e0fe6a`, from `C:/PR/worktrees/sfs/336/sfs_axes` or canonical `main`) and `scripts/run_benchmark_172.py` into `<run>/work/impl_a1_k0/`.
3. Apply ONLY the Ticket 365 `a1_k0` patch inside `<run>/work/impl_a1_k0/sfs_axes/` (exact reference diff: `/data/gpfs/projects/punim2657/SfSpp/runs/20261118-0242_308c771_t365-k0-preservation-postjoin/work/src_axes_ab.diff`), layered on top of Ticket 335's landed `orient_base_axis` (keep `BASE_ORIENT` enabled by default!):
   - `profile.py`: add `refine_axis_profile_tilt(vt, walls, centre, size, maxfev=400)` optimizing ONLY the 2 direction-tilt DoFs `(x[0], x[1])` with `foot = vt[3:6] + ((centre - vt[3:6]) @ a) * a` fixed (`x[2] = x[3] = 0`).
   - `select.py`: in `rank_by_profile`, sort pool by `cost_in`, apply `_distinct(pool, ..., 5.0)[:8]`, polish each candidate with `refine_axis_profile_tilt`, keep pre-polish `c_in` in `fin` (NO `fin.sort()`), dedup `fin` via `_distinct(..., 5.0)`; then `select_union_lines` applies `keep_lines(c_in, tau=1.2, kmax=3)` followed by Ticket 335's `orient_base_axis(vt, C)`.
   - Save unified diff `<run>/work/impl_a1_k0.diff` so provenance is exact.
4. Keep `C:/PR/worktrees/sfs/336` source tree **100% unmodified** (`git status --short` may change ONLY this ticket file `.scratch/pota-repro/issues/336-validate-a1-k0-ten-pots.md`).

## Part A — 163-piece corpus (`Pot A..J`) + `def_3x` Juglet axis extraction & scoring (Spartan compute node)

1. Extract `<run>/out/axes336_a1_k0/` over all `163` corpus pieces (`Pot A..J`) using `<run>/work/impl_a1_k0/scripts/run_benchmark_172.py --pots A,B,C,D,E,F,G,H,I,J --out <run>/out/axes336_a1_k0 --jobs 24 --cap 6 --seeds 10 --step 10` (`normalized=True, line_rule=True, base_orient=True`).
2. Extract `<run>/out/axes336_juglet_def3x/` over all 9 clean `t80` `def_3x` Juglet walls (`/data/gpfs/projects/punim2657/SfSpp/runs/20261117-0430_d272313_t80-default-on/out/cell_def_3x/geom/Juglet_Piece_{1..9}.S{0,1}`) using `<run>/work/impl_a1_k0` `run_potsac_union(C0, C1, seeds=list(range(10)), step=10, max_candidates=6, normalized=True, line_rule=True, base_orient=True)`.
3. Score and compare (`<run>/out/axes336_summary.json` -> fetch to `C:/PR/artifacts/t336/axes336_summary.json`):
   - **163 corpus pieces (`Pot A..J`):** score against `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Ground Truth Axes` & `Axes`, reporting per-pot `K=1 <= 10 deg`, `K<=3 <= 10 deg`, `mean_K`, base-flipped count, AND per-pot / per-piece comparison vs Ticket 335's shipped `/data/gpfs/projects/punim2657/SfSpp/runs/20261119-1644_ac60d8d_t335-ship-base-orient/out/axes335/`.
   - **9 `def_3x` Juglet pieces:** score against `/data/gpfs/projects/punim2657/Dataset/Juglet_large` (**divide BOTH `p` and `c_mean` by `scale = 3.0`** so `d_perp_origin_mm` and `d_perp_sherd_mm` are in real `1x mm`), verify `is_base_fragment=True` on Piece 7 only, `SignAxisGuard = 0/18 (0.00%)`, and verify agreement with `t366`'s `axes_a1_base` (`/data/gpfs/projects/punim2657/SfSpp/runs/20261118-1435_78581fb_t366-base-sign-4dof/out/axes/axes_a1_base/`).

## Part B — 10-pot end-to-end assembly (`Pot A..J`, 2 repeats each) + `def_3x` Juglet (`2` repeats) on Spartan compute nodes

1. **All 10 paper pots (`Pot A..J`) in parallel (`--dependency=afterok:<axes_job>`):**
   - For each `P` in `A B C D E F G H I J`: clone `/data/gpfs/projects/punim2657/SfSpp/runs/20261109-1426_ecd5bb8_t319-pot<P>` into a fresh run dir `/data/gpfs/projects/punim2657/SfSpp/runs/<STAMP>_<git7>_t336-pot<P>` following `SfSpp_preprocessing/.scratch/pota-repro/t323/make_e2e_323.sh`:
     - Copy `work/` helpers (`*.py`, `arm67.sh`, `shim`, `inc_src`) into `t336-pot<P>/work/`.
     - Substitute `AX_318=<run>/out/axes336_a1_k0`, update `--job-name=t336-pot<P>`, and assert `grep -q "^AX_318=<run>/out/axes336_a1_k0" submit.sbatch` and `grep -q "_MOR1" submit.sbatch`.
     - Run all 4 arms per pot (`${P}_MOR1`, `${P}_MOR2` authors' axes control; `${P}_K3R1`, `${P}_K3R2` `a1_k0 + orient_base_axis`). Check `CORPUS-UNCHANGED` on every pot job!
     - Compare each pot's `K3R1`, `K3R2`, `MOR1`, `MOR2` against **both** the `t323` floors AND `t323` (`axes323`) achieved scores (`/data/gpfs/projects/punim2657/SfSpp/runs/20261110-0740_d628fc0_t323-pot<P>/score/acc.tsv`):
       - `Pot A`: floor `8/8, 15/15` (`axes323`: `8/8, 15/15`)
       - `Pot B`: floor `9/9, 15/15` (`axes323`: `9/9, 15/15`)
       - `Pot C`: floor `4/4, 5/5` (`axes323`: `4/4, 5/5`)
       - `Pot D`: floor `>=23/28, >=55/69` (`axes323`: `26/28, 63/69`)
       - `Pot E`: floor `>=29/31, >=57/62` (`axes323`: `31/31, 62/62`)
       - `Pot F`: floor `5/5, 7/7` (`axes323`: `5/5, 7/7`)
       - `Pot G`: floor `7/7, 10/10` (`axes323`: `7/7, 10/10`)
       - `Pot H`: floor `11/11, 17/17` (`axes323`: `11/11, 17/17`)
       - `Pot I`: floor `>=25/26, >=59/62` (`axes323`: `25/26, 59/62`)
       - `Pot J`: floor `>=8/11, >=16/21` (`axes323`: `8/11, 16/21`)
2. **`def_3x` Juglet (`2` repeats):**
   - Run `juglet_a1_k0_r1` and `juglet_a1_k0_r2` using `<run>/out/axes336_juglet_def3x/` on the exact `t363`/`t366` container & shim (`floor 10`, shim md5 `0c216463ae27fe4571b200cc2292da99`, `XY_BREAK=1`, `XY_STATE=1`, `SFS_AXIS_LOCK_ICP` unset, `SFS_AXIS_SIGN=1`).
   - Score with `score58` (`13.788` tree = `4.596 mm` real) AND `/data/gpfs/projects/punim2657/SfSpp/runs/20261119-0412_bf3fc0b_t368-bounded-4dof-cref/tools/cluster366.py` (fixed md5 `81f347cc1f80b7b84a163337959ec073`), plus Piece 7 upright `CAND` / `CAND338` and `4/4` Piece 7 GT joins (`3-7, 6-7, 7-8, 7-9`).

## Part C — Deliverables & Visual Check (`C:/PR/artifacts/t336/`)

- Fetch to `C:/PR/artifacts/t336/`:
  - `axes336_summary.json` — complete Part A (all 10 pots `163` pieces + `9` Juglet `def_3x` pieces + deltas vs `axes335`) & Part B (`Pot A..J` `MOR1/2` + `K3R1/2` vs `t323` floors & `axes323`, plus `juglet_a1_k0_r1/r2`).
  - `gate336.tsv` — exact 7-column header `group\tpiece\tmetric\tvalue\treference\tverdict\tnote` covering all 10 pots `A..J` + `Juglet`.
  - `render336_tenpots.png` — multi-panel labelled render covering **all 10 pots (`Pot A..J`) + `Juglet def_3x`** final `a1_k0` assemblies against GT/perspective (`SfSpp_preprocessing/.scratch/pota-repro/t323/render323.py` style or a combined 11-panel montage). **Inspect visually before writing `Reading:`.**
  - `score/` — fetched `acc_potA.tsv` .. `acc_potJ.tsv` + Juglet `score58` & `cluster` JSONs (e.g., `juglet_a1_k0_r1.json`, `juglet_a1_k0_r2.json`, `*_cluster.json`).
- Append rows to `/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv` (`verdict` and `human_note` blank) for the `t336` axis run, the 10 pot runs, and the Juglet run.
- Record all Slurm job IDs + final `sacct -X` table (`COMPLETED 0:0`), `CORPUS-UNCHANGED` confirmation, Part A & Part B summary tables, one bare `Reading:` line, and end with `**End state:** ready`.

## Readings (pick one verbatim on a bare `Reading:` line)

- `a1-k0-passes-all-ten-pots-and-juglet` — all 10 pots (`Pot A..J`) meet or exceed their `t323` floors on `a1_k0 + orient_base_axis` (specify `20/20` or per-pot repeat counts & comparison against `axes323` on `D..J`) AND `def_3x` Juglet closes `9/9` sherds (`0/18 SignAxisGuard`, vertex cluster `<= 0.6 mm`).
- `a1-k0-regresses-corpus-pot` — one or more of `Pot A..J` falls below its `t323` floor on `a1_k0 + orient_base_axis` (name exact pot(s), sherd/edge drop, and which axis piece(s) changed vs `axes335`), even while Juglet passes.
- `blocked: control-or-input-failed` — any `MO` control drops unexpectedly, Juglet positive/rig check fails, or a named template/input is missing.

## Out of scope

- Editing ANY tracked source file (`sfs_axes/`, `scripts/`, `tests/`, `structure-from-sherds-pp/class/`, `Dataset/`), committing, pushing, merging, or running `ticket_close.sh`.

## Acceptance

- [ ] Prototype `impl_a1_k0` exists strictly inside Spartan `<run>/work/` on top of landed Ticket 335 (`9e0fe6a`); worktree `C:/PR/worktrees/sfs/336` has ZERO tracked source edits.
- [ ] Part A extracts `axes336_a1_k0` (`163` corpus pieces `Pot A..J`) and `axes336_juglet_def3x` (`9` `def_3x` Juglet pieces), scores against GT & Ticket 335 `axes335` (`SignAxisGuard = 0/18`, real `mm` units `/ 3.0` on Juglet) into `axes336_summary.json`.
- [ ] Part B runs all 10 paper pots (`Pot A..J`, 2 repeats `MOR1/2 + K3R1/2`) AND `Juglet def_3x` (`2` repeats) on Spartan compute nodes (`sacct -X` `COMPLETED 0:0`, `CORPUS-UNCHANGED`), fetching `score/acc_pot{A..J}.tsv` and Juglet `score58` + `cluster` JSONs.
- [ ] Part C delivers `C:/PR/artifacts/t336/{axes336_summary.json,gate336.tsv,render336_tenpots.png,score/}`, visually inspects `render336_tenpots.png`, appends `runs/index.tsv` rows, writes complete `## Comments` + bare `Reading:` line + `**End state:** ready`.

## Comments
