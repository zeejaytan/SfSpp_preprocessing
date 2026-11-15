# 72 — Trim the break face out of the interior surface, so its boundary can land on the inner lip

**What to build:** the cure the conservator ruled for on 2026-11-15 — stop the interior
surface from swallowing the break face, using the ray-pair signal ticket 59 measured, run as a
trim AFTER the growth instead of a stop INSIDE it. Part A is read-only and comes first: prove
on sherds 5-8 that the outboard stretches of the traced line are break-face points of the
interior patch, not a tracer fault. Part B is one default-off switch (`SFS_BREAK_TRIM`) with its
ray window derived at run time. Part C is the gate the conservator set, with a before/after
render. A null Part A (the outboard dots' carrier points pair like wall) ends the ticket: then
the patch is not the carrier and the tracer is.

**Why now (2026-11-15, conservator, verbatim):** "I'd fix the surface first, not the trace
guard. The guard picks between edge lines that already exist, and on sherds 5-8 the line you
want was never produced. ... In the paper's design, the edge line is the boundary of an
interior surface that stops before the break face. Ticket 04 saw this work on Pot A piece 2:
the points the growth refused, which were the break face, sat on the true rim at 0.53 mm. On
sherds 5-8 the growth swallows the break face, so the boundary lands on the outer lip. This is
claim (1): the method fails. It is not the measurement or the reference." Then: "write the
ticket and dispatch with normal subagent".

**Answers:** U19 (does the pipeline put the Juglet back together), E1 (do our breaklines let
SfS find joins)

**Blocked by:** none. Uses ticket 59's archived arm code and the t333 3x tree READ-ONLY.
Ticket 65's separation scorer is the J1 ruler and must not be re-invented; ticket 328's
per-pair sign numbers are the sign ruler.

**Status:** ready-for-agent
**Working in:** not started
**Branch:** to be created at dispatch
**Worker:** unassigned

## Spec

### Given (measured facts this stands on — do not re-measure, cite these)

1. **The line leaves the inner lip on sherds 5-8, and it is the line we ship.** On the 3x tree
   (`/data/gpfs/projects/punim2657/SfSpp/runs/20261112-1238_55473e9_t333-juglet-large/work/trees/px3/juglet`),
   distance of each Breakline_0 dot to the nearest point of the interior patch (Surface_0):
   dots more than **0.8 mm** off the inner wall — piece 5 **21 of 150 (14 %)** over 13 of
   90 mm of contour, piece 6 **3 of 141 (2 %)** over 2 of 85 mm, piece 7 **53 of 174 (30 %)**
   over 31 of 105 mm, piece 8 **9 of 126 (7 %)** over 5 of 75 mm. At the tighter 0.5 mm cut:
   27/150 (18 %), 6/141 (4 %), 56/174 (31 %), 11/126 (9 %). Median drift off the wall
   1.2 / 0.8 / 1.9 / 1.4 mm, maxima 2.1 / 1.2 / 2.7 / 1.6 mm. Script of record for these
   numbers: `C:/PR/artifacts/visual-qa/edgeline_juglet/offlip08.py` (0.8 mm) and `offlip.py`
   (0.5 mm).
2. **The tracer reads the patch, not the mesh.** `processFragmentData` gives the edgeline
   extractor the cleaned surface patch (`edgeline_extraction_headless.cpp:3212-3215`:
   `cleanSamples(surfacePointCloudFilePath)` then
   `estimatePatchNormalsAndBreakLinesFromSimpleAlgo_BSplineSurface`). The trace sits
   0.25-0.29 tree units (0.08-0.10 real mm) from its own input patch, so the tracer is
   faithful and the patch is the carrier. No direction or face guard exists anywhere in the
   extractor (grep `cone|forward|heading` finds only an unrelated comment at :725).
3. **Surface_0 is the interior on all nine (ticket 328), and it carries the break face on
   5-8.** Outward-facing points *inside* Surface_0 (normal dot radial-outward > 0.2): piece 5
   **486**, piece 6 **115**, piece 7 **2672**, piece 8 **109**; their median distance to the
   exterior patch Surface_1 is 3.34 / 0.73 / 3.44 / 1.14 tree units. The trace dots that sit
   on those points: 27 / 20 / 59 / 11. So the fault enters at the patch boundary, not at the
   face choice: Surface_0 is interior at the surface level (87.5-100 % inward normals) and the
   T04 interior-first swap is a no-op on this vessel.
4. **The paper's expectation is that the boundary of the interior surface is the rim.** Ticket
   04: on Pot A piece 2 the points the growth refused were the break face and they sat on the
   true rim at 0.53 mm. Ticket 26 (lead verdict 2026-10-27): shrinking the 3 mm admission
   window changes which points land where but produces **no** new genuine Juglet wall pair —
   the window is neither the repair nor the thing that merges the walls. Do not re-open it.
5. **The signal exists, measured on all nine, and its code is archived.** Ticket 59 Stage 0:
   thickness pairing — a ray from a point along its normal within [0.5, 2.5] x wall thickness
   meets the opposing wall — pairs **89.15-97.50 %** of wall points per piece against
   **5.6-16.4 %** of fracture-face points and 1.1-25.5 % of roll points; interior/anomaly faces
   pair at 63-83 %. Window envelope over the nine pieces 0.938-7.098 mm. The implementation of
   that arm is kept at
   `/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1416_638504b_t59-breakstop-arm/work/mesh_processing_headless.patched.cpp`
   with its diff at `.../work/patch.diff` (8 `BREAK_STOP` sites). **Port that predicate**
   (`g_breakStop`, `SFS_BREAK_STOP_{MIN,MAX,EPS}_MM`, `_EXIT_DOT`, defaults 0.9 / 7.2 /
   0.45 / -0.4) — do not reinvent the ray cast.
6. **Why 59's stop failed, and why a trim is a different experiment.** Armed on all nine it
   removed the surface on J1 (13,850 points -> 351) and dropped the genuine-pair guard to 8/9
   (job 34199881, COMPLETED 0:0), so it was never adopted. Two reasons, both avoidable now:
   (a) that run used the pre-ticket-62 normals, which were 41.88 % flipped on J1, and ticket 62
   fixed the normal estimation the next day; (b) it ran as a stop INSIDE the growth
   (`mesh_processing_headless.cpp:4894-4908`, theta consumed by the region grow at :3853), so
   rejecting one point also blocked everything beyond it — a trim after the growth cannot
   starve the surface that way. It was also scored on far-side spill, never on how far the line
   sits from the inner lip, so it has never been tested on this defect.
7. **Scale.** The tree is the 3x bundle: **1 real mm = 3 tree units** (ticket 350, verified:
   translation ratio exactly 3.000000). Ticket 59's window 0.9-7.2 mm was set on the 1x chain,
   so in a 3x run those absolutes are 3x too small. The window must be derived per run (Part B).
8. **The guard route is closed.** Pot A tickets 75/78 cured a different fault (two parallel
   loops, a hop between them; on 5-8 there is only one loop). Do not implement, default-on, or
   re-propose a trace guard in this ticket.

### Part A — read-only: whose points is the line on? (sherds 5-8, 3x tree, no code change)

For every Breakline_0 dot of pieces 5-8, find its nearest Surface_0 point (the carrier) and
report, per dot:

    dot  d_inner_mm  d_outer_mm  carrier_pairing  carrier_pair_mm  carrier_dot_radial  off_lip_08  carrier_offS1_tu

where `carrier_pairing` is ticket 59's predicate evaluated on the carrier point (1 = a ray
within [0.5, 2.5] x the run's median paired thickness meets the opposing wall, 0 = it does
not), `carrier_pair_mm` the hit distance (blank when unpaired), and `carrier_dot_radial` the
carrier normal dotted with the outward radial direction. Deliver
`C:/PR/artifacts/t72/carrier72.tsv` (one row per dot, about 590 rows) and a summary that
answers, with numbers:

