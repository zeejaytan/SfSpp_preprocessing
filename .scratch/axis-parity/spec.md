# Spec: Axis Parity & Fidelity — Matching or Beating Authors' Axes Without Losing Robustness

**Answers:** E1
**Prior work searched:** GitHub "PotSAC" / "Structure-from-Sherds" / "compute_biaxial_cao_error" / "SfSpp_preprocessing"; arXiv 2502.13986v1 (C:/PR/papers/text/sfspp-2502.13986v1.md); project page https://sj-yoo.info/sfs/. Found: https://github.com/SeongJong-Yoo/structure-from-sherds, https://github.com/SeongJong-Yoo/structure-from-sherds-pp, https://github.com/DominicoRyu/SfSpp_preprocessing (vendored MATLAB AxisExtraction/ in this repo), and PotSAC (Hong et al., ICCV Workshops 2019).

---

## 1. Where Things Actually Stand (141 GT-Scored Pieces + Paper Table V + `def_3x` Juglet)

Before proposing changes, we audited shipped `axes335` (`commit 9e0fe6a`, `C:/PR/artifacts/axis_audit/`) directly against both Authors' released `Axes/` and `Ground Truth Axes/` across all `141` GT-scorable corpus pieces (`Pot A..J`), plus downstream `t323` assembly scores and Paper Table V (`C:/PR/papers/text/sfspp-2502.13986v1.md:345-356`):

| Metric (`141` GT-scored corpus pieces) | Authors' `Axes/` | Shipped `axes335` (`9e0fe6a`) | Delta (`axes335` vs Auth) |
|---|---|---|---|
| `K1 <= 10°` (rank-0) | `105/141` (`74.5%`) | **`109/141` (`77.3%`)** | **`+4`** (Ours wins `16`, Auth wins `12`) |
| `K3 <= 10°` (best of top 3) | `116/141` (`82.3%`) | **`121/141` (`85.8%`)** | **`+5`** (Ours wins `13`, Auth wins `8`) |
| Rank-0 angle median / mean | **`2.78°`** / `14.26°` | `3.06°` / **`9.67°`** | Median `+0.28°` worse / Mean **`-4.59°` better** |
| Rank-0 radial offset to GT origin med / mean | **`4.38 mm`** / `14.82 mm` | `4.53 mm` / **`10.54 mm`** | Median `+0.15 mm` worse / Mean **`-4.28 mm` better** |
| Top-3 radial offset median | **`3.80 mm`** | `4.12 mm` | `+0.32 mm` worse |

### Per-Pot Breakdown (`141` GT Pieces, `t323` E2E Assembly, and Paper Table V)

