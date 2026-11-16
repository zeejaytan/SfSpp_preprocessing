# 77 — Wall-guided fit and admission on top of chord growth

**What to build:** first a read-only Stage 0 over existing dumps and geometries that checks whether filtering *both* the grown cluster (before `fitSplineSurfaceToCluster`) and the refinement add-backs by distance to the wall-oriented core cures Sherd 7's last 30 off-lip dots without harming Pot A (including flat base `Pot_A_Piece_01`) or Sherd 1; then **two default-off arms** built on the proven Ticket 74 foundation (`Gnr` + `Mnr`, no Ticket-73 refine gate) to settle whether gating add-backs alone (`SFS_REFINE_WALL_FROM`-style) suffices or whether the cluster and B-spline fit itself must see only the wall.

**Why now (2026-11-16):** Tickets 74–76 together isolated the exact state of the 3× Juglet surface chain:

1. **Ticket 74's chord growth + merge gate without Ticket 73's refine gate (`Gnr` + `Mnr`) already solves 8 of 9 Juglet sherds and passes every control.** Under `Gnr` (`SFS_GROW_BASE_MM=1.5`, `SFS_GROW_BASE_THETA_DEG=25`), off-lip dots at `0.8 mm` drop to `0` on Sherds 1, 2, 4, 5, 6, 8, 9 and `1/122` on Sherd 3 (down from `14/125`), Pot A passes `8/8` within 1 dot, and J1's 1× ruler is identical to `off`. Only **Sherd 7** keeps an off-lip stretch (`30/171 = 17.40 mm`, down from `54/173 = 31.80 mm`).
2. **Ticket 75 closed two open threads:** (a) the `6-7` sign flip (`-0.997 → +0.657`) is the cure, not a failure — Sherd 7's seam dots moved from `1.91 mm` off its inner wall (on the break face) to `0.15 mm` on its inner wall (`pairloc75.py`, Adjudication 2); (b) a longer growth chord (`Arm L`, `3.0 mm / 45 deg`) fails (`30 → 30`, `18.00 mm`) because along Sherd 7's worn stretch the lip turns at `9.6 deg` over `1.5 mm` (`23.8 deg` over `3.0 mm`), inside the curved inner wall's own distribution.
3. **Ticket 76 proved why naive in-loop admission gates fail and found the wall-offset ruler — with one missing piece:**
   - `fitSplineSurfaceToCluster` (`mesh_processing_headless.cpp:1462`) crosses the fracture face (`d_fitted_mm` median `0.124 mm` off-lip vs `0.078 mm` on-lip), so no local residual, branch angle, or `nearest_claimed_mm` threshold separates the strip.
   - `SFS_REFINE_WALL_GATE=1` (`nearest_claimed_mm <= 0.8 mm`) hurt Pot A (`P02 0→4`, `P04 3→10`, refusing `314` and `284` inward wall points where growth stopped short of the rim) and dropped J1 `r2f_le1` by `-24.9%`.
   - Ticket 76's oracle (`wall_offset_mm <= 0.8 mm`) removed `64/65 (98.46%)` off-lip carriers at `0.000` on-lip carrier cost. However, Ticket 76 proposed applying it only to refinement add-backs (`SFS_REFINE_WALL_FROM`). Direct inspection of `C:/PR/artifacts/t75/dump75` (`Gnr_3x` Sherd 7) and `off_3x` shows `c0` *itself* still carries `536` points `> 0.8 mm` off the inner wall in `Gnr_3x` (`1,816` in `off_3x`), and `finishImprovedSurface` (`:1567`) copies all of `c0` unconditionally — so gating add-backs alone leaves `24/30` off-lip dots (`median 1.633 mm`) in `Gnr_3x` and `46/53` (`1.702 mm`) in `off_3x`.

**Answers:** E1
**Depends on:** 74 (`fad4e5f`), 75 (`7a69763`), 76 (`c9b8ecc`, merged `e8f4760`), 328 (`t328::axisFit`)
**Status:** landed
**Working in:** chat on Thinkbook16 (2026-11-16)
**Branch:** 77-wall-guided-fit-and-admission-on-chord-growth, in /c/PR/worktrees/sfs/77
**Worker:** dsh one-shot subagent w77
**Budget:** medium
**Hand-over:** DeepSeek — dsh one-shot subagent w77, dispatched 2026-11-16 by the lead (acceptance re-read by the lead from `stage0_77.tsv`, `gate77.tsv`, `render77_before_after.png`)

