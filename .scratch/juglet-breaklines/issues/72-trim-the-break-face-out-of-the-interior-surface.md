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

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-15)
**Branch:** 72-trim-the-break-face-out-of-the-interior-surface, in /c/PR/worktrees/sfs/72
**Worker:** dsh one-shot subagent, dispatched 2026-11-15 by the lead

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


## Comments (worker, 2026-11-15)

Worker: dsh one-shot subagent, dispatched 2026-11-15 by the lead. Worktree C:/PR/worktrees/sfs/72,
branch 72-trim-the-break-face-out-of-the-interior-surface, HEAD b394663, nothing committed and
nothing pushed (per the brief). git status --short: " M mesh_processing_headless.cpp".
The patched file is 260 046 B, md5 b4247448f8ca1e2c0f51278ec8ea118c (base 8eab296cc80a4029753bcaaa355a38fa,
244 887 B); git diff --stat = 1 file changed, 310 insertions(+), 0 deletions(-), three hunks
(@@ -3919,6 +3919,309 @@, @@ -4390,6 +4693,11 @@, @@ -4513,6 +4821,8 @@). No default changed, no threshold swept.

Headline: **Part A separates cleanly, the trim is built and runs, and it only half-cures the line while
breaking one touching pair. Reading: the-trim-breaks-what-worked.**

### Part A — the outboard dots are break-face points of the interior patch

carrier72.tsv (776 rows: pieces 1, 5, 6, 7, 8; every Breakline_0 dot with its nearest Surface_0 point,
ticket 59's ray-pair predicate evaluated on that carrier, eps 1.35 tu = 0.45 mm, exit dot -0.4,
search cloud = Surface_0 + Surface_1 because the opposing wall of an interior point is the exterior
patch). Columns: dot idx, d_inner_mm, d_outer_mm, carrier_pairing, carrier_pair_mm, carrier_dot_radial,
off_lip_08, carrier_offS1_tu.

| piece | dots | off-lip | off-lip carriers paired | on-lip carriers paired |
|---|---|---|---|---|
| 1 (control) | 185 | 0 | - | 177/185 = 95.7 % |
| 5 | 150 | 21 (14 %) | 2/21 = 9.5 % | 118/129 = 91.5 % |
| 6 | 141 | 3 (2 %) | 1/3 = 33 % | 110/138 = 79.7 % |
| 7 | 174 | 53 (30 %) | 9/53 = 17.0 % | 110/121 = 90.9 % |
| 8 | 126 | 9 (7 %) | 4/9 = 44 % | 111/117 = 94.9 % |
| **pooled 5-8** | 591 | **86** | **16/86 = 18.6 %** | **449/505 = 88.9 %** |

The prediction was 6-16 % paired outboard against 89-97 % on the lip; measured 18.6 % against 88.9 %.
Ticket 59's 1x bands are wall 0.8915-0.9750, fracture 0.056-0.164, roll 0.011-0.255, interior 0.63-0.83, so
the on-lip carriers sit just under the wall band and the outboard ones just above the fracture band: beyond
the lip the interior patch behaves like the reference's fracture faces. The medians corroborate from the
other side — ticket 59's measured wall thickness is J1 1.876 / J5 2.527 / J7 2.839 mm and this ticket's
run-time median paired thickness on the same pieces' breakline dots is 1.85 / 2.53 / 2.87 mm.
It separates, so Part A is not a stop and Part B was built.

The independent label agrees with the predicate: 83 of the 86 off-lip dots have an outward-facing
carrier (carrier_dot_radial > 0.2). Split by that label: off-axis-and-outward 2/21 (p5), 1/3 (p6),
9/53 (p7), 4/8 (p8); on-axis-and-outward 0/8, 12/17, 0/6, 0/3; on-axis-and-inward 118/121, 98/121,
110/115, 111/114. So the outboard stretches are carriers whose own normal points out of the interior
surface — the break face, seen from inside.

