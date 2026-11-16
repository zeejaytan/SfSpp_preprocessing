# 76 — Why the refinement takes the break face back, and which gate stops it without costing the wall

**What to build:** first a read-only stage that explains, point by point, *why* the boundary
refinement re-admits the strips the growth refused — the distance to the fitted surface, the
normal angle, the branch taken, the nearest claimed point, and how wall-like the point is by
ticket 59's ray-pair test; then a separation table over the four tunables that could refuse
the add-back, scored on the bad section, on the good band, and on the control sherds; then
exactly **one** default-off gate, chosen by that table, measured on the 3x Juglet, the 1x
Juglet and Pot A.

This is the step the last four tickets kept pointing at. Tickets 72–75 closed every door on
the growth side and the line on sherd 7 still runs 17.4 mm on the break face; the carriers of
that section are not grown points at all, they are points the refinement put back after the
growth had refused them.

**Answers:** E1
**Depends on:** 73 (the re-admission path, landed 9ff83e7), 72 (the trim, landed c27284c),
74 (the three doors, landed fad4e5f), 75 (the remainder, landed 7a69763), 59 (the ray-pair
signal), 26 (the admission window), 328 (the wall side)
**Budget:** medium. One read-only stage over the nine 3x pieces plus Pot A and 1x baselines,
one build, six to eight cells.

**Status:** landed
**Working in:** chat on Thinkbook16 (2026-11-16)
**Branch:** 76-why-the-refinement-takes-the-break-face-back (merged, e8f4760)
**Worker:** dsh one-shot subagent w76b, dispatched 2026-11-16 by the lead (first worker w76 died mid-run; jobs 35179176 / 35179476 / 35180198)

## Given — what the numbers already say

1. **The line rides points the growth never claimed.** On sherd 7 of the 3x run
   (`20261115-2005_b394663_t73-arms`, cell `off_3x`), the exported interior patch
   `Juglet_Piece_7.S0` has 46,235 rows over 24,702 distinct positions; **2,526 of those rows
   are points with `cluster_id = -1` at the pre-merge rung** — never claimed by the growth.
   Those rows are exactly the set the refinement **admitted** at rung 4: 2,489 of the 2,526
   match the recorded admitted points within 0.02 tree units (2,512 within 0.5), median 0.000.
   The rung's own counts reconcile: 29,744 + 1,792 = 31,536 one way, 22,104 + 2,510 = 24,614
   the other. No merge happened on this piece (`r3 merges []`, 66 pairs tested).

2. **The line's carriers are those rows.** 141 of the 173 Breakline_0 dots sit on admitted rows,
   and **40 of the 54 off-lip dots** do; the on-lip dots ride the same band (101 of 119). So the
   band is not a defect in itself — the line simply follows the patch boundary, and the patch
   boundary is the outer edge of the admitted band.

3. **The band is mostly wall; only a section of it crosses the face.** The lead measured
   ticket 59's ray-pair test on piece 7 (ray through the clay along `-n`, t 1.5–10 mm,
   perpendicular tolerance 0.45 mm, 1,200-point samples, tree units):

   | population | n | paired |
   |---|---|---|
   | the 2,510 admitted points | 1,200 | **0.578** |
   | grown cluster 1 (wall) | 1,200 | **0.641** |
   | the 119 on-lip dots | 1,200 | 0.605 |
   | the 54 off-lip dots | 54 | **0.074** |

   The admitted band is wall-like, not break-face-like. The defect is the part of it that
   reaches across the fracture face, and that part is exactly where the off-lip dots sit.

4. **Geometry of the band.** Admitted points sit 0.23 mm (median) from the nearest grown point,
   p90 0.60 mm, max 1.31 mm; 14% of the band lies more than 0.8 mm off the inner wall. The
   section that carries the 54 off-lip dots sits 0.85–2.73 mm off the inner wall over roughly
   15 mm of the rim — the strip that made ticket 72's trim shrink the whole patch when it was
   aimed at it.

5. **The admission rule, as the code stands.** `improveSurfaceBoundaryByFittingBSplineSurface`
   (`mesh_processing_headless.cpp:2536`) measures a window per surface with
   `window26Select` (:2314) from the fitted B-spline's residual and the other cluster's
   distance, raw 3.0 mm default, clamped to [0.5, 6.0] (:1687–1698, :2366–2368), then admits a
   point when `euclideanDistance(ptOnFittedSurface, ptOnOriginalMesh) < windowLenMM` **and**
   `angleDiff > 140` (:2671) or **and** `angleDiff < 40` (:2683). Ticket 73's
   `admit73` (:2636–2669, `SFS_REFINE_ADD_GATE`, default off, angle 30 deg) already
   refuses some of these, but it moved only 4 dots of 86 at 3x: the nearest claimed point is
   almost always within 30 deg of the added point, because the band is wall.

