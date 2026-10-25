# 295 — Verify the conservator's reading of the eleven below-bar lanes

Status: done (accepted: six claims adjudicated; partition owns the eleven, no welded facet, the gate cannot fix it)
Working in: chat on Thinkbook16 (2026-10-25)
Branch: 295-verify-the-conservators-read, in /c/PR/worktrees/sfs/295
Answers: E1
Created: 2026-10-25
Follows: 293 (the mechanism), 294 (the pictures), 279 (a reference is the boundary of the authors' kept surface)

## Why

The conservator read the eleven figures of ticket 294 and gave a reading of each lane. Every claim below
is a statement about geometry, so every one can be measured. This ticket measures them and says plainly
where the reading holds, where it needs qualifying, and what the answer implies for the pipeline.

**The claims, as stated by the conservator (2026-10-25):**

- **C1 — Pot I 25.** Agreed the lanes are swapped. The open question is *why this single piece got the
  interior/exterior the other way round from the authors*, and *who is correct* — we fixed the
  interior/exterior detection and every other piece agreed with them.
- **C2 — Pot C 03 Bl1.** Our line is much better; the authors' line did not trace the break at all, it
  traced the base.
- **C3 — Pot D 22 Bl0 and D 27 Bl0/Bl1.** Ours is the better match to the mesh/surface; D 27 "clearly
  better".
- **C4 — Pot H 10 Bl1.** Either another mismatched edgeline, or our surface is bigger than the authors'
  line implies.
- **C5 — Pot I 06 Bl1 and I 13 Bl1.** Same category: our mesh is bigger, so our traced line is bigger,
  and it looks as if our surface includes part of the break surface.

## What to measure

Q1 (C1) **Which of the authors' two surfaces is the interior?** For every piece in the corpus with
author artefacts (163 pieces), load the authors' `Surface_0` and `Surface_1`, the piece axis, and decide
each surface's side two independent ways: (a) radial position -- median distance from the axis; (b) normal
direction -- the sign of the mean dot of the surface normals with the outward radial direction. Report the
split as a count ("Surface_0 is the inner face on N of 163 pieces, by radius; by normals on M"), the
definition used, and the pieces that disagree. Then for **Pot I 25** specifically: which of the authors'
surfaces does their `Breakline_0` ride, which does `Breakline_1`, and is that surface the inner or the
outer one. Compare against our own decision line for that piece, printed by the mesh stage as
`[PAPER-234] classify: face0 n=... interior_frac=... face1 n=... interior_frac=... satA=... satB=...`
(ticket 293's log has it: face0 n=3072 interior_frac=0.0000, face1 n=2321 interior_frac=0.9931,
satA=16.0000 satB=5377.0000, then "swapped -> Surface_0=interior"). Say which side is physically the
interior for this sherd, with the evidence, and whether the authors or we are the outlier.

Q2 (C2) **Does the authors' Pot C 03 Bl1 line follow the base?** Measure: the distance of every author
dot to (i) the base band's outer rim, (ii) the band's interior, (iii) our line; the share of their dots
lying on the flat of the band (in-band cross-section); and whether their dots sit on material that the
pipeline dropped. State in one line what edge their line is, and what edge ours is.

Q3 (C3) **Is the reference a break edge at all on D 22 Bl0, D 27 Bl0 and D 27 Bl1?** For each: the share
of reference dots within 2 mm of material; the share whose tangent-plane angular gap marks them as on a
boundary (> 100 deg, the ticket 280 statistic); for D 22 the share of the arc lying over empty space (the
chord); and for D 27 the distance of their line from the face's own boundary. Conclusion per lane: is the
reference a boundary curve, a curve through the interior of the face, or a chord over a void.

Q4 (C4) **Pot H 10 Bl1 — mismatch, or a bigger surface?** Decide between: (a) another interior/exterior
label mismatch; (b) our kept face spans a step/crease and the reference turns at it; (c) our kept face
includes break-surface material. Measure on our kept face: the local surface normal deviation from the
face's dominant plane along the 39.6 mm stretch, histogrammed; the axial/height profile of our surface
across the stretch; the share of the stretch lying over the dropped cluster `c5` (ticket 281: 629 points,
0.3191 mm from kept `c1`, carrying 21 of 88 Bl1 dots); and the distance of the reference dots from our
fitted plane. One conclusion.

Q5 (C5) **Pot I 06 Bl1 and I 13 Bl1 — is our face bigger because it includes the break surface?** Same
instrument as Q4, plus: the local surface tilt at each reference dot (covered vs uncovered) and the share
of our kept face in the stretch whose tilt exceeds, say, 45 deg from the face's dominant plane -- break
facets are steep, a wall face is not. If our face does weld the break facet, say at what share of the
stretch and how far the welded band reaches. Note I 13 additionally swings between two kept faces
(ticket 293: 68.75% nearest `c1`, 31.25% `c0`), so say whether it is one case or two.

## Data you already have

- `..\20261025-0456_3ada802_p293-census/out/` -- ticket 293's tables (`crosspair.tsv`,
  `assign_summary.tsv`, `clusters.tsv`, per-dot `assign.tsv`), the nine piece cluster dumps in `out/diag/`
  (text: mesh points with cluster and surface labels; if normals are missing, derive them by local PCA),
  the eleven figures in `out/png/`, and the logs.