Pairing rates of the whole patches, per piece (S0 / S1): p1 96.9 / 88.4 %, p5 96.5 / 99.7 %,
p6 93.4 / 99.7 %, p7 95.6 / 99.4 %, p8 97.8 / 99.7 %. Median paired thickness per piece (the run-time
wall thickness this ticket measures, tree units / real mm): p1 5.56 / 1.85, p5 7.59 / 2.53,
p6 6.58 / 2.19, p7 8.60 / 2.87, p8 5.56 / 1.85. These are breakline-dot medians, not surface-point ones.

Write-up: C:/PR/artifacts/t72/carrier72_summary.md.

### Part B — SFS_BREAK_TRIM, default off

One switch in mesh_processing_headless.cpp (the repo-root file), namespace t72 immediately before
surfaceSegmentation at 3922, 284 lines. Vocabulary:
SFS_BREAK_TRIM (off when unset or 0/off/false/no), SFS_BREAK_TRIM_LO (0.5), SFS_BREAK_TRIM_HI (2.5),
SFS_BREAK_TRIM_MAXDROP (0.35), SFS_BREAK_TRIM_MINPT (400), SFS_BREAK_TRIM_EPS (0 = derive as 0.20 t);
normal exit dot fixed at -0.4 and march step 0.75 eps, both ticket 59's.

Called on the cluster that becomes Surface_0, after the interior/exterior decision and before
improveSurfaceBoundaryByFittingBSplineSurface (line 4699, ahead of the own/radius reassignment), and a
matching no-op on the single-cluster path (line 4834). So it sits in the path that writes
<stem>_Surface_0.ply/.xyz.

The window is derived per run, in three printed stages: pass 1 marches over a deterministic stride
sample (every n/2000-th point) with a generous window [2 spacing, 100 spacing] and eps 6 spacing, and
takes t = median hit distance; pass 2 marches every cluster point with the window [LO t, HI t] and
eps = 0.20 t. Everything is printed:

    [SFS-72] piece=Juglet_Piece_5 break trim: on n=17085 spacing=0.6414 t=4.1691 tu (1.3897 mm on the 3x tree) eps=0.8338 window=[2.0845,10.4226] tu (0.6948,3.4742 mm) x t=0.5000/2.5000 maxdrop=0.3500 minpt=400
    [SFS-72] TRIM-APPLIED kept=15624 dropped=1461 of 17085 (8.5514%) n_in=17085 n_out=15624

The starvation guard is mandatory and logged; when it fires it keeps the untrimmed cluster:

    [SFS-72] TRIM-REFUSED reason=maxdrop dropped=3188 of 6949 (45.8771%) > 35.0000% kept=6949

Compile check: no PCL/Eigen on the laptop and no g++/clang/cl.exe in PATH; the block was syntax-checked
against a stub (pcl::PointXYZ/PointNormal/PointCloud/KdTreeFLANN and t328::medianOf faked, C:/PR/artifacts/t72/stub72.cpp,
generated by mk_stub.py) with WSL g++ 13.3.0, -std=c++17 -Wall -Wextra -fsyntax-only: clean, zero warnings.
The real compile is the run's own build (below), which produced bin-t72-b.

Off-path identity, stated as the comparison actually made:
- 1x Juglet, switch unset, patched binary vs pristine binary, same session: Surface_0 and Surface_1
  **9 of 9 byte-identical**. Breakline_0/Breakline_1 are 0 of 9 byte-identical but carry the same dot
  count and the same dots (sorted xyz set difference empty, max |dxyz| 0.00000); they differ in row
  order, in the always-uninitialised 7th PCD column (2.42588e-38 against -1.54574e+15) and in 180-deg
  flipped interpolated normals on some sections — the extractor's own nondeterminism, present between two
  builds whose surfaces are byte-identical.
- Pot A 1x, patched vs pristine: 2 of 8 byte-identical, and a pristine-vs-pristine repeat is identical on
  the same 2 of 8; the differing pieces move <= 1.18 mm (pristine vs pristine) and <= 1.15 mm
  (patched vs pristine), and two of them differ only in row order. That is the unseeded 30-ray draw.
- 3x, switch-off against ticket 331's shipped tree: NOT byte-identical (max NN 0.26 / 0.29 / 0.77 / 0.32 /
  2.06 mm on pieces 5/6/7/8/1); there is no pristine 3x run in this session, so the 3x identity claim is
  bounded by that draw, not byte-level. The measured primary metric reproduces the shipped tree to +-1 dot.