6. **The tunables that exist or could exist** — this ticket must rank them by measurement, not
   by preference:
   (a) **the window length** (`clampedMM`, and its clamps 0.5 / 6.0). No env switch today.
   (b) **the normal-angle branches** (140 deg / 40 deg), hard literals at :2671 and :2683.
   (c) **a per-point ray-pair gate** ported from ticket 59 (arm code archived at
   `/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1416_638504b_t59-breakstop-arm/work/mesh_processing_headless.patched.cpp`).
   (d) **a wall-side band test**: refuse an add-back whose radial offset from the interior
   cluster's own band exceeds a margin (the 0.8 mm cut that gates every reading in tickets 72–75).
   Ticket 26 already refuted "shrink the window to 0.5 mm" as a *repair* — it changed which
   points land where without producing a new genuine wall pair — so (a) is a candidate here for
   the opposite purpose (refusing), not a rerun of ticket 26.

7. **Controls and their role.** 3x Juglet (nine pieces), 1x Juglet (nine, with J1's frozen ruler),
   Pot A (eight). Pot A's accepted merges reach internal normal dots 0.807 and 0.815, so any gate
   that shrinks surfaces must be checked there, not just on the Juglet. 1x is where ticket 72's
   pass-1 estimator collapsed; if a gate is geometry-based it must not depend on that estimator.

## Part A — Stage 0, read-only (nothing armed)

Run the nine 3x pieces with a new per-point admission record. Nothing may change geometry.

**A1 — the record.** Add a `[SFS-76] ADMITDOT` line inside the admission loop (print the
values the decision already computes) and a `refine76.tsv` with one row per added-back point:

| column | meaning |
|---|---|
| `piece`, `surface` | Juglet piece, surface index (0 interior / 1 exterior) |
| `point_index` | index in the piece cloud |
| `d_fitted_mm` | `euclideanDistance(ptOnFittedSurface, ptOnOriginalMesh)` |
| `angle_deg` | `angleDiff` at the decision |
| `branch` | `own` (>140) or `other` (<40) |
| `cluster_id_r2` | the growth's verdict at the pre-merge rung |
| `nearest_claimed_mm` | distance to the nearest claimed point |
| `nearest_claimed_ang_deg` | angle to that point's normal |
| `pair_rate` | ticket 59's predicate at the point (ray through the clay) |
| `wall_offset_mm` | distance off the interior wall (the 0.8 mm ruler) |
| `carrier_of_line` | 1 if a Breakline_0 dot sits within one spacing of this point |
| `off_lip_carrier` | 1 if that dot is off-lip at 0.8 mm |

**A2 — the separation table.** `sep76.tsv`: for each candidate gate of Given 6, over a small
threshold grid, the confusion on the 3x pieces 5–8:
- **removed** — share of the off-lip section's carriers the gate refuses (target ≥ 0.60),
- **cost** — share of the added band that is *not* an off-lip carrier the gate also refuses,
- **surfaces** — the nine pieces still produce S0/S1,
then the same numbers re-scored on Pot A and on 1x, labelled as the control cost.

**A3 — stop rule.** If no candidate reaches 0.60 removed at ≤ 0.05 cost, stop with the reading
`no-gate-separates` and name the closest; do not guess one.

**A4 — the fit itself.** Report `d_fitted_mm` for the off-lip carriers against the on-lip
carriers on the same piece. If the bad section is no closer to the fitted surface than the good
band, the cause is not the threshold but the **fitted surface bulging across the fracture face**
— say so, because that changes the fix (the fit, not the gate).

## Part B — exactly one default-off gate, chosen by A2

One switch, off by default, today's path byte-identical when unset:

- `SFS_REFINE_WALL_GATE=1` with at most two thresholds (`SFS_REFINE_WALL_MAX_MM`,
  `SFS_REFINE_PAIR_MIN`) — the names follow whichever of Given 6 A2 selects; if (a) or (b)
  wins instead, expose `SFS_REFINE_WINDOW_MM` / `SFS_REFINE_ANGLE_DEG` in the same shape.
- Log `[SFS-76] REFWALL` per refusal and a `[SFS-76] REFWALL-SUM` per surface with
  `candidates / refused / kept`, so the cost is visible in the run, not just in the table.
- No starvation: the existing trim guard stays; if a surface would lose more than
  `SFS_REFINE_MAXDROP` (default 0.35) of its points, refuse the gate for that surface and
  print `[SFS-76] REFUSED` — a starving surface is worse than a travelling line.

## Part C — cells and the gate table

| cell | bundle | pieces | purpose |
|---|---|---|---|
| `off_3x` | 3x | 9 | baseline, gate unset |
| `gate_3x` | 3x | 9 | the gate |
| `off_1x` | 1x | 9 | baseline, J1 ruler |
| `gate_1x` | 1x | 9 | the gate at 1x (no geometry estimator may be needed) |
| `pota_off` | Pot A | 8 | control baseline |
| `pota_gate` | Pot A | 8 | control under the gate |

`gate76.tsv` — columns `group, metric, piece, off, gate, ref, verdict`, groups
`primary`, `pairs`, `j1_ruler`, `pota`, `coverage`, `identity`.
Bars:

- **primary**: sherd 7 off-lip contour < 12 mm; sherds 5, 6, 8 not worse than their off counts
  (21 / 3 / 9 dots); pooled not worse than 87 / 590 dots;
- **wall cost** (the new column this ticket needs): S0 and S1 vertex counts on every 3x piece
  not down more than 10% against `off_3x`, and the 1x surfaces not down more than 10%;
- **pairs**: the nine touching-pair median normal dots keep their sign, 1-4 positive with 0
  opposed, other pairs within 0.10 of the off arm;
- **j1_ruler**: no column worse by more than 10% on the four frozen numbers
  (blind stretch, far-skin share, reverse coverage, r2f_le1) from
  `/data/gpfs/projects/punim2657/SfSpp/runs/20261102-0450_05be12c_t57-sweep/check_separation.py`;
- **pota**: 8 of 8 pieces within 1 off-lip dot of the Pot A baseline, and every Pot A line's own
  dot count within 1% — the controls are the point of this ticket, not an afterthought;
- **coverage**: S0, S1, Bl0, Bl1 on 9 of 9 3x, 9 of 9 1x, 8 of 8 Pot A;
- **identity**: with the switch unset, byte-identical 1x outputs and ≤ 0.71 mm 3x nearest-point
  drift against `off_3x`.

Render `render76_before_after.png`: sherd 7 (and sherd 5) off vs gate, the off-lip dots
marked, plus one Pot A piece where the gate bites hardest.

## Part D — readings (pick one, verbatim)

- `the-gate-removes-the-section-and-keeps-the-wall`
- `the-gate-removes-the-section-but-costs-the-wall`
- `the-fit-crosses-the-face-and-no-threshold-gate-can-separate-it`
- `no-gate-separates`
- `the-gate-is-neutral-and-the-band-is-wall`

## Part E — acceptance

- [x] `refine76.tsv` has one row per added-back point on all nine 3x pieces.
- [x] `sep76.tsv` scores all four candidate gates of Given 6 over a threshold grid.
- [x] The stop rule of A3 was applied, and A4 answers whether the fitted surface crosses the face.
- [x] Exactly one switch, default-off, with today's path unchanged when unset.
- [x] `gate76.tsv` carries the wall-cost columns, not just the off-lip ones.
- [x] Pot A and 1x were run, and their deltas are in the table.
- [x] The render was looked at before the reading was chosen.
- [x] Every `sbatch` has its `sacct` State/ExitCode recorded.
- [x] Nothing is committed by the worker; the lead lands it.

## Out of scope

- The trace-side guard (closed by the conservator's ruling, 2026-11-15).
- The growth-side doors of tickets 72–75 (closed; they may be armed as controls but are not
  retuned here).
- Sweeping the growth thresholds or the merge gate.
- Anything under `class/`, `hpc/`, `assembler/`; `run_cell66.sh` itself; `Dataset/`; the
  `px3` tree.

## Comments (worker, 2026-11-16) — w76b

Second worker on this ticket; the first died mid-run without a message. Run directory for
everything below: `/data/gpfs/projects/punim2657/SfSpp/runs/20261116-0103_3e898d6_t76-stage0`
(branch head `3e898d6`, the ticket-76 patch uncommitted in the worktree, binary `bin-t76`).

### A1 — the per-point admission record

`out/refine76_raw.tsv` — 27,049 rows, one per add-back actually admitted by the refinement on the
nine 3x pieces, columns as the ticket asks (the three ruler columns are `-1` here; the scoring pass
fills them). Scoring pass `C:/PR/artifacts/t76/stage0_76.py` rewrites it as `out/refine76.tsv` and
writes the dot-side table `out/refine76_dots.tsv`.

Two corrections had to be made before the ruler columns meant anything, and both are worth
recording because they are silent failures, not errors:

- **The record's `x y z` are TREE UNITS**, byte-identical frame to `.S0`/`.Bl0` (piece 7: record
  max x 145.442993 = `S0` max x 145.442993). The first draft divided the breakline dots to mm and
  then queried them with raw record coordinates: median nearest-dot distance 1047.56 mm and
  `carrier_of_line` 0 on all nine pieces. Fixed by dividing the record by 3 before every query
  (median 2.31 mm, non-zero carriers).
- **The record covers BOTH surfaces** (piece 7: 3,098 rows on surface 0, 2,155 on surface 1; 15,726
  of the 27,049 rows are surface 0). `Breakline_0` belongs to surface 0 alone, and the interior
  0.8 mm ruler is meaningless for an exterior line (piece 1's `Bl1` is 205 of 206 dots "off-lip").
  The carrier test is now per surface (surface 0 ↔ `Bl0`, surface 1 ↔ `Bl1`) and A2 scores
  surface 0 only.

Frame check (a sanity gate, passed): median distance from a breakline dot to its own surface is
0.074–0.107 mm for `Bl0` and 0.079–0.175 mm for `Bl1` on all nine pieces.

Per piece — `rows / s0 rows / s0 carriers / s0 off-carriers | Bl0 dots / off-lip / carried / off-carried`:

| piece | rows | s0 | s0 carr | s0 off-carr | Bl0 | off-lip | carried | off-carried |
|---|---|---|---|---|---|---|---|---|
| 1 | 8643 | 5330 | 94 | 0 | 184 | 0 | 76 | 0 |
| 2 | 1379 | 530 | 76 | 0 | 96 | 0 | 57 | 0 |
| 3 | 2613 | 1962 | 90 | 1 | 125 | 14 | 67 | 1 |
| 4 | 1147 | 602 | 56 | 0 | 102 | 0 | 49 | 0 |
| 5 | 2159 | 1168 | 100 | 13 | 150 | 21 | 73 | 8 |
| 6 | 2793 | 1576 | 87 | 0 | 142 | 3 | 72 | 0 |
| 7 | 5253 | 3098 | 133 | 38 | 176 | 53 | 101 | 30 |
| 8 | 1999 | 921 | 96 | 13 | 126 | 9 | 66 | 8 |
| 9 | 1063 | 539 | 48 | 0 | 77 | 0 | 39 | 0 |
| **all** | **27049** | **15726** | **780** | **65** | — | — | — | — |

**What reproduces and what does not.** The off-lip dot counts reproduce the lead's ruler within the
run-to-run drift of the unseeded 30-point ray cast (`mesh_processing_headless.cpp:1526-1527`):
pieces 5/6/7/8 give **21 / 3 / 53 / 9** against the lead's 21 / 3 / 54 / 9, `Bl0` dot totals
**150 / 142 / 176 / 126** against 150 / 141 / 173 / 126, and piece 7's `cluster_id_r2 = -1` count on
surface 0 is **2,513** against the lead's 2,526.

The **carrier counts do not reproduce at one cloud spacing**, and this is a definition, not a bug:
at one spacing (0.099 mm on piece 7) I get **101 of 176** dots carried and **30 of 53** off-lip dots,
against the lead's 141 of 173 and 40 of 54. A tolerance sweep puts the lead's numbers at **1.5 ×
spacing (0.15 mm)**: exactly 141 of 176 and 43 of 53. So the lead's carrier test was half again
wider than one spacing; every carrier number in this ticket's table is at **1.0 spacing** unless
labelled otherwise. The band on piece 7 surface 0 is 3,098 rows, of which 2,513 are
`cluster_id_r2 = -1` and 585 were claimed by the growth into clusters 4/5 and re-admitted.

### A2 — the separation table (`out/sep76.tsv`)

Scored on surface 0 only: 15,726 rows, 65 off-lip carriers, 285 on-lip carriers. The ticket asks for
pieces 5–8; pieces 1, 2, 4 and 9 have no off-lip carrier and piece 3 has one, so the nine-piece set
and the 5–8 set differ by a single carrier (64 on 5–8, of which the ruler removes 63). `removed` =
share of the off-lip carriers refused, `cost` = share of the added band that is not an off-lip
carrier refused.

| candidate | best point on the bar | removed | cost | cost on carriers |
|---|---|---|---|---|
| (a) window `d_fitted_mm > T` | T = 0.10 | 0.4769 | 0.5976 | 0.3874 |
| (b) branch-angle margin | margin 5 deg | 0.1385 | 0.0934 | 0.1849 |
| (c) ray-pair `pair_rate < T` | T = 0.05 | 0.8615 | 0.2577 | 0.2238 |
| (d) band `nearest_claimed_mm > T` | T = 0.10 | 1.0000 | 0.9652 | 0.9832 |
| (d′) ruler `wall_offset_mm > T` — **oracle** | T = 0.80 | **0.9846** | **0.0495** | **0.0000** |
| combos (d ∨ c) | every pair | 1.0000 | ≥ 0.9300 | ≥ 0.99 |

At cost ≤ 0.05 **every implementable candidate removes nothing**: `a_window` T = 0.70 → 0.0000 /
0.0436, `d_band` T = 1.50 → 0.0000 / 0.0488, `c_pair` → no threshold that low is above 0, `b_angle`
→ 0.0000 at margin 0. The only row on the bar is the ruler, and it is an oracle: `wall_offset_mm` is
measured against `Surface_0`'s inner vertices, which exist only after the refinement has exported the
surface it is deciding about. It refuses **64 of 65** off-lip carriers at 0.8 mm, refuses **no on-lip
carrier at all** (`cost_carrier = 0.000`), costs the band 4.95 % and the worst surface 14.1 %, under
the 35 % starvation guard.

The gap between (d) and (d′) is the whole finding: **the same "distance off the band" test removes
98 % of the bad section when it is measured against the wall and 0 % when it is measured against the
nearest claimed point of the same surface** — because the break face is surrounded by claimed
break-face points, so a point on the face is never far from its own cluster.

### A3 — the stop rule, applied

The rule fires. No implementable candidate reaches removed ≥ 0.60 at cost ≤ 0.05; the closest is the
ruler oracle (0.9846 removed at 0.0495 cost), and no threshold on any quantity the admission loop
actually holds gets past removed 0.14 at the cost bar. So there is nothing for Part B to tune, and
Part C measures the switch **as built** (candidate (d) in its implementable form at the ticket's own
0.8 mm), which is the honest thing to hand the lead: the number is what the gate would do to the
corpus, not what a threshold chosen after seeing the answer would do.

### A4 — the fit itself

`d_fitted_mm`, median / p90 / max, on the pieces that carry the section (`out/a4_76.tsv`):

| piece | off-lip carriers | on-lip carriers | band, not a carrier |
|---|---|---|---|
| 7 | n=38 — **0.124 / 0.267 / 0.415** | n=95 — 0.078 / 0.404 / 0.877 | n=2965 — 0.153 / 0.508 |
| 5 | n=13 — 0.081 / 0.143 / 0.163 | n=87 — 0.106 / 0.205 / 0.276 | — |
| 8 | n=13 — 0.030 / 0.196 / 0.278 | n=83 — 0.044 / 0.102 / 0.202 | — |
| 6 | n=0 | n=87 — 0.073 / — / — | — |
| 3 | n=1 — 0.329 | — | — |

The bad section is **no closer** to the fitted surface than the good band — on sherd 7 it is 1.6×
further out (0.124 against 0.078 mm) — and every population sits far inside the admission window
(max `d_fitted` 0.98 mm against a window near 1.0 mm). So the ticket's A4 condition is met: the
cause is not the threshold, it is the **fitted surface running across the fracture face**. The
section is 0.85–2.73 mm off the inner wall and ~0.12 mm off the fit, which is what "the fit goes
there" looks like in these numbers. The fix is the fit, not a gate on the residual.

---

## Comments (worker, 2026-11-16) — w76b, Part C

### Where this ran

Branch `76-why-the-refinement-takes-the-break-face-back` at `3e898d6`; run dir
`/data/gpfs/projects/punim2657/SfSpp/runs/20261116-0103_3e898d6_t76-stage0` (`$RUN` below).
Six cells (3x Juglet 9 pieces, 1x Juglet 9 pieces, Pot A 8 pieces; off and gate each) plus two
extra **switch-unset** cells that measure the run-to-run noise floor. Every job below:

| job | cell | sacct |
|-----|------|-------|
| 35157883 | stage 0 build + the three off cells' driver | `COMPLETED 0:0` 00:01:59 |
| 35157927_0 | off_3x | `COMPLETED 0:0` 00:08:28 |
| 35157927_1 | off_1x | `COMPLETED 0:0` 00:01:47 |
| 35157927_2 | pota_off | `COMPLETED 0:0` 00:02:54 |
| 35179176_0 | gate_3x | `COMPLETED 0:0` 00:09:30 |
| 35179176_1 | gate_1x | `COMPLETED 0:0` 00:01:33 |
| 35179176_2 | pota_gate | `COMPLETED 0:0` 00:02:52 |
| 35179176_3 | id_3x — second switch-unset 3x run (noise floor) | `COMPLETED 0:0` 00:06:35 |
| 35179176_4 | id_1x — second switch-unset 1x run (noise floor) | `COMPLETED 0:0` 00:01:42 |
| 35179476 | measurement pass, all six cells | `COMPLETED 0:0` 00:21:56 |
| 35180198 | the two noise-floor cells' measurement | `COMPLETED 0:0` 00:07:27 |

`sacct -j 35179176,35179476,35180198,35157927,35157883 --format=JobID,State,ExitCode,Elapsed`
returns `COMPLETED 0:0` on every row; no cell was requeued, cancelled or failed.

### Part B — what was actually armed, and why it was not tuned

One switch, off by default, today's path unchanged when unset (no kd-tree is even built without
it): `SFS_REFINE_WALL_GATE=1`, with `SFS_REFINE_WALL_MAX_MM` (default 0.8) and
`SFS_REFINE_PAIR_MIN` (default -1 = off). Units are declared rather than assumed:
`SFS_TREE_UNITS_PER_MM` = 3.0 on the 3x tree, 1.0 at 1x and on Pot A. The band test is the
candidate's distance to the nearest **claimed point of the same surface**
(`segmentedSurfacePointCloud1/2`), in mm; the pair test is ticket 59's predicate in scene units,
unrescaled. `[SFS-76] REFWALL` per refusal, `[SFS-76] REFWALL-SUM piece= surface= candidates=
refused= kept= max_mm=` per surface, and the starvation guard at `SFS_REFINE_MAXDROP` 0.35
printing `[SFS-76] REFUSED`.

**The gate is armed at 0.8 mm as built, because A2's stop rule fired and left nothing to set.**
At cost ≤ 0.05 every implementable candidate removes 0.0000 of the section; the only rule that
reaches 0.60 removed is the `wall_offset_mm` oracle (0.9846 at 0.0495), and the oracle reads the
**exported** S0, so it cannot exist at the admission rung. The pair gate stayed at its default
off. This is Part B's instruction resolving to the default the code already carries — recorded
here rather than tuned to fit the outcome.

### Part C — `gate76.tsv`

`$RUN/out/gate76.tsv`, 160 rows, columns `group metric piece off gate ref verdict`, groups
`primary`, `pairs`, `j1_ruler`, `pota`, `coverage`, `identity` (+ a `switch` census and the
`render` row). Built by `$RUN/tools/gate76.py` (mirror `C:/PR/artifacts/t76/gate76.py`).

**Primary, 3x, the four bar pieces** (`meas_off_3x.tsv` vs `meas_gate_3x.tsv`):

| piece | off-lip dots off → gate | off-lip contour mm off → gate | contour mm | bar | verdict |
|-------|------------------------|-------------------------------|------------|-----|---------|
| 5 | 21/150 → 21/150 | 12.6 → 12.6 | 90.32 → 90.36 | not worse than 21 dots | PASS |
| 6 | 3/142 → 2/138 | 1.8 → 1.2 | 85.26 → 83.13 | not worse than 3 dots | PASS |
| 7 | 53/176 → 48/168 | **31.20 → 28.20** | 105.51 → 100.60 | **< 12 mm** | **FAIL, by 16.20 mm** |
| 8 | 9/126 → 9/128 | 5.4 → 5.4 | 75.36 → 76.12 | not worse than 9 dots | PASS |
| pooled 5–8 | 86/594 → 80/584 | — | — | not worse than 87/590 | PASS |

Sherd 7 loses 5 off-lip dots and 3.00 mm of its 31.20 mm section — 9.6% of the section — and
the section is still 16.20 mm above the bar afterwards. The bar asks for 31.20 → under 12.00 mm.

**Noise floor** (`meas_id_3x.tsv`, a second switch-unset run of the same binary; the mesh stage
draws 30 unseeded ray-cast points, `mesh_processing_headless.cpp:1526-1527`): off-lip dots
5: 21→21, 6: 3→3, **7: 53→52**, 8: 9→9; off-lip contour identical on all four; `nBl0` ±3;
piece 1 `blindDeg` 25.24 → 24.41. So the gate's 5 dots on sherd 7 is ≈4 dots beyond noise, and
its 3.00 mm is a real but small move: the section survives at 28.20 mm.

**The gate's effect is not confined to the bar pieces.** On the 3x tree the biggest mover is
**piece 3** (not in the bar set): 14 off-lip dots → 5, 9.06 mm → 3.00 mm. On piece 1 the gate
makes the blind stretch **worse**: `blindDeg` 25.24 → 35.48 (+10.2°). At 1x piece 1 improves
hugely (10 → 2 off-lip dots, 21.4 → 3.6 mm, `nBl0` 28 → 57, `blindDeg` 45.89 → 21.40) while
piece 7 and piece 5 get slightly worse (7: 19 → 20 dots, 32.4 → 34.2 mm; 5: 5 → 6, 9.0 → 10.8 mm);
pooled 1x pieces 5–8 is **37 → 37**. A rule whose sign flips with the piece and the bundle cannot
carry a reading on its own; that is why the reading below rests on A4 plus this table, not on the
gate's arithmetic.

**Wall cost — all PASS.** 3x S0+S1 vertex counts, worst −1.7% (piece 1 S0, 90,735 → 89,159);
1x worst −7.6% (piece 1 S0, 13,834 → 12,778); Pot A worst −1.7% (P06 S0, 22,830 → 22,446).
Nothing near the 10% bar; the trim guard never fired.

**Pairs** (Juglet, `pairdot72.py` vs `Dataset/Juglet_GT`): the nine touching-pair median normal
dot products keep their sign on 9 of 9, 8 of 9 positive in both arms, every median within 0.10
between `off_3x` and `gate_3x`. `pair_pota_*.tsv` do not exist — `pairdot72.py` needs GT poses
and Pot A has none; the pairs group is Juglet-only by construction.

**J1's frozen ruler** (piece 1, `off_1x` vs `gate_1x`; the noise column is 0, `id_1x` == `off_1x`
on every frozen number): `blindDeg` 45.89 → 21.40 PASS, `farS0` 0.8936 → 0.5254 PASS,
`ring_cov_deg5` 355 → 360 PASS, `f2r_le1` 0.4497 → 0.8584 PASS, **`r2f_le1` 0.4435 → 0.3329
FAIL (−24.9% against a 10% bar)**. The frozen t57 reference values (68.38° / 0.6729 / 250° /
0.4211) do not match `off_1x` either, so the four numbers are only readable as a within-session
delta — four of five move the right way by a wide margin and one moves the wrong way.

