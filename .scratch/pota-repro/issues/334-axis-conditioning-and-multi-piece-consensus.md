# 334: Axis conditioning and multi-piece consensus — replace the single-sherd ceiling on spherical sherds

**What to build:** a **diagnostic and offline prototype measurement** (no production edit to `sfs_axes/` or `structure-from-sherds-pp/class/`) that tests the two concrete mechanisms left open by tickets 332, 333, and the SfS++ paper re-check (`§IV-B2` / `§IV-C2`):

1. **Single-sherd hygiene + conditioning (Stage A–B):** how far does fixing only the mechanical defects already found in `sfs_axes/` — **5° bounded polish + start+refined ordering** (ticket 333 `job 35240144`) and **protecting raw uncollapsed basins** from `refine_axis_normalized` / `[:8]` starvation — take **3× Juglet** and the **172-piece corpus**; and does a dimensionless conditioning metric (Pottmann `s2/s3`, normalised-residual Hessian conditioning) cleanly separate well-anchored sherds (`p1`, `p7`, Pots A–J) from spherical-belly sherds (`p2, p3, p8, p9`)?
2. **Multi-piece joint axis consensus (Stage C):** when 2–3 joined sherds are pooled in a common frame (the mechanism the paper’s own assembler invokes in `GraphAxisRefinement`, `ranking_system.cpp:2554`, tested here with **scale-free** `sfs_axes` rather than raw-mm Cao error), does pooling break the `11.9°`/`28.4°`/`89°` spherical attractors and recover the vessel axis within `≤ 5°` across **all nine** Juglet pieces with **no Juglet-specific constants**?

**Answers:** E1
**Blocked by:** None (can start immediately). Tickets 332 (`3c4b118`) and 333 (`4a3b400`) closed the single-sherd `(r, z)` thinness route; `sfs_axes/` on `main` is unchanged.
**Status:** resolved
**Branch:** 334-axis-conditioning-and-multi-piece-consensus, in /c/PR/worktrees/sfs/334 (merged, ace8edd)
**Worker:** dsh one-shot subagent w334
**Budget:** medium 5
**Hand-over:** DeepSeek — Spartan compute node (read-only over frozen corpora and existing `runs/`). Check path: the lead re-reads `artifacts/t334/gate334.tsv` (Stages A–C), verifies the 172-pot rank-0 / best-of-3 comparison against `axes323`, verifies the multi-piece Juglet table against `Dataset/Juglet_GT`, and **looks at** `artifacts/t334/render334_multi.png` before recording any verdict. No `sfs_axes/` or `class/` source edit ships from this ticket.

## Given (verified in 322, 332, 333 and the paper check — do not re-derive as if new)

- **Shipped baseline (`axes323`):**
  - 10 pots (163 corpus pieces): **135/163** rank-0, **146/163** best-of-3 within 10° (ticket 322), holding **20/20** pot assembly runs at/above floor (ticket 324).
  - Juglet 1× geom: **6/9** rank-0 (`p2 13.16, p3 28.39, p7 47.92` deg), **7/9** best-of-3 (`p7` line 2 is `2.56°`).
  - Juglet 1× corpus cloud: **7/9** rank-0 (`p7 13.61, p9 12.25` deg).
  - Juglet 3× cloud (`runs/20261112-0218_b1e1580_t331-large/cloud_mesh`): **7/9** rank-0, **8/9** best-of-3 (`p3 10.11°` with line 2 at `6.06°`; `p9 29.81°`, whose `2.35°` pool line sits at pre-refine rank **100/120**).
- **Single-sherd `(r, z)` thinness & local curvature hit a physical ceiling (ticket 333):**
  - `profile_band` broke the pots (`0/163` byte-identical, rank-0 median delta `39.99°`, corpus `137/172 → 33/172`) because `p90(r) - p10(r)` in `z`-slabs measures meridian slope `|dr/dz| · Δz_slab`, not perpendicular wall thickness.
  - Across **25 single-sherd statistics**, none put a `<= 10°` line in the top 8 on all nine Juglet pieces; on **9/9** pieces `cost(key) > cost(delivered)` by `+0.022 to +0.435 mm`.
  - **Root geometry:** Juglet is a small handmade globular vessel (`diag = 23–63 mm`, `r ≈ 14.5–18 mm`, median Pottmann `s2/s3 = 1.9` vs `2.9–11.8` on Pots A–J). Short belly belts (`p2` `Δz ≈ 8 mm`, `p3` `Δz ≈ 13 mm`) are near-spherical; an `11.9°` tilt around the belly curvature centre moves `(r, z)` by well under `1 mm` and local shape-operator shear `S_uv` vanishes near umbilics (`κ_1 ≈ κ_2`). Only `p1` (rim/neck) and `p7` (base) are non-spherical anchors.
- **Unshipped partial rescue from 333 (`job 35240144`):**
  - Using shipped `w24` + **5° bounded Nelder–Mead polish** (`Bar 5`: 9/9 key drift ≤ 5.00°) + **start+refined ordering** ("never promote a refined line above a better start") lifted 1× Juglet to **7/9** (`0.98, 13.16, 28.39, 5.49, 3.72, 1.86, 2.56, 3.59, 4.56` deg — fixing `p7` `47.92° → 2.56°`, keeping `p8` `3.59°`). Its behaviour on **3× Juglet** and the **172 pots** was never measured.
