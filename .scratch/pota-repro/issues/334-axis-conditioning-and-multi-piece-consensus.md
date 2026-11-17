# 334: Axis conditioning and multi-piece consensus — replace the single-sherd ceiling on spherical sherds

**What to build:** a **diagnostic and offline prototype measurement** (no production edit to `sfs_axes/` or `structure-from-sherds-pp/class/`) that tests the two concrete mechanisms left open by tickets 332, 333, and the SfS++ paper re-check (`§IV-B2` / `§IV-C2`):

1. **Single-sherd hygiene + conditioning (Stage A–B):** how far does fixing only the mechanical defects already found in `sfs_axes/` — **5° bounded polish + start+refined ordering** (ticket 333 `job 35240144`) and **protecting raw uncollapsed basins** from `refine_axis_normalized` / `[:8]` starvation — take **3× Juglet** and the **172-piece corpus**; and does a dimensionless conditioning metric (Pottmann `s2/s3`, normalised-residual Hessian conditioning) cleanly separate well-anchored sherds (`p1`, `p7`, Pots A–J) from spherical-belly sherds (`p2, p3, p8, p9`)?
2. **Multi-piece joint axis consensus (Stage C):** when 2–3 joined sherds are pooled in a common frame (the mechanism the paper’s own assembler invokes in `GraphAxisRefinement`, `ranking_system.cpp:2554`, tested here with **scale-free** `sfs_axes` rather than raw-mm Cao error), does pooling break the `11.9°`/`28.4°`/`89°` spherical attractors and recover the vessel axis within `≤ 5°` across **all nine** Juglet pieces with **no Juglet-specific constants**?

**Answers:** E1
**Blocked by:** None (can start immediately). Tickets 332 (`3c4b118`) and 333 (`4a3b400`) closed the single-sherd `(r, z)` thinness route; `sfs_axes/` on `main` is unchanged.
**Status:** ready-for-agent
**Worker:** unassigned
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