- split the dots at the conservator's 0.8 mm line and report the **pairing rate of the
  carriers** on each side, per piece and pooled: the prediction is that the outboard dots'
  carriers are mostly unpaired (break face) and the on-lip dots' carriers mostly paired (wall).
  Ticket 59's separator is 89-97 % vs 6-16 %; state the two rates you measure.
- the same split by `carrier_dot_radial > 0.2` (outward-facing carrier), so the two independent
  labels can be compared without either one defining the answer.
- the pairing rate of Surface_0 as a whole per piece, and of Surface_1, so the 3x chain can be
  compared with 59's 1x numbers (5-8 and, as a control, piece 1).
- the run-time median paired thickness per piece in tree units **and** real mm.

Part A is a stop: if the outboard dots' carriers pair at the same rate as the on-lip dots' (no
separation), say so with the numbers, take the reading, and do **not** build Part B.

### Part B — the trim (one switch, default off)

Add `SFS_BREAK_TRIM` (default off, banner `break trim: off|on` and the derived window printed).
Where it applies: the cluster assigned to **Surface_0**, after the interior/exterior decision and
**before** `improveSurfaceBoundaryByFittingBSplineSurface`, in the path that writes
`<stem>_Surface_0.ply/.xyz` (locate the block; ticket 327 cites :3688 and :4008, ticket 26 cites
:1250 — report the exact lines you used in the write-back). Semantics:

1. **Window, derived per run — not 59's absolutes.** Pass 1: evaluate the pairing test over a
   deterministic sample of the sherd's points with a generous search, take the median hit
   distance `t` (this is measured on wall points and is the sherd's wall thickness at that
   scale). Window pass 2: `[SFS_BREAK_TRIM_LO * t, SFS_BREAK_TRIM_HI * t]` with defaults 0.5 and
   2.5. Print `t` in tree units and in real mm (divide by 3).
2. **Trim:** remove every Surface_0 point the predicate calls unpaired, keep the rest, then let
   the existing boundary improvement and save run unchanged on what is left.
3. **Starvation guard (mandatory, logged):** if the trim would drop more than
   `SFS_BREAK_TRIM_MAXDROP` (default 0.35) of the cluster, or leave fewer than
   `SFS_BREAK_TRIM_MINPT` (default 400 at 3x; scale with the point count as the other count
   floors do), **keep the untrimmed surface** and print a `[SFS-72] TRIM-REFUSED` line with the
   counts. This is the J1 lesson (13,850 -> 351) made into a rule, not a hope.
4. **Off-path identity:** with the switch unset, the run must reproduce the shipped tree's
   `Surfaces/*.ply|.xyz` and `Breaklines/*_Breakline_0.pcd` dot-for-dot (state which comparison
   you used: byte-identical, or identical point count plus max deviation 0).

### Part C — the gate (the conservator's numbers)

One 3x cell per arm and one 1x control cell, all from a patched private build; no canonical
input is edited; each job's `sacct` State/ExitCode recorded.

| arm | pot | cell | purpose |
| --- | --- | --- | --- |
| trim_off | Juglet_large (3x) | `SFS_BREAK_TRIM` unset | identity against the shipped tree |
| trim_on | Juglet_large (3x) | `SFS_BREAK_TRIM=1` | the cure, pieces 5-8 and all nine |
| ctl_jug | Juglet (1x) | `SFS_BREAK_TRIM=1` | J1's boundary must not get worse; the other eight unchanged |
| ctl_pota | Pot A (1x) | `SFS_BREAK_TRIM=1` | no harm on the pot that works |

Measure and tabulate (`C:/PR/artifacts/t72/gate72.tsv`):

- **the primary gate:** the off-lip share at 0.8 mm on pieces 5-8, before -> after, per piece
  and pooled, with the contour length it covers in mm. Baseline 14 / 2 / 30 / 7 %.
- **J1's boundary, before -> after**, in ticket 65's frozen ruler numbers (blind stretch,
  far-skin share, reverse coverage) from
  `.../runs/20261102-0450_05be12c_t57-sweep/check_separation.py` — run it, do not re-invent it.
  J1's worn quarter is the ceiling: it may not get worse.