- **Paper check (`SfS++ §IV-B2`, `§IV-C2`):**
  - Single-sherd Modified PotSAC has a centroid lever-arm bias on small sherds (ticket 312: `6/10` failing Pot E pieces slide monotonically into centroid decoys; authors’ own `Axes/` are `105/141 = 74.5% ≤ 10°` and `27/141 = 19.1% ≥ 25°`).
  - Inside the C++ assembler, `GraphAxisRefinement` (`structure-from-sherds-pp/class/ranking_system.cpp:2554-2598`) calls multi-sherd `RefineAxis(geom_ptr, ...)` (`axis_estimation.cpp:259-321`) across all joined sherds in a graph — **but** uses unnormalised `BiaxialCaoError`, and `feature_matching.cpp` still depends on each single sherd’s input axis before sherds connect.

## Stages

**Run all heavy work on a Spartan compute node in a fresh run dir `runs/<YYYYMMDD-HHMM>_<git7>_t334-axis/`.** Copy `sfs_axes/` into the run dir’s `work/` for prototype variants; do **not** modify tracked `sfs_axes/` on `main`. Record every job ID and final `sacct` State/ExitCode.

### A — Measure the unshipped `w24` polish + raw-basin protection (1×, 3×, and 172 pots)
Compare three variants against shipped `axes323` (`main`):
- **A0 (control):** unchanged `main` (`axes323` path), confirming baseline reproduction on Juglet 1× geom (`6/9`), 3× (`7/9` rank-0, `8/9` best-of-3), and 172 pots (`172/172` byte-identical to `runs/20261110-0740_d628fc0_t323-axes/out/axes323`).
- **A1 (`w24` + 5° bounded polish + start+refined ordering):** the `job 35240144` recipe (`PROFILE_TILT_DEG=5.0`, `PROFILE_SHIFT=0.5`, rank by `max(start_cost, refined_cost)` or no-promote-above-better-start). Measure Juglet 1× geom, Juglet 3× cloud, and all 172 pots (rank-0 and best-of-3 within 10°, plus `cmp` / per-pot delta vs `axes323`, specifically checking Pot A Piece 08 and Pot E).
- **A2 (A1 + uncollapsed raw-basin shortlist):** prevent `refine_axis_normalized` collapse from crowding out distinct raw Pottmann basins before `w24` sees them (e.g., shortlist top `refine_k` distinct raw basins *and* top `refine_k` refined basins separately, or raise `PROFILE_REFINE_K` to `16` / `24` with 15° dedup before polishing). Measure whether **3× Juglet** recovers `p9`’s rank-100 (`2.35°`) basin to reach **8/9 or 9/9** (rank-0 and best-of-3) and whether the 172-pot rank-0 / best-of-3 table holds `>= 135/163` and `>= 146/163`.

### B — Per-piece conditioning audit (all 172 pieces: 163 pots + 9 Juglet)
Without reading any ground truth inside the metric, compute for every piece (1× geom and 3× Juglet, plus 163 pots):
1. **Pottmann conditioning:** singular-value ratio `s2 / s3` (`s[-2] / s[-1]` of reduced $3\times 3$ matrix `M` in `sfs_axes/pottmann.py` on the whole piece cloud).
2. **Normalised-residual Hessian conditioning:** singular-value ratio (and smallest singular value) of the $4\times 4$ tangent-space Jacobian of `compute_normalized_residual` at the rank-0 axis.
3. **Basin ambiguity:** cost ratio `cost(second_distinct_basin) / cost(best_basin)` and number of distinct `15°` basins within `1.2x` of the minimum under A1/A2.

Report the per-piece table for Juglet 1–9 and summary percentiles (plus worst-10 pieces) for Pots A–J. Answer: **does conditioning cleanly flag `p2, p3, p8, p9` (and ill-conditioned pot sherds) while marking `p1`, `p7`, and well-curved pot sherds as anchored?**

### C — Multi-piece joint axis consensus (the physical test)
Test on:
- **All 9 Juglet touching pairs** (`1-2, 1-4, 1-8, 1-9, 2-5, 2-9, 3-5, 6-7, 7-9`), on both 1× geom walls and 3× clouds (`t331` `cloud_mesh`),
- **4 representative 3-sherd chains** (`1-2-5`, `1-4-8`, `6-7-9`, `2-5-3`),
- **4 Pot controls** (e.g. Pot A `02-08`, `04-08`, and Pot E `24-25`, `26-27`, using their GT transforms).

For each pair/cluster, transform the pieces’ `(X_i, n_i)` into the cluster frame using (i) **exact GT transforms** (testing the axis estimator given a true join) and (ii) **perturbed poses** (`+3°` rotation / `+1 mm` real-scale translation noise, testing robustness to ICP join error), then evaluate three joint axis estimators:
1. **Pooled `sfs_axes` (A1):** run `run_potsac_union` (`w24` + 5° bounded polish) on the concatenated walls of the cluster.
2. **Conditioning-seeded joint refine:** seed from the higher-`s2/s3` piece’s rank-0 axis, then run `refine_axis_normalized` + 5° bounded `w24` polish on the pooled cluster walls.
3. **Unnormalised `BiaxialCaoError` (paper `GraphAxisRefinement` equivalent):** seed from the higher-`s2/s3` piece (and from `(0,0,1)` in the aligned anchor frame, as `ranking_system.cpp:2571-2576` does) and refine on the pooled walls, to check whether raw-mm Cao error still drifts on 1×/3× Juglet clusters.

