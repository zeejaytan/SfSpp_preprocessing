# 04: Scale-free `GraphAxisRefinement` inside the C++ assembler (`structure-from-sherds-pp`)

**What to build:** Resolve the physical single-sherd spherical ceiling (`Gap 3`: `Juglet P2, P3, P9` and small near-spherical sherds like `Pot J P08, P11, P12`, proved unsolvable from a single sherd in Ticket 334 while 2–3 joined sherds recover all `9/9` pieces within `< 1°`) by implementing an **opt-in scale-free normalized residual** (`SFS_GRAPH_AXIS_NORM=1`, default OFF until proven) in `structure-from-sherds-pp`'s multi-sherd `GraphAxisRefinement` / `RefineAxis` (`class/axis_estimation.cpp:259-321`, `class/ranking_system.cpp:2554-2598`).

**Answers:** E1
**Blocked by:** 03-ship-joint-axis-and-e2e-own-surfaces-gate
**Status:** needs-triage — blocked by Ticket 03
**Worker:** unassigned
**Budget:** large 8
**Hand-over:** DeepSeek — hidden acceptance check at `C:/PR/artifacts/dsh-handover/axis-parity-04/accept.py` to be staged before dispatch

---

## Background (`structure-from-sherds-pp` & Ticket 334 proof)

1. In `structure-from-sherds-pp/class/ranking_system.cpp:2554-2598`, `GraphAxisRefinement` already re-estimates the vessel axis jointly across all sherds `geom_ptr` currently in `toprank_graph`, using the vector overload `RefineAxis(vector<Geom*> const geom_ptr, ...)` (`class/axis_estimation.cpp:259-321`).
2. However, `RefineAxis` currently minimizes **unnormalized `BiaxialCaoError`**, which has physical length units (`mm`) and suffers centroid lever-arm collapse on small vessels/clusters: Ticket 334 proved that on `3x` Juglet clusters `2-9` and `7-9`, unnormalized `BiaxialCaoError` drifts **`54°–75°`**, whereas normalized residual `e_hat_i = ((p_i - p0) . (n_i x a)) / max(||(p_i - p0) x a||, eps)` keeps clusters anchored within `~1°`.
3. Upstream `feature_matching.cpp` still relies on good single-sherd input axes (addressed by Tickets 01–03); once initial pairs join, replacing unnormalized Cao inside `GraphAxisRefinement` stops small clusters from tilting the growing vessel's axis away from true geometry before subsequent joins (`Juglet` `4-6`/`4-7` wrong join vs `12/18`–`18/18` edges; `Pot J` `P08/P11/P12`).

---

## Implementation & Validation Plan (Spartan build + compute nodes only)

1. **Opt-in C++ change (`structure-from-sherds-pp/class/`):**
   - Add `BiaxialNormalizedAxisError` (Ceres auto-diff functor matching `normalized.py:compute_normalized_residual`) alongside existing `BiaxialCaoError` in `axis_estimation.cpp`, plus env switch `SFS_GRAPH_AXIS_NORM=1` (default OFF, preserving LF `\n`) selecting normalized residual in the multi-sherd `RefineAxis(vector<Geom*> const geom_ptr, ...)` called by `GraphAxisRefinement`.
   - Rebuild the batch binary cleanly on Spartan following `docs/notes/build.md`; verify **default OFF** (`SFS_GRAPH_AXIS_NORM` unset/`0`) matches shipped Pot A (`8/8 15/15`) and `def_3x` Juglet controls identically.
2. **A/B validation with Ticket 03's landed own-code axes:**
   - **`Pot A` positive control (4 repeats OFF vs ON):** must hold `8/8, 15/15` (`0` regressions).
   - **`def_3x` Juglet (4 repeats OFF vs ON, `t368 cluster366.py` + `score58` at real `4.596 mm`):** measure `k_sherd`, `k_edge` (`>= 12/18`), GT joins (`18/18`), Piece 7 joins (`4/4`), vertex cluster (`<= 0.50 mm`), and whether wrong join `4-6`/`4-7` disappears.
   - **All `10` paper pots (`Pot A..J`, 2 repeats OFF vs ON, `CORPUS-UNCHANGED`):** measure whether all `10/10` hold/improve over `t323` and whether **`Pot J`** recovers any of `P08 / P11 / P12` above `8/11, 16/21` (and `Pot D` above `26/28, 63/69`).
3. **Deliverables & Visual Check (`C:/PR/artifacts/axis-parity-04/`):**
   - Fetch `gate04.tsv`, `score/acc_pot{A..J}.tsv`, `juglet/`, `render04_juglet_potJ.png` (and stage `visual-qa` pair if any sherd recovers/changes pose). Inspect visually before writing `Reading:`.

---

## Readings (pick one verbatim on a bare `Reading:` line)
- `graph-norm-improves-juglet-and-holds-ten-pots` — `SFS_GRAPH_AXIS_NORM=1` holds `10/10` paper pots (report any gains on `Pot D`/`Pot J`), improves `def_3x` Juglet edges/joins/cluster (`9/9, >= 12/18`, clean seams), and leaves default-OFF invariant; ready for decision to flip default ON.
- `graph-norm-juglet-only-or-regresses-pot` — helps Juglet or a named pot (`Pot J`) while regressing another pot (`A..J`), or leaves Juglet unchanged (`4-6`/`4-7` caused by matcher/overlap rather than `GraphAxisRefinement`).
- `blocked: build-or-control-failed` — C++ build failure or default-OFF control discrepancy.

## Out of scope
- Flipping `SFS_GRAPH_AXIS_NORM=1` default ON without a separate shipping decision after Ticket 04 metrics are reviewed.

## Acceptance
- [ ] `structure-from-sherds-pp/class/` edits are gated behind `SFS_GRAPH_AXIS_NORM=1` (default OFF); default-OFF control reproduces Pot A (`8/8 15/15`) cleanly.
- [ ] A/B (`OFF` vs `ON`) measured on `Pot A..J` (2 repeats each) and `def_3x` Juglet (`4` repeats) on Spartan compute nodes (`sacct -X COMPLETED 0:0`, `CORPUS-UNCHANGED`).
- [ ] `C:/PR/artifacts/axis-parity-04/{gate04.tsv,render04_juglet_potJ.png,score/,juglet/}` fetched and visually inspected before writing bare `Reading:` and `**End state:** ready`.