**Pot A: the 8-of-8 bar FAILS.** 6 of 8 within 1 off-lip dot (P02 0 → 4, P04 3 → 10) and 6 of 8
lines within 1% of their own dot count (P04 147 → 145, P06 145 → 142). P01 is 210/210 off-lip in
both arms (its own baseline). On a control bundle with no break-face problem to solve, the gate
**moves dots off the wall**: P02's 4 and P04's 7 are dots the switch made read as off-lip.

**Coverage:** S0/S1/Bl0/Bl1 present on 9 of 9 3x off and gate, 9 of 9 1x off and gate, 8 of 8
Pot A off and gate — PASS throughout.

**Identity:** at 1x the geometry is identical (max nearest-point distance 0.000 mm on 9 of 9) but
the bytes are 18 of 36 — S0/S1 byte-identical, Bl0/Bl1 differ on every piece. That difference is
**not attributable to the switch**: both `off_1x` and `id_1x` are switch-unset, and the
uninitialised curvature column makes Bl0/Bl1 differ between any two runs. The ticket's
*"byte-identical 1x outputs"* is therefore **not met as written**; what is met is identical
geometry and a byte difference that predates this ticket. At 3x the max nearest-point drift is
piece 1 **2.147 mm**, P7 0.641, P6 0.417, P5 0.390, P8 0.330, the rest 0.000 — against the
ticket's 0.71 mm bound this **FAILS on piece 1**, but piece 1's own run-to-run spread was measured
at 2.418 mm (ticket 73), i.e. the bound is tighter than the corpus's own non-determinism on that
piece. Read the 3x identity column as "the drift is inside the noise the binary already has",
not as a pass.

