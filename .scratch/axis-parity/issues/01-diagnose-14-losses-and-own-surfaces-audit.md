# 01: Diagnose 14 axis loss pieces, profile-vs-normal misses, and own-surfaces baseline

**What to build:** A **read-only diagnostic & offline probe** (ZERO edits to tracked code in `SfSpp_preprocessing` or `structure-from-sherds-pp`) on Spartan compute nodes that (A) decomposes why shipped `axes335` (`commit 9e0fe6a`) loses to Authors' `Axes/` on the 8 `K3` and 6 `K1`-only corpus pieces plus `Pot A`/`Pot G` radial precision and `def_3x` Juglet edges, (B) probes whether joint scale-free normal+profile ranking and profile-guarded full-cloud analytical LM refinement close those gaps without hurting other pieces, and (C) measures shipped `axes335` on **our own `MeshPreprocessingHeadless` surfaces** across `Pot A..J`.

**Answers:** E1
**Blocked by:** None (can start immediately; Tickets 335 `9e0fe6a` and 336 `e0cfcce` complete)
**Status:** resolved
**Branch:** 01-diagnose-14-losses-and-own-surfaces-audit, in /c/PR/worktrees/sfs/01
**Worker:** DeepSeek -- dsh one-shot subagent w01-axis-parity
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
- [x] Zero tracked source edits (`git status --short` changes only this ticket file); all heavy runs executed on Spartan compute nodes (`sacct -X COMPLETED 0:0`, `CORPUS-UNCHANGED`).
- [x] Stage A classifies all 14 loss pieces (`8` K3 + `6` K1-only), `Pot A`, `Pot G`, and `def_3x` Juglet across `M1..M5` with full `cost/deg/mm` diagnostics.
- [x] Stage B evaluates offline joint normal+profile ranking + profile-guarded analytical LM across all `141` GT pieces and `def_3x` Juglet (`0/18 SignAxisGuard`).
- [x] Stage C benchmarks shipped `axes335` on our own `MeshPreprocessingHeadless` surfaces across `Pot A..J` (`141` GT pieces) beside Authors' `Axes/` and Authors'-surface `axes335`.
- [x] `C:/PR/artifacts/axis-parity-01/{diag01_summary.json,gate01.tsv,render01_misses.png}` fetched locally and `render01_misses.png` visually inspected before writing bare `Reading:` and `**End state:** ready`.

---

## Comments

**2026-11-20 — DeepSeek (`w01-axis-parity`) — read-only diagnosis, zero tracked source edits**

`Run:` `/data/gpfs/projects/punim2657/SfSpp/runs/20261120-0227_2c14fe3_t01-diag-axis-parity` — `run.json`, `submit_*.sbatch`, `logs/`, `work/`, `out/`, `impl/`, `out_poth/`. `impl/` is a byte copy of this worktree's `sfs_axes/`, `scripts/`, `tests/`; `diff --strip-trailing-cr` against the `t335-ship-base-orient` impl gives **0 content diffs**, so every number below is the code that shipped `axes335` (`9e0fe6a`). `C:/PR/SfSpp_preprocessing` and `C:/PR/structure-from-sherds-pp` were not touched.

**Commands (all `sbatch`, compute nodes only; no laptop or login-node compute)**

```
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261120-0227_2c14fe3_t01-diag-axis-parity
sbatch $RUN/submit_cache.sbatch       # cache: 150 stems' union pool -> out/cache/<stem>.npz|.json
sbatch $RUN/submit_analyze.sbatch     # Stage A staging + classification + rim check
sbatch --dependency=afterok:35409788 $RUN/submit_own.sbatch   # axes335 on OUR surfaces
sbatch $RUN/submit_poth.sbatch        # Pot H own surfaces, t305-lane recipe (commit 9c5eec2)
sbatch $RUN/submit_bchain.sbatch      # Stage B structural probe, 6 configs
sbatch $RUN/submit_assemble.sbatch    # diag01_summary.json + gate01.tsv
sbatch $RUN/submit_render.sbatch      # render01_misses.png
```