| Pot | `n` (GT) | Auth `K1/K3` | Our `K1/K3` | Auth r0 med/mn | Our r0 med/mn | Auth rad med | Our rad med | E2E `t323` `K3` vs `MO` | Paper Table V (`SA / EA`) |
|---|---:|---|---|---|---|---|---|---|---:|
| **A** | 8 | `6/8`, `7/8` | `6/8`, `7/8` | `1.68° / 10.92°` | `3.17° / 9.42°` | **`1.92 mm`** | `6.97 mm` (`K3 5.57`) | `8/8 15/15` vs `8/8 15/15` | `100% / 100%` |
| **B** | 9 | `6/9`, `7/9` | **`7/9`, `9/9`** | `2.42° / 6.50°` | `4.32° / 6.29°` | `3.60 mm` | **`2.07 mm`** | `9/9 15/15` vs `9/9 15/15` | `100% / 100%` |
| **C** | 4 | `2/4`, `3/4` | **`3/4`, `3/4`** | `11.39° / 21.28°` | **`4.75° / 8.41°`** | `7.04 mm` | **`5.44 mm`** | `4/4 5/5` vs `4/4 5/5` | `100% / 100%` |
| **D** | 28 | `20/28`, `21/28` | `20/28`, **`23/28`** | `2.54° / 18.47°` | `3.59° / 12.64°` | **`5.81 mm`** | `6.63 mm` | **`26/28 63/69`** vs `23/28 55/69` | `82.1% / 83.3%` |
| **E** | 31 | **`26/31`, `29/31`** | `24/31`, `27/31` | `2.81° / 10.38°` | `2.98° / 7.00°` | `2.46 mm` | **`2.43 mm`** | `31/31 62/62` vs `31/31 62/62` | `100% / 100%` |
| **F** | 5 | **`5/5`, `5/5`** | `4/5`, `4/5` | `4.56° / 6.21°` | `4.56° / 6.40°` | `4.38 mm` | **`4.12 mm`** | `5/5 7/7` vs `5/5 7/7` | `100% / 100%` |
| **G** | 7 | `7/7`, `7/7` | `7/7`, `7/7` | `2.17° / 1.64°` | `1.91° / 2.85°` | **`1.37 mm`** | `1.81 mm` | `7/7 10/10` vs `7/7 10/10` | `100% / 100%` |
| **H** | 11 | `5/11`, `9/11` | **`9/11`, `11/11`** | `29.08° / 34.09°` | **`0.88° / 9.55°`** | `74.39 mm` | **`5.53 mm`** | **`11/11 17/17`** vs `8-10/11` | `90.9% / 88.2%` |
| **I** | 27 | `24/27`, `24/27` | `24/27`, `24/27` | `2.22° / 6.11°` | `2.83° / 7.03°` | **`4.94 mm`** | `5.52 mm` | `25/26 59/62` vs `25/26 59/62` | `92.6% / 90.8%` |
| **J** | 11 | `4/11`, `4/11` | **`5/11`, `6/11`** | `25.65° / 32.57°` | **`10.95° / 25.48°`** | `10.91 mm` | **`8.06 mm`** | `8/11 16/21` vs `8/11 16/21` | `72.7% / 76.2%` |

Note on **Pot J**: The paper itself (`sfspp-2502.13986v1.md:345-356`, Table V) only achieves **`72.7%` SA (`8/11`) and `76.2%` EA (`16/21`)** on Pot J — identical to our `J_K3` and `J_MOR` — and Authors' `Axes/` (`4/11`) are *worse* than our `axes335` (`5/11 K1`, `6/11 K3`).

---

## 2. Exact Pieces Where Shipped `axes335` Loses to Authors' `Axes/`

Across `141` GT pieces, shipped `axes335` loses on **8 `K3` pieces** (none of top-3 within `10°` while Authors are `<= 10°`) and **6 `K1`-only pieces** (rank-0 misses `10°` while top-3 recovers):

**8 `K3` Losses (`Auth K3 <= 10°` vs `Our K3 > 10°`):**
1. `Pot_A_Piece_07`: Auth `r0=58.87° k3=5.39° d0=52.6mm (K=3)` vs Ours `r0=26.83° k3=26.83° d0=56.6mm (K=1)`
2. `Pot_D_Piece_23`: Auth `r0=6.23° k3=6.23° d0=3.4mm (K=1)` vs Ours `r0=10.67° k3=10.67° d0=13.6mm (K=1)`
3. `Pot_E_Piece_25`: Auth `r0=8.59° k3=8.59° d0=2.9mm (K=1)` vs Ours `r0=13.70° k3=13.70° d0=3.7mm (K=1)`
4. `Pot_E_Piece_29`: Auth `r0=0.91° k3=0.91° d0=2.5mm (K=1)` vs Ours `r0=17.35° k3=10.73° d0=24.8mm (K=2)`
5. `Pot_E_Piece_31`: Auth `r0=54.77° k3=9.36° d0=31.9mm (K=3)` vs Ours `r0=16.10° k3=16.10° d0=7.8mm (K=2)`
6. `Pot_F_Piece_05`: Auth `r0=8.88° k3=8.88° d0=2.5mm (K=1)` vs Ours `r0=10.68° k3=10.68° d0=3.4mm (K=2)`
7. `Pot_I_Piece_20`: Auth `r0=0.97° k3=0.97° d0=4.9mm (K=1)` vs Ours `r0=21.79° k3=21.79° d0=22.5mm (K=1)`
8. `Pot_J_Piece_02`: Auth `r0=8.91° k3=8.91° d0=7.4mm (K=1)` vs Ours `r0=10.95° k3=10.95° d0=9.7mm (K=2)`

