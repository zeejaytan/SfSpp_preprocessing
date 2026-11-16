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

**Status:** ready-for-agent
**Working in:** chat on Thinkbook16 (2026-11-16)
**Branch:** to be created at dispatch
**Worker:** unassigned

## Given — what the numbers already say

1. **The line rides points the growth never claimed.** On sherd 7 of the 3x run
   (\`20261115-2005_b394663_t73-arms\`, cell \`off_3x\`), the exported interior patch
   \`Juglet_Piece_7.S0\` has 46,235 rows over 24,702 distinct positions; **2,526 of those rows
   are points with \`cluster_id = -1\` at the pre-merge rung** — never claimed by the growth.
   Those rows are exactly the set the refinement **admitted** at rung 4: 2,489 of the 2,526
   match the recorded admitted points within 0.02 tree units (2,512 within 0.5), median 0.000.
   The rung's own counts reconcile: 29,744 + 1,792 = 31,536 one way, 22,104 + 2,510 = 24,614
   the other. No merge happened on this piece (\`r3 merges []\`, 66 pairs tested).

2. **The line's carriers are those rows.** 141 of the 173 Breakline_0 dots sit on admitted rows,
   and **40 of the 54 off-lip dots** do; the on-lip dots ride the same band (101 of 119). So the
   band is not a defect in itself — the line simply follows the patch boundary, and the patch
   boundary is the outer edge of the admitted band.

3. **The band is mostly wall; only a section of it crosses the face.** The lead measured
   ticket 59's ray-pair test on piece 7 (ray through the clay along \`-n\`, t 1.5–10 mm,
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

5. **The admission rule, as the code stands.** \`improveSurfaceBoundaryByFittingBSplineSurface\`
   (\`mesh_processing_headless.cpp:2536\`) measures a window per surface with
   \`window26Select\` (:2314) from the fitted B-spline's residual and the other cluster's
   distance, raw 3.0 mm default, clamped to [0.5, 6.0] (:1687–1698, :2366–2368), then admits a
   point when \`euclideanDistance(ptOnFittedSurface, ptOnOriginalMesh) < windowLenMM\` **and**
   \`angleDiff > 140\` (:2671) or **and** \`angleDiff < 40\` (:2683). Ticket 73's
   \`admit73\` (:2636–2669, \`SFS_REFINE_ADD_GATE\`, default off, angle 30 deg) already
   refuses some of these, but it moved only 4 dots of 86 at 3x: the nearest claimed point is
   almost always within 30 deg of the added point, because the band is wall.

6. **The tunables that exist or could exist** — this ticket must rank them by measurement, not
   by preference:
   (a) **the window length** (\`clampedMM\`, and its clamps 0.5 / 6.0). No env switch today.
   (b) **the normal-angle branches** (140 deg / 40 deg), hard literals at :2671 and :2683.
   (c) **a per-point ray-pair gate** ported from ticket 59 (arm code archived at
   \`/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1416_638504b_t59-breakstop-arm/work/mesh_processing_headless.patched.cpp\`).
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

**A1 — the record.** Add a \`[SFS-76] ADMITDOT\` line inside the admission loop (print the
values the decision already computes) and a \`refine76.tsv\` with one row per added-back point:

| column | meaning |
|---|---|
| \`piece\`, \`surface\` | Juglet piece, surface index (0 interior / 1 exterior) |
| \`point_index\` | index in the piece cloud |
| \`d_fitted_mm\` | \`euclideanDistance(ptOnFittedSurface, ptOnOriginalMesh)\` |
| \`angle_deg\` | \`angleDiff\` at the decision |
| \`branch\` | \`own\` (>140) or \`other\` (<40) |
| \`cluster_id_r2\` | the growth's verdict at the pre-merge rung |
| \`nearest_claimed_mm\` | distance to the nearest claimed point |
| \`nearest_claimed_ang_deg\` | angle to that point's normal |
| \`pair_rate\` | ticket 59's predicate at the point (ray through the clay) |
| \`wall_offset_mm\` | distance off the interior wall (the 0.8 mm ruler) |
| \`carrier_of_line\` | 1 if a Breakline_0 dot sits within one spacing of this point |
| \`off_lip_carrier\` | 1 if that dot is off-lip at 0.8 mm |

**A2 — the separation table.** \`sep76.tsv\`: for each candidate gate of Given 6, over a small
threshold grid, the confusion on the 3x pieces 5–8:
- **removed** — share of the off-lip section's carriers the gate refuses (target ≥ 0.60),
- **cost** — share of the added band that is *not* an off-lip carrier the gate also refuses,
- **surfaces** — the nine pieces still produce S0/S1,
then the same numbers re-scored on Pot A and on 1x, labelled as the control cost.

**A3 — stop rule.** If no candidate reaches 0.60 removed at ≤ 0.05 cost, stop with the reading
\`no-gate-separates\` and name the closest; do not guess one.

**A4 — the fit itself.** Report \`d_fitted_mm\` for the off-lip carriers against the on-lip
carriers on the same piece. If the bad section is no closer to the fitted surface than the good
band, the cause is not the threshold but the **fitted surface bulging across the fracture face**
— say so, because that changes the fix (the fit, not the gate).

## Part B — exactly one default-off gate, chosen by A2

One switch, off by default, today's path byte-identical when unset:

- \`SFS_REFINE_WALL_GATE=1\` with at most two thresholds (\`SFS_REFINE_WALL_MAX_MM\`,
  \`SFS_REFINE_PAIR_MIN\`) — the names follow whichever of Given 6 A2 selects; if (a) or (b)
  wins instead, expose \`SFS_REFINE_WINDOW_MM\` / \`SFS_REFINE_ANGLE_DEG\` in the same shape.
- Log \`[SFS-76] REFWALL\` per refusal and a \`[SFS-76] REFWALL-SUM\` per surface with
  \`candidates / refused / kept\`, so the cost is visible in the run, not just in the table.
- No starvation: the existing trim guard stays; if a surface would lose more than
  \`SFS_REFINE_MAXDROP\` (default 0.35) of its points, refuse the gate for that surface and
  print \`[SFS-76] REFUSED\` — a starving surface is worse than a travelling line.

## Part C — cells and the gate table

| cell | bundle | pieces | purpose |
|---|---|---|---|
| \`off_3x\` | 3x | 9 | baseline, gate unset |
| \`gate_3x\` | 3x | 9 | the gate |
| \`off_1x\` | 1x | 9 | baseline, J1 ruler |
| \`gate_1x\` | 1x | 9 | the gate at 1x (no geometry estimator may be needed) |
| \`pota_off\` | Pot A | 8 | control baseline |
| \`pota_gate\` | Pot A | 8 | control under the gate |

\`gate76.tsv\` — columns \`group, metric, piece, off, gate, ref, verdict\`, groups
\`primary\`, \`pairs\`, \`j1_ruler\`, \`pota\`, \`coverage\`, \`identity\`.
Bars:

- **primary**: sherd 7 off-lip contour < 12 mm; sherds 5, 6, 8 not worse than their off counts
  (21 / 3 / 9 dots); pooled not worse than 87 / 590 dots;
- **wall cost** (the new column this ticket needs): S0 and S1 vertex counts on every 3x piece
  not down more than 10% against \`off_3x\`, and the 1x surfaces not down more than 10%;
- **pairs**: the nine touching-pair median normal dots keep their sign, 1-4 positive with 0
  opposed, other pairs within 0.10 of the off arm;
- **j1_ruler**: no column worse by more than 10% on the four frozen numbers
  (blind stretch, far-skin share, reverse coverage, r2f_le1) from
  \`/data/gpfs/projects/punim2657/SfSpp/runs/20261102-0450_05be12c_t57-sweep/check_separation.py\`;
- **pota**: 8 of 8 pieces within 1 off-lip dot of the Pot A baseline, and every Pot A line's own
  dot count within 1% — the controls are the point of this ticket, not an afterthought;
- **coverage**: S0, S1, Bl0, Bl1 on 9 of 9 3x, 9 of 9 1x, 8 of 8 Pot A;
- **identity**: with the switch unset, byte-identical 1x outputs and ≤ 0.71 mm 3x nearest-point
  drift against \`off_3x\`.

Render \`render76_before_after.png\`: sherd 7 (and sherd 5) off vs gate, the off-lip dots
marked, plus one Pot A piece where the gate bites hardest.

## Part D — readings (pick one, verbatim)

- \`the-gate-removes-the-section-and-keeps-the-wall\`
- \`the-gate-removes-the-section-but-costs-the-wall\`
- \`the-fit-crosses-the-face-and-no-threshold-gate-can-separate-it\`
- \`no-gate-separates\`
- \`the-gate-is-neutral-and-the-band-is-wall\`

## Part E — acceptance

- [ ] \`refine76.tsv\` has one row per added-back point on all nine 3x pieces.
- [ ] \`sep76.tsv\` scores all four candidate gates of Given 6 over a threshold grid.
- [ ] The stop rule of A3 was applied, and A4 answers whether the fitted surface crosses the face.
- [ ] Exactly one switch, default-off, with today's path unchanged when unset.
- [ ] \`gate76.tsv\` carries the wall-cost columns, not just the off-lip ones.
- [ ] Pot A and 1x were run, and their deltas are in the table.
- [ ] The render was looked at before the reading was chosen.
- [ ] Every \`sbatch\` has its \`sacct\` State/ExitCode recorded.
- [ ] Nothing is committed by the worker; the lead lands it.

## Out of scope

- The trace-side guard (closed by the conservator's ruling, 2026-11-15).
- The growth-side doors of tickets 72–75 (closed; they may be armed as controls but are not
  retuned here).
- Sweeping the growth thresholds or the merge gate.
- Anything under \`class/\`, \`hpc/\`, \`assembler/\`; \`run_cell66.sh\` itself; \`Dataset/\`; the
  \`px3\` tree.
