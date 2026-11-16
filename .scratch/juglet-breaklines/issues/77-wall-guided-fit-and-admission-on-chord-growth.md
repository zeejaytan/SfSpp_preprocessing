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
**Status:** in-progress
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