Report rank-0 direction error (deg) and centroid offset (mm) vs `Dataset/Juglet_GT` for every pair, chain, and Pot control, and report how many of the 9 Juglet pieces lie within **≤ 5°** and **≤ 10°** once joined into a 2-sherd or 3-sherd cluster.

### D — Report and look
- `artifacts/t334/gate334.tsv` — columns `group piece metric value reference verdict note` covering Stages A, B, and C.
- `artifacts/t334/render334_multi.png` — for Juglet `p2`, `p3`, `p9`, and Pot E `27`: show the single-sherd rank-0 axis, the 2-sherd joint axis, and the GT key drawn on the paired sherd clouds in the vessel frame. **Look at it before writing the Reading**, and state in one sentence what the eye adds beyond the numbers.

## Readings (pick one, verbatim, on a `Reading:` line)

- `multi-piece-resolves-spherical-axis` — single-sherd conditioning flags the spherical sherds, and 2–3 sherd pooling brings all 9 Juglet pieces within 10° (most ≤ 5°) while holding Pot controls: next ticket wires conditioning + cluster axis refinement into the pipeline.
- `raw-shortlist-fixes-3x-alone` — Stage A’s bounded polish + uncollapsed shortlist already hits 9/9 within 10° on 3× Juglet without breaking the 172 pots: ship the `sfs_axes/` fix first.
- `conditioning-and-pairing-still-short` — even 2–3 joined sherds fail to break the attractor on named pairs; report which pairs and why.
- `blocked: missing-input` — named missing surface, transform, or run input.

## Out of scope

- Editing shipped `sfs_axes/` on `main`, `structure-from-sherds-pp/class/`, `AxisExtraction/*.m`, or `Dataset/`.
- Running full end-to-end assembly jobs (`structure-from-sherds-pp` binary).
- Inventing a 26th single-sherd `(r, z)` thickness/curvature cost (closed by ticket 333) or adding any Juglet-specific constant.

## Acceptance

- [ ] Stage A: A0 reproduces `axes323` (`172/172` `cmp`); A1 and A2 tables reported for 1× Juglet, 3× Juglet, and all 172 pots (rank-0 and best-of-3 within 10°, plus pot delta vs `axes323`).
- [ ] Stage B: conditioning table (`s2/s3`, normalised Hessian ratio, basin spread) for all 9 Juglet pieces and 163-pot summary.
- [ ] Stage C: all 9 Juglet touching pairs, 4 chains, and 4 Pot controls scored under exact and perturbed (`3° / 1 mm`) poses for estimators 1–3.
- [ ] Stage D: `artifacts/t334/gate334.tsv` and `artifacts/t334/render334_multi.png` (looked at before the Reading line).
- [ ] All Slurm job IDs, `sacct` State/ExitCode, and run dir path recorded; working tree on `main` clean of code edits.

## Comments (worker, 2026-11-17) - w334

Run directory: `/data/gpfs/projects/punim2657/SfSpp/runs/20261117-1650_2b19818_t334-axis` (`run.json` with every job id and state, `submitA.sbatch`, `submitB*.sbatch`, `submitC*.sbatch`, `out/`, `logs/`, `work/`). Branch `334-axis-conditioning-and-multi-piece-consensus`, commit `2b19818`. One row appended to `runs/index.tsv` (its jobid column carries `35261784`, the A0 job; the full list lives in `run.json`). Nothing committed, nothing pushed; the only file this worker changed in the worktree is this ticket.

All code variants live in the run dir: `work/a0` (pristine copy of `sfs_axes/` at 2b19818 + `scripts/run_benchmark_172.py`), `work/a1` (`+ work/patch334.py` and `work/patch_nopromote.py`), `work/score_key.py`, `work/potscore.py`, `work/bdrive.py`, `work/cluster334.py`, `work/condB.py`, `work/ambA.py`, `work/export_render.py`. Nothing under `sfs_axes/`, `class/`, `AxisExtraction/`, `Dataset/` was touched.

### Stage A - does the bounded polish ship?

A0 is the shipped tree and reproduces `axes323`: after staging, `cmp` says 172/172 identical (181 files including the nine `Pot_JUGLET_*` alias files the driver also writes). The patched tree with every switch unset is also byte-identical on all 172 (job 35262399, `out/logB3_jug.txt` first stage: `identity_gate same=181 diff=0`) - so A1 and A2 differ from shipped only where a switch is on.

A1 = shipped `w24` profile cost + 5-deg bounded tilt polish + "never promote a refined line above a better start". A2 = A1 + uncollapsed raw-basin shortlist (top `PROFILE_REFINE_K` distinct raw basins and top `PROFILE_REFINE_K` distinct refined basins, deduped at 15 deg). Rank-0 within 10 deg:

| arm | Juglet 1x geom | Juglet 3x cloud | corpus 141 scorable | corpus best-3 |
|-----|----------------|-----------------|---------------------|----------------|
| A0 shipped | 6/9 | 7/9 | 121/141 | 129/141 |
| A1 | **7/9** | **3/9** | **106/141** | 117/141 |
| A2 | 5/9 | 5/9 | 75/141 | 99/141 |