### The render — looked at before the reading

`C:/PR/artifacts/t76/render76_before_after.png` (also `$RUN/out/render76_before_after.png`),
three panels per row, top `off` / bottom `gate`, off-lip dots red (>0.8 mm off the inner lip),
on-lip green. Sherd 7: 176 dots / 53 off-lip (30.1%) → 168 / 48 (28.6%) — the red arc runs
straight across the fracture face in **both** panels, unobstructed. Sherd 5: 150/21 → 150/21,
visually identical. Pot A P02 (highest refused share on its surface 0, 334 of 766 = 43.6%):
163 dots / 0 off-lip → 162 / 4 — the gate puts red where there was none.

### Reading

**`the-fit-crosses-the-face-and-no-threshold-gate-can-separate-it`**

Part A's A4 found the off-lip carriers no farther from the fitted surface than the on-lip band
(piece 7: 0.124 mm median against 0.078), every population inside a ~1.0 mm window — so the fit
spans the face. Part C shows what follows: the one rule that would remove the section (the oracle)
cannot be evaluated at the admission rung, and the implementable rule leaves 90% of the section in
place while making the blind stretch worse on one 3x piece, splitting on the 1x bundle, and moving
dots off the wall on Pot A. The gate is neither the repair nor neutral; it is aimed at the wrong
quantity.