**6 `K1`-only Losses (`Auth r0 <= 10°`, `Our r0 > 10°`, `Our k3 <= 10°`):**
1. `Pot_A_Piece_06`: Auth `0.95° d0=2.0mm` vs Ours `r0=34.99° d0=47.3mm / k3=3.89° (K=2)`
2. `Pot_D_Piece_20`: Auth `9.64° d0=12.6mm` vs Ours `r0=18.86° d0=19.5mm / k3=3.03° (K=2)`
3. `Pot_D_Piece_27`: Auth `6.09° d0=8.1mm` vs Ours `r0=23.17° d0=16.7mm / k3=5.58° (K=3)`
4. `Pot_E_Piece_14`: Auth `6.32° d0=1.8mm` vs Ours `r0=56.35° d0=35.7mm / k3=9.38° (K=3)`
5. `Pot_E_Piece_26`: Auth `6.64° d0=6.7mm` vs Ours `r0=10.08° d0=6.7mm / k3=9.18° (K=2)`
6. `Pot_J_Piece_07`: Auth `1.79° d0=1.6mm` vs Ours `r0=20.42° d0=14.3mm / k3=6.60° (K=2)`

---

## 3. Paper & Code Gap Analysis (`SfS++`, `PotSAC`, `AxisExtraction/`, `sfs_axes/`, `class/`)

Comparing the paper (`C:/PR/papers/text/sfspp-2502.13986v1.md §IV-B2:173-177`, `Appendix B:519-533`), the authors' MATLAB `AxisExtraction/` (`run_potsac.m`, `compute_biaxial_cao_error.m`, `compute_rim_errors.m`, `check_base_and_rim.m`), and the C++ assembler (`ranking_system.cpp:2554-2598`, `axis_estimation.cpp:259-321`) against our `sfs_axes/` exposes **four real gaps**:

1. **Gap 1 — Precision & normal-blindness on well-curved sherds:** Authors' median error (`2.78° / 4.38 mm`) is tighter than ours (`3.06° / 4.53 mm`), starkly on `Pot A` (`1.92 mm` vs `6.97 mm` median radial), `Pot G` (`1.64° / 1.32 mm` vs `2.85° / 2.14 mm`), and single pieces like `Pot_I_Piece_20` (`0.97°` vs `21.79°`) and `Pot_E_Piece_29` (`0.91°` vs `17.35°`). Our shipped pipeline discards surface normals during final selection and refinement.
2. **Gap 2 — Paper mechanism gap (`select.py` & `profile.py` vs `run_potsac.m`):**
   - The authors' MATLAB chain (`run_potsac.m:66-68`) finishes surviving axes with analytical Levenberg–Marquardt (`tol=1e-9`) using **100% of surface points and normals** (`compute_biaxial_cao_error.m`), plus `check_base_and_rim.m` / `compute_rim_errors.m` (`SfS++ §IV-B2:177`, `Appendix B:533`) captures rim coplanarity (`h = a . p`, `r` constancy).
   - Our `sfs_axes/select.py:76-86` + `profile.py:38-82` instead ranks and finishes with **400 Nelder–Mead evaluations of `wall_thickness` on 2,500 strided positions ONLY — completely ignoring surface normals `n_i`**.
   - Neither invariant works alone: unnormalized Cao collapses into sherd centroids on small fragments (Ticket 312); normalized normal alignment alone suffers conical/spherical drift (Ticket 322, median `6.4°` drift, `> 10°` on `70/163`); pure `(r, z)` thickness alone admits normal-violating decoys (`A06` `34.99°`, `E14` `56.35°`, `I20` `21.79°`, `J07` `20.42°`) and suffers Nelder–Mead position jitter (`Pot A 6.97 mm`). **Jointly enforcing both scale-free invariants (normal coplanarity `e_hat_i` + `(r, z)` profile thinness) and finishing with profile-guarded full-cloud analytical LM has never been tested.**
