# 01: Diagnose 14 axis loss pieces, profile-vs-normal misses, and own-surfaces baseline

**What to build:** A **read-only diagnostic & offline probe** (ZERO edits to tracked code in `SfSpp_preprocessing` or `structure-from-sherds-pp`) on Spartan compute nodes that (A) decomposes why shipped `axes335` (`commit 9e0fe6a`) loses to Authors' `Axes/` on the 8 `K3` and 6 `K1`-only corpus pieces plus `Pot A`/`Pot G` radial precision and `def_3x` Juglet edges, (B) probes whether joint scale-free normal+profile ranking and profile-guarded full-cloud analytical LM refinement close those gaps without hurting other pieces, and (C) measures shipped `axes335` on **our own `MeshPreprocessingHeadless` surfaces** across `Pot A..J`.

**Answers:** E1
**Blocked by:** None (can start immediately; Tickets 335 `9e0fe6a` and 336 `e0cfcce` complete)
**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-20)
**Branch:** 01-diagnose-14-losses-and-own-surfaces-audit, in /c/PR/worktrees/sfs/01
**Worker:** unassigned
**Budget:** medium 5
**Hand-over:** DeepSeek — hidden acceptance check at `C:/PR/artifacts/dsh-handover/axis-parity-01/accept.py` to be staged before dispatch

---

## Background & exact target pieces (verified in `C:/PR/artifacts/axis_audit/`)

Across `141` GT-scored corpus pieces (`Pot A..J`), shipped `axes335` (`9e0fe6a`) already beats Authors' `Axes/` overall (`K1 <= 10°`: `109/141` vs `105/141`; `K3 <= 10°`: `121/141` vs `116/141`; mean `9.67° / 10.54 mm` vs `14.26° / 14.82 mm`), yet still trails in three specific places:

1. **8 `K3` losses (`Auth K3 <= 10°` vs `axes335 K3 > 10°`):**
   - `Pot_A_Piece_07` (`5.39° K=3` vs `26.83° K=1`)
   - `Pot_D_Piece_23` (`6.23°` vs `10.67°`)
   - `Pot_E_Piece_25` (`8.59°` vs `13.70°`)
   - `Pot_E_Piece_29` (`0.91°` vs `17.35° / K3 10.73°`)
   - `Pot_E_Piece_31` (`9.36°` vs `16.10°`)
   - `Pot_F_Piece_05` (`8.88°` vs `10.68°`)
   - `Pot_I_Piece_20` (`0.97°` vs `21.79°`)
   - `Pot_J_Piece_02` (`8.91°` vs `10.95°`)
2. **6 `K1`-only losses (`Auth r0 <= 10°`, `axes335 r0 > 10°` while `K3 <= 10°`):**
   - `Pot_A_Piece_06` (`0.95°` vs `34.99° / 3.89°`)
   - `Pot_D_Piece_20` (`9.64°` vs `18.86° / 3.03°`)
   - `Pot_D_Piece_27` (`6.09°` vs `23.17° / 5.58°`)
   - `Pot_E_Piece_14` (`6.32°` vs `56.35° / 9.38°`)
   - `Pot_E_Piece_26` (`6.64°` vs `10.08° / 9.18°`)
   - `Pot_J_Piece_07` (`1.79°` vs `20.42° / 6.60°`)
3. **Median radial & angular tightness:** Authors' `Pot A` median radial offset is `1.92 mm` vs `axes335` `6.97 mm` (`K3 5.57 mm`); overall `141`-piece median is `2.78° / 4.38 mm` vs `3.06° / 4.53 mm`.
4. **Why it likely happens (`select.py:76-86`, `profile.py:38-82` vs `run_potsac.m:66-68`):** `rank_by_profile` and `refine_axis_profile` use ONLY 2,500 strided positions per wall via 400-eval Nelder–Mead on `wall_thickness`, ignoring surface normals `n_i` completely at ranking & final polish time (whereas Authors finish surviving candidates with analytical `tol=1e-9` LM on **100% of surface points + normals**). Also check rim coplanarity (`SfS++ §IV-B2:177`, `compute_rim_errors.m`, `check_base_and_rim.m`) where applicable.