### End state: ready

Everything Part E asks for exists and every bar above carries its verdict. In sum: the primary
bar fails on sherd 7 only (16.20 mm short) while the other three pieces and the pool hold; wall
cost holds everywhere and nowhere near 10%; the nine pair signs hold; four of J1's five frozen
numbers hold and `r2f_le1` does not; Pot A's 8-of-8 fails at 6 of 8; and the 3x identity bound
fails on piece 1 against a noise floor it does not clear.
Nothing is committed — the lead lands the branch. Two tracked files carry the work:
`mesh_processing_headless.cpp` (+277/−2 against `3e898d6`) and this ticket; everything else is
scripts and tables under `$RUN` and `C:/PR/artifacts/t76/`.

## Lead — verification and adjudication (2026-11-16, Thinkbook16)

### What the lead recomputed itself

- **The off-lip ruler** (`C:/PR/artifacts/t76/lead_offlip76.py`, the frozen rule: inner = normal ·
  radial < −0.2, off = nearest inner point > 0.8 mm, contour = consecutive steps), run on the cells'
  own exported geometry (`outoff_3x/geom`, `outgate_3x/geom`): `off_3x` 1 184/0 (110.85 mm),
  5 150/21 (12.60 of 90.32), 6 142/3 (1.80 of 85.26), 7 176/53 (31.20 of 105.51, median 0.183),
  8 126/9 (5.40 of 75.36), pooled 594/86 (51.00 mm); `gate_3x` 181/0, 150/21 (12.60), 138/2 (1.20),
  168/48 (28.20 of 100.60), 128/9 (5.40), pooled 584/80 (47.40 mm). Exact match to every row of
  `gate76.tsv`.