3. **Gap 3 — `def_3x` Juglet / spherical-sherd ceiling & assembler `GraphAxisRefinement`:**
   - On `def_3x` Juglet, shipped `axes335` achieves `8/18` edges (`6/9 <= 4.596 mm`, `5.56 mm` origin gauge) vs GT-axes oracle's `13/18` (`9/9`, `0.459 mm` cluster).
   - Ticket 334 proved single-sherd criteria hit a physical wall on nearly-spherical belly sherds (`Juglet P2, P3, P9`; and similarly tiny `Pot J P08, P11, P12`), while pooling 2–3 joined sherds drops all `9/9` Juglet pieces below `1°`.
   - Inside `structure-from-sherds-pp/class/ranking_system.cpp:2554-2598`, `GraphAxisRefinement` already re-estimates the axis jointly across all sherds in a subgraph, **but calls unnormalized `BiaxialCaoError`** (`axis_estimation.cpp:259-321`), which Ticket 334 measured drifting `36°–74°` on small Juglet clusters.
4. **Gap 4 — 100%-own-code E2E surfaces gap:**
   - `scripts/run_benchmark_172.py` (`axes323`, `axes335`, `axes336`) still feeds **authors' released `original_samples/SfS_pp/Surfaces/`** into `sfs_axes` for `Pot A..J` (`163` pieces), not our own `MeshPreprocessingHeadless` surfaces (`t305`/`t319` or freshly generated).

---

## 4. Closed Dead-Ends (Do NOT Re-Test)

The following single-sherd hypotheses have already been falsified across Tickets 312–336 and 366–368 and must NOT be re-proposed:
- **Unnormalized Cao objective alone** on small isolated sherds — centroid lever-arm collapse on 6/10 failing Pot E pieces (`50–75%` lever-arm drop, Ticket 312).
- **Pure normalized normal residual LM alone (`e_hat_i`)** — drifts a median `6.4°` (`> 10°` on `70/163` pieces) into conical/spherical attractors (Ticket 322).
- **Single-sherd `(r, z)` slab thickness (`profile_band`) and 25 single-sherd `(r, z)` / curvature stats** — measures meridian slope `|dr/dz|` rather than perpendicular wall thickness, drops corpus accuracy `137/172 -> 33/172` (Ticket 333).
- **`5°` bounded Nelder–Mead `A1` and uncollapsed raw shortlist `A2`** — breaks `3x` Juglet (`3/9`) and costs `15–46` of `141` corpus pieces (Ticket 334).
- **`2-DoF` pivot-locked `a1_k0`** — drops corpus `K1` `135/163 -> 116/163` and regresses Pots `D, E, H, J` below `t323` floors in 2/2 repeats (Ticket 336).
- **`4-DoF c_in` ranking and `6°`-guarded `4-DoF c_ref`** — both regress `Pot_A_Piece_08` to `7/8, 13/15` because Pot A Pieces `06` and `08` require `18.4°–35.1°` 4-DoF walks from pool seeds (Tickets 367–368).
- **Naive multiplicative re-weighting of `(profile_cost, unrobustified normalized_huber_cost)` + unrobustified guarded LM (`joint-both-lm-11`)** — nets `0` (`109/141 K1`, `121/141 K3`), worsens overall median angle (`3.064° -> 3.317°`) and `Pot A` origin radial (`8.113 -> 9.501 mm`), and rejects `187/219` LM steps because `robustifier_huber(width=1.0)` never triggers on `|e_hat_i| <= 1.0` and decoy lines beat GT on both unfixed objectives (`Pot_A_Piece_07` `0.0319` vs `0.0478 mm` profile; `0.00614` vs `0.00665` `cnorm`; Ticket 01 `b432fb9`).
- **Serial `A1 -> Hermite gate -> joint NM -> Cao re-rank -> guarded polish` (`Arm D`) and standalone `A2`/`C1`/`C2`** — standalone `A2` (`62/64`) and `C1/C2` (`68–83`) collapse on flat/small sherds; serial `Arm D` loses a net 18 `K1` pieces relative to its own Stage 1 `A1` (`92/141` vs `110/141`; `Pot_A_Piece_08 = 15.47°`; Ticket 02 `46f064c`). Do NOT tune `Arm D`'s serial chain.

---

## 5. Four-Ticket Research Direction & Pre-Registered Bars