- **the sign gate:** for each of the nine touching pairs at the key poses, the median normal dot
  between the two lines' facing dots, before -> after; none may turn negative, and none may
  fall more than 0.10 below ticket 328's recorded value. State the nine values.
- **Pot A:** the same separation numbers as `ctl_pota` shipped gives, before -> after, with no
  harm stated as numbers.
- **the line lives:** Breakline_0 dot counts per piece, before -> after, and the count of pieces
  that still produce a line at all (must stay 9/9 at 3x and at 1x).

Render `C:/PR/artifacts/t72/render72_trim_before_after.png`: four panels over sherds 5-8 (or
the worst two), before above and after below, with the patch's break-face strip shaded, the line
coloured by side of the 0.8 mm test, and the per-piece count in the caption
(`21 of 150 -> n of m`). A figure that cannot be read at that size is not a figure.

### Part D — readings (exactly one, as a final line `Reading: <slug>`)

- `the-patch-carries-the-line-and-the-trim-cures-it` — Part A separates, and the gate's primary
  number falls on 5-8 with J1, the signs and Pot A all clean.
- `the-patch-carries-the-line-but-the-trim-does-not-cure-it` — Part A separates, the trim runs,
  but the line stays outboard (say by how much, and whether the boundary moved at all — if the
  boundary moved and the line did not, the carrier claim is wrong somewhere).
- `the-line-is-not-on-break-face-points` — Part A does not separate: the tracer, not the patch,
  is the carrier. Give the two rates.
- `the-trim-breaks-what-worked` — 5-8 improve but J1's boundary, a touching-pair sign, or Pot A
  gets worse. A real possible ending; report it, do not tune it away.
- `inconclusive` — the chain did not complete, or a ruler could not be applied. Say which.

### Part E — acceptance (tick each; the lead verifies each)

- [ ] Part A table at `C:/PR/artifacts/t72/carrier72.tsv` with the columns above, one row per dot
      for pieces 5-8, and the paired-vs-unpaired split reported per piece and pooled.
- [ ] The 3x pairing rates for Surface_0 and Surface_1 per piece, beside ticket 59's 1x rates, and
      the run-time median thickness per piece in tree units and real mm.
- [ ] `SFS_BREAK_TRIM` exists, is default off, announces itself, and the window is derived per run
      and printed (not 0.9-7.2 mm).
- [ ] The starvation guard exists, is logged with counts, and its firing (or not) is stated.
- [ ] `trim_off` reproduces the shipped 3x Surfaces and Breaklines within the stated comparison.
- [ ] `trim_on` published its Surfaces and Breaklines; dot counts and the 9/9 line count stated.
- [ ] Gate table `C:/PR/artifacts/t72/gate72.tsv` with the primary number per piece before -> after,
      J1's three ruler numbers before -> after, the nine sign values, and Pot A's numbers.
- [ ] The render exists, was opened, and its captions carry real counts.
- [ ] Every job's `sacct` State/ExitCode is in the write-back; no FAILED job left unexplained.
- [ ] No default changed, no threshold tuned to make the gate pass, nothing committed, no canonical
      input edited; `git status --short` in the write-back.
- [ ] Write-back section `## Comments (worker, <date>)`, and one `End state:` line naming
      ready / incomplete / blocked / stopped.

### Out of scope

The trace guard (75/78) and any change to the extractor's ordering or sphere march. The 3 mm
admission window (26). The normal estimator (62/63) and the interior vote (328). Any change to
the assembler or the assembly lane's switches. Tuning the trim's `LO`/`HI` to make the gate
pass: try the defaults first and report; if they fail, report the failure, do not sweep.

### Budget

Medium. Three cells at 3x plus two at 1x is the bulk; if a 3x cell cannot finish inside the
array's wall clock, report it as `blocked` with the sacct, do not fall back to 1x and do not
silently shrink the piece set.