A1 1x per piece, deg: p1 0.978, p2 8.477, p3 29.519, p4 5.707, p5 3.709, p6 4.274, p7 2.557, p8 11.884, p9 8.230. A1 3x per piece: 0.883, 11.174, 16.468, 8.438, 5.909, 11.987, 15.348, 10.079, 37.697. A2 1x: 1.930, 10.543, 29.519, 5.707, 15.569, 9.185, 2.557, 11.884, 8.230. Score files `out/scoreA0_1x.tsv`, `out/scoreA1_1x.tsv`, `out/scoreA2_1x.tsv`, `out/scoreA0_3x.tsv`, `out/scoreA1_3x.tsv`, `out/scoreA2_3x.tsv`, `out/scoreA0_pots.tsv`, `out/scoreA1_pots.tsv`, `out/scoreA2_pots.tsv`.

What the numbers say, in order of weight:

1. **A1 buys one piece and costs the 3x lane.** On 1x it turns p7 47.92 -> 2.56 (that line exists at A0 rank 1, so the polish plus the no-promote ordering lifts a *correct* line to rank 0). On 3x it turns p7 2.06 -> 15.35 and p9 29.81 -> 37.70, where A0 was already 7/9 rank-0 and 8/9 best-3. A1 is a 1x-only improvement: it is not a shippable change.
2. **The shift bound is inert.** A1 with the shift cap at 1.0 instead of 0.5 gives scores identical to six decimals (job 35264041, tag `A1s1`), so only the tilt cap changes anything. Under a 5-deg cap a refinement can only lower a candidate's cost, so "rank by max(start, refined)" leaves the start-cost ordering intact - the bounded polish improves the returned *direction* for the winner, not the *ranking*. That is why the no-promote patch, once implemented, changed nothing.
3. **A2 admits the right lines and still cannot rank them.** On 3x, p3's 8.22-deg and p8's 5.29-deg lines are both in the shortlist and both at rank 1; on 1x A2 is *worse* than A1 because the extra candidates break p5 (3.709 -> 15.569). The uncollapsed shortlist does not fix the 3x lane on its own.
4. **Neither arm holds the corpus.** A1 costs 15 of the 141 scorable corpus pieces (rank-0 121 -> 106, mean error 5.59 -> 8.40 deg); A2 costs 46 (to 75/141, mean 18.68, worst Pot_D_Piece_19 89.1 deg). Holds-vs-breaks is decided here and the answer is "breaks".

Two measurement scopes that must travel with these rows:

- **141, not 163.** `work/potscore.py` uses the shipped reference rule (`ref_err = min(err to Ground Truth Axes, err to the released Axes file)`). Only 141 of the 163 corpus pieces carry *both* files, so the pot tallies above are /141 and comparable arm-to-arm only. The driver's own pot table (`out/logA0_172.txt`) counts all 172 and reports Total 137/172 rank-0, 146/172 best-3 - which is 135/163 and 143/163 on the corpus, i.e. **this ticket's "146/163 best-of-3" premise is 3 high**; 146 is the 172-piece total and it includes the nine Juglet stems.

- **The ticket's A1 1x set is not reproducible.** The ticket quotes "7/9: 0.98, 13.16, 28.39, 5.49, 3.72, 1.86, 2.56, 3.59, 4.56". A1 as specified gives 0.978, 8.477, 29.519, 5.707, 3.709, 4.274, 2.557, 11.884, 8.230. Four of the quoted values are A0's rank-0 results (p2 13.164, p3 28.390, p6 1.845, p9 4.564) and p7 2.557 is A0's rank-1 value, so the quoted set looks like A0 with p7's rank-1 substituted. I also tested 333's own `impl2` tree as-is and A1 with shift 1.0 (job 35264041, tag `X333`): 5/9 with 1.52 11.59 10.92 9.06 7.00 2.01 21.04 19.22 4.50 - closer to nothing in particular. Ticket premise wrong on this point; the Stage A1 rows above are what the recipe actually does.

### Stage B - does a dimensionless conditioning number separate?

Per piece, from `out/b_A1_J1X.jsonl` (`work/condB.py`): `s2/s3` is the Pottmann 3x3 M's second-over-third singular value on the whole piece cloud; `cond4` is the ratio of largest to smallest singular value of the 4x4 tangent-space Jacobian of `compute_normalized_residual` at the rank-0 axis; the percentile is the piece's rank among the 163 corpus pieces.

| piece | s2/s3 | corpus pct | cond4 | delivered K | single-sherd status |
|-------|-------|-----------|-------|-------------|---------------------|
| p1 | 6.342 | 63.2 | 3.22e8 | 1 | rank-0 0.98 (ok) |
| p2 | 1.404 | 3.1 | 1.78e10 | 1 | 1x 8.48, 3x 11.17 (miss) |
| p3 | 1.529 | 4.3 | 1.03e10 | 1 | 1x 29.52, 3x 16.47 (miss) |
| p4 | 1.934 | 9.2 | 5.46e9 | 2 | ok |
| p5 | 1.621 | 5.5 | 1.06e10 | 1 | ok |
| p6 | 1.634 | 6.1 | 1.36e9 | 1 | ok |
| p7 | 3.029 | 25.8 | 5.21e8 | 1 | 1x 2.56 (ok) |
| p8 | 1.913 | 8.6 | 2.83e9 | 2 | 1x 11.88 (miss) |
| p9 | 3.630 | 33.7 | 5.60e7 | 1 | 3x 29.81 (miss) |