- Authors' artefacts for all 163 pieces: `/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/`
  (`Surfaces/`, `Breaklines/`, `Axes/`).
- Meshes (DS for most pieces): `original_samples_backup/SfS_pp/Mesh/`.
- Frozen clouds: `original_samples/SfS_pp/Point/` (manifests beside them, ticket 290).

## Constraints

- **Read-only.** No pipeline run, no rebuild, no default, threshold or C++ change. Analysis code lives on
  the ticket branch. If you must run something on Spartan, a short batch job in a run directory is fine,
  and every job gets `SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_<tag>/` with `run.json`, `submit.sbatch`,
  `logs/`, `out/` and a row in `runs/index.tsv` (verdict and human_note empty -- those are the lead's).
- Stage by symlink (`scripts/stage_piece.sh`) if you need a piece, and delete geometry before you report;
  keep the tables.
- Never `build.sh --target nurbs`: that target compiles the pre-247 duplicate in
  `original_nurbs_preprocessing/` (ticket 282).
- Anything you quote from ticket 293 must reproduce to **0.05 mm and 1 coverage point**, or the
  difference must be stated.

## Acceptance

1. Q1: the 163-piece split as counts, the definition used, the disagreeing pieces named, and the Pot I 25
   verdict with the evidence that decides which side is the interior. A plain answer to "who is correct".
2. Q2-Q5: one row of metrics per lane as specified, plus one plain-language conclusion per lane, marked
   **holds** / **holds with qualification** / **does not hold** against the conservator's claim.
3. A closing paragraph: which of C1-C5 hold, what the exceptions are, and -- if any lane is a welded break
   facet -- what mechanism would have to change (growth, classify, or partition), stated as a hypothesis
   with the number that supports it.
4. Every number traceable to a file in the run or analysis directory; nothing quoted from memory.

## Results

Run: `SfSpp/runs/20261025-1824_ca18c8f_p295-lanes/` (job 33761910; `run.json`, `submit.sbatch`,
`scripts/`, `out/`). Read-only: no build, no pipeline binary, no geometry written. Every number below is a cell
of `out/lanes.tsv`, `out/q6.tsv`, `out/q1_*.tsv`, `out/meshrim.tsv` or `out/repro295.tsv` in that run.

### 0. The gate: what reproduces

`out/repro295.tsv` — `TOTAL 385/385 reproduced`: `assign_summary` 54/54 (worst delta **0.0050**),
`crosspair` 20/20 (0.0041), `lanes_fresh` 15/15 (0.0005), `clusters` 296/296 (0.0000). Every ticket-293
number quoted below is inside the 0.05 mm / 1 coverage point gate.

**Not reproducible, and not quoted as if it were:** (i) ticket 293's classify decision lines
(`[PAPER-234] classify: face0 ... interior_frac ...`) come from the pipeline binary, which would need a build
the constraints forbid — they are quoted from the 293 log as 293's own statement, and my independent
interior/exterior census (Q1) is the check on them; (ii) 293's Phase-B dot index (`i0`/`i1`) was computed on
geometry deleted with `out/geom`, so our **line** cannot be re-measured directly — where a lane needs "where
is our line", the >100 deg boundary of our kept material stands in for it (293 measured our lines riding that
edge at 0.98 mm, ring 0.40-0.46 mm); (iii) 293's per-dot cluster assignment (`assign.tsv`) answers a different
question from a nearest-label count, and the two are reconciled lane by lane where they differ (D 22, H 10,
I 13).