**`sacct -X` — the eight jobs whose output is used are all `COMPLETED`, `ExitCode 0:0`:** `35409752` t01-cache 07:24 · `35409950` t01-analyze 02:19 · `35409951` t01-own 03:50 · `35409788` t305-lane (Pot H) 05:20 · `35410066` t01-bchain 20:19 · `35410190` t01-render 00:05 · `35410187` t01-assemble 00:03 · `35410257` t01-assemble rerun 00:00. Jobs that failed and were fixed and resubmitted (all polled, all recorded in `run.json` and in `jobs.sacct` of `diag01_summary.json`): `35409753` `FAILED 1:0` (rim SVD reshape), `35409781` `FAILED 3:0` (missing `stage305.sh`), `35409952` `FAILED 2:0` (bad CLI flag), `35410027` `FAILED 1:0` (`AttributeError`), `35410059` `FAILED 1:0` (`NpzFile` assignment), `35410068` `FAILED 1:0` (assemble `stageC.pots` list bug); `35409643`/`35409646` cancelled after the `n_basins` `KeyError`. **`CORPUS-UNCHANGED: yes (2103 files)`** printed by t01-cache, t01-own (both passes) and the Pot H job (corpus md5 before/after).

### Stage A — the 14 losses, each in exactly one mode

Staged angles (deg) along the shipped chain: best in the full union pool | in top-60 raw | after `refine_axis_normalized` | in `PROFILE_REFINE_K=8` | final (`keep_lines` + NM). All from `out/stageA.json`; mode is assigned by the stage at which the <10° line dies.

| piece | loss | pool | top60 / nref | top-8 | final | mode |
|---|---|---|---|---|---|---|
| Pot_A_Piece_07 | K3 | 7.71 | 7.71 / 19.78 | 19.78 | 26.83 | M2 |
| Pot_E_Piece_25 | K3 | 2.38 | 2.38 / 38.27 | 10.21 | 13.70 | M2 |
| Pot_E_Piece_29 | K3 | 4.51 | 6.43 / 14.75 | 12.42 | 10.73 | M2 |
| Pot_E_Piece_31 | K3 | 6.37 | 6.59 / 66.01 | 15.08 | 16.10 | M2 |
| Pot_F_Piece_05 | K3 | 6.09 | 6.09 / 10.59 | 10.59 | 10.68 | M2 |
| Pot_E_Piece_26 | K1 | 1.41 | 1.41 / 56.11 | 12.26 | 9.18 | M2 |
| Pot_J_Piece_07 | K1 | 5.43 | 5.43 / 41.86 | 17.03 | 6.60 | M2 |
| Pot_D_Piece_23 | K3 | 4.12 | 4.12 / 66.43 | 9.70 | 10.67 | M4 |
| Pot_I_Piece_20 | K3 | 6.24 | 6.24 / 21.21 | 6.24 | 21.79 | M4 |
| Pot_J_Piece_02 | K3 | 6.91 | 6.91 / 8.30 | 8.34 | 10.95 | M4 |
| Pot_A_Piece_06 | K1 | 2.85 | 2.85 / 5.96 | 2.85 | 3.89 | M3 |
| Pot_E_Piece_14 | K1 | 3.35 | 8.51 / 31.10 | 8.51 | 9.38 | M3 |
| Pot_D_Piece_20 | K1 | 3.71 | 3.71 / 72.25 | 3.71 | 3.03 | M5 |
| Pot_D_Piece_27 | K1 | 3.94 | 3.94 / 53.18 | 9.08 | 5.58 | M5 |

**Tally: M2 x7, M4 x3, M3 x2, M5 x2; M1 x0.** No loss is a pool-coverage problem: every one has a line within 10° of GT in the raw 60-basin pool (best 1.41–7.71°), so the fail point is downstream of `_cluster_union`. The M2 group dies at the `refine_axis_normalized` + `15°` dedup + `[:8]` cut — for seven pieces the normalized refine *moves the true line away* (e.g. A07 7.71 -> 19.78, E31 6.59 -> 66.01, E26 1.41 -> 56.11) and it then loses the profile-cost sort. Non-loss rows that also trip a mode: `Pot_A_Piece_08` M2 (still 2.29°), `Pot_G_Piece_05`/`Pot_G_Piece_07` M2 (still < 5°); `Juglet_Piece_2` is M4 and ends at 15.73° (`Juglet_Piece_6` is the 4.71° one) — the Juglet is not part of the pot loss accounting.