Do NOT re-test closed dead-ends listed in `spec.md` §4 (`unnormalized Cao alone`, `pure normalized LM alone`, `profile_band`, `5° bounded NM A1`, `2-DoF a1_k0`, `c_in` / `6° guarded c_ref`).

---

## Stages (Spartan compute node only; zero source edits)

Create run directory `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t01-diag-axis-parity/`. Copy `sfs_axes/` (`9e0fe6a`) into `<run>/work/` only if instrumentation is needed; never modify tracked repo files.

### Stage A — Exact per-piece bottleneck decomposition
On the **14 loss pieces** (`8` K3 + `6` K1-only), **`Pot A` (`8` pieces)**, **`Pot G` (`7` pieces)**, and **`def_3x` Juglet (`9` pieces)** using the exact `run_potsac_union` inputs (`normalized=True`):
1. **Pool coverage (`reps` before `PROFILE_BASINS=60` and inside `60`):** Report best GT-angle in the full `_cluster_union` basin pool, in top-`60`, after `refine_axis_normalized`, in `PROFILE_REFINE_K=8` (`15°` dedup), and after `refine_axis_profile` + `keep_lines(tau=1.2, kmax=3)`.
2. **Stage-by-stage attribution:** Classify each of the 14 losses into exactly one failure mode:
   - *(M1) Missing from 60-basin pool* (`best_pool_deg > 10°` even before ranking — check `STEP`, `MAX_ITERS`, or `Cd` sampling),
   - *(M2) Lost in `[:8]` / `15°` dedup*,
   - *(M3) Killed by `profile_cost` decoy* (true basin exists in pool/top-8, but a normal-violating line gets lower `profile_cost` — check `normalized_huber_cost` at both!),
   - *(M4) Drifted by unconstrained `refine_axis_profile`* (`v_ref` walked `> 5°` or radial error jumped despite good start), or
   - *(M5) Pruned by `keep_lines(tau=1.2, kmax=3)`*.
3. **Diagnostic table:** Report for `GT`, `Authors`, `axes335 rank-0`, and `best-in-pool`: angle to GT (deg), radial distance to GT origin (mm), `profile_cost` (mm), `normalized_huber_cost` (full cloud & 2500-strided), worst-wall normalized cost, and centroid clearance `d_c`.

### Stage B — Offline probe of paper-aligned invariants on all 141 GT pieces + `def_3x` Juglet
Using ONLY cached candidate pools / point clouds (fast offline probe, zero E2E yet), test:
1. **Joint scale-free ranking:** Combine `profile_cost` (or relative ratio `c_prof / min(c_prof)`) and `normalized_huber_cost` (`c_norm`, evaluated with normals!) so normal-violating thin-profile decoys (`A06, E14, I20, J07`, etc.) are rejected without causing `c_norm`-only cone/sphere drift (`Pot_A_Piece_08` safe!).
2. **Profile-guarded full-cloud analytical LM polish:** Starting from top distinct surviving candidates, run analytical `refine_axis_normalized` (`full` cloud or dense stride, `tol=1e-9`) **guarded by `(r, z)` profile consistency + `Pot A` walk safety** (accepting the analytical LM refinement only if it reduces normal cost without inflating `profile_cost` past a small tolerance, OR initialized after `refine_axis_profile`), testing both residual sharpness (`Pot A` `6.97 mm -> <= 2.5 mm`) and angle recovery on the 8 `K3` misses.
3. Also report whether any of the 14 losses carry clear rim curves (`SfS++ §IV-B2:177` / `check_base_and_rim.m` criteria) where rim plane normal coplanarity helps.