---

## Stage 0 — Read-only replay & control check (a STOP before building)

Run offline on the existing local geometry/dumps (`C:/PR/artifacts/t75/geom_Gnr75`, `C:/PR/artifacts/t75/dump75`, `C:/PR/artifacts/t76/outoff_3x/geom`, `C:/PR/artifacts/t76/outoff_1x/geom`, `C:/PR/artifacts/t76/outpota_off/geom`, axes in `C:/PR/artifacts/t74/off3x_root/ax` and `C:/PR/artifacts/t76/Axes_PotA`; plus 1× Juglet axes from `Dataset/Axes/Juglet` on Spartan if needed for 1× P2/P9). No Slurm job, no code edit.

1. **Define the guarded wall-core selector** (no hardcoded `-radial` assumption on flat bases or bad axes):
   For a surface cluster `C` (or exported `S0`) and the piece's symmetry axis `(P, D)`:
   - Compute `axisFit = frac(|n · (D × radial)| < 0.3)` (the `t328` axis-fit check already at `mesh_processing_headless.cpp:4482, 4631`) and `ndot = n · radial` over `C`.
   - **Guard:** the radial wall-core rule applies **only** when `axisFit >= 0.80` **and** `|median(ndot)| >= 0.40`. (This automatically skips flat bases like `Pot_A_Piece_01` where `|n · D| = 0.94`, `median(ndot) = +0.312`, and skips pieces with bad axes like 1× Juglet `P2`/`P9` in `Dataset/Axes/Juglet`.)
   - When the guard passes, set `sgn = (median(ndot) < 0) ? -1.0 : +1.0`. A point `p` is **wall-oriented** iff `sgn * (n(p) · radial(p)) > 0.2`. A point `p` passes the **wall-band test** iff it is **either** wall-oriented **or** within `W = 0.80 mm` (`W * SFS_TREE_UNITS_PER_MM` scene units) of a wall-oriented reference point.
     *(Note why the "either wall-oriented OR within 0.8 mm" clause matters: on `Pot_A_Piece_02`/`04` and on Sherd 7 `dots 100–103`, refinement legitimately recovers `284–359` inward-facing wall points `> 0.8 mm` beyond `c0`; keeping wall-oriented points preserves them where Ticket 76's `nearest_claimed_mm` dropped them.)*

2. **Deliver `C:/PR/artifacts/t77/stage0_77.tsv` and `stage0_77_summary.md`** answering:
   - **(a) Single-pass `c0_wall` vs two-pass `S0_wall`:** On `Gnr_3x` Sherd 7 (`dump75`) and all 9 pieces of `off_3x` / `Gnr_3x`, compare the wall-oriented reference set built from pre-refinement `c0` against the set built from exported `S0`. Report the fraction of points and carriers where the `0.80 mm` wall-band verdict agrees.
   - **(b) Add-backs-only vs cluster+fit+add-backs:** Replay both on `Gnr_3x` Sherd 7 (`dump75` + `geom_Gnr75`) and `off_3x` Sherd 7: how many of Sherd 7's `30` (`Gnr_3x`) and `53` (`off_3x`) off-lip `Bl0` dots still have a surviving `S0` point within `0.40 mm` whose `wall_offset > 0.80 mm`? (Lead baseline check predicts `24/30` and `46/53` remain under add-backs-only, `0/30` and `0/53` under cluster+fit+add-backs.)
   - **(c) Control safety before building:** On all 8 pieces of `Pot A` (`outpota_off`) and all 9 pieces of `1x Juglet` (`outoff_1x`, with `Dataset/Axes/Juglet` and with `Juglet_large/3`) and all 9 pieces of `Gnr_3x`, report `axisFit`, `|median(ndot)|`, whether the guard activates, and how many `S0` points and `Bl0` dots are dropped.
   - **Stop rule:** if on `Pot A` (`P02–P08`) or `1x J1` the guarded wall-band rule drops `> 5%` of `S0` or flips `>= 2` valid on-lip `Bl0` dots off-wall, stop and report `wall-core-hurts-controls` — do not proceed to Part B.

---

## Part B — Default-off switches (`mesh_processing_headless.cpp` only)

Build on top of the landed `main` binary (which already carries `SFS_GROW_BASE_MM`, `SFS_GROW_BASE_THETA_DEG`, `SFS_MERGE_CLUSTER_DOT` from Ticket 74). All new switches **default off**, leaving the unset path byte-identical on `1x` surfaces and within the existing unseeded ray-cast noise on `3x`.

Add **one** switch `SFS_WALL_FILTER=<mode>` (default `off`; modes `add` | `fit` | `two_pass_add`):
- Reuse `SFS_AXIS_FILE` (already required and loaded in `classifyAndOrderPaper234` at `:4583`, stored as `axPt`/`axDir` before `improveSurfaceBoundaryByFittingBSplineSurfaceOwn`) and `SFS_TREE_UNITS_PER_MM` (default `3.0` on `3x`, `1.0` on `1x`/Pot A).
- Optional overrides (not swept): `SFS_WALL_FILTER_MM` (default `0.80`), `SFS_WALL_RADIAL_MIN` (default `0.20`), `SFS_WALL_AXISFIT_MIN` (default `0.80`), `SFS_WALL_MEDRAD_MIN` (default `0.40`), `SFS_WALL_MAXDROP` (default `0.35`, mandatory starvation guard restoring the unfiltered surface if drop exceeds `0.35`).
- Optionally accept `SFS_REFINE_WALL_FROM=<dir_or_ply>` for two-pass comparison if Stage 0 shows `c0_wall` and `S0_wall` disagree by `> 2%` on any piece.
- Behaviour per mode (applied to `Surface_0` — and optionally `Surface_1`? Test `Surface_0` only first, record `Surface_1` unchanged):
  1. **`SFS_WALL_FILTER=add` (add-backs-only control, testing Ticket 76's lead proposal on `GMnr`):** `c0` (`segmentedSurfacePointCloud1`) is untouched and fitted as today; inside `improveSurfaceBoundaryByFittingBSplineSurfaceOwn`, out-of-cluster points added to `Surface_0` must pass the guarded wall-band rule (`wall-oriented OR dist_to_wall_core <= 0.80 mm`).
  2. **`SFS_WALL_FILTER=fit` (wall-guided cluster + B-spline fit + add-backs):** Before `fitSplineSurfaceToCluster(segmentedSurfacePointCloud1, fitted1)`, build the wall-core of `segmentedSurfacePointCloud1` (guarded by `axisFit >= 0.80` and `|median(ndot)| >= 0.40`). Trim `segmentedSurfacePointCloud1` to points passing the wall-band rule (`wall-oriented OR dist_to_wall_core <= 0.80 mm`, with starvation guard), **fit the B-spline to that clean wall cluster**, and enforce the same wall-band rule on out-of-cluster add-backs inside `improveSurfaceBoundaryByFittingBSplineSurfaceOwn`.
- Log once per piece: `[SFS-77] WALLFILT piece=<p> mode=<m> active=<0|1> axisFit=<f> medRad=<f> c0_in=<n> c0_kept=<n> add_refused=<n> reason=<ok|base_skip|bad_axis|maxdrop>`.

---

## Part C — Cells and gates

Use the ticket-74/76 cell driver (`stage66/run_cell66.sh`, `WORNESS=0.7`, `SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0` on `3x`, `MESH_ENV=""` on `1x` and Pot A; **NO `SFS_REFINE_ADD_GATE`** and **NO `SFS_REFINE_WALL_GATE`**).

| cell | bundle | switches | purpose |
|---|---|---|---|
| `off_3x` | 3× Juglet (9) | none | baseline + identity vs Ticket 76 `off_3x` |
| `gmnr_3x` | 3× Juglet (9) | `SFS_GROW_BASE_MM=1.5 SFS_GROW_BASE_THETA_DEG=25 SFS_MERGE_CLUSTER_DOT=0.887` | Ticket 74 foundation (no refine gate) |
| `wadd_3x` | 3× Juglet (9) | `gmnr` switches + `SFS_WALL_FILTER=add` | Ticket 76 add-backs-only on `GMnr` |
| `wfit_3x` | 3× Juglet (9) | `gmnr` switches + `SFS_WALL_FILTER=fit` | wall-filtered cluster + B-spline fit + add-backs |
| `off_1x`, `wfit_1x` | 1× Juglet (9) | `off` vs `gmnr` + `SFS_WALL_FILTER=fit` (`SFS_TREE_UNITS_PER_MM=1.0`) | J1 frozen ruler + 1× identity |
| `pota_off`, `pota_wfit` | Pot A 1× (8) | `off` vs `gmnr` + `SFS_WALL_FILTER=fit` (`SFS_TREE_UNITS_PER_MM=1.0`) | Pot A control (flat base P01 + P02/P04) |

Deliver `C:/PR/artifacts/t77/gate77.tsv` (columns `group metric piece off gmnr wadd wfit ref verdict`) with bars:
- **primary (3×, all 9 pieces reported, 5–8 gated):**
  - Sherd 7 off-lip contour **`< 12.0 mm`** (goal `<= 3.0 mm`, down from `31.2–31.8 mm` in `off_3x` and `17.4 mm` in `Gnr_3x`).
  - Sherds 5, 6, 8 hold **`0` off-lip dots** (`0/0/0`); Sherd 3 `<= 2`; Sherds 1, 2, 4, 9 hold `0`; pooled 5–8 `<= 5` dots.
- **line_displacement & wall_cost:**
  - `S0` and `S1` vertex counts within `10%` of `gmnr_3x` on all 9 pieces.
  - On-lip `Bl0` dot displacement (median NN between `wfit_3x` and `gmnr_3x` on dots that were already on-lip in `gmnr_3x`) `< 0.50 mm` per piece (Ticket 75 Adjudication 3).
- **pairs (3× Juglet, `pairdot72.py --scale 1` + `pairloc75.py`):**
  - `1-4` positive with `0` opposed dots.
  - **`6-7` evaluated WITH dot-wall position (`pairloc75.py`, Ticket 75 Adjudication 2):** Sherd 7's seam dots sit on its inner wall (`median d_inner <= 0.8 mm`, not `1.91 mm` on the break face) and agree in sign with Sherd 6 (`dot > 0`).
  - Every other touching pair (`1-2, 1-8, 1-9, 2-5, 2-9, 3-5, 7-9`) keeps positive median within `0.10` of `off_3x`.
- **j1_ruler (1× piece 1, `check_separation.py`):** all 5 frozen columns (`blindDeg`, `farS0`, `ring_cov_deg5`, `f2r_le1`, `r2f_le1`) within `10%` of `off_1x` (`r2f_le1` must NOT drop like Ticket 73/76's `-25%/-35%`).
- **pota (1× Pot A, 8 pieces):** `8 of 8` pieces within `1` off-lip dot of `pota_off`, `Bl0` dot counts within `2%`, `Pot_A_Piece_01` skipped by `medRad < 0.40` (`reason=base_skip`), no crash.
- **coverage:** `S0`, `S1`, `Bl0`, `Bl1` exported on `9/9` 3×, `9/9` 1×, `8/8` Pot A.
- **identity:** `off_1x` geometry `0.000 mm` NN against Ticket 76 `off_1x` (surfaces byte-identical); `off_3x` within run-to-run unseeded ray-cast spread (`<= 2.5 mm` worst on P1, `<= 0.71 mm` on 5–8).
- **render:** `C:/PR/artifacts/t77/render77_before_after.png` — rows `off_3x`, `gmnr_3x`, `wadd_3x`, `wfit_3x` across Sherds 5–8 (green = `<= 0.8 mm` inner wall, red = `> 0.8 mm`), plus Pot A `P01`, `P02`, `P04` and the `6-7` seam in `off_3x` vs `wfit_3x`.

---

## Part D — Readings (pick one verbatim on a `Reading:` line)

- `wall-fit-with-chord-growth-cures-all-nine-sherds` — `wfit_3x` clears Sherd 7 (`< 12 mm`), holds 5/6/8 at `0`, passes `1-4` and `6-7` (with wall position), J1 ruler, and Pot A `8/8`.
- `add-backs-only-suffices-on-chord-growth` — `wadd_3x` already passes every bar without touching `c0`.
- `wall-fit-removes-sherd-7-but-breaks-controls` — Sherd 7 clears, but `1-4`, J1 ruler, or Pot A fails (state exact piece and mechanism).
- `wall-core-hurts-controls` — Stage 0 stop rule fired before Part B.
- `sherd-7-survives-wall-fit` — even `wfit_3x` leaves Sherd 7 `>= 12 mm` off-lip (explain where the surviving carrier sits).

---

## Part E — Acceptance

- [ ] Stage 0 (`stage0_77.tsv`, `stage0_77_summary.md`) completed and stop rule evaluated before any Slurm build.
- [ ] Exactly one new switch `SFS_WALL_FILTER` (`add` | `fit`), default `off`, no default changed anywhere.
- [ ] `gate77.tsv` carries all groups (`primary`, `line_displacement`, `wall_cost`, `pairs`, `j1_ruler`, `pota`, `coverage`, `identity`) with PASS/FAIL per row.
- [ ] Pair `6-7` scored with `pairloc75.py` dot-wall position alongside normal dot product.
- [ ] Every `sbatch` polled with `scripts/remote/job_status.sh` and `sacct` State/ExitCode recorded.
- [ ] `render77_before_after.png` generated, opened, and described before choosing the `Reading:` line.
- [ ] No commit made by the worker; `git status --short` shows only `mesh_processing_headless.cpp` and this ticket.

## Out of scope

- Trace-side guard (Pot A tickets 75/78, closed 2026-11-15).
- Ticket 73's `SFS_REFINE_ADD_GATE` or Ticket 76's `SFS_REFINE_WALL_GATE` (`nearest_claimed_mm`).
- Re-tuning `SFS_GROW_BASE_MM`, `SFS_GROW_BASE_THETA_DEG`, `SFS_MERGE_CLUSTER_DOT`, or `thetaDeg` as sweeps.
- Editing `class/`, `hpc/`, `run_cell66.sh`, `Dataset/`, or the `px3` tree.

---

## Comments (worker, 2026-11-16) — w77

**Reading:** `wall-core-hurts-controls`

**Stage 0 stop rule: FIRED (limb 1).** Part B was not built, Part C was not run, nothing was committed.

Stage 0 ran offline and read-only on the existing `t74`/`t75`/`t76` geometry (`t75/geom_Gnr75`, `t75/dump75`,
`t76/outoff_3x/geom`, `t76/outoff_1x/geom`, `t76/outpota_off/geom`, `t76/refine76.tsv`, axes `t355/tree/juglet/Axes`
+ `Dataset/Axes/Juglet` fetched to `t77/ax_1x` + `t76/Axes_PotA`). Zero `sbatch`, zero `sacct` rows, no source
file touched, no `git` write of any kind.

### Stop-rule arithmetic

| piece | dropped of S0 | bar | |
|---|---|---|---|
| Pot A P02 | 1945 / 42398 = 4.59% | 5% | under |
| Pot A P03 | 314 / 40050 = 0.78% | 5% | under |
| Pot A P04 | 1147 / 32697 = 3.51% | 5% | under |
| **Pot A P05** | **2468 / 31786 = 7.76%** | 5% | **OVER** |
| Pot A P06 / P07 / P08 | 0 | 5% | under |
| Pot A P01 | guard inactive (`\|medRad\|` 0.3123 < 0.40) | — | skipped, as predicted |
| **1× J1** | **1056 / 13834 = 7.63%** | 5% | **OVER** |

Flip limb (>= 2 valid on-lip `Bl0` dots off-wall on P02–P08 or 1× J1): P04 **1**, all others **0** — not fired.
The drop limb alone fires, on two controls.

### (a) `c0_wall` vs `S0_wall` (0.80 mm verdict agreement)

Point-level agreement 0.9898–1.0000 (worst off J7 0.9898, gnr J7 0.9910 — max disagreement 1.02%, under the
ticket's 2% `SFS_REFINE_WALL_FROM` trigger). Carrier-level 0.9597–1.0000 (off J3 0.9597, off J7 0.9598,
gnr J7 0.9706 — 4.03% disagreement, over 2% on the carrier metric only). Full 10-row table in
`stage0_77_summary.md` §(a). Side finding that matters below: measured against the `c0` core the off-lip
contour *grows* (off J1 0 → 34 dots / 20.84 mm; off J7 53 → 75 / 44.40; gnr J7 30 → 50 / 30.00) because the
add-backs put wall-oriented points back at the lip. The `c0` core is a subset of the `S0` core, so the `S0`
core is the strict reading and the one used in (c) where no dump exists.

### (b) add-backs-only vs cluster+fit+add-backs (Sherd 7, carrier radius 0.40 mm)

| arm | add-backs-only | cluster+fit+add-backs |
|---|---|---|
| gnr_3x (30 off-lip dots) | **19/30** (nearest-any-distance 27) | **0/30** (nearest 4 / 0) |
| off_3x (53 off-lip dots) | **45/53** (nearest 50) | **0/53** (nearest 4 / 0) |

The ticket's contrast holds: only trimming `c0` itself reaches 0. Your baseline **24/30 and 46/53 reproduces**
under the looser reading (carrier = nearest surviving point, any distance) with the `S0`-core gate and
`wall_offset` to the `S0` core; with the single-pass `c0`-core gate that reading gives 27/30 and 50/53.

### (c) the mechanism of the stop

- **Pot A P05, the 2468 refused points:** one coherent annulus, t 236.2–237.5 mm, radius 42.6–49.9 mm,
  `\|n·D\|` 0.982–0.995 (median 0.988), 0.9–2.65 mm outside the band; the kept wall band starts at radius
  50.7 mm. That is **the pot's interior base floor** — the wall band cuts the floor off where the wall meets it.
  P02 is the same signature (t 350–352 mm, radius 47.6–57.2 mm, 4.59%). The whole-piece guard cannot save it:
  the floor is 5–8% of the points, so `\|median nd\|` stays 0.63–0.67 and the guard stays active.
- **1× J1, the 1056 refused points:** coherent arcs 1.5–2.2 mm from the band with `sgn·nd` median -0.946 — a
  strip of the wall's own thickness whose normals fail the 0.2 test. On off_3x J7 the same red mass *is* the
  off-lip flap the filter is meant to remove: the same rule is the cure on the target and the defect on the control.
- Band-width sensitivity (`w77_sens.tsv`): P05 7.76 / 6.50 / 5.80 / 3.86 / 2.31% at W = 0.8 / 1.0 / 1.2 / 1.6 / 2.0 mm,
  1× J1 7.63 / 7.35 / 7.21 / 5.75 / 1.86%, off_3x J7 4.88 / 3.74 / 2.86 / 1.43 / 0.36%. No W clears the 5% bar on
  P05 while still acting on Sherd 7.
- Skips, as predicted: `Pot_A_Piece_01` (0.3123), 1× J2 (axisFit 0.3588), 1× J9 (0.2404); plus 1× J6
  (`\|medRad\|` 0.0470, mixed normals) which the ticket did not name. With the cross-frame `Juglet_large/3` axis
  on all nine 1× pieces axisFit is 0.024–0.471 ⇒ guard inactive, 0 dropped anywhere: a wrong axis only disables
  the rule, it never damages a surface.

### Render (looked at before choosing the Reading)

`C:/PR/artifacts/t77/stage0_77_drops.png` — 4 panels in axis space (axial t vs radius), grey kept / red dropped
(P05, P02, 1× J1, off_3x J7). The eye sees, on P05 and P02, a **solid red ring at the end of the profile where
the wall becomes the base** — a whole feature removed, not scattered noise; on 1× J1 a red band running along
the wall at a constant offset; on off_3x J7 a red patch on the off-lip flap. That is why the reading is
`wall-core-hurts-controls` rather than a tolerance complaint about the 5% bar. `render77_before_after.png` was
not produced — it needs the Part C cells, which the stop rule forbids.

### Artifacts

`C:/PR/artifacts/t77/stage0_77.tsv` (62 rows: 10 + 8 + 26 + 9), `stage0_77_summary.md` (full (a)/(b)/(c)
tables, frames, c0 recovery, corrections), `stage0_77.py`, `render_stage0.py`, `stage0_77_drops.png`,
`w77_sens.py`, `w77_sens.tsv`, `ax_1x/`, `ax_large/`.

### What went wrong, and how I knew

1. Off-lip contour summed dot steps in tree units (93.59 mm instead of 31.20 mm). Caught against the frozen
   ruler `lead_offlip76.py`; fixed by dividing by `SFS_TREE_UNITS_PER_MM` — now reproduces 31.20 mm / 53 dots
   (off J7) and 18.00 mm / 30 dots (gnr J7; your 17.40 mm came from a 171-dot dump, this dump has 170).
2. A dump↔export match at 1e-6 found 818 coincidences and looked like a frame mismatch. At 1e-3 it is 41 750 of
   44 799 and `c0` + the 3 098 add-back rows account for all of `S0` (`c0` carries exactly **536** points
   > 0.8 mm off the wall core, your ticket-76 figure). Tolerance, not frame.
3. A first sensitivity run mixed frames (axis point divided, geometry not) and reported a 41% drop on Sherd 7;
   aligned, it is 2.96%. The per-arm radius sanity check (Juglet 10–16 mm, Pot A 69–78 mm, P01 37 mm flat) is
   what now guards the instrument.

`git status --short` in the worktree: this ticket file only (no `mesh_processing_headless.cpp` change exists,
because Part B was not built).

**End state:** ready
## Lead verification (2026-11-16) — lead

Read the render, recomputed the rule and the stop-rule fractions from the staged clouds, and re-read the
tables this record rests on.

1. **The eye agrees with the table, and that is the point.** `artifacts/t77/stage0_77_drops.png` shows on
   Pot A P05 and P02 a **solid red band at the end of the profile where the wall turns into the base** —
   one contiguous feature, the whole interior floor beyond 0.8 mm of the wall band; on 1× J1 a red strip
   running along the wall at constant offset; on J7 the flap patch the rule exists to remove. Nothing is
   scattered.
2. **The stop rule fires as claimed.** Recomputed with the lead's own code (`artifacts/t77/lead_verify77.py`:
   core from the S0 cloud, sign from median(nd), W×units): P05 **7.76%** (2 468/31 786), 1× J1 **7.63%**
   (1 056/13 834), P02 4.59%, P03 0.78%, P04 3.51% with 1 on-lip flip; guard inactive on P01 (0.3123),
   1× J2 (0.3588), 1× J6 (0.0470), 1× J9 (0.2404). The bar is met on two controls, neither predicted.
3. **The refused points are whole surfaces, measured.** P05's 2 468 sit in one annulus, t 236–238 mm,
   r 42.6–49.9 mm, |n·D| median **0.988** — the interior base floor; P02's 1 945 the same (r 47.6–57.2 mm,
   |n·D| 0.988). J1's 1 056 are arcs 1.5–2.2 mm off the band with median |n·D| 0.311, i.e. wall thickness
   the radial test misses. The worker's mechanism is reproduced independently.
4. **(b) holds.** add-backs-only leaves 19/30 (gnr) and 45/53 (off) of Sherd 7's off-lip dots;
   cluster+fit+add-backs leaves 0/30 and 0/53. Only trimming `c0` reaches zero — which is why the control
   cost above is the decisive measurement and not a side effect.
5. **One correction to the worker's text, none to the verdict.** The `c` rows' J7 fractions (gnr 3.86%,
   off 5.90%) are computed against the `c0` core; under the `S0` core — the strict reading the ticket
   names and the one its own sensitivity run and the lead's recomputation use — J7 drops **2.96% / 4.88%**.
   The stop rule fires on P05 and J1 under either core.
6. **The sensitivity is a trade-off, not a missing setting.** At W = 1.6 mm P05's cut falls to 3.86%,
   under the bar, but J7's falls to 0.81% (gnr) and 1.43% (off) — about a quarter of the flap — and at
   2.0 mm to 0.31% / 0.36%. No width clears the control bar while still removing the flap.

**Verdict: `wall-core-hurts-controls` accepted — claim (1), the rule fails; the measurement is sound.**
For E1 this closes the wall-distance family in the form the ticket tested: distance to a wall-oriented
band cannot tell a fracture flap from a legitimate surface that is simply not the inner wall (Pot A's
base floor, J1's wall thickness), which is why the only filter that reaches 0 off-lip dots on Sherd 7
also cuts 7.76% of a control's points. What it does **not** settle: a **localised** form — the same
ruler applied only inside the break-face neighbourhood, or only to add-backs already flagged at the
fracture edge — which is untested and must be replayed offline on `stage0_77.tsv` before any job.

verified: `C:/PR/artifacts/t77/lead_verify77.py` -> P05 7.76/3.86/2.31%, J1 7.63/5.75/1.86%,
gnr J7 2.96/0.81/0.31%, off J7 4.88/1.43/0.36% at W 0.8/1.6/2.0 mm; `stage0_77.tsv` rows
`c pota Pot_A_Piece_02` 1945/42398 and `Pot_A_Piece_05` 2468/31786, `c off_1x Juglet_Piece_1`
1056/13834; `w77_sens.tsv` rows match the recomputation; `stage0_77_drops.png` read.