- **The A2 separation table** (`C:/PR/artifacts/t76/lead_sep76.py`, recomputed from
  `refine76.tsv`): band 0.10 → removed 1.0000 / cost 0.9652, 0.20 → 0.7077/0.7184, 1.50 →
  0.0000/0.0488; window 0.10 → 0.4769/0.5976, 0.25 → 0.1231/0.2640, 0.50 → 0.0000/0.0972;
  pair 0.05 → 0.8615/0.2577, 0.20 → 0.9538/0.9763; ruler 0.60 → 1.0000/0.0635, 0.80 →
  0.9846/0.0495, 1.00 → 0.8923/0.0428. Every number reproduced.
- **The render**, opened before the reading: sherd 7 carries the red arc across the lower-right rim in
  both panels (176/53 → 168/48, the arc slightly shorter, still crossing the face); sherd 5 is
  unchanged 150/21; Pot A P02 goes 163/0 → 162/4 with red appearing on the right rim where there was
  none.
- **The noise floor**: `id_3x` (switch unset, same binary) piece 5 21/21, 6 3/3, 7 53/52 (−1 dot,
  +0.0 mm), 8 9/9 — so the gate's 5-dot move on sherd 7 is above its own repeat spread.
- `accept76.py` 32/34; the two failures are mine (`boxes_ticked`, ticked at landing, and
  `refine76_pieces`, whose parser expected an integer piece column where the table carries
  `Juglet_Piece_<n>`).