### Stage C — Own-surfaces baseline audit (`MeshPreprocessingHeadless` surfaces)
Run shipped `axes335` (`9e0fe6a`) over **`Pot A..J`** using **our own `MeshPreprocessingHeadless` surfaces** (`S0`/`S1` generated by our `t305`/`t319` runs or default-on preprocessing on Spartan — cite exact source run paths/manifests in `gate01.tsv`!), scored identically on the `141` GT pieces, and compare side-by-side:
- `Authors' Axes/` vs `axes335` on Authors' `Surfaces/` vs `axes335` on **Our Own Surfaces** (`K1 <= 10°`, `K3 <= 10°`, median/mean deg & radial mm per pot).
- Flag any piece where switching from Authors' surfaces to Our Own Surfaces introduces a new axis regression (distinguishing surface-segmentation differences vs axis-fitter differences).

### Stage D — Deliverables & Visual Check (`C:/PR/artifacts/axis-parity-01/`)
- `diag01_summary.json` — full Stage A, B, and C structured JSON results.
- `gate01.tsv` — 7-column TSV (`group\tpiece\tmetric\tvalue\treference\tverdict\tnote`).
- `render01_misses.png` — multi-panel visual inspection of the worst `K3` and `K1` loss pieces (`Pot_A_Piece_07`, `Pot_A_Piece_06`, `Pot_E_Piece_29`, `Pot_I_Piece_20`, `Pot_J_Piece_02`, `Pot_J_Piece_07`) + `(r, z)` profile plots comparing GT (black), Authors (blue), `axes335` (red), and best offline joint/guarded candidate (green). **Inspect visually before writing `Reading:`.**
- Check `CORPUS-UNCHANGED` across all frozen inputs; record all Slurm job IDs and final `sacct -X`.

---

## Readings (pick one verbatim on a bare `Reading:` line)
- `normal-profile-gap-isolated-ready-for-t02` — Stage A/B isolates the exact failure mode(s) of the 14 loss pieces AND offline joint normal+profile scoring / guarded analytical LM improves `K1`/`K3` and `Pot A` radial precision while preserving `Pot_A_Piece_08` & `0/18 SignAxisGuard`; Stage C documents own-surfaces parity gap; proceed to Ticket 02 prototype.
- `own-surfaces-differ-upstream-first` — Stage C shows a large (`> 10` pieces or pot-breaking) gap attributable to our `MeshPreprocessingHeadless` surfaces vs Authors' `Surfaces/` before axis fitting; upstream surface parity must be scoped alongside Ticket 02.
- `blocked: missing-input` — required Stage C own surfaces or run inputs are missing on Spartan.

## Out of scope
- Editing ANY tracked file in `SfSpp_preprocessing/` or `structure-from-sherds-pp/`.
- Running E2E assembly (`Pot A..J` sbatch sweeps belong to Ticket 02 once Stage B selects the exact formulation).

## Acceptance
- [ ] Zero tracked source edits (`git status --short` changes only this ticket file); all heavy runs executed on Spartan compute nodes (`sacct -X COMPLETED 0:0`, `CORPUS-UNCHANGED`).
- [ ] Stage A classifies all 14 loss pieces (`8` K3 + `6` K1-only), `Pot A`, `Pot G`, and `def_3x` Juglet across `M1..M5` with full `cost/deg/mm` diagnostics.
- [ ] Stage B evaluates offline joint normal+profile ranking + profile-guarded analytical LM across all `141` GT pieces and `def_3x` Juglet (`0/18 SignAxisGuard`).
- [ ] Stage C benchmarks shipped `axes335` on our own `MeshPreprocessingHeadless` surfaces across `Pot A..J` (`141` GT pieces) beside Authors' `Axes/` and Authors'-surface `axes335`.
- [ ] `C:/PR/artifacts/axis-parity-01/{diag01_summary.json,gate01.tsv,render01_misses.png}` fetched locally and `render01_misses.png` visually inspected before writing bare `Reading:` and `**End state:** ready`.