Corpus percentiles: `s2/s3` p5 1.583, p25 3.005, median 4.693, p75 8.859, p95 21.720; `cond4` p5 2.74e4, p25 5.15e6, median 4.68e7, p75 3.44e8, p95 3.72e9. Worst pot `cond4`: Pot_D_Piece_27 2.25e10, Pot_F_Piece_07 1.17e10, Pot_G_Piece_06 1.15e10; best Pot_J_Piece_02 2198.

Answer: **no clean separation.** `s2/s3` flags p2, p3 and p8 (all below the corpus 10th percentile) but puts **p9 at the 34th percentile**, comfortably inside the corpus normal range - and p9 is the piece that misses by 29.8 deg on the 3x lane. `cond4` flags p2, p3, p8 and also p4, p5, p6, which are all solved at rank 0 (five of nine pieces above the corpus p75). So the metric marks "thin wall" and "few walls", not "this axis is wrong". The one thing it does track is that p1 and p7, the two most strongly curved sherds, sit high (`s2/s3` 6.34 and 3.03): high conditioning is a necessary but not sufficient sign of an anchored line.

Basin ambiguity (metric 3) is **not measured**. The `SFS_AXES_T334_DUMP` hook inserted into the patched `select.py` did not fire in any of 181 subprocesses (env var visible in the child, `select.__file__` the patched file, `_dump_basins` present in the file text, `__pycache__` cleared, `PYTHONDONTWRITEBYTECODE=1`); the cause is unresolved and this is declared, not dropped. The restricted substitute (job 35267666, `work/ambA.py`) re-costs the *delivered* shortlist with `sfs_axes.profile.profile_cost`: K=1 for seven of nine pieces (p1 0.2089, p2 0.1390, p3 0.1578, p5 0.2559, p6 0.3361, p7 0.1713, p9 0.1005), K=2 for p4 (second/best 0.847) and p8 (1.011). So the line rule returns a single line precisely on the pieces that are wrong, and nothing downstream can see the ambiguity.

### Stage C - does pooling joined sherds recover the axis?

Estimator 1 (pooled A1 `run_potsac_union` on the concatenated walls), exact GT poses, 1x geom walls, rank-0 direction error and line-to-line offset against the vessel key mapped into the cluster frame:

| cluster | deg | offset mm | cluster | deg | offset mm |
|---------|-----|-----------|---------|-----|-----------|
| 1-2 | 1.03 | 0.053 | 2-9 | 18.32 | 0.820 |
| 1-4 | 1.34 | 0.011 | 3-5 | 1.16 | 0.312 |
| 1-8 | 0.85 | 0.086 | 6-7 | 1.21 | 0.550 |
| 1-9 | 0.92 | 0.048 | 7-9 | 4.67 | 0.756 |
| 2-5 | 0.83 | 0.296 | | | |

Chains: 1-2-5 0.71 deg / 0.033 mm, 1-4-8 1.15 / 0.097, 2-5-3 0.98 / 0.230, 6-7-9 1.60 / 0.264. So **8 of 9 pairs and 4 of 4 chains land within 5 deg**, and the one exception is not a pooling failure: on 2-9 estimator 2 (seeded from the higher-`s2/s3` piece, `refine_axis_normalized` + 5-deg polish) lands at **0.98 deg**, while unnormalised Cao seeded from the same piece stays at 36.78 deg. The attractor that beat the single-sherd line is beaten by the cluster; what the unnormalised cost does on a 33 mm vessel is drift.

Per-piece best exact joint: p1 0.71 (1-2-5), p2 0.71 (1-2-5), p3 0.98 (2-5-3), p4 0.98 (1-4-8), p5 0.71, p6 0.63 (6-7), p7 0.63 (6-7), p8 0.85 (1-8), p9 0.92 (1-9) - **9/9 within 5 deg, 9/9 within 10 deg**. The four spherical sherds (p2 8.5, p3 29.5, p8 11.9, p9 8.2 on their own) sit at 0.71-0.98 deg once joined.

Perturbed poses (+3 deg rotation, +1 mm translation on every non-seed piece): pairs 0.92, 0.62, 1.14, 2.51, 19.79 (2-9), 0.93, 1.97, 8.80 (7-9), 0.96 -> 8/9 within 5 deg, 8/9 within 10; chains 1.82, 3.17, 1.14, 2.64 -> 4/4 within 5. Pooling survives a 3-degree join error on eight of nine pairs.

Pot controls (exact pose, `out/cluster_pot.tsv`): Pot_A_02-08 2.28 deg / 0.349 mm pooled (seeded_polished 2.68, Cao-from-z 2.63, Cao-from-piece 85.27); Pot_A_04-08 1.35 / 1.668 (seeded_polished 1.45, Cao-from-z 2.75, Cao-from-piece 38.84). **Pot E 24-25 (12.29 / 0.895) is a weak control** - the two pieces already touch at 1.46 mm under the identity pose, so its T is nearly the identity and the pair carries little pose information. **Pot E 26-27 is not a control at all**: under the GT transforms the two pieces sit 107.76 mm apart, so its 3.88-deg pooled row cannot be read as a method result either way. Convention note that cost me one void table: corpus pot GT axes are the vessel +z expressed in each *piece's* frame, and mapping each by its piece T gives (0.000 -0.000 1.000) on all four Pot E and three Pot A pieces I checked - zero disagreement.

### Stage C (continued) - the 3x cloud lane, recorded

Two jobs, two densities, all three estimators. Density is quoted with every number below because it moves the answer at the 5-deg bar.