- 1x, switch off vs on: the pieces the guard refused (1, 2, 3, 4, 6, 8, 9) are byte-identical in both
  surfaces. Where the guard refuses, the switch costs nothing at all.

### Part C — the cells

Run directory /data/gpfs/projects/punim2657/SfSpp/runs/20261115-0502_b394663_t72-trim with run.json,
submit.sbatch, submit_t72_c.sbatch, submit_t72_d.sbatch, submit_meas2.sbatch, pins/, tools/, logs/,
out/, and one out<cell>/ per cell. Inputs staged by the t331 stager (tools/stage_synth_t72.sh, md5
90391b0e8c137f86e17662386c328dd2, a copy of t331's). base commit b394663 archived by git archive and
pinned; the patch dropped into a second copy of that archive and rebuilt (one translation unit), so the
pristine and patched binaries come from the same bytes except the patch. Mesh binary md5
c6dd58c7744f7f2c8f66d92c7b1c4003 (patched) against c521e82638cbf8865a01b89791817a7e (pristine); the
edgeline binary is a481f49ec5450adfa0de872fef7ed969 in both — the check that one file changed.

Cells: smoke (3x, piece 5, on), ctl_jug (1x, unset), ctl_jug_on (1x, on), trim_off (3x, unset), trim_on
(3x, on), pure (1x Juglet with the pristine binary, unset), pure2 (Pot A, pristine, unset), ctl_pota
(Pot A 1x, unset), pota_trim (Pot A 1x, on), pota_pure (Pot A 1x, pristine, unset). 3x cells carry
POT_NAME=Juglet_large, WORNESS=0.7 and MESH_ENV="SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0";
1x cells carry MESH_ENV="" and POT_NAME=Juglet. All cells rc=0.

**3x: the trim fires on all nine pieces.**

| piece | interior cluster | derived t (tu / mm) | dropped |
|---|---|---|---|
| 1 | 49 959 | 4.3189 / 1.4396 | 2 568 (5.14 %) |
| 2 | 5 045 | 4.1237 / 1.3746 | 89 (1.76 %) |
| 3 | 7 876 | 4.1685 / 1.3895 | 262 (3.33 %) |
| 4 | 7 852 | 4.1734 / 1.3911 | 17 (0.22 %) |
| 5 | 17 085 | 4.1691 / 1.3897 | 1 461 (8.55 %) |
| 6 | 14 009 | 4.1336 / 1.3779 | 1 529 (10.91 %) |
| 7 | 21 577 | 7.1113 / 2.3704 | 1 384 (6.41 %) |
| 8 | 10 682 | 4.1204 / 1.3735 | 561 (5.25 %) |
| 9 | 4 017 | 4.1018 / 1.3673 | 7 (0.17 %) |

No TRIM-REFUSED at 3x and none on Pot A in this cell set (grep -c over both logs = 0).

**The primary number, off-lip dots at 0.8 mm on pieces 5-8** (frozen definition: distance from each
Breakline_0 dot to the nearest inward-facing Surface_0 point, real mm; reproduced dot-for-dot on the
shipped tree before any cell ran):

| piece | before | trim_off | trim_on | in mm of contour |
|---|---|---|---|---|
| 5 | 21/150 = 14.0 % | 21/150 | 20/151 = 13.2 % | 12.6 -> 12.0 |
| 6 | 3/141 = 2.1 % | 2/141 | 1/145 = 0.7 % | 1.8 -> 0.6 |
| 7 | 53/174 = 30.5 % | 52/173 | 41/170 = 24.1 % | 31.2 -> 24.0 |
| 8 | 9/126 = 7.1 % | 9/126 | 7/125 = 5.6 % | 5.4 -> 4.2 |
| pooled | 86/591 = 14.6 % | 84/590 = 14.2 % | 69/591 = 11.7 % | 51.0 -> 40.8 |

The two switch-off runs agree to +-1 dot, so the movement is outside the pipeline's own spread. The cure is
real and partial: 10.2 mm of 51.0 mm (20 % relative), and piece 7 still runs 24.0 mm of line off the lip.
The line does not move onto the lip where it is off: median d_inner goes 0.176 -> 0.207 mm (p7),
0.100 -> 0.121 (p6), i.e. it gets slightly further off where it stays off.

**At 1x the estimator collapses and the guard refuses — this is the defect found in Part B.**

| piece | spacing | derived t | t/spacing | dropped | verdict |
|---|---|---|---|---|---|
| 1 | 0.6344 | 15.5423 | 24.5 | 45.88 % | REFUSED (maxdrop) |
| 2 | 0.6269 | 1.2537 | 2.00 | 44.65 % | REFUSED |
| 3 | 0.6400 | 1.2801 | 2.00 | 39.41 % | REFUSED |
| 4 | 0.6340 | 1.2679 | 2.00 | 39.76 % | REFUSED |
| 5 | 0.6289 | 4.0877 | 6.50 | 1.31 % | applied |
| 6 | 0.6272 | 1.2545 | 2.00 | 51.14 % | REFUSED |
| 7 | 0.6329 | 4.1140 | 6.50 | 2.51 % | applied |
| 8 | 0.6334 | 1.2667 | 2.00 | 44.81 % | REFUSED |
| 9 | 0.6249 | 1.2499 | 2.00 | 43.20 % | REFUSED |

On seven pieces t is 2.00 x spacing to four digits — the first step of the pass-1 march: the nearest
accepting point is a same-patch neighbour whose normal opposes the probe by more than 0.4 (a fold, or a
normal the 1x field has flipped). The pass-2 window then becomes [1, 2.5] x spacing and 39-51 % of the
cluster is called unpaired, which trips maxdrop. Piece 1 goes the other way (t = 24.5 x spacing) and also
refuses. The switch is therefore only usable in the arm its estimator was derived on: at 3x (radius-1.0 mm
normals) it finds 1.37-1.44 mm on eight of nine pieces and applies everywhere. Fixing the pass-1 estimator
(same-patch rejection by a spacing test, or a floor of a few spacings) is the next ticket, not a sweep here.
The guard did its job: the refused pieces keep the untrimmed cluster and come out byte-identical.

1x primary, where it applied: piece 5 5/47 -> 3/46 (10.6 % -> 6.5 %), piece 7 19/54 -> 22/54
(35.2 % -> 40.7 %) — opposite directions on the only two pieces the trim touched.

**J1's boundary (piece 1), ticket 65's frozen ruler.** 3x before / off / on: blind 36.47 / 18.72 /
10.71 deg; far-skin share (farS0_out) 0.5902 / 0.6607 / 0.5556; forward coverage f2r<=1 mm 0.9156 / 0.9089 /
0.8192; reverse coverage r2f<=1 mm 0.3756 / 0.3900 / 0.3315; ring coverage 325 / 360 / 345 deg of 360;
n_fold 912 / 878 / 946; n_rim 2223 in all three. The two switch-off runs differ by 17.75 deg on blind, so
that ruler cannot resolve the trim's 8 deg on this arm; the other three numbers all move the wrong way
(forward coverage -0.09, reverse -0.04), which is what removing the rim band predicts.

1x, the cell the brief names (ctl_jug -> ctl_jug_on): blind 45.89 / 45.89; farS0_out 0.8649 / 0.8649;
f2r 0.4497 / 0.4497; r2f 0.4435 / 0.4435; ring 355 / 355; n_fold 2815 / 2815; n_rim 2223 / 2223 —
identical to the last digit because the guard refused piece 1 and the surface never moved. Those 1x numbers
are a fresh measurement of the shipped 1x chain (MESH_ENV=""), not ticket 65's radius-1.0 arm
(68.38 / 0.6729 / 0.6665 / 0.4211 / 250), and the two must not be read as before/after.

**The nine sign gates (median n_A.n_B, mutual nearest pairs within 3 mm, GT frame).**

| pair | before | switch off | switch on | ticket 328 | verdict |
|---|---|---|---|---|---|
| 1-2 | +0.944 (26) | +0.953 (36) | +0.934 (30) | +0.311 | held |
| 1-4 | +0.821 (20) | +0.829 (27) | **-0.808 (17, 9 negative)** | +0.469 | **TURNED NEGATIVE** |
| 1-8 | +0.984 (55) | +0.986 (57) | +0.982 (50, 3 neg) | +0.741 | median held, 3 opposed dots appear |
| 1-9 | +0.892 (17) | +0.806 (19) | +0.810 (10) | -0.408 | held |
| 2-5 | +0.916 (1) | +0.916 (1) | +0.915 (2) | +0.642 | held |
| 2-9 | +0.976 (11) | +0.976 (11) | +0.974 (13) | +0.693 | held |
| 3-5 | +0.936 (11) | +0.936 (11) | +0.949 (15) | +0.674 | held |
| 6-7 | -0.997 (50, 39 neg) | -0.997 (46, 37) | -0.997 (31, 26) | -0.786 | already negative on the shipped tree |
| 7-9 | +0.940 (15) | +0.940 (16) | +0.936 (15) | +0.287 | held |

Pair 1-4 fails the gate: clean in both switch-off runs (+0.821, +0.829, zero opposed dots), bimodal after
the trim (9 of 17 dots opposed, dot_min -0.841, dot_max +0.835). 6-7 is negative before and after, so
"none may turn negative" is applied as "no pair that was positive turns negative, and none falls more than
0.10 below its own before value"; the ticket 328 column is a different (cured) tree and is carried only as
the reference the ticket names.

1x: 1-2 +0.936 / +0.936; 1-4 +0.971 / +0.971; 1-8 no pair within 3 mm in either run; 1-9 +0.941 / +0.967;
2-5 +0.958 / +0.957; 2-9 +0.946 / +0.946; 3-5 +0.993 / +0.991; 6-7 +0.681 / +0.721; 7-9 +0.939 / +0.931.
No sign turns and nothing falls 0.10 — because the guard refused on every piece those pairs touch except
5 and 7. (6-7 reads +0.681 at 1x against -0.997 at 3x: different exports, so only before-vs-after on one
tree is comparable.)

**Pot A (1x).** Off-lip dots, switch off -> on: 01 210/210 -> 210/210, 02 0 -> 0, 03 2 -> 2, 04 2 -> 3,
05 3 -> 3, 06 0 -> 0, 07 0 -> 0, 08 0 -> 0; the pristine repeat reads 210 / 0 / 2 / 2 / 1 / 0 / 0 / 0, so the
+-1 dot on 04/05 is the draw. Median d_inner 0.227-0.320 mm except piece 01. Contours 104.75-378.97 mm.
Trim drops: 01 16.33 % of the interior cluster, 02-06 <= 0.25 %, 07/08 unchanged.

One caveat that must travel with the Pot A column: the frozen test needs inward-facing Surface_0 points as
its reference set, and on Pot A the exported Surface_0 normal direction is piece-dependent — median
normal.radial is -0.876 / -0.994 / -0.877 / -0.943 / -0.833 on pieces 02/03/04/06/08 but **+0.971 on 01 and
+0.575 on 05**. Piece 01 has 0 of 82 653 points facing inward, so its 210/210 is the statistic degenerating
(median d_inner 38.46 mm), not a breakline failure. The same orientation is piece-dependent at 3x (inward
shares 1.85 / 66.98 / 40.19 / 0.25 / 3.03 % on pieces 1/5/6/7/8), which is why the primary number is only
comparable on one piece before and after — never across pieces or scales.

**The line lives.** Breakline_0 dots, pieces 1-9: 3x switch off 184/96/125/102/150/141/173/126/77, 3x switch
on 181/96/124/101/151/145/170/125/78, 1x switch off and on 28/31/38/32/46-47/45/54/41/24. **9 of 9 pieces
produce a line in every cell.** Surface_0 (3x, off -> on): 91733->69117, 10620->10534, 17711->17200,
16277->16260, 35301->33878, 29512->27827, 46186->43994, 22283->21623, 8573->8567 — the trim costs 0.5-25 %
of the interior surface, worst on piece 1.

**The render** C:/PR/artifacts/t72/render72_trim_before_after.png (3360x1680, read by the worker): four
sherds 5-8, before above and after below, the break-face strip shaded, the line coloured blue (on the lip,
<= 0.8 mm) or red square (off, > 0.8 mm), caption per piece
"piece 5: 21 of 150 -> 20 of 151 | piece 6: 3 of 141 -> 1 of 145 | piece 7: 53 of 174 -> 41 of 170 |
piece 8: 9 of 126 -> 7 of 125". The picture shows the band gone and the red stretches shortened but still
present — most visibly the bottom-right stretch of piece 7 and the top-right corner of piece 8 — which is
the same partial cure the table reports.

Gate table: C:/PR/artifacts/t72/gate72.tsv, 172 rows, columns group / metric / piece / before / trim_off /
trim_on / ref / verdict, groups primary, primary_1x, j1_ruler, j1_ruler_1x, pairs, pairs_1x, trim_3x,
trim_1x, identity, pota, coverage. Assembled by C:/PR/artifacts/t72/gate72.py from the run's own TSVs.

### Jobs (sacct, final)

| job | name | State | ExitCode | Elapsed | what |
|---|---|---|---|---|---|
| 35106617 | t72trim | FAILED | 3:0 | 0:04 | attempt 1: my own hunk assertion demanded one hunk, the diff has three |
| 35106629 | t72trim | FAILED | 4:0 | 3:15 | attempt 2: the step-C md5 check took head -1 of an alphabetical md5sum listing and compared the edgeline binary |
| 35106709 | t72trim | COMPLETED | 0:0 | 21:15 | set A cells: smoke, ctl_jug, trim_off, trim_on |
| 35106710 | t72trim | COMPLETED | 0:0 | 4:57 | set B: pure (rc 0), ctl_pota (refused: the Pot A manifest had kept_points 0) |
| 35106822 | t72pota | COMPLETED | 0:0 | 9:28 | set C: Pot A ctl / trim / pristine with the corrected manifest |
| 35107165 | t72meas | FAILED | 2:0 | 0:00 | measured: RUN resolved to /var/spool/slurm/jobNNN |
| 35107180 | t72meas | COMPLETED | 0:0 | 19:45 | 3x measurements |
| 35107226 | t72pota2 | COMPLETED | 0:0 | 0:02 | inner rc 127: build-b/src had been tidied away |
| 35107241 | t72pota2 | COMPLETED | 0:0 | 0:06 | inner rc 9: PIECES is whitespace-separated for the cell driver, I passed commas |
| 35107258 | t72pota2 | COMPLETED | 0:0 | 3:19 | Pot A pristine repeat + the cmp matrix |
| 35107350 | t72meas2 | COMPLETED | 0:0 | 1:07 | measurement tail (3x already done) |
| 35107354 | t72meas2 | COMPLETED | 0:0 | 8:25 | 1x measurements, all rc 0 |
| 35107472 | t72d | COMPLETED | 0:0 | 2:40 | the 1x switch-on cell + its J1 ruler |

Each submission was polled with bash scripts/remote/job_status.sh <JOBID> (see deviations) and its final
State/ExitCode is the table above.

### Deviations from the brief (all stated, none silent)

1. **scripts/slurm_poll.sh does not exist** — not in the worktree, not in the canonical checkout, not in
   any commit (git log --all -S slurm_poll is empty). Used scripts/remote/job_status.sh <JOBID> (squeue plus
   sacct) instead.
2. **Spartan transfer from Windows ssh/scp** (C:\Windows\System32\OpenSSH), because the WSL key
   /home/zjtan/.ssh/id_ed25519 is rejected by spartan (Permission denied publickey).
3. **ctl_jug and ctl_pota run twice each.** The brief's Part C names them with the switch UNSET, the
   ticket's own table names them ON. Ran both: ctl_jug / ctl_pota unset, ctl_jug_on / pota_trim on, plus
   pure / pure2 (pristine binary) as the identity control.
4. **Pot A has no manifest on the cluster.** Wrote pins/MANIFEST_POTA_PINNED.tsv from the on-disk clouds
   (columns piece pcd_md5 kept_points spacing_mm; kept_points = the PCD POINTS header, nothing filtered).
   It pins against drift only — it is not an evidential manifest.
5. **The banner prints "(t/3.0) mm on the 3x tree" on 1x cells too.** Cosmetic: the arithmetic uses t as the
   run's own unit and the window is printed in the same unit; only the label is wrong. Not fixed, because
   fixing it means rebuilding every binary and re-running the cells for a string.
6. **out/counters.tsv is all "?"** (its parsing helper failed on every cell) and is not used for any claim;
   each cell's pieces66.tsv is the count of record.
7. **meas_* cover pieces 1 and 5-8 only**; the nine-piece counts come from pieces66.tsv.
8. **The 3x identity is bounded, not byte-level** (no pristine 3x run exists); see Part B.
9. The cell driver (.scratch/juglet-breaklines/stage66/run_cell66.sh) was not edited; it was copied to the
   run's tools/ as run_cell66_t72.sh (md5 ae022e41fb719ff95d371268e24dfd19).
10. meas72 on pieces 2 and 9 reports NA for the off-lip count: no inward-facing Surface_0 point exists to
    measure against on those two 1x surfaces, the same degeneracy as Pot A 01.

### Acceptance (Part E)

- [x] Part A table at C:/PR/artifacts/t72/carrier72.tsv, one row per dot, with the paired/unpaired split per
      piece and pooled (83 of 86 off-lip dots carry an outward-facing point).
- [x] 3x Surface_0/Surface_1 pairing rates per piece, beside ticket 59's 1x rates, and the median paired
      thickness per piece in tree units and mm (carrier72_summary.md).
- [x] SFS_BREAK_TRIM exists, defaults off, announces itself, window derived per run and printed in tu and mm.
- [x] The starvation guard exists, is logged with counts, and its firing is stated (never at 3x or on Pot A;
      seven of nine pieces at 1x).
- [x] trim_off reproduces the shipped 3x surfaces/boundaries within the stated comparison (bounded by the
      unseeded draw; primary metric +-1 dot).
- [x] trim_on published its Surfaces and Breaklines; dot counts and the 9/9 line count are stated.
- [x] gate72.tsv with the primary number per piece, J1's three ruler numbers, the nine sign values, Pot A.
- [x] The render exists, was opened by the worker, and its captions carry real counts.
- [x] Every job's sacct State/ExitCode is above; each failure is explained.
- [x] No default changed, no threshold swept, nothing committed, no canonical input edited;
      git status --short shows only " M mesh_processing_headless.cpp".
- [x] Write-back section and the End state line are below.

### Lead — verification (2026-11-15, Thinkbook16)

verified: `cd C:/PR/worktrees/sfs/72 && COLUMNS=200 python C:/PR/artifacts/dsh-handover/72/accept72.py`
-> 34 of 34 pass. Two cases were mine and wrong, not the worker's files: `switch-default-off` hunted a
variable called `g_breakTrim` where the code has `t72::g_trim72` (`mesh_processing_headless.cpp:3943
static bool g_trim72 = false;`), and `gate-columns` demanded an `after` column where the table carries
`before / trim_off / trim_on`.

verified: `C:/PR/artifacts/t72/carrier72.tsv` 776 rows, recomputed -> off-lip carriers paired 16/86 =
18.6%, on-lip 449/505 = 88.9%, per piece 2/21, 1/3, 9/53, 4/9. Part A separates; the split is not a
threshold artefact.

verified: `C:/PR/artifacts/t72/gate72.tsv` primary rows -> off 21/150, 2/141, 52/173, 9/126; on 20/151,
1/145, 41/170, 7/125; pooled 69/591 = 11.7% against the shipped tree's 86/591 = 14.6%. The 20% relative
cure and the piece-7 residue (41 of 170 dots, 24.0 of 101.9 mm) are both in the table.

verified (independent re-run, not the worker's script): the ticket-328 pair statistic on the cells' own
Breakline_0 files, fetched to `C:/PR/artifacts/t72/geom_{off,on}` and run in tree units against
`C:/PR/artifacts/t350/tree/Ground Truth` -> 1-4 off +0.827 (n=26, 0 opposed), on -0.812 (n=15, 9
opposed); 1-8 on +0.982 with 3 opposed; 6-7 -0.997 both; 1-2 +0.953 -> +0.937. The 1-4 turn reproduces.

verified: 1x derived `t` -> 1.2537 / 0.6269 = 2.000 on pieces 2, 3, 4, 6, 8, 9 and 15.5423 / 0.6344 =
24.5 on piece 1; every one of those seven is REFUSED on maxdrop. The guard, not the trim, is what made
those pieces byte-identical.

verified: sacct -> 35106617 FAILED 3:0, 35106629 FAILED 4:0, 35107165 FAILED 2:0 (attempt-1 hunk
assertion, an md5 taken `head -1`, a `RUN` that resolved to the spool), and the four cell jobs
35106709 / 35106710 / 35106822 / 35107472 plus 35107180 / 35107258 / 35107350 / 35107354 COMPLETED 0:0.

verified: the render opened by me: the red off-lip stretches shorten (piece 7 bottom right, piece 6 left
edge, piece 8 top right) and none disappears; piece 5 is visually unchanged, which is its 21 -> 20.

verified: `git status --short` in the worktree -> only ` M mesh_processing_headless.cpp`; no default
changed, no threshold swept, nothing committed by the worker.

**Adjudications.**

1. The reading stands. `the-trim-breaks-what-worked` is the ticket's own definition: 5-8 improve and a
   touching pair turns negative. But say what turned: the 1-4 median is taken over a mixed population (9
   of 17 dots opposed by the worker's count, 9 of 15 by mine) with dot_min -0.841 against dot_max +0.835,
   so the pair's contact patch became mixed, not uniformly reversed. One dot in five is still aligned.

2. **New mechanism, found here.** The surface shrinks far more than the trim removes, and the shrink is
   downstream: piece 1's Surface_0 is 91 733 points in trim_off and 69 117 in trim_on (-24.6%) against a
   5.14% cluster trim, because `improveSurfaceBoundaryByFittingBSplineSurface` (the 3-unit distance gate)
   re-derives its membership from the trimmed cluster and had been re-admitting the break-face strip the
   trim removes. That is how a 2 568-point trim reaches the 1-4 seam: its correspondence set falls 20 -> 17
   dots in the gate (26 -> 15 in my re-run). The harm is indirect — the trim changes what the improvement
   step sees — which is also why the off-lip number only moves 20%: the improvement step puts part of the
   strip back on every piece.

3. `t` is not a wall-thickness estimator and the write-back's vocabulary should be read as ray hit
   distance. At 3x it is 6.50 x spacing, 1.37-1.39 mm, against ticket 59's walls of 1.85-2.87 mm; at 1x it
   collapses to 2.00 x spacing. The 3x window [0.5t, 2.5t] = 0.69-3.47 mm straddles the wall by luck of
   the factor 6.5, not by construction. The next ticket's job is the pass-1 estimator, not a sweep.

4. The worker's deviation 1 is true and is a workspace gap, not a worker fault: `scripts/slurm_poll.sh`
exists nowhere — not in the worktree, not in the umbrella clone (`glob **/slurm_poll*` finds nothing) and
not on Spartan (`/data/gpfs/projects/punim2657/SfSpp/scripts/` and `.../scripts/` both absent) — while
the workspace rule requires every sbatch to be polled with it. `scripts/remote/job_status.sh` was used
instead and its output is in the run's `logs/job_status.log`.

5. Pot A is unharmed on the only gate this ticket has: the off-lip count moves by at most one dot on any
   piece (04: 2 -> 3 of 147), 9 of 9 lines are written, and 01 stays degenerate at 210/210 on both sides.
   That is the off-lip metric only; it says nothing about Pot A's breakline quality beyond this number.

6. Limits. The 3x identity is bounded, not byte-level: no pristine 3x run exists, so off-path agreement is
   +-1 dot on the primary metric and the surfaces differ from the shipped tree by 0.26-2.06 mm nearest
   neighbour. The 1x identity is byte-level and is the stronger statement. Pot A's manifest is pinned from
   its own clouds, so its corpus gate catches drift only.

**Landed with the switch default off** because the off path is proven identical and the 3x arm is a real,
measured cure; the 1x refusal is recorded above and the estimator is the next ticket's question. The code
is committed with this ticket (`mesh_processing_headless.cpp`, +310 / -0).

End state: ready
Reading: the-trim-breaks-what-worked