### 1. Q1 (C1) — the interior/exterior naming over 163 pieces

Definitions, all three reported (`out/q1_summary.txt`, per piece in `out/q1_pieces.tsv`):

- **concavity (PRIMARY)** — the face whose normals look at the axis: `m = mean(n_hat . r_hat)` negative.
  Discriminative (|dm| >= 0.10) on **160 of 163** pieces: **Surface_0 is the interior on 158, Surface_1 on 2**
  — the two are **Pot I 25** (dm -0.39) and **Pot J 14** (dm -0.85).
- **radius** (the coarser consequence, patch-coverage sensitive) — the smaller median distance to the axis:
  discriminative (|dr| >= 1.0 mm) on **158 of 163**: **Surface_0 interior on 152, Surface_1 on 6** —
  **Pot C 03** (dr -8.59), **Pot H 04** (-2.65), **Pot I 25** (-2.34), **Pot J 03** (-6.18), **Pot J 08**
  (-4.22), **Pot J 14** (-4.07).
- **HEADLINE:** both criteria discriminative on 157; they name the same interior face on **153** and a
  different one on **4** (C 03, H 04, J 03, J 08 — all plate-like, plate_ratio 0.43-0.74, where the faces
  separate along the axis rather than radially). On those 153 agreeing pieces, **Surface_0 is the interior on
  151**. No criterion discriminative: **Pot I 30, Pot J 19**.
- **mutual offset, tested and discarded** — `s = mean(n_hat . u)` to the other surface: S0 median -0.975, S1
  median -0.978, both faces negative on **163/163** pieces. The two faces' normals point away from each other
  on nearly every piece, which validates the shell but cannot say which side is the pot's inside. The sign test
  was written on the wrong premise; reported so it is not repeated.

**Which face each of the authors' breaklines rides** (`out/q1_lines.tsv`): **Breakline_0 rides the interior on
161 of 163**; the two exceptions are **Pot I 25** and **Pot J 14** — the same two pieces the concavity criterion
names Surface_1-interior. Both lines ride the same face on **0** pieces; the assignment is ambiguous (margin
< 0.50 mm) on **0**; both lines lie on their surface (<= 2.0 mm) on **163/163**. The index pairing is exact:
**Bl0 on Surface_0 on 163/163, Bl1 on Surface_1 on 163/163**. Ride margin: median 5.83 mm, p5 2.54, min 1.82.

**Pot I 25, in context** (`out/q1_i25_surfaces.tsv`, `out/q1_i25_lines.tsv`, `out/q1_i25_ours.tsv`):

| | r50 (mm) | m | area (mm2) | n_ax |
|---|---|---|---|---|
| authors Surface_0 | 15.32 | **+0.221** (normal away from the axis = exterior) | 325.2 | 0.981 |
| authors Surface_1 | **12.98** | **-0.168** (normal toward the axis = interior) | 225.4 | 0.980 |