### Stage B — offline probe, 141 GT pieces (+ Juglet separately)

The probe keeps the shipped structure by construction — `select.rank_by_profile(...)` -> `[:6]` -> `keep_lines(tau=1.2, kmax=3)` — and swaps only the ranking key (`(pc/min pc)^1 * (cn/min cn)^a_norm`, `cn = normalized_huber_cost` on the combined 6xN cloud) and an optional guarded LM (`cn` must not rise, `pc` may rise <= 10%). Control run reproduces the shipped axes335 exactly: **`mirror vs shipped: worst max_deg=0 over 150 pieces, k-mismatch=0`**.

| config | K1 | K3 | median deg | radial med mm | Pot A radial med mm | Pot_A_Piece_08 |
|---|---|---|---|---|---|---|
| shipped-mirror (control) | 109 | 121 | 3.06 | 11.88 | 8.11 | 2.29 |
| joint-rank | 108 | 120 | 3.10 | 11.88 | 8.11 | 2.29 |
| joint-both | 110 | 120 | 3.06 | 11.77 | 8.11 | 2.29 |
| joint-rank-lm | 108 | 120 | 3.10 | 11.88 | 8.11 | 2.29 |
| joint-both-lm | 110 | 120 | 3.06 | 11.77 | 8.11 | 2.29 |
| joint-both-lm-11 | 109 | 121 | 3.32 | 11.32 | 9.50 | 2.29 |

**On the 141 scored pieces the joint ranking is flat, and the named losses are not what it fixes.** `joint-both` is +1 K1 / -1 K3 at the same median angle with a marginally better radial median; the strongest config `joint-both-lm-11` lands on exactly the control's 109 / 121, with a worse median angle (3.06 -> 3.32°) and a worse Pot A radial (8.11 -> 9.50 mm). It recovers three of the 14 named losses — `Pot_A_Piece_07` (26.83 -> 6.66°), `Pot_A_Piece_06` (34.99 -> 3.89°), `Pot_E_Piece_14` (56.35 -> 9.38°) — and leaves the other eleven mixed: `Pot_D_Piece_20`, `Pot_E_Piece_25`, `Pot_E_Piece_29`, `Pot_E_Piece_31`, `Pot_F_Piece_05`, `Pot_J_Piece_02`, `Pot_J_Piece_07` sit at their shipped angles, while `Pot_D_Piece_23` (rank-0 10.67 -> 11.07°), `Pot_D_Piece_27` (23.17 -> 69.74°), `Pot_E_Piece_26` (10.08 -> 12.55°) and `Pot_I_Piece_20` (K3 21.79 -> 15.86°) move without clearing 10°. Those three gains are cancelled by four new K1 losses — `Pot_E_Piece_09` (2.91 -> 22.71°), `Pot_E_Piece_23` (2.00 -> 11.21°), `Pot_J_Piece_05` (2.83 -> 21.74°), `Pot_J_Piece_06` (1.72 -> 42.51°) — plus one gain outside the list, `Pot_H_Piece_11` (70.36 -> 1.90°); on K3 it gains `Pot_A_Piece_07` and loses `Pot_E_Piece_23`. Net zero. Two safeguards hold: `Pot_A_Piece_08` stays 2.29° in every config (no `c_norm`-only cone drift) and the `def_3x` Juglet sign guard passes **`pairs_gt_90 = 0/18`** over 9 pieces (graph `Dataset/Juglet_large/Juglet_simple_graph.txt`).