### Adjudications

1. **The primary bar fails on one sherd, and by a distance that matters.** Sherd 7 is 31.20 mm
   against the landed 31.80 mm, so the armed gate removes 3.0 mm — 9.6% of the section — not the 62%
   the < 12 mm bar asks for. Sherds 5, 6, 8 and the pool hold.
2. **The Pot A control convicts the 0.8 mm band rule on its own terms.** P02 0 → 4 off-lip dots and
   P04 3 → 10, i.e. 6 of 8 within 1 dot, so this rule cannot be a default whatever it buys on the
   juglet.
3. **J1's ruler worsens on one column, `r2f_le1` 0.4435 → 0.3329 (−24.9%)**, against a bar of 10%.
   Four of the five frozen numbers hold (blind stretch, far-skin share and ring coverage improve).
4. **The 3x identity bound is not evidence either way**: piece 1's 2.147 mm sits inside the 2.418 mm
   run-to-run spread already measured on that piece (ticket 74), and 0 identical subsets on every 3x
   piece is the normal shape of a multi-threaded non-deterministic build. The 1x surface subsets are
   byte-identical (18 of 36), and the breakline byte difference is the known writer defect — the PCD
   segment header's `totalPts` and the uninitialised curvature field differ (piece 5: `# 2 49 0`
   against `# 2 47 0`, `WIDTH 47` both) while the geometry is identical (0.000 mm).