1. **Ticket 01 (`01-diagnose-14-losses-and-own-surfaces-audit.md`, resolved at `62ff33c`) — Root-cause decomposition & own-surfaces audit:**
   - Proved `M1 = 0/14` (`1.41°–7.71°` true-basin seeds in pool; `M2 = 7`, `M4 = 3`, `M3 = 2`, `M5 = 2`), `0/14` rim coplanarity (`24.85°–86.05°`), own `MeshPreprocessingHeadless` surfaces at parity (`113/141 K1`, `118/141 K3` vs `109/141`, `121/141`), and falsified simple `(pc, cn)` weight blending.
2. **Ticket 02 (`02-joint-normal-profile-axis-refiner.md`, resolved at `46f064c` / `4246c74`) — Cost-landscape ablation (Phase 1 early-stop, zero E2E spend):**
   - Proved all three thickness costs prefer shipped decoys over GT on `150/150` pieces; established `line_shift <= size` eliminates Juglet base flips (`0/18 SignAxisGuard`); proved standalone calibrated Huber `A1` (`width=0.05`) beats Authors and `axes335` on rank-0 accuracy and precision (`110/141 K1` Authors / `116/141` Own, `2.705°`/`2.563°` median, `4.338`/`3.778 mm` `d_gt_to_est`, `Pot A 2.473 mm`, `6/8` K3 recoveries, `Pot_A_Piece_08 = 4.741°`, missing only `K3 113` vs `121`); rejected serial `Arm D` (`92/94`); and showed parallel `A1 + B2` (`112/116`, `Pot_A_Piece_08 = 3.42°`) at `K <= 2` reaches **`126/141` (`89.4%`)** Authors / **`125/141` (`88.7%`)** Own with `7/8` K3 recoveries and `Pot G 7/7` at `K = 1`.
   - **Ticket 05 (`05-parallel-a1-b2-selector-and-e2e.md`, resolved at `e1cf772` / `277a754`, `Reading: dual-selector-improves-axes-but-misses-e2e-bar`):** Proved parallel `dual_k2` (`A1` rank-0 first + `B2` rank-0 if `>= 15°` apart, `line_shift <= size`, `orient_base_axis`, no `canonicalize()`) passes **12/12 Part A bars** (`110/141 K1`, `121/141 K3`, `2.7054°`, `4.3383 mm`, `Pot A 2.4733 mm`, `Pot G 7/7 K=1`, `7/8` K3 recoveries; Own `116/141 K1`, `122/141 K3`, `2.5631°`, `3.7781 mm`; Juglet `7/9 K1`, `8/9 K3`, `0/18 SignAxisGuard`), **9/10 paper pots** (incl. `Pot H 11/11 17/17` beating Authors `10/11 10/17`, and a new **100% `Pot I 26/26 62/62`** beating both Authors and `t323` `25/26 59/62`), AND **4/4 native 3x `def_3x` Juglet repeats** (`9/9` sherds, **`11–13/18` edges**, `9/9` cluster **`0.465–0.477 mm`** vs oracle `0.459 mm`, `4/4` Piece 7 joins `1.79°–3.05°`, after fixing a v1 `1/3`-scale write bug). Sole miss: **`Pot J`** (`6/11 9/21`, `5/11 8/21` vs `8/11 16/21`), traced to `Pot_J_Piece_05` (`axes335 = 2.8°` vs `A1 = 20.6° / B2 = 26.7°`) and `15°` dedup clipping `Pot_J_Piece_11` (`B2 = 3.4°` vs `A1 = 11.0°`).
   - **Ticket 06 (`06-tri-invariant-selector-potj-and-tenpots.md`, resolved at `ad0cc0f`, `Reading: tri-selector-passes-all-ten-pots-and-juglet`):** Proved the **tri-invariant parallel selector (`tri_psec_d10`: `A1` + `B2` + shipped position-only `profile_cost` rank-0 & secondaries at `10°` dedup, `K <= 3`, `orient_base_axis`)** clears **12/12 Part A bars** (`110/141 K1`, `128/141 K3` Authors / `116/141 K1`, `127/141 K3` Own, `2.7054°`/`2.5631°`, `4.3383`/`3.7781 mm`, `Pot G 7/7 K=1`, `Pot J K3 8/11` recovering `J05=2.83°`, `J07=6.60°`, `J11=3.40°`, `0/18` worst-case `SignAxisGuard`), **10/10 paper pots (`20/20` repeats at/above floor, incl. `Pot J 8/11 16/21` twice, `Pot H 11/11 17/17` twice, `Pot I 26/26 62/62` twice, `Pot D 24/28 58/69` twice vs Authors `23/28 55/69`)**, and `def_3x` Juglet best-of-4 (`r3`, `1/4` repeats: `9/9`, `13/18`, `0.483 mm`, `4/4` Piece 7 joins `1.47°–3.09°`; `r1/r2/r4` `8/9, 5–7/18, 0.466–0.558 mm` due to `K=3` on `Juglet_Piece_7`). Unblocks Ticket 03.