Both criteria name **Surface_1 the interior**; there is no ambiguity on this piece. Their `Breakline_0` rides
Surface_0 at 0.277 mm (margin 6.611) and `Breakline_1` rides Surface_1 at 0.299 mm (6.522) — so on I 25 the
authors' Bl0 rides the **exterior** face, against their own 161/163 convention. Our side: our kept face of
**2321 points sits 0.296 mm from their Surface_1** (the interior) and our **3072-point face 0.310 mm from their
Surface_0**; 293's classify log for this piece reads `face0 n=3072 interior_frac=0.0000, face1 n=2321
interior_frac=0.9931` — i.e. our measurement names the *same* physical face interior as both corpus criteria,
and the pipeline then swapped so that our `Surface_0` is the interior face (the 2321-point one).

**The verdict on C1.** The conservator's "ours is right, the authors are the outlier" **holds, with a
qualification that changes what the word "swap" means here.** The authors are the corpus outlier: on I 25 (and
J 14) their Surface_0 is the physically exterior face, against 151-158 of 163 pieces. We are not: our
interior/exterior decision on I 25 agrees with the corpus on both criteria. But the two releases' *lines* are
**not** on different faces — their Bl0 and our Bl0 both ride the exterior face (0.249 mm apart), their Bl1 and
our Bl1 both the interior one (0.242 mm apart), and both lanes are inside the 2 mm bar on both sides (no
reference dot further than **1.475 / 1.690 mm** from our material, 0.00% beyond 2 mm). So there is a **naming
inversion, not a geometric one**: it is the surface files whose order is inverted between the releases on this
piece (our `Surface_0` = their `Surface_1`), and on our side it shows up as the line-to-surface index pairing,
our Bl0 riding the face we write as `Surface_1`. The answer to "why did this one piece differ" is therefore:
**the authors' surface order differs on this piece, not our detection of the interior.**

### 2. Q2-Q5 — the lanes, one row each

Columns: *their dots -> our material* med/max (mm, `d_kept_med`/`d_kept_max`); *their line -> their own
surface's >100 deg rim* med and share on it (`own_d_rim_med`/`own_share_gt100`); *>2 mm share* of their dots
(`share_drim_gt2`); *our band under their line* — median angle and perpendicular offset to the authors' own
normal (`w_ang_med`/`w_s_abs`, the "extra surface" test) with the share pitched >45 deg; *nearest dump label*
(`near_kept`/`near_dropped`/`near_neg1`, %); *stretch* = the longest run of their dots further than 2 mm from
our material (`stretch_arc` mm, `stretch_share` %), in it *our material* and *our edge* distances
(`stretch_dkept_med`/`rim_d_ref_med`); *areas* ours/theirs (mm2).

| lane | C | their dots->our material | -> own >100 rim | >2 mm | our band: angle, offset, %>45 | nearest label kept/dropped/-1 | stretch | in it: material / our edge | areas ours/theirs | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| C 03 Bl1 | C2 | 3.567 / 5.053 | 0.296, 90.83% | 100.00% | **81.56 deg, 2.215 mm, 100%** | 0.00 / 10.00 / 90.00 | 273.7 mm, 100% | 3.567 / n-a | 5820.9 / **897.2** | **holds** |
| I 25 Bl0 | C1 | 0.715 / 1.475 | 0.291, 88.41% | 0.00% | 1.12 deg, 0.006 mm, 0% | 11.59 / 0.00 / 88.41 | none | - | 260.3 / 325.2 | **holds with qualification** |
| I 25 Bl1 | C1 | 0.520 / 1.690 | 0.299, 91.67% | 0.00% | 1.23 deg, 0.007 mm, 0% | 23.33 / 0.00 / 76.67 | none | - | 189.5 / 225.4 | **holds with qualification** |
| D 22 Bl0 | C3 | 1.046 / 11.116 | 0.280, 89.47% | 66.92% | 2.28 deg, 0.005 mm, 0% | 10.53 / 16.54 / 72.93 | 45.0 mm, 18.65% | 0.898 / 5.974 | 1285.0 / 1707.1 | **holds with qualification** |
| D 27 Bl0 | C3 | 0.517 / 1.692 | 0.257, 85.42% | 10.42% | 1.11 deg, 0.007 mm, 0% | 39.58 / 0.00 / 60.42 | 7.2 mm, 8.48% | 0.240 / 6.729 | 543.6 / 489.5 | **holds with qualification** |
| D 27 Bl1 | C3 | 0.463 / 1.373 | 0.277, 97.96% | 20.41% | 0.73 deg, 0.005 mm, 0% | 38.78 / 0.00 / 61.22 | 16.2 mm, 18.64% | 0.205 / 8.133 | 601.5 / 454.9 | **holds with qualification** |
| H 10 Bl1 | C4 | 0.931 / 3.098 | 0.283, 92.05% | 9.09% | 2.19 deg, 0.009 mm, 0% | 5.68 / 13.64 / 80.68 | 12.6 mm, 8.10% | **2.332 / 2.412**, stretch over dropped **c5** 100% | **633.9 / 734.9** | **does not hold** |
| I 06 Bl1 | C5 | 0.682 / 2.130 | 0.290, 88.27% | 2.79% | 1.74 deg, 0.007 mm, 0% | 32.96 / 0.00 / 67.04 | 3.6 mm, 1.13% | 0.302 / 1.354 | 6144.6 / 6260.4 | **does not hold** |
| I 13 Bl1 | C5 | 0.531 / 1.461 | 0.272, 91.25% | 1.88% | 1.40 deg, 0.006 mm, 0% | 31.87 / 0.00 / 68.12 | 1.8 mm, 0.63% | - | 4607.1 / 4673.5 | **does not hold** |

Cross-check on the stretch's plane (`p_*` columns): on every matched lane the band our material contributes
under the stretch's dots agrees with the authors' own normal at **0.7-5.5 deg median** (p90 <= 12.0), with
**0.00% above 45 deg** on all nine matched lanes and an offset along their normal of **0.004-0.023 mm**. Our
face under their line is the *same* face, everywhere.

- **C2 (Pot C 03 Bl1) — holds.** Their line is the outer rim of their own surface (0.296 mm, 90.8% on a >100 deg
  edge) — but that surface is small (897.2 mm2, 8150 points, plate-like: n_ax 0.939) and **5.826 mm** from our
  kept face, which is **6.5x larger** (5820.9 mm2, 23898 points, n_ax 0.978). Our band inside 2 mm of their line
  is at **81.6 deg** with a **2.215 mm** offset (the one lane the test calls `different_surface`), and **90% of
  their dots' nearest dump point is unclustered, 10% a dropped cluster, 0% kept**. "The authors traced the base and
  not the break" holds in the sense that their line is the boundary of a separate, small, plate-like face that
  our pipeline did not keep and that no part of our surface comes within 2 mm of.
- **C1 (Pot I 25, both lanes) — holds with qualification.** See section 1: nothing geometric is swapped, both
  lanes are inside the bar (max 1.475 / 1.690 mm), and the inversion is the authors' surface order.
- **C3 (D 22 Bl0, D 27 Bl0/B1) — holds with qualification.** All three reference lines are genuine boundaries of
  the authors' *own* faces (0.257-0.280 mm, 85.4-98.0% on a >100 deg edge), not chords (chord_ratio 0.0075 /
  0.0212 / 0.0207) and not scribbles through a face's interior in their own release. What separates the releases
  is where the *same* face ends: our face continues under their line to 0.7-2.3 deg and 0.005 mm, and our
  material's >100 deg edge lies **5.97 / 6.73 / 8.13 mm** further out, across a stretch of 45.0 / 7.2 / 16.2 mm.
  In the stretch, their dots sit **0.90 / 0.24 / 0.21 mm above our material** (so the stretch is over our face, not
  off it), and their nearest dump labels there are 92.3% unclustered on D 22 but 100% kept (c0 / c1) on D 27.
  D 22 is the one lane where **their** face is the larger (1707.1 against our 1285.0 mm2); on D 27 ours is
  (11% / 32%). So "ours is the better match to the mesh/surface" cannot be settled by size either way — the
  measurable statement is a face-extent difference of 6-8 mm on the same face, and that is what the conservator
  is seeing in the pictures.
- **C4 (Pot H 10 Bl1) — does not hold.** Neither alternative he offered survives. Not (a) a label mismatch: their
  line rides their Surface_1 at 0.283 mm and our face is 0.252 mm from that same Surface_1 (pair margin 6.756).
  Not (b) or (c): our surface is **not bigger** — 633.9 against their 734.9 mm2, **14% smaller** — and the whole
  12.6 mm stretch lies over material **2.332 mm outside** our kept face, **100% nearest the dropped cluster c5**
  (dump size 685). The reference follows a band our pipeline dropped; ours does not span it.
- **C5 (Pot I 06 Bl1, I 13 Bl1) — does not hold.** Our mesh is not bigger: the areas match to **1.8% and 1.4%**
  (6144.6 / 6260.4 and 4607.1 / 4673.5 mm2, ours the smaller on both), and no part of our kept face is break
  surface — the band under their lines is **1.74 / 1.40 deg** off the authors' own normals with **0.00% above
  45 deg** and offsets of **0.007 / 0.006 mm**. The departure from the bar is 2.79% and 1.88% of the loop
  (3.6 mm and 1.8 mm), over material **0.302 mm** (I 06) below their line; I 13 has no stretch of three dots at
  all. **I 13 is one case, not two:** over its 160 dots the nearest dump label is 31.87% kept (all c1) and 68.12%
  unclustered, with **0% nearest c0** — 293's "68.75% nearest c1 / 31.25% c0" is its own per-dot assignment, and
  the dump does not reproduce a second face on this lane.

### 3. Q6 (C6) — Pot E 16 Bl0, and Pot H 02 both lanes

**Q6a, Pot E 16 Bl0 — "our edgeline fits better than the reference" holds with qualification.**
Their line rides our material closely (median 0.672 mm, p95 1.337, max 1.552) and **52.7%** of its dots are
within 1 mm of our >100 deg edge; our band under it agrees with the authors' own normals to **3.28 deg**
(93.4% under 10 deg, 0.00% above 30) at an offset of **0.023 mm** (p95 0.142). But on a **41.4 mm stretch
(20.8% of the loop)** their line runs up to **10.86 mm inside our face**, still only **0.206 mm** above our
material (i.e. on the face, not off it), while our edge is **7.67 mm** from their line there — and the material
immediately past our edge is at **68.6 deg** median from our face's local normal (**71.4%** beyond 45 deg), a
sharp, real turn. So on four fifths of the loop the reference sits on our edge and on one fifth it is inset by
up to 10.9 mm; "ours fits better" is right about that fifth, but their line is not a boundary of a *different*
surface anywhere on this lane.

**Q6b, Pot H 02 — the decisive question.** Neither (i) nor (ii) as posed; the measurement separates them.

- **The turn is real and sharp, so (ii) is refuted.** Non-kept material within 2 mm of our face's rim sits at
  **48.4 deg** median from our face's local normal on Bl0 (**54.8%** beyond 45 deg, n=4015) and **44.2 deg** on
  Bl1 (**48.5%**, n=1707); E 16's corresponding figure is 68.6 deg. A shallow crease or a small scan gap would be
  a few degrees.
- **It is not (i) either.** The material past our line is the dish's own base-rim — a second real face of the
  same piece, coupled to our face (Bl0: **282** unclustered points within one sample spacing (0.637 mm) of our
  kept material; Bl1: **36**), not the sherd's broken face and not a sampling gap: the largest distance from any
  reference dot to any dump point is **0.487 mm** (lead's probe, reproduced as "no dot further than 2 mm from
  material"; my max distance to our kept material is 2.090 / 1.962 mm on Bl0/Bl1).
- **Their line does not trace that turn either.** On Bl1 the 59.4 mm stretch (34 dots, 24.2%) has their dots
  **0.221 mm above our kept wall face** and **4.67 mm from our edge**; on Bl0 there is no departure at all
  (**p95 1.332 mm, max 2.090 mm**, longest run beyond 2 mm = 1 dot) and 71.2% of their dots are within 1 mm of
  our >100 deg edge.
- **Bl0 is clean.** Its band agrees to **1.73 deg** (97.0% under 10 deg, 0.00% above 30) at 0.006 mm; nothing on
  the at-bar lane needs qualifying.
- **Verdict, two sentences.** Our line stops at a **real, sharp turn of the pottery at 44-48 deg**, and the material
  past it is the dish's own base-rim left unlabelled by growth (a partition effect, as the lead's probe says), not
  a shallow crease or a scan gap — so the conservator's *judgement* that ours is the better edge **holds**, and on
  Bl1 it holds for the opposite reason to the one he gave: the authors' line does not go past our line at all, it
  runs 4.67 mm inside our face, so what "continues" past our line is the base, which neither release's line
  follows. His claim that our line stopped short of the end of *that* face is refuted.

### 4. The authors' surface has no mesh boundary (Q3's other half)

`out/meshrim.tsv` — all **nine** DS meshes are **CLOSED**: every edge shared by exactly two triangles
(C 03 46584/46584, D 22 27174/27174, D 27 16206, E 16 72459, H 02 53019, H 10 28950, I 06 68562, I 13 53556,
I 25 18099; zero boundary edges, zero non-manifold edges; median edge 0.606-1.175 mm). "Where does the authors'
mesh end at the break" therefore has no answer on that artefact, and the reference's edge can only be read on
the surface geometry — which is what the >100 deg tangent-plane gap used throughout does. The planned mesh-rim
distance is dropped rather than reported as a number it cannot be.

### 5. What holds, and the one mechanism the numbers do name

Of the conservator's five claims: **C2 holds**; **C1 and C3 hold with qualification** (C1: the inversion is in the
authors' surface order, not in our detection, and no line is on a different face; C3: all three reference lines are
real boundaries of the authors' own faces and the difference is where the same face ends); **C4 and C5 do not
hold** (on H 10, I 06 and I 13 our kept face is the *smaller* one, by 14%, 1.8% and 1.4%, and no part of it is
break material). On C6 the conservator's judgement holds on both pieces, his stated reasons do not: on E 16 their
line is inset up to 10.9 mm inside our face, and on H 02 the "surface that continues" past our line is the dish's
base-rim, which their line does not follow either.

**No lane is a welded break facet, and that is measured, not assumed.** On all nine matched lanes, the share of
the 2 mm band that our kept material contributes under the reference and that is pitched more than 45 deg off the
authors' own normal is **0.00%** (median 0.7-5.5 deg, offset 0.004-0.023 mm); the extra-surface test returns
`coplanar` on eight lanes and `different_surface` only on C 03, where the second surface is the authors' own
small face, not a facet welded into ours. So the "our surface includes part of the break surface" mechanism is
not present in this sample and does not need a growth or classify change.

**The mechanism the numbers do implicate is partition, and here is its number.** Our edgeline is the boundary of
the *labelled* face. Immediately outside that boundary there is real material of the same sherd that the growth
left unlabelled — on H 02 a **2311-point** unclustered band inside the 2 mm corridor (89 on Bl1), with **282 / 36**
of its points within one sample spacing of the labelled face, at **48.4 / 44.2 deg** from it; on E 16 68.6 deg;
and on C 03, D 22 and H 10 the reference line runs mostly or wholly over material we dropped or never labelled
(90% / 92.3% unclustered on C 03 / D 22 in the stretch, 100% over the dropped cluster c5 on H 10). Where the
material past that boundary *is* labelled, our face extends **2.4-9.6 mm** past the reference (`rim_d_ref_med`),
on the same plane. Hypothesis for ticket 296: **the face-extent rule is what decides these lanes — the >100 deg
growth boundary ends the face 2.4-9.6 mm outside the authors' boundary on the coplanar lanes, and leaves a
one-facet band (44-69 deg) unlabelled at the piece's own turns** — so a change here belongs to growth/partition
(predict: growing across the measured turn moves our edge toward the reference on E 16, D 22, D 27 and H 02 Bl1,
and does nothing on I 06/I 13, where the offset is 0.2-0.3 mm and already inside the bar), not to the walk seed
and not to a weld test.

### 6. Deviations and things not measured

1. **Our line's own geometry is gone** (293 deleted `out/geom`); where a lane needed "where is our line", the
   >100 deg boundary of our kept material stands in (293: our lines ride that edge at 0.98 mm, ring 0.40-0.46 mm).
   No lane's verdict rests on that substitution alone.
2. **The welded-facet instrument was amended once, before any lane's verdict was read** — the pre-registered
   annulus-plane control wrapped around a >100 deg edge (on D 22 it returned an 81 deg "plane"), so the test
   became a direct per-point comparison against the authors' own supplied normals. **No threshold moved.**
3. **Ticket 293's I 13 split (68.75% c1 / 31.25% c0) is not a nearest-label count** of the dump; mine (31.87%
   kept / 68.12% unclustered, 0% c0) answers the different question actually asked. Reported, not silently
   replaced. Likewise **H 10's "21 of 88 dots over c5"**: I count 12 of 88 nearest a dropped cluster, 8 in the
   stretch, and the dump's c5 is **685 points** against ticket 281's 629.
4. **Dump cluster ids are survivors re-issued in descending size order** (ticket 283), while PAIR lines index the
   pre-merge list. Every `c`-number above is a dump id with its size stated where it matters; none is cross-indexed
   with 293's PAIR or classify faces. The lead's probe labels were reproduced independently (Bl0 87.82/12.18,
   Bl1 75.18/24.82 nearest c0/c1 for the same 156 / 137 dots).
5. **Not measured:** the physical cloud/mesh distance for any lane (the ticket's instrument is the authors' own
   artefacts); our edgelines' own arc length on the Phase-B lanes (ours_arc is nan there, geometry deleted); the
   corpus-wide pairing of *our* breakline index to *our* surface index (only I 25 was checked, and that is where
   it inverts); Pot I 30 and Pot J 19, where no interior criterion discriminates.
6. **The Pot I 25 "swap" is a naming inversion, not a lane swap** — stated in section 1 with the numbers, because
   the ticket's premise ("the lanes are swapped") reads as fewer than it is.

### 7. Files

`out/q1_summary.txt`, `out/q1_pieces.tsv` (163 rows), `out/q1_lines.tsv`, `out/q1_disagree.tsv`,
`out/q1_i25_surfaces.tsv`, `out/q1_i25_lines.tsv`, `out/q1_i25_ours.tsv`; `out/lanes.tsv` (11 lanes, 81
columns), `out/pairing.tsv`, `out/detail_<piece>_Bl<k>.json`; `out/q6.tsv`; `out/meshrim.tsv`;
`out/repro293.tsv`, `out/repro295.tsv`; scripts `p295_lib.py`, `p295_repro.py`, `p295_q1.py`,
`p295_lanes.py`, `p295_q6.py`, `p295_meshrim.py` (copies in `scripts/`, md5 in `scripts.MD5`; the same
files are on branch `295-verify-the-conservators-read` under `.scratch/pota-repro/295/`).

## Lead verdict (2026-10-25)

**Accepted.** The reproduction gate (385/385 ticket-293 numbers, worst delta 0.0050) plus three numbers I checked myself before landing: Pot H 02 Bl1 = 137 dots / 245.168 mm with a median 0.221 mm to our material, Pot E 16 Bl0 = 112 / 199.1, Pot I 25 Bl0 = 69 / 124.26. Run directory present with `run.json`, `submit.sbatch`, `scripts.MD5`, no geometry; index row appended with the verdict field left to me.

**1. The adjudication stands: C2 holds; C1 and C3 hold with qualification; C4 and C5 do not hold; C6's judgements hold with both stated reasons corrected.** Two of the six failures are in our own favour — H 10, I 06 and I 13 are *not* cases of our surface growing over the break — and that is the least comfortable direction for them to fail in, so they are recorded as measured, not as relief.

**2. My own reading was wrong, and it is the second time this exact error has appeared.** I told the conservator that on H 02 Bl1 "the authors' line runs mostly over the unlabelled band and carries on over the turn". It does not. The band is an unlabelled corridor **inside** our face — 1.525 mm (Bl0) / 0.667 mm (Bl1) from the kept material, 282 / 36 points within one sample spacing of it — and their line lies 0.221 mm above our wall face and **4.67 mm inside our edge**. The first instance was Pot D 22, where the chord turned out to be the reference's. **Rule to carry: which line stops short is not readable from a plot; only the per-dot signed position says it.**

**3. The welded-facet hypothesis is dead on measured grounds.** On all nine matched lanes, **0.00%** of the 2 mm band our kept material contributes under the reference is pitched more than 45 deg off the authors' own normals (median 0.7-5.5 deg, offset 0.004-0.023 mm). Nothing here licenses a growth or classify change on the "our surface swallowed part of the break face" story, and that includes I 06 / I 13.

**4. The gate cannot be the fix, and this amends the ticket's own 296 prediction.** The measured turns do not differ in per-step size: H 02's straddling pairs have a median step of **3.23 deg** with **52.7%** at or below the 3.4 deg gate (ticket 281), while Pot D P03's severing bottleneck is **3.45 deg** and P22's **3.06** (ticket 271). A gate loose enough to cross H 02's base-rim also crosses P03's flank and re-breaks the lane 271 fixed. So "grow across the turn" must not be attempted by moving theta; what remains is **which faces are kept** — a third surface, or the paper's own base treatment (`C:/PR/papers/text/sfspp-2502.13986v1.md:313` counts base sherds as detected parts, `:460` lists base handling as future work).

**5. No lane changes state.** Pot I 25's two lanes were already counted at bar (283 of 292 sound lanes); Pot C 03 Bl1 stays a partition mismatch until the conservator rules; Pot D 22 Bl0 stays a miss whose reference is a chord. The two rulings this ticket now supports are the ones on his desk: strike C 03 Bl1 (283/291) and/or D 22 Bl0 (283/290).

**6. If ticket 296 is cut, it is a partition test, not a growth sweep:** keep a third surface (or label the unlabelled corridor) and show the edge move toward the reference on E 16, D 22, D 27 and H 02 Bl1 while I 06, I 13 and every at-bar lane stay unchanged, with P 03 Bl1 and both P 22 lanes as regression guards, and with no claim of corpus-wide identity (ticket 284: the input clouds cannot be regenerated).

**7. Deviation 1 is accepted as the honest limit of this ticket.** Our lines' own geometry is gone, so the >100 deg boundary of the kept material stands in for them. No verdict rests on the substitution alone, and ticket 293 measured our lines to ride that boundary at 0.98 mm, so it is sound for this purpose — but every number in this ticket inherits it and must be quoted with it.