**Mechanism (the real finding).** For `Pot_A_Piece_07` the correct line is not merely out-ranked, it is **dominated on both costs**: winning profile cost `0.031897` vs true `0.047763` (x1.497) and winning `cnorm 0.006143` vs true `0.006652`. Re-weighting two costs that both prefer the wrong line cannot recover it; the cost landscape, not the mixing weight, is the gap. That is why re-weighting moves the same Pot A pieces while the E/I/J losses stay where they were.

**Rim coplanarity does not help on these 14:** **0/14** carry a breakline curve coplanar enough to constrain (best plane-normal vs GT 24.85–86.05° across all 14; A07 best 24.85°, D23 67.74°, E25 62.90°; planarity 0.029–0.317, radius spread 8.2–43.0 mm). The `SfS++ §IV-B2` rim term has no purchase here.

### Stage C — own `MeshPreprocessingHeadless` surfaces, all 141 GT pieces, 10 pots

Pot H had no `.S0`/`.S1` anywhere under `runs/`, so it was regenerated with the t305-lane recipe (`sbatch submit_poth.sbatch`, commit `9c5eec2`, shipped `MESH_ENV`, job `35409788`) into `<run>/out_poth/geom` (44 files = 11 x {.S0,.S1,.Bl0,.Bl1}); every other pot reuses the verified t305/t66 run dirs, each cited per piece in `gate01.tsv`.

| arm | K1 | K3 | median deg | radial med mm |
|---|---|---|---|---|
| axes335 on OUR surfaces | 113/141 | 118/141 | 3.13 | 10.25 |
| axes335 on Authors' surfaces | 109/141 | 121/141 | 3.06 | 11.88 |
| Authors' released `Axes/` | 105/141 | 116/141 | 2.78 | 11.64 |