**Recorded lane: `out/cluster_c3m.tsv`, job 35270887 (sacct COMPLETED 0:0, 01:04:38), `submitC3m.sbatch`, 8 workers, `SFS_T334_CAP=200000` per wall - pooled n 840 866-841 216 points per pair, ~1.26M per chain.** Each wall was strided to 200k points, i.e. 4x thinned from the 3x clouds; that thinning is the denominator this lane rests on.

Pairs, pooled rank-0 direction error, exact / perturbed pose (deg): 1-2 1.23/0.80, 1-4 1.64/1.11, 1-8 1.05/2.07, 1-9 0.94/1.06, 2-5 2.51/3.26, 2-9 14.19/16.15, 3-5 12.12/13.90, 6-7 0.47/0.31, 7-9 15.28/17.50 -> **6 of 9 pairs within 5 deg on both poses**, and 6 of 9 within 10 (3-5, 2-9, 7-9 stay out).
Chains: 1-2-5 1.10/3.79, 1-4-8 2.12/2.47, 6-7-9 6.39/8.51, 2-5-3 5.14/7.03 -> 2 of 4 within 5 deg pooled, 3 of 4 once estimator 3 is allowed on 2-5-3 (Cao seeded from the anchor piece: 1.72 exact / 1.22 perturbed).
Estimators 2 and 3 on the pooled misses: estimator 2 `seeded_normalized` recovers 3-5 to **0.98 / 0.98 deg** (`seeded_polished` 4.72 / 4.74) and recovers neither 2-9 (18.90 / 20.89) nor 7-9 (34.42 / 33.12); Cao is worse on both (74.29 / 74.66 and 54.64 / 52.77).
Per-piece best, any cluster and any estimator: p1 0.74, p2 0.74, p3 0.98, p4 1.11, p5 0.74, p6 0.31, p7 0.31, p8 1.05, p9 0.94 -> **9 of 9 within 5 deg**. That is a per-piece ceiling selected across 13 clusters and 3 estimators, not the result of one estimator.

**Full density: job 35268428 (sacct TIMEOUT 0:0, 04:00:10, killed at its 4 h wall), `submitC3f.sbatch`, no cap, pooled n 3 362 950-3 364 858 per pair and 5 046 404 per chain.** It flushed **122 of ~132 rows and wrote no `cluster_c3f.tsv`; chain 2-5-3 was never reached and 6-7-9 exists only in the exact pose.** Rows read from `out/logC_c3f.txt`.

Pairs, pooled exact / perturbed: 1-2 1.18/0.84, 1-4 1.62/0.91, 1-8 0.72/2.81, 1-9 0.92/1.06, 2-5 5.19/7.30, 2-9 7.18/9.17, 3-5 12.95/14.72, 6-7 0.24/0.98, 7-9 13.88/16.38 -> **5 of 9 within 5 deg on both poses**, 7 of 9 exact within 10 (3-5 12.95 and 7-9 13.88 out). Chains reached: 1-2-5 0.95/4.09, 1-4-8 3.26/1.32, 6-7-9 6.15 (exact only). Estimator 2 here: 3-5 0.98/0.98 again, 2-9 18.93/76.52, 7-9 34.47/33.17, 2-5 17.52/15.96. Per-piece best: p1 0.72, p2 0.83, p3 0.98, p4 0.91, p5 0.95, p6 0.24, p7 0.24, p8 0.72, p9 0.92 -> 9 of 9 within 5 deg.

**What the two densities agree on, and what they do not.** 3-5 and 7-9 are wrong by 12-17 deg at every density and under every estimator, so those two are a property of the pooled geometry, not of sampling. 2-9 moves the other way (14.19 at 840k, 7.18 at 3.36M) and 2-5 moves against density (2.51 at 840k, 5.19 at 3.36M), so 2-5 straddles the 5-deg bar and 2-9 the 10-deg bar. The 60k-per-piece run (job 35267705, `out/cluster_c3q.tsv`) gave 1.17 1.66 0.86 1.08 4.56 14.71 12.75 5.54 14.83, i.e. 5 of 9 within 5. **Nothing on this lane is stable to the degree at which the 1x lane is stable**, and the full-density comparison is missing two chain poses (2-5-3 both, 6-7-9 perturbed) because that job hit its wall.

### Stage D - artifacts

- `C:/PR/artifacts/t334/gate334.tsv` - 89 data rows, header exactly `group piece metric value reference verdict note`, groups A, A2, B, C, C3, artifact. The C3 rows carry both 3x densities separately (`pair_*` at 200k/wall, `fd_pair_*` at full density) plus three density-sensitivity rows, so the lane's denominator is in the file, not only in this text. Every verdict in it recomputes from the score files above.
- `C:/PR/artifacts/t334/render334_multi.png` - 1725x1920, four rows (p2 on 1-2, p3 on 2-5-3, p9 on 1-9, Pot E 27 on 26-27), each piece's cloud mapped into the world frame by its T, the key as a black line, the single-sherd rank-0 line red dashed, the pooled joint line green, the seeded+polished joint line blue dash-dot. Titles compute their own angles: p2 single 8.3 / joint 1.1, p3 29.6 / 1.3, p9 8.1 / 1.0, Pot E 27 37.8 / 48.2 deg. Data from `out/render334.npz` (job 35267284), built by `work/export_render.py` and `C:/PR/artifacts/t334/render334.py`.