3. **Ticket 03 (`03-ship-joint-axis-and-e2e-own-surfaces-gate.md`) — Land winning axis selector & run 100%-own-code E2E gate:**
   - Land Ticket 05/06's validated parallel multi-invariant selector (`impl_t06.diff` or `t05`) in `sfs_axes/` (opt-out restoring exact `axes335` bytes, unit tests) and run full own-code E2E (`MeshPreprocessingHeadless` surfaces -> `sfs_axes` -> `EdgeLineExtraction` -> `structure-from-sherds-pp`) across `Pot A..J` and `def_3x` Juglet.
4. **Ticket 04 (`04-scale-free-graph-axis-refinement-in-assembler.md`) — Scale-free `GraphAxisRefinement` inside the C++ assembler:**
   - Address the physical single-sherd spherical ceiling (`Juglet P2/P3/P9`, small `Pot J` sherds) by adding an opt-in scale-free normalized residual (`SFS_GRAPH_AXIS_NORM=1`) to `GraphAxisRefinement` / `RefineAxis` (`structure-from-sherds-pp/class/`), testing `def_3x` Juglet (`>= 12/18` edges, eliminating `4-6`/`4-7` wrong join), `Pot J`, `Pot A` control, and all 10 pots before flipping default ON.

5. **Ticket 07 (`07-pot-j-own-surface-axes.md`, resolved at `1a19c9a`, `Reading: pot-j-own-surface-not-fixed-offline`) — Pot J on our own surfaces:**
   - Proved our own walls carry `45.8–48.1 %` exact-duplicate coordinates and `4.0–4.6×` the Authors' point count, while a `<= 10°` seed exists on `11/11` Pot J stems on both surface sets: the loss is the selector, not the pool or the surface. The nearest-to-GT basin costs out at rank `29–128` of `116–131` basins; carried fix F1 (symmetric merge) reaches own `129/141 K3` and own Pot J `8/11`, but Part A fails own `Pot_J_Piece_12` (`63.51°` vs `<= 30°`), so no E2E was run.
6. **Ticket 08 (`08-dedup-surfaces-and-shortlist-cost.md`) — Dedup, the Authors' surfaces, and the rank-29–128 cause:**
   - Measure and attribute the duplicate defect over the whole corpus, rerun Part A with duplicates removed (Authors' null control must be byte-identical), diagnose the rank mechanically (C1–C5), then at most two pre-registered scale-free shortlist/cost fixes; Part A gates the E2E.
7. **Ticket 09 (`09-write-each-surface-point-once.md`, resolved at `ee6345c`, `Reading: writer-writes-each-point-once`) — Fix the writer so it writes each point once:**
   - `finishImprovedSurface` no longer re-appends rows the surface already holds: it skips a source row whose x,y,z is already present and keeps the surface's own row with its normal (`surface_dedupe.h:155-190`), the TICKET-27 de-duplication is the same position rule made deterministic, and the `[DEDUPE-27]` line reports `dups_skipped=` and `normal_maxdiff=`. A 6-float key was tried and withdrawn - the same point's normal differs by one float32 ulp between the two code paths and PCL prints 8 digits, so the exported file showed a repeat that memory did not have. Unit test red then green (U1-U5); two real cells: `Pot_J_Piece_12` writes 2310/2590 rows against 4222/4842 and no repeated position, `Pot_D_Piece_03` still appends 1645 new tail rows. No Part A rerun - Ticket 08 measured the effect (own 116/127 -> 111/123, Authors' unchanged); a regeneration lane is still owed.