5. **The worker's closing summary is right and the pooled table row is not a contradiction.** "The
   nine pair signs hold" is the true statement: 6-7 is negative in both arms by construction (its
   break-face line is anti-parallel), so the pooled row's "8 of 9 positive" counts positives, not
   agreements. Nobody should read 8 of 9 as a failed sign.
6. **The carrier definition is the lead's, not the ticket's, and the conclusion does not depend on
   it.** At 1.5× cloud spacing piece 7 carries 141 of 176 dots with 43 of its 53 off-lip dots
   carried; at the ticket's 1.0× it carries 101 of 176 with 30 of 53. The off-lip ruler is
   dot-based, so A2's separation verdict stands either way.
7. **A4 is accepted with its caveat.** "The fit crosses the face" is consistent with the numbers —
   the off-lip carriers are no farther from the fitted surface than the on-lip band, and every
   population lies inside a ~1.0 mm window against a 0.98 mm maximum — but it is not proven
   geometrically. What *is* proven, and is enough, is that no residual threshold separates the two
   populations.
8. **The reading stands, and it is claim (1), the method fails.** The section is carried by the
   fitted surface, so any gate that works must measure the wall that the surface covers; at the
   admission rung that wall does not exist yet, which is why the only rule that would work (the
   oracle, 64 of 65 refused, 0.0 carrier cost) is not implementable there and why every implementable
   rule either removes nothing at a 5% wall cost or costs 60–97% of the wall to remove part of the
   section.

### What the lead proposes next (proposed, not written)

The admission needs the wall as an input rather than an inference: a **two-pass admission** — export
once with the gate off, measure every added point's distance to the interior wall of that pass, then
re-run the admission with that ruler supplied (e.g. `SFS_REFINE_WALL_FROM=<ply>`). It can be
replayed offline on `refine76.tsv` before any job. The cheaper alternative is to estimate the wall
inside the loop from the claimed cluster's own boundary offset along the ray-pair direction, and the
measurement that decides between the two is whether that estimate reproduces the oracle's refusal set
(64 of 65 at 0.8 mm).

verified: `C:/PR/artifacts/t76/lead_offlip76.py` -> gate_3x 168/48 (28.20 mm), off_3x 176/53
(31.20 mm); `C:/PR/artifacts/t76/lead_sep76.py` -> ruler 0.80 gives 0.9846/0.0495, band 1.50 gives
0.0000/0.0488; `gate76.tsv` pota P02 0→4, P04 3→10; run repeat `id_3x` 53→52 dots.