**What the eye adds, in one sentence:** the joint line lies *inside* the wall band of both sherds while the single-sherd line runs across the band at an angle and, on p2, sits ~48 mm above the pottery in the v panel - so the angle is visible as a line that stays in the clay, not as a number. The Pot E 27 panel is the counter-example and reads as what it is: two clouds whose GT key crosses them at a large angle, the unusable pose showing up as geometry before it shows up as degrees.

### Defects I introduced, owned

1. The first "A1 identity gate" (job 35261784) is vacuous: `submitA.sbatch` exported `PYTHONPATH=$S/work/a0` for every stage and never re-exported it, so the gate compared pristine code with itself. The gate that counts is job 35262399 (patched tree, all switches off, `same=181 diff=0`). Nothing from job 35261784's A1 lane is quoted above except the A0 control, which is unaffected.
2. My first Stage C pot table was void because `key_world("POTS", ...)` returned the piece-frame GT direction without applying the piece T; corrected in job 35266929.
3. My first Stage C submit (jobs 35264640/35264641) died in 4 s on sbatch assembly (`TAG` concatenated onto a `cd` line), the second (35264851/35264852) died on a tuple-vs-array bug in the perturbed branch, and the third's 3x half produced no rows and was cancelled. Each is fixed in `work/cluster334.py`; the surviving rows are the ones quoted.

### Jobs (sacct -X)

| job | name | State | ExitCode | elapsed |
|-----|------|-------|----------|---------|
| 35261783 | t334P | COMPLETED | 0:0 | 12 s (pose gate v1, wrong convention) |
| 35261784 | t334A | COMPLETED | 0:0 | 21:53 (A0 + vacuous gate) |
| 35262004 | t334P2 | COMPLETED | 0:0 | 24 s |
| 35262111 | t334P3 | COMPLETED | 0:0 | 34 s |
| 35262173 | t334P4 | COMPLETED | 0:0 | 4:12 |
| 35262399 | t334B | COMPLETED | 0:0 | 23:53 (real identity gate 172/172) |
| 35262400 | t334B2 | CANCELLED by 18130 | 0:0 | 24:37 (xcheck, 163/163 shown) |
| 35263681 | t334B3 | COMPLETED | 0:0 | 6:03 (A1/A2 Juglet) |
| 35263682 | t334B4 | COMPLETED | 0:0 | 19:50 (A1/A2 pots) |
| 35263683 | t334X | COMPLETED | 0:0 | 7 s (died: missing --dump) |
| 35264041 | t334X2 | COMPLETED | 0:0 | 1:26 |
| 35264640 | t334C | FAILED | 1:0 | 4 s |
| 35264641 | t334C | FAILED | 1:0 | 4 s |
| 35264851 | t334jug | COMPLETED | 0:0 | 7 s (shape bug) |
| 35264852 | t334pot | COMPLETED | 0:0 | 7 s (void key) |
| 35265480 | t334dbg | COMPLETED | 0:0 | 7 s |
| 35265685 | t334ps | COMPLETED | 0:0 | 5 s (pot scoring) |
| 35266020 | t334jug | CANCELLED by 18130 | 0:0 | 28:13 (Stage C 1x rows + 3x stall) |
| 35266929 | t334pot | COMPLETED | 0:0 | 1:26 (pot controls) |
| 35267284 | t334D | COMPLETED | 0:0 | 7 s (render export) |
| 35267666 | t334amb | COMPLETED | 0:0 | 4 s |
| 35267705 | t334c3q | COMPLETED | 0:0 | 2:56 (3x capped 60k) |
| 35268428 | t334c3f | TIMEOUT | 0:0 | 04:00:10 (3x full density, 122/~132 rows, no tsv) |
| 35270887 | t334c3m | COMPLETED | 0:0 | 01:04:38 (3x recorded lane, 200k/wall) |

### Declared gaps

Three acceptance items are not met and are declared rather than dropped: Stage B metric 3 (the 15-deg basin pool - the dump hook never fired), Stage B's separation claim (the conditioning number does not flag p9) and Stage C's full-density 3x table (job 35268428 hit its 4 h wall at 122 of ~132 rows). The recorded 3x lane is the 200k-per-wall job 35270887, with the full-density pairs and three of four chains reported above and two chain-poses missing. Each gap has a substitute or a partial above, and each is work I would do first on a follow-up rather than re-run blind.

Reading: multi-piece-resolves-spherical-axis

Scope of that reading: on 1x geom walls with poses GIVEN (exact: 9 of 9 pieces within 5 deg, 4 of 4 chains, 8 of 9 pairs; perturbed +3 deg / +1 mm: 8 of 9 pairs, 4 of 4 chains), and on the 3x cloud lane only through the choice of estimator: pooled reaches 5 of 9 pairs within 5 deg at full density and 6 of 9 at 200k/wall, while each of the four spherical sherds is still carried inside 5 deg by at least one estimator at both densities (p2 0.74/0.83, p3 0.98, p8 1.05/0.72, p9 0.94/0.92), with 2-9 and 7-9 failing at every estimator and every density. Not claimed: that the 3x lane matches the 1x lane, or that any single delivered line is right at rank 0.

End-state: ready

---

## Verdict (lead, 2026-11-17)

**Reading accepted — `multi-piece-resolves-spherical-axis` — with its scope made explicit in the sentence that
follows it, not only in the tables: at 1x with the pose GIVEN, 9 of 9 pieces come within 5 deg (exact) and 8 of 9
pairs within 5 deg perturbed; at 3x, every piece comes within 5 deg under at least one estimator at both
densities, but the *pair* level is 6 of 9 at 200k and 5 of 9 at full density, and two pairs (3-5, 7-9) fail at
every estimator and every density. Nothing ships, and no tracked file was touched.**