Own surfaces are at parity, not behind: +4 K1 and the best radial median of the three, at -3 K3. **Switching surfaces introduces 3 regressions** — `Pot_F_Piece_04` (10.03 vs 9.12), `Pot_H_Piece_07` (25.55 vs 0.88, +24.68), `Pot_J_Piece_05` (24.81 vs 2.83, +21.98) — and **7 recoveries** — `Pot_E_Piece_26`, `Pot_E_Piece_29`, `Pot_F_Piece_05`, `Pot_H_Piece_08` (1.42 vs 25.09), `Pot_I_Piece_25` (1.84 vs 84.02), `Pot_I_Piece_27`, `Pot_J_Piece_11`. No pot is broken. Per-pot rows (own / authors'-surface / authors) are in `gate01.tsv` group `C`.

### Visual check — `render01_misses.png` (inspected before the `Reading:` line)

Six rows, each a 3D four-axis view plus the GT-frame `(r,z)` view where a correct axis is the vertical line at `r=0`; GT black, Authors blue, axes335 red, Stage B `joint-both-lm-11` rank-0 green.
- `Pot_A_Piece_07`: green is the only line that turns back towards vertical (6.7° / 36.1 mm) while red cuts 26.8° across the band and blue is 58.9° / 60.3 mm — but green is still 36 mm out in *position*.
- `Pot_A_Piece_06`: green essentially vertical (3.9° / 10.6 mm), red 35.0° — same pattern, direction recovered, position not.
- `Pot_E_Piece_29`, `Pot_I_Piece_20`, `Pot_J_Piece_02`, `Pot_J_Piece_07`: green lies exactly on red — the probe does not move them.
- The grey wall points sit far from every line in A06 (a band at r ≈ 25-50 mm while every axis sits near r = 0) and in E29 (top of the z range): both angle and placement are wrong there, so a direction-only fix cannot rescue them.

### Checks

- `python -m pytest C:/PR/worktrees/sfs/01/tests` -> **42 passed in 33.03s** (on the laptop; the Spartan `tora` env has no pytest).
- `git status --short` in the worktree: empty; the branch carries a single worker commit whose only changed file is this ticket.
- Deliverables fetched to `C:/PR/artifacts/axis-parity-01/`: `diag01_summary.json` (360,617 B), `gate01.tsv` (170 data rows, header `group\tpiece\tmetric\tvalue\treference\tverdict\tnote`, 7 columns on every line), `render01_misses.png` (1,206,235 B, 2,250x4,230), `render01_misses.json`, plus the run scripts under `work/`. The gate and summary were regenerated by `35410257` (adds the Authors'-released rows to gate group `C`) and then `35410291` (adds the superseded job ids to `jobs.sacct`); the final file's `jobs.sacct` lists 17 ids up to and including `35410257` — an assemble run cannot list its own id.

**What this means for Ticket 02:** the fail point is inside the shipped ranking/refinement, not the pool (M1 = 0) and not the rim. Joint normal+profile re-weighting recovers three of the 14 but loses four other K1 pieces (net zero) and hurts Pot A radial precision, so it is not the prototype to carry forward as-is; the A07 evidence says t02 should change the cost landscape (what makes the wrong line cheaper than the right one) rather than re-weight the two existing terms.

**Note on the `Reading:` line below (honest reading of its precondition).** Of the three allowed readings only `normal-profile-gap-isolated-ready-for-t02` describes what Stage A/B established: every loss is a downstream ranking/refinement failure (M1 = 0) and the A07 double-domination evidence isolates the mechanism. Its *improvement* clause is **not** met — on the 141 scored pieces the best joint config is flat at 109 / 121 with a worse Pot A radial (8.11 -> 9.50 mm) — so Ticket 02 should be scoped to changing the cost landscape, not to carrying this ranking forward. `own-surfaces-differ-upstream-first` is contradicted by Stage C (own surfaces are at parity: 113 / 118 vs 109 / 121, 3 regressions / 7 recoveries, no pot broken) and no required input is missing, so `blocked: missing-input` would be false.

Reading: normal-profile-gap-isolated-ready-for-t02

**End state:** done

### Lead verification (2026-11-20)

- `verified:` `python C:/PR/artifacts/dsh-handover/axis-parity-01/accept.py` -> `ACCEPTANCE PASSED` (0 errors: worktree touches ticket file only, `pytest` 42/42, JSON/TSV/PNG deliverables valid, zero unchecked boxes, bare `Reading:` present).
- `verified:` `ssh spartan` `sacct -X` -> `35409752`, `35409788`, `35409950`, `35409951`, `35410066`, `35410187`, `35410190`, `35410257`, `35410291` all `COMPLETED 0:0`; `out_poth/geom` contains 44 files; `CORPUS-UNCHANGED: yes (2103 files)` in `t01-cache_35409752.out` and `t01-own_35409951.out`; `runs/index.tsv` rows appended.
- `verified:` `C:/PR/artifacts/axis-parity-01/diag01_summary.json` -> Stage A `loss_modes` `{'M2': 7, 'M4': 3, 'M3': 2, 'M5': 2}` (`M1=0`; `Pot_A_Piece_07` double-dominated: winning profile cost `0.031897` vs true `0.047763`, winning `cnorm` `0.006143` vs `0.006652`), Stage B `joint-both-lm-11` flat at `109/141` `K1` and `121/141` `K3` (`Pot_A_Piece_08 = 2.293°`, Juglet `sign_guard pairs_gt_90 = 0/18`), Stage C own surfaces `113/141` `K1` / `118/141` `K3` (med `3.135° / 10.251 mm`) vs `109/141` `K1` / `121/141` `K3` (`3.064° / 11.881 mm`) on Authors' surfaces and `105/141` `K1` / `116/141` `K3` (`2.777° / 11.638 mm`) Authors' released `Axes/` (`3` regressions vs `7` recoveries, no pot broken).
- `verified:` visual inspection of `C:/PR/artifacts/axis-parity-01/render01_misses.png` -> confirms green (`joint-both-lm-11`) tilts toward GT only on `Pot_A_Piece_07` (`6.7° / 36.1 mm` radial error remains) and `Pot_A_Piece_06` (`3.9° / 10.6 mm`) while lying coincident on red (`axes335`) in `Pot_E_Piece_29`, `Pot_I_Piece_20`, `Pot_J_Piece_02`, and `Pot_J_Piece_07`; Stage B's negative result on joint `(pc, cn)` re-weighting establishes that Ticket 02 must change the axis-cost landscape itself rather than tuning weights.


