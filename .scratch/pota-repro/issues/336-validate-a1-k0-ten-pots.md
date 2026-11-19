# 336: Validate 2-DoF tilt-only `a1_k0` + landed `orient_base_axis` across all 10 paper pots (`Pot A..J`) and `def_3x` Juglet

**What to build:** A **measurement and 10-pot validation run** (ZERO edits to tracked `SfSpp_preprocessing/sfs_axes/`, `scripts/`, `tests/`, `structure-from-sherds-pp/class/`, or `Dataset/`; all prototype `a1_k0` code lives strictly inside the Spartan run directory's `<run>/work/impl_a1_k0/`) evaluating Ticket 365's 2-DoF tilt-only `a1_k0` ranking rule layered on top of Ticket 335's landed `orient_base_axis` (`commit 9e0fe6a`) across **all 10 paper pots (`Pot A..J`, 163 corpus pieces, 2 repeats each)** and **`def_3x` Juglet (`9` pieces, 2 repeats)** before deciding whether to promote `a1_k0` over shipped 4-DoF `c_ref`.

**Answers:** E1
**Blocked by:** None (Ticket 335 resolved and landed on `SfSpp_preprocessing` `main` at `9e0fe6a`)
**Status:** results-in
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
  - `axes336_summary.json` — complete Part A (all 10 pots `163` pieces + deltas vs `axes335`, plus the `def_3x` Juglet `juglet_def3x` block with `SignAxisGuard` and the `/3.0` real-mm distances). Part B evidence is `gate336.tsv` plus `score/acc_pot{A..J}.tsv`; the summary does not carry the assembly arms.
  - `gate336.tsv` — exact 7-column header `group\tpiece\tmetric\tvalue\treference\tverdict\tnote` covering all 10 pots `A..J` + `Juglet`.
  - `render336_tenpots.png` — multi-panel labelled render covering **all 10 pots (`Pot A..J`) + `Juglet def_3x`** final `a1_k0` assemblies against GT/perspective (`SfSpp_preprocessing/.scratch/pota-repro/t323/render323.py` style or a combined 11-panel montage). **Inspect visually before writing `Reading:`.**
  - `score/` — fetched `acc_potA.tsv` .. `acc_potJ.tsv` (ten files) plus the axes-side `axes336_juglet_def3x.json`; the Juglet assembly `score58` and `cluster366` JSONs (including `_xy2`, `_xy3` and `oracle_xy_cluster`) are fetched into `C:/PR/artifacts/t336/juglet/`.
- Append rows to `/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv` (`verdict` and `human_note` blank) for the `t336` axis run, the 10 pot runs, and the Juglet run.
- Record all Slurm job IDs + final `sacct -X` table (`COMPLETED 0:0`), `CORPUS-UNCHANGED` confirmation, Part A & Part B summary tables, one bare `Reading:` line, and end with `**End state:** ready`.

## Readings (pick one verbatim on a bare `Reading:` line)

- `a1-k0-passes-all-ten-pots-and-juglet` — all 10 pots (`Pot A..J`) meet or exceed their `t323` floors on `a1_k0 + orient_base_axis` (specify `20/20` or per-pot repeat counts & comparison against `axes323` on `D..J`) AND `def_3x` Juglet closes `9/9` sherds (`0/18 SignAxisGuard`, vertex cluster `<= 0.6 mm`).
- `a1-k0-regresses-corpus-pot` — one or more of `Pot A..J` falls below its `t323` floor on `a1_k0 + orient_base_axis` (name exact pot(s), sherd/edge drop, and which axis piece(s) changed vs `axes335`), even while Juglet passes.
- `blocked: control-or-input-failed` — any `MO` control drops unexpectedly, Juglet positive/rig check fails, or a named template/input is missing.

## Out of scope

- Editing ANY tracked source file (`sfs_axes/`, `scripts/`, `tests/`, `structure-from-sherds-pp/class/`, `Dataset/`), committing, pushing, merging, or running `ticket_close.sh`.

## Acceptance

- [x] Prototype `impl_a1_k0` exists strictly inside Spartan `<run>/work/` on top of landed Ticket 335 (`9e0fe6a`); worktree `C:/PR/worktrees/sfs/336` has ZERO tracked source edits.
- [x] Part A extracts `axes336_a1_k0` (`163` corpus pieces `Pot A..J`) and `axes336_juglet_def3x` (`9` `def_3x` Juglet pieces), scores against GT & Ticket 335 `axes335` (`SignAxisGuard = 0/18`, real `mm` units `/ 3.0` on Juglet) into `axes336_summary.json`.
- [x] Part B runs all 10 paper pots (`Pot A..J`, 2 repeats `MOR1/2 + K3R1/2`) AND `Juglet def_3x` (`2` repeats) on Spartan compute nodes (`sacct -X` `COMPLETED 0:0`, `CORPUS-UNCHANGED`), fetching `score/acc_pot{A..J}.tsv` and Juglet `score58` + `cluster` JSONs.
- [x] Part C delivers `C:/PR/artifacts/t336/{axes336_summary.json,gate336.tsv,render336_tenpots.png,score/}`, visually inspects `render336_tenpots.png`, appends `runs/index.tsv` rows, writes complete `## Comments` + bare `Reading:` line + `**End state:** ready`.

## Comments

Worked in DSH Baton w336 by worker `dsh one-shot subagent w336` (2026-11-19).

### Run directories (Spartan `/data/gpfs/projects/punim2657/SfSpp/runs/`)

| run | job id | sacct -X |
|---|---|---|
| `t336-precheck` (manual dry-run 1) | 35399016 | COMPLETED 0:0, 00:00:21 — diff 154 lines, `patch rc=1` (that local check did not line up; superseded) |
| `t336-precheck` (manual dry-run 2) | 35399038 | COMPLETED 0:0, 00:01:21 — diff 165 lines, `patch rc=0` but `diff -r` counted `__pycache__` and reported a mismatch; the submitted job's `diff -ruN -x __pycache__` produced the 154-line diff that reproduces exactly |
| `20261119-1823_f86432b_t336-a1-k0-ten-pots` (axes + gate + render) | 35399077 | COMPLETED 0:0, 00:05:23, 24 cpus |
| `20261119-1823_f86432b_t336-potA` | 35399078 | COMPLETED 0:0, 00:03:06 |
| `_potB` | 35399079 | COMPLETED 0:0, 00:07:06 |
| `_potC` | 35399080 | COMPLETED 0:0, 00:01:36 |
| `_potD` | 35399081 | COMPLETED 0:0, 00:46:04 |
| `_potE` | 35399082 | COMPLETED 0:0, 00:31:40 |
| `_potF` | 35399083 | COMPLETED 0:0, 00:01:03 |
| `_potG` | 35399084 | COMPLETED 0:0, 00:01:20 |
| `_potH` | 35399085 | COMPLETED 0:0, 00:05:13 |
| `_potI` | 35399086 | COMPLETED 0:0, 00:22:29 |
| `_potJ` | 35399087 | COMPLETED 0:0, 00:09:01 |
| `_t336-juglet` (first array, 3 arms) | 35399088_0.._2 | FAILED 1:0 (harness banner gate read `1` where the binary prints `on`; the three arms ran to the end and scored — cosmetic, fixed, see below) |
| `_t336-juglet` (rerun array, 4 arms + 3 controls) | 35399920_0.._3 | COMPLETED 0:0, 00:11:14 / 00:09:39 / 00:10:27 / 00:08:32 |
| `t336-rescore` (audit rewrite) | 35399919 | FAILED 1:0 (`KeyError mean_deg0_335_gt`, fixed) |
| `t336-rescore` | 35399983 | COMPLETED 0:0 |
| `t336-post` (gate + render) | 35401529 | COMPLETED 0:0, 00:00:20 |
| `t336-post` | 35401720 | COMPLETED 0:0, 00:00:19 |
| `t336-post` | 35401739 | FAILED 1:0 (best-of-2 arm label `<P>_K3R<n>`, fixed) |
| `t336-post` | 35401752 | COMPLETED 0:0, 00:00:21 |
| `t336-post` | 35401802 | FAILED 1:0, 00:00:00 (`KeyError: 'countresult'` while best-of-two-comparing the oracle controls, fixed) |
| `t336-post` | 35401806 | COMPLETED 0:0, 00:00:21 — the gate/render pair recorded here |
| `t336-post` (regenerate gate after the identity wording fix) | 35401961 | COMPLETED 0:0, 00:00:22 — `gate336.tsv` md5 `331fb3b21674920e518d75e515c93b1f`, render unchanged |

`runs/index.tsv` rows appended at submission (lines 848–859): the axis run, the ten pot runs and the juglet run, `verdict` and `human_note` left blank.

### Prototype build — no tracked file touched

- `<run>/work/head` = landed `sfs_axes/` + `scripts/run_benchmark_172.py` at `9e0fe6a`; `<run>/work/impl_a1_k0` = `head` + the Ticket 365 `a1_k0` patch only. `profile.py` and four `select.py` hunks applied verbatim; three hunks hand-merged where `orient_base_axis` moved the context (the `select.py` import line, the `select_union_lines` signature, and the `_thresholds(tau, kmax)` call after the `line_rule` default).
- `<run>/work/impl_a1_k0.diff`: 154 lines, md5 `c802e5ceb74047b7fd4c2349e52c671d`.
- `verified: grep 'impl_a1_k0.diff reproduces' <run>/logs/axes336_35399077.out -> "impl_a1_k0.diff reproduces work/impl_a1_k0 exactly (154 lines)"` (the job re-applies the diff with `patch -p1` into a fresh copy of `head` and `diff -r`s the result).
- `verified: `pytest <run>/work/tests336 -q` -> 42 passed in 20.62 s, rc=0` (`/data/gpfs/projects/punim2657/CRAG/.venv/bin/python3`); 0 of the 5 failed-run budget used.
- `SFS_AXES_K0=1` exported for the extraction; `SFS_AXES_K0_DEDUP`, `SFS_AXES_LINE_TAU/KMAX`, `SFS_AXES_BASE_ORIENT` left unset so the patched defaults (5.0 deg, tau 1.2, kmax 3) and landed `BASE_ORIENT=1` applied.
- `verified: corpus_md5.py before/after -> "CORPUS-UNCHANGED: yes (2087 files)"` on the axis run; every pot job printed `CORPUS-UNCHANGED`.
- Worktree `C:/PR/worktrees/sfs/336` at `f86432b`: `git status --short` shows this ticket file only.

### Part A — 163 corpus pieces vs GT (`out/axes336_summary.json`, `out/gate_axes.tsv`)

Rule: the project's own — each candidate scored against the better of `Ground Truth Axes` and that piece's `Axes` file (this is what `run_benchmark_172.py` prints). `_gt_only` rows give the strict Ground-Truth-only count beside it.

| pot | n | K1 <= 10 deg | K3 <= 10 deg | axes335 K1/K3 | GT-only K1 | mean rank0 (axes335) |
|---|---|---|---|---|---|---|
| A | 8 | 7 | 7 | 6 / 7 | 6 | 3.82 deg (7.50) |
| B | 9 | 5 | 5 | 9 / 9 | 5 | 18.23 deg (3.02) |
| C | 6 | 4 | 6 | 5 / 6 | 4 | 10.39 deg (5.73) |
| D | 32 | 21 | 27 | 27 / 29 | 19 | 13.02 deg (8.78) |
| E | 34 | 25 | 27 | 32 / 33 | 23 | 8.07 deg (4.09) |
| F | 7 | 4 | 6 | 6 / 6 | 4 | 10.08 deg (3.87) |
| G | 7 | 3 | 6 | 7 / 7 | 3 | 12.60 deg (2.12) |
| H | 11 | 10 | 10 | 9 / 11 | 10 | 5.39 deg (6.66) |
| I | 30 | 25 | 25 | 25 / 25 | 23 | 6.68 deg (6.62) |
| J | 19 | 12 | 12 | 9 / 10 | 8 | 22.06 deg (24.20) |
| **all** | **163** | **116** | **131** | **135 / 143** | **105** | **10.95 deg (8.07)** |

- `<run>/out/axes336_summary.json` (md5 `6822ea1683789d6e6343dc04badf7fba`, fetched to `C:/PR/artifacts/t336/axes336_summary.json`) carries the 163-piece table above plus the `juglet_def3x` block copied verbatim from `score/axes336_juglet_def3x.json`, so one file answers both Part A bullets; its `note` records the min-rule headline and the `3.0` scaling of the juglet distances.
- All 163 axis files differ from `axes335`; none is a pure sign flip.
- By the strict GT-only reading (`new` vs `old` in `axes336_summary.json` pieces), 22 pieces crossed from inside 10 deg to outside it and 12 crossed the other way; by the min-rule reading used for the headline counts above (`best` vs `best_old`) the same comparison is 28 out and 9 in. The strict-read 22: A8 (2.3 -> 21.2 deg), B2 (3.7 -> 10.4), B6 (0.4 -> 87.2), B9 (3.2 -> 22.0), C2 (1.5 -> 84.9), D15 (4.7 -> 16.6), D17 (2.4 -> 37.7), D24 (9.9 -> 34.0), E9 (2.9 -> 45.1), E23 (2.0 -> 32.2), E27 (7.2 -> 25.3), E28 (3.6 -> 22.6), E32 (0.7 -> 10.3), E33 (2.7 -> 31.0), F4 (9.1 -> 25.5), G4 (4.6 -> 36.5), G5 (1.9 -> 12.3), G6 (2.7 -> 22.1), G7 (0.7 -> 15.1), I17 (3.4 -> 17.9), I19 (7.2 -> 12.6), J6 (1.7 -> 44.8).
- `mean_K` (candidates kept per piece, axes335 in brackets): A 1.00 (1.38), B 2.33 (1.67), C 2.00 (1.83), D 1.50 (1.50), E 1.53 (1.32), F 1.71 (1.57), G 1.57 (1.00), H 1.09 (1.36), I 1.10 (1.20), J 2.05 (2.05). The `a1_k0` lane keeps more candidates on B and G, so the loss is in direction, not in candidate count.
- `base_flipped` at rank 0 (axes335 in brackets): A 2 (2), B 4 (3), C 0 (1), D 18 (17), E 16 (17), F 3 (3), G 4 (4), H 2 (1), I 9 (9), J 12 (12) — the landed base-orient test flips about the same number of pieces as before.

### Part A — `def_3x` Juglet axes (`out/axes336_juglet_def3x`, `score/axes336_juglet_def3x.json`)

- 9 pieces from `<t80>/out/cell_def_3x/geom/Juglet_Piece_{1..9}.S{0,1}` through `run_potsac_union(C0, C1, seeds=list(range(10)), step=10, max_candidates=6, normalized=True, line_rule=True, base_orient=True)`.
- `K1 7/9`, `K3 7/9`, mean rank0 6.752 deg; `d_perp_sherd` rank-0 mean **0.941 mm**, max 4.552 mm in **real 1x mm** (`p`, `p_gt` and `c_mean` each divided by `scale = 3.0`, distances reported directly).
- `is_base_fragment` true on **Juglet_Piece_7 only**.
- `SignAxisGuard = 0/18 (0.00%)`; every per-piece count 0.
- `verified: agree_t366_axes_a1_base / agree_t365_axes_a1_k0 -> 0.000000 deg, 0.000000 mm on all 9 pieces`: the hand-merged `a1_k0` build reproduces t366's and t365's juglet axis values on this input (max `|dpos| = 5.68e-13 mm`, max sign-agnostic `|d| = 4.89e-13`, candidate counts equal; the text differs only in formatting, 12 decimals versus `%.17g`, and t365's direction sign is the opposite because it predates `orient_base_axis`; not byte-identical), so its 7/9 K1 is inherited from the landed method, not produced by the re-application.

### Part B — ten pots, four arms each (best of two repeats)

`MOR` = authors' axes control (input identical to t323's `MO`), `K3` = `axes336_a1_k0`.

| pot | MOR1 | MOR2 | K3R1 | K3R2 | floor (t323 achieved) | verdict |
|---|---|---|---|---|---|---|
| A | 8/8, 15/15 | 8/8, 15/15 | 8/8, 15/15 | 8/8, 15/15 | 8/8, 15/15 (8/8, 15/15) | PASS |
| B | 9/9, 15/15 | 9/9, 15/15 | 8/9, 12/15 | 9/9, 15/15 | 9/9, 15/15 (9/9, 15/15) | PASS (one K3 repeat short) |
| C | 4/4, 5/5 | 4/4, 5/5 | 4/4, 5/5 | 4/4, 5/5 | 4/4, 5/5 (4/4, 5/5) | PASS |
| D | 23/28, 55/69 | 24/28, 57/69 | 23/28, 52/69 | 23/28, 52/69 | >=23/28, >=55/69 (26/28, 63/69) | **FAIL** (joins 52 < 55) |
| E | 31/31, 62/62 | 31/31, 62/62 | 25/31, 47/62 | 25/31, 47/62 | >=29/31, >=57/62 (31/31, 62/62) | **FAIL** (sherds and joins) |
| F | 5/5, 7/7 | 5/5, 7/7 | 5/5, 6/7 | 5/5, 7/7 | 5/5, 7/7 (5/5, 7/7) | PASS (best of two) |
| G | 7/7, 10/10 | 7/7, 10/10 | 7/7, 10/10 | 7/7, 10/10 | 7/7, 10/10 (7/7, 10/10) | PASS |
| H | 8/11, 9/17 | 5/11, 7/17 | 10/11, 15/17 | 10/11, 15/17 | 11/11, 17/17 (11/11, 17/17; t323 MO 10/11 10/17 and 8/11 9/17) | **FAIL** |
| I | 25/26, 59/62 | 25/26, 59/62 | 25/26, 59/62 | 25/26, 59/62 | >=25/26, >=59/62 (25/26, 59/62) | PASS |
| J | 8/11, 16/21 | 8/11, 16/21 | 5/11, 8/21 | 5/11, 8/21 | >=8/11, >=16/21 (8/11, 16/21) | **FAIL** (both repeats) |

Six of ten pots hold or beat their floor; **D, E, H and J fall below it**. E and J fail in both repeats by the same margin (E 25/31, 47/62; J 5/11, 8/21), so those are not repeat noise. D loses only joins in the `a1_k0` lane (52 and 52 vs 55 and 57 in its own control, 55/69 in t323). H's own control arm fell to 5/11 while the `a1_k0` lane sat 10/11 twice, so on H the lane ordering reverses between repeats and a 2–3-sherd difference is inside what the control itself moves on this pot.

`CORPUS-UNCHANGED` printed by all ten pot jobs.

### Part B — `def_3x` Juglet assembly (`t368` cluster366.py, md5 `81f347cc1f80b7b84a163337959ec073`)

`verified: grep 'variant source md5' <jug>/logs/submit_*.log -> 0c216463ae27fe4571b200cc2292da99 expected 0c216463ae27fe4571b200cc2292da99 for floor 10`; provenance `all_equal=yes equal=9/9` against `axes336_juglet_def3x`; `tree unchanged by the run` in all 7 tasks.

| arm | sherds | edges | directed | cluster | max chamfer | GT joins | piece-7 joins |
|---|---|---|---|---|---|---|---|
| juglet_a1_k0_r1 | 9/9 | 12/18 | 25/36 | 9/9 | 0.482 mm | 18/18 | 4/4 |
| juglet_a1_k0_r2 | 8/9 | 7/18 | 15/36 | 9/9 | 0.486 mm | 15/18 | 3/4 |
| juglet_a1_k0_r3 | 9/9 | 11/18 | 23/36 | 9/9 | 0.467 mm | 16/18 | 4/4 |
| juglet_a1_k0_r4 | 7/9 | 4/18 | 9/36 | 9/9 | 0.556 mm | 8/18 | 2/4 |
| control `juglet_oracle_xy` (GT axes) | 8/9 | 8/18 | 16/36 | 9/9 | 0.469 mm | — | — |
| control `_xy2` | 9/9 | 13/18 | 27/36 | 9/9 | 0.471 mm | — | — |
| control `_xy3` | 9/9 | 13/18 | 27/36 | 9/9 | 0.459 mm | — | — |

- Best of four `a1_k0` repeats: 9/9 sherds, 12/18 edges, 18/18 joins, piece-7 **4/4** (3-7, 6-7, 7-8, 7-9), vertex cluster 9/9 at 0.482 mm — inside the 0.6 mm bar.
- Piece 7 upright candidates, identical in all four `a1_k0` repeats: `CAND336 27/100 upright (min rot 1.733 deg)`, `CAND338 8/17 upright, 6 on a GT edge`. The perfect-axes control gives `13/42` and `3/8 (3 on a GT edge)`.
- The rig is not deterministic: the same tree, same binary and same axes give 18/18, 15/18, 16/18 and 8/18 joins over four repeats, and the GT-axes control itself spans 8/9–9/9 sherds. So the juglet result is a best-of-four, read beside its control, not a fixed score.
- `score58`'s `seated_count` reads 0/9 in **every** arm including t366's own baseline (`own_place=False`), so that field is inert here; the seating evidence is `k_sherd`, `k_directed_pass` and cluster366's `cluster_seated`/`cluster_max_chamfer`.

### Visual check (`C:/PR/artifacts/t336/render336_tenpots.png`, 11 panels)

Rendered 35401806, reproduced unchanged by 35401961 (md5 `f56ac699d61a994bc088ac80f7fa090a`), inspected before writing this Reading. Every panel shows the GT cloud in grey with the `K=3` arm's coloured pieces over it, labelled with its staged count. A, B, C, E, F, G, H and I read as single coherent vessels with rims where the corpus has them; no piece sits detached or wildly off its body in any panel. Pot J is the sparsest: the GT cloud fills the panel and the arm's pieces are narrow colour bands at the rim, matching its 5/11 seated K3 lane. Pot D reads as one vessel, but a red piece at its base sits visibly below the grey body outline rather than flush with it — the one geometrically visible defect in the montage, and consistent with D losing joins (55/69 and 57/69 in its own control, 52/69 in both a1_k0 repeats). The Juglet panel (def_3x, scale 3) shows a closed vessel body.

### What this measures

On the corpus, `a1_k0` changes the axis on all 163 pieces and is worse than shipped `axes335` overall (116 vs 135 K1, 131 vs 143 K3, mean rank0 10.95 vs 8.07 deg), with big per-piece swings in both directions (strict GT-only reading: 22 pieces out of tolerance, 12 newly inside; min-rule reading: 28 out, 9 in). The assembly lane tracks that only partly: six pots hold, four fall below their t323 floor. On the Juglet the re-applied patch reproduces t366's shipped-axis values to within `6e-13 mm` (not byte-identical: 12-decimal formatting versus `%.17g`) and passes every juglet bar as a best-of-four.

`verified: awk -F'\\t' '$3 ~ /^acc_K3_best/' <run>/out/gate336.tsv -> D 23/28 52/69, E 25/31 47/62, H 10/11 15/17, J 5/11 8/21 (each below its floor)`
`verified: python3 -c "...axes336_summary.json totals..." -> k1 116 (335: 135), k3 131 (335: 143), mean_deg0 10.951 (335: 8.069)`
`verified: score/axes336_juglet_def3x.json -> sign_guard 0/18, base_pieces ["Juglet_Piece_7"], mean_d_perp_sherd_mm 0.941, max 4.552`

Reading: a1-k0-regresses-corpus-pot

**End state:** ready