### What I verified myself

- **Slurm.** `35268428` **TIMEOUT 0:0 at 04:00:10**, `35270887` **COMPLETED 0:0 at 01:04:38**, both by my own
  `sacct -X`. The timeout is the full-density job, which is why it has no tsv.
- **The full-density rows, recomputed from their own record.** The job wrote no tsv; the numbers live in
  `out/logC_c3f.txt` (122 JSON rows, 18 pooled-rank0 pair rows, all nine pairs with both poses present). I parsed
  it myself: 1-2 1.18/0.84, 1-4 1.62/0.91, 1-8 0.72/2.81, 1-9 0.92/1.06, 2-5 **5.19/7.30**, 2-9 **7.18/9.17**,
  3-5 **12.95/14.72**, 6-7 0.24/0.98, 7-9 **13.88/16.38** — **5 of 9 within 5 deg**, 7 of 9 within 10, exactly the
  gate's `fd_*` rows. My first pass disagreed with the gate on five pairs; the fault was mine (I let a later
  `best3` row overwrite the `rank0` row for the same pair), and with `extra=="rank0"` held fixed the two agree
  row for row.
- **The 200k lane** from `out/cluster_c3m.tsv` itself: 1-2 1.23/0.80, 1-4 1.64/1.11, 1-8 1.05/2.07,
  1-9 0.94/1.06, 2-5 2.51/3.26, 2-9 14.19/16.15, 3-5 12.12/13.90, 6-7 0.47/0.31, 7-9 15.28/17.50 — **6 of 9**.
- **Per-piece best, at both densities and by my own reduction**: full density 1 0.72, 2 0.95, 3 0.98, 4 1.62,
  5 0.95, 6 0.24, 7 0.24, 8 0.72, 9 0.92 (**9 of 9 within 5**); 200k 1 0.74, 2 0.74, 3 0.98, 4 1.64, 5 0.74,
  6 0.47, 7 0.47, 8 1.05, 9 0.94 (**9 of 9**). So "every spherical sherd is recoverable" is true; "the pair is
  resolved" is not.
- **The estimator claim on 3-5**: seeded-normalised gives **0.98** at full density where pooled gives 12.95;
  2-9's best is 14.46 (seeded-polished) and 7-9's 30.13 — so those two are not estimator choice, they are
  geometry or pose.
- **Stage A and the identity gate**, from the run's own axis files with my own angle code: A0 6/9 (1x) and 7/9
  (3x), A1 **7/9 then 3/9**, A2 **5/9 then 5/9** — the worker's rows to the decimal. `cmp` of `axesA0_172`,
  `axesA1off_172`, `axesA1off2_172` against shipped `axes323`: **172 compared, 0 differ** in all three, so the
  switch-off identity is real and the gate that counts is 35262399, not the vacuous one the worker disowned.
- **The gate and the tree**: `gate334.tsv` is 89 data rows with 16 explicit `fail` and 3 `flags`; the worktree shows
  the ticket file only.

### What it means

**The axis of a nearly-spherical sherd cannot be pinned from that sherd alone — and this ticket shows the way out
is not a better single-sherd criterion but the pair.** With the pose given, joining two or three sherds drags
piece 2 from 13 deg to ~1, piece 3 from 28.4 to ~1, piece 9 from 29.8 to ~0.9. Every route that tries to fix the
single piece is now closed by measurement: the wall-thickness cost (ticket 333), the bounded polish (A1, which also
costs the 3x lane and 15 corpus pieces), the uncollapsed shortlist (A2, worse still), and now conditioning, which
flags three of the four spherical pieces but puts p9 — the worst 3x miss — at the 34th corpus percentile, and
flags four pieces that are already solved. **High conditioning is necessary, not sufficient.**

**The catch, which must travel with every quotation of this result: the pose was GIVEN.** Pooling is not a fix that
runs before the search, it is a refinement that runs *inside* it — join on today's axes, re-fit the axis from the
joined pair, re-join. That loop has not been built or measured, and until it is, the honest statement is
"the axis is recoverable once the join is known", which is the wrong direction for a pipeline whose joins depend on
the axis. The 3x lane also tells us not to expect the 1x numbers there: density moves 2-5 from 2.51 to 5.19 and
2-9 from 14.19 to 7.18, i.e. across both bars, while 3-5 and 7-9 stay 12-16 deg at every setting — two real
pooled-geometry failures, not sampling noise.

**Two limits on the controls.** Only two Pot controls are usable (Pot_A 02-08 2.28 deg / 0.349 mm, 04-08 1.35 /
1.668); Pot E 24-25 already touches at 1.46 mm under identity and Pot E 26-27 is 107.76 mm apart under the ground
truth, so neither can fail. And the basin-ambiguity metric is unmeasured because its dump hook never fired in 181
subprocesses — the substitute (K=1 on seven of nine pieces, exactly the wrong ones) is suggestive and is not the
metric.

**Nothing ships, correctly**: no tracked file edited, `sfs_axes/` on main unchanged, the pot corpus untouched, 8
deviations declared in `run.json`. The next step this evidence supports is the joint loop (join → pool → re-fit →
re-join) with its own bars, and the conservator is the one to decide whether that is worth a ticket.
