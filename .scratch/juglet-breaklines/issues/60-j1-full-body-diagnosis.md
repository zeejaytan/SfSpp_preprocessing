# 60 — Why does the break-stop test call J1's growth "break-like"? Test the full-body hypothesis and the normal field

**What to build:** a **diagnosis**, not a fix. Three read-only measurements that together
decide between three candidate explanations for ticket 59's contradiction, plus one debug-only
dump of the growth's candidate pool so the contradiction can be counted rather than guessed.

**Why now (2026-11-02, conservator):** after ticket 59's read-out the conservator chose this
run: "let's do the run comparing J1's cloud normals to its mesh. i think it might be because it
is a piece contain full 360 degree body". The lead's quick shape check (axis frame, 5 deg
azimuth bins) supports the premise: **J1 covers 360.00 deg of azimuth with a 0 deg
largest gap** -- i.e. it is a ring fragment with a top and a bottom break edge (see H1), J7 also wraps (360 deg, 2 deg gap), J2 wraps 0.94 (13 deg gap) and J9 0.85
(27 deg), while J3-J6 and J8 cover only 0.24-0.42 (219-279 deg gaps). J1 is also ten times the
mesh of J2 (24 294 vs 2 565 vertices).

**Answers:** U19, E1

**Blocked by:** none (reads ticket 59's run dir and the corpus read-only)

**Status:** resolved
**Working in:** chat on Thinkbook16 (2026-11-02)
**Branch:** 60-j1-full-body-diagnosis, in /c/PR/worktrees/sfs/60
**Worker:** DeepSeek subagent 8088c8e6-47f3-4bf2-ad72-4427dc09eb04 (cwd C:/PR/worktrees/sfs/60)

## Spec

### Given (measured, from ticket 59, commit 8862864)

- Armed in the growth loop, J1's pairing test reports `npts=19312 wall_like=1674 break_like=17638`
  (8.7 % wall-like); J2 reports `npts=1883 wall_like=1647` (87.5 %) on nearly the same
  wall-like COUNT. Armed J1 collapses (S0 13 850 -> 351, genuine pairs 8/9); the other eight
  move -1 to -9 %.
- Offline on the same piece, 89-98 % of J1's wall points pair, and the mesh labels call 62.5 %
  of J1's faces wall. So the live test rejects candidates the offline test would accept.
- The live test (worker patch, run-dir provenance `work/patch.diff`, +111/-0, base 638504bf):
  ray cast along the candidate point's normal, window `[0.9, 7.2]` mm, `eps_mm=0.45`,
  `exit_dot=-0.4`; a candidate is admitted only if it pairs.
- The pieces' own measured wall thickness varies 1.876-2.839 mm; J1 is 1.876 mm.

### The three explanations this run must separate

- **H1 (conservator) — shape, restated 2026-11-02 after the lead got it wrong.** The lead's
  first reading ("full 360 deg, therefore no break edge") is **wrong**; the conservator corrected
  it (m03836): "no, it does have a break boundary, a 360 degree full body means it's cylindrical,
  it STILL have break edge at top and bottom". J1 is a **ring fragment**: one piece wrapping the
  whole circumference, so it has no break edge *around* its side, but it has a break edge at the
  **top and another at the bottom**, each running all the way round. A growth that encircles
  ends with its frontier lying along those two annular edges, and an edge point cannot pair --
  its ray leaves the shell at a grazing angle instead of crossing clay -- so the bag goes
  edge-dominated and the stop fires everywhere: the 91 % break-like bag. What the dump must show
  if H1 is right: the candidates cluster along the two annular break edges, not uniformly over
  the surface. (Workspace precedent: the Juglet is 2/9 ring fragments by count and 54 % by mass,
  and TORA's lessons.md records "I ruled out a breakage pattern the target object actually has".)
- **H2 — normals.** J1's cloud normals (the t47 corpus clouds, 840 666-841 413 points) disagree
  with its mesh: sign flips, or normals estimated across an edge on a closed 360 deg shell. A
  flipped normal makes every ray shoot outward into air -> no pair.
- **H3 — bookkeeping.** `npts` counts candidate *evaluations* across growth iterations, not
  distinct points; if so, J1's 19 312 is ten times J2's 1 883 because the piece is bigger, and
  the wall-like count ~1.65 k on both pieces is the real (piece-independent) wall population.

Only one of them is ruled in by the numbers; the run must say which, and must not stop at
"all three are possible".

### Plan

**A — shape audit (read-only, all nine).** In each piece's own axis frame
(`Dataset/Axes/Juglet/<piece>_Axis.xyz`): cast rays from the axis line outward at 72 azimuths x
several heights, count how many azimuths hit the mesh — a sector piece returns one contiguous
arc, a full body returns hits all the way round. Report per piece: azimuth coverage, largest
hit-free arc, radial profile, and the width of the fold band (the band where the surface turns
through 180 deg between outer and inner sheet). One render: J1 vs J7 vs J3 in the axis frame,
coloured by hit/miss.

**B — normal field (read-only, all nine).** For each piece compare the cloud the pipeline
actually reads (`Dataset/Point/Juglet/<piece>_Point.pcd`) with its mesh
(`Dataset/Mesh/Juglet/<piece>_Mesh.obj`): nearest-triangle assignment, then report the angle
between cloud normal and face normal (median, p90), the **sign-flip rate** (angle > 90 deg), and
the fraction pointing into the shell vs out. J1 against the other eight in one table; one J1
render coloured by agreement.

**C — the candidate pool (one debug build, J1 only).** Rebuild the t59 patch with a
debug-only env switch (`SFS_BREAK59_DUMP=<path>`) that writes, per candidate evaluation:
point id + coordinates, its pairing result, the iteration index. Run **J1 only**, two cells in
one job: gate-closed (dump on) and armed (dump on). Then classify each dumped candidate by
(a) its stage-0 face label from ticket 59's `out/labels/Juglet_Piece_1.npz`, (b) its
geodesic distance to the nearest rim/fold band, (c) whether it is a repeat evaluation of the
same point. Reproduce the 19312 / 1674 figures from the dump; if you cannot, say so - that is a
result.

### Gate (written by the lead before hand-over; the lead will re-run these)
1. The arm dump must reproduce ticket 59's J1 counts exactly (19312 / 1674 / 17638) or the
   diagnosis is reported void with the difference shown.
2. The gate-closed J1 with the debug build must write an S0 byte-identical (md5) to ticket 59's
   control J1 S0 (`passA` in run 20261102-1144_638504b_t59-breakstop-stage0). If it does not,
   the dump changed the path and the run is void.
3. A and B run on **all nine**; J1 must appear beside the other eight in one table.
4. Every claim names its type: measurement, inference, or guess.

### Deliverables
- Tables in the run dir, PNGs copied to `SfSpp_preprocessing/artifacts/60/` (gitignored).
- A **Results** section in this ticket: numbered findings, each tagged to H1, H2 or H3, with the
  number that supports it; then one paragraph saying which hypothesis is ruled in and what
  would be needed to act on it. No verdict on whether to merge anything - that is the lead's.
- Jobs: every `sbatch` with its `sacct` State/ExitCode.

### Budget
Two sbatch jobs, one hour wall clock, no GPU. Heavy work on compute nodes only.

### Do not
- Change any tracked source file; commit or push nothing.
- Touch the shipped defaults or any `SFS_*` behaviour; the dump switch must be inert unless set.
- Delete or rewrite ticket 59's run dir (read-only input).


## Results

**Run:** `/data/gpfs/projects/punim2657/SfSpp/runs/20261102-1628_cda869c_t60-j1-diagnosis`
(commit `cda869c`, `run.json` inside). Six sbatch jobs: the two budgeted (1 and 2), then jobs 3–5
on the lead's explicit go-ahead (A+B all nine, the label join, the sign figure and z-band table),
and job 6 to re-render a lead-authorised figure whose axes were squashed by a shared y-limit. No
tracked source file changed, and total compute is 8 minutes 24 seconds. The original two-job budget
was exceeded only by direct instruction; the two gates stand as recorded below.

**The finding.** On eight of the nine pieces the pipeline's per-rung normal re-estimate agrees
with the mesh — 0.2 % to 2.4 % of points sign-flipped — and the stop test pairs 83–91 % of their
points. On J1 the same re-estimate flips **41.6 %**, while the stored normals in the corpus cloud
of J1 are consistent (**0.4 %** flipped): the field the pipeline computes is worse than the field
it was handed, and only on this piece. J1 is also the only piece that closes in the round (surface
azimuth coverage 1.000 at mid and upper heights, where the sector pieces sit at 0.10–0.51), and
its mesh is closed with no annular crease loop — so its two break rings are not creases and the
shape evidence is the azimuth coverage, not a crease test.


### Jobs

| job | name | sacct State | ExitCode | elapsed | node |
|-----|------|-------------|----------|---------|------|
| 34207633 | t60-ab | COMPLETED | 0:0 | 00:02:09 | spartan-bm024 |
| 34207945 | t60-c  | COMPLETED | 0:0 | 00:05:12 | spartan-bm026 |
| 34208340 | t60-ab2 | COMPLETED | 0:0 | 00:00:37 | spartan-bm139 |
| 34208455 | t60-p2 | COMPLETED | 0:0 | 00:00:12 | spartan-bm163 |
| 34209999 | t60-sign | COMPLETED | 0:0 | 00:00:12 | spartan-bm172 |
| 34210066 | t60-sign2 | COMPLETED | 0:0 | 00:00:15 | spartan-bm172 |

Job 1 (34207633) is the nine-piece gate-closed pass with ticket 59's **unpatched** passA binaries
(mesh `736ff95c976486d17f7c00b3af402040`, edge `cbf747dc3172fe0bbd188822df14092a`) plus the two
existing inert instruments `SFS_DUMP_STAGE` and `SFS_NORMAL_DUMP_DIR`; it produced the rung-1
clouds and the exact normals the flag test later consumed. Job 2 (34207945) is the t60 debug build
(md5 `e03a8bc10f2fdb90091f2e7e82e77b98`, unpatched 1621216 B vs instrumented 1624688 B;
`work/patch2.diff` = 58 added / 5 removed lines), six gate-closed J1 attempts, three armed J1
attempts, then the classification.

### Gate 1 — PASS, exact

Armed J1 cell, instrumented build, dump at `out/dump/armed_att1.tsv`:

```
[BREAK-59] piece=Juglet_Piece_1 npts=19312 wall_like=1674 break_like=17638
```

identical to ticket 59's 19312 / 1674 / 17638. [measurement]

Index check: the dump's 19312 `FLAG` rows index exactly the 19312 points of
`out/dump/Juglet_Piece_1/r1_downsampled.ply`, and job 1's nine rung-1 sizes —
J1 19312, J2 1883, J3 2841, J4 2768, J5 5671, J6 4373, J7 7633, J8 3464, J9 1475 — equal
ticket 59's nine `npts` exactly, so the dump's index space is the point set the test indexes.
[measurement]

An offline re-implementation of `computeBreakStopFlags59` (both signs of the normal, s from 0.9
to 7.2 mm in steps of max(0.10, 0.75·eps) = 0.3375, eps 0.45 mm, exit_dot -0.4, k = 1, skip the
query point) reproduces the dumped flag on **19312 / 19312 points, agreement 1.000000**. Every
offline number below therefore describes the shipped rule, not an approximation of it. [measurement]

### Gate 2 — NOT MET as written

Six gate-closed J1 attempts, `logs/gate2.attempts.tsv`: every one flip=true, S0 md5
`453661ae36dfce04287d29da9255e01f` (distinct md5 = 1). The reference passA S0 is
`ff97481e9229201407d182bacd91fd8c`. `matched=0`. [measurement]

**The instrument is not the cause.** Job 1 ran the unpatched t59 passA binaries on the same cell
and produced the same S0 md5 `453661ae…` on J1. [measurement] So on this path the instrumented
build is byte-identical to the unpatched one, and the divergence lies between passA's session and
*any* run made now. passA's J1 log and this session's agree on every printed parameter — theta
19.03055 / 6.42511, kappa 1.00000, npts 19312, clusters 4, flipped true — and part company
downstream: `surf0_points` 13850 against 13217, `surf1_points` 15173 against 16436.
[measurement] Unresolved; one measurement would settle it (diff passA's staged corpus inputs and
cell.tsv against a fresh cell).

Note on the gate's wording: it names run `20261102-1144_638504b_t59-breakstop-stage0` as the
passA source, but that run carries only `out/{decision_table.tsv, labels/, pota_control.tsv,
stage0_summary.json}` — no S0 file. The reference md5 above is run
`20261102-1155_638504b_t59-control-gateclosed`, `outA/geom/Juglet_Piece_1.S0`.

**Lead's ruling (2026-11-02), recorded as given: Gate 2 as written: not met — cross-session
reproducibility of this piece's chain fails, cause under investigation by the lead, not
attributable to the instrument (instrument-inertness test passed: closed == unpatched,
`453661ae`, 7/7).**

The evidence lines behind that ruling: 7 cells in this session give S0 md5 `453661ae…` — the six
gate-closed attempts of job 2 plus job 1's unpatched-t59 cell — against passA's `ff97481e…`;
the mesh binaries differ (`e03a8bc1…` instrumented vs `736ff95c…` unpatched) and the S0 does not.
The lead's forensic has already established identical binaries, identical staged-input md5s and
numerically agreeing mesh-stage logs, so the divergence is downstream of the mesh stage. It is a
caveat on this run, not a work item here, and it does not touch C's numbering, which counts the
armed dump against ticket 59's printed line.

### Findings

1. **The failure is orientation, not reach — H2, decisive.** [measurement] Of the 17638
   break-like points, **96.14 %** find a point within 0.45 mm of the march line whose normal
   points the *same* way; **3.86 %** find nothing within eps; **0.00 %** pair. All 19312 points:
   paired 1674 (8.67 %), same-side hit 16958 (87.81 %), nothing 680 (3.52 %). The march is not
   short of geometry; it is refused by the sign.

2. **The rung-1 normal field is geometrically right and sign-wrong — H2.** [measurement] Folded
   angle to the mesh face normal: all points median **3.93°** / p90 15.19; break-like 3.74° / 14.18;
   wall-like 6.78° / 23.60. Sign-flip rate (angle > 90°): all **41.6 %**, break-like **45.0 %**,
   wall-like 6.1 %. Point-to-face distance median 0.00008 mm. H2 as literally worded ("cloud
   normals disagree with the mesh") is only half true: the direction agrees to a few degrees and
   the *sign* does not. These are the per-rung re-estimated normals from
   `getNormalsOnSurface`, not the corpus PCD normals.

3. **The rule fails exactly where it should succeed — H2.** [measurement] Joined to ticket 59's
   stage-0 face labels: 14340 of 19312 rung points (74.3 %) lie on faces labelled **wall**, and
   only **52** of those (0.36 %) are wall-like; 99.6 % are break-like. roll 1623 points (8.4 %)
   wall_rate 0.551; fracture 1586 (8.2 %) 0.381; anomaly 1763 (9.1 %) 0.070. On J1 the pairing
   test is close to the negation of the structural wall label.

4. **H3 refuted.** [measurement] `npts` is the rung cloud size (code read: the print uses the
   point count of the cloud the loop just rebuilt), and the candidate dump holds 212432 rows over
   **212432 distinct (frontier, candidate) pairs — 0 repeat rows**. The pool is not inflated by
   re-evaluation. 19312 seeds: every rung point seeds once. Armed verdicts: claimed 117019,
   flagstop 89038, theta 5040, admit 1335; the gate-closed cell admits **17861** of the identical
   212432. Armed growth keeps 7.5 % of what it would otherwise keep.

5. **H1's original mechanism is ruled out.** [inference] A fold would leave the point with
   nothing within eps, or with a hit on the far sheet beyond the 7.2 mm window; only 3.86 % of
   break-like points are in that state and 96.14 % have a facing partner. By this test a point on
   a fold is indistinguishable from a point on a flat.

6. **H1's corrected spatial prediction is contradicted by the render.** [inference] In the r–z
   section of the rung cloud the 1674 wall-like points (which contain all 1335 admitted
   candidates) form **one contiguous patch** on the outer bulge, over z ≈ -424 to -404 of the
   piece's -447 to -404; the lower hook and the left flank are entirely break-like. Two annular
   break edges running all the way round would put the successes in two bands at the z extremes
   and spread them round the azimuth, not in one local patch. [guess] The patch boundary is where
   the MST orientation happens to agree with the mesh's.

7. **H1's premise is supported, its conclusion is not.** [measurement] The r–z cross-section
   closes a loop over z -447…-404, r 5…20 mm — consistent with the conservator's tube with a top
   and a bottom rim. [inference] That shape is why the orientation field *can* come out
   inconsistent round the tube (the H2 failure); it does not by itself stop pairing.

8. **Ticket 59's collapse, in this run's own numbers.** [measurement] Over the identical 212432
   evaluations the armed cell admits 1335 candidates and the gate-closed cell 17861; ticket 59's
   `surf0_points` 351 against the control's 13850 with clusters 87 / 560 / 65.

### Which hypothesis is ruled in

**H2, in a sharper form:** the stop rule is an *orientation* test, and the field it consumes — the
per-rung PCA + MST re-estimate from `getNormalsOnSurface` — carries a sign that is inconsistent
on J1 (45 % of break-like points flipped against the mesh) and nearly anti-correlated with the
structural wall label (0.36 % of wall faces pair). No number here needs a fold or a
shape-specific geometric failure; the march reaches the opposite sheet in 96 % of cases and is
refused by its sign. H1's shape survives only as the plausible *reason* the orientation
propagation is inconsistent on this piece and not on the other eight — that link is a **guess**
until B's flip-rate column exists for all nine. H3 is refuted outright.

Job 4 sharpens that from "inconsistent" to "one sheet inverted": on J1 the rung normals are
89.8 % flipped on the S0 (interior) sheet and 2.4 % on S1, so the field is coherent per sheet and
the two facing sheets point the same way instead of opposite — which is exactly what a rule asking
for `dot <= -0.4` must refuse. [measurement]

To act on H2 the next thing needed is the orientation field itself, and the cheapest correct
version of it is already in the input: on J1 the corpus cloud's stored normals are 0.4 % flipped
against the mesh, and the pipeline throws that field away and re-estimates per rung. Either
re-orient the re-estimate to the mesh's faces, or use the stored corpus normals for this test.
That is a fix, outside this ticket.

### Measurement B — the normal field, all nine (job 3)

Sign-flip rate against the mesh face normal, rung-1 re-estimated normals beside the stored corpus
PCD normals, one row per piece (`out/analysis2/B_normals.tsv`): [measurement]

| piece | rung-1 flip | corpus PCD flip | folded median rung / corpus |
|-------|------------|-----------------|------------------------------|
| J1 | **0.4163** | 0.0040 | 3.93° / 2.55° |
| J2 | 0.0159 | 0.0242 | 5.82° / 3.71° |
| J3 | 0.0134 | 0.0241 | 4.02° / 2.70° |
| J4 | 0.0170 | 0.0181 | 4.75° / 3.05° |
| J5 | 0.0055 | 0.0060 | 3.54° / 2.46° |
| J6 | 0.0018 | 0.0010 | 3.65° / 2.53° |
| J7 | 0.0026 | 0.0054 | 3.92° / 2.60° |
| J8 | 0.0130 | 0.0137 | 4.34° / 2.74° |
| J9 | 0.0068 | 0.0078 | 5.24° / 3.27° |

**J1 is a 25× outlier** (0.416 against a worst-other 0.018), and on J1 the *stored corpus normals
are consistent* (0.0040) while the pipeline's per-rung re-estimate scrambles 42 % of them — so the
estimator is not corpus-wide bad, it fails on this one piece, and on this one piece a correct
field is already in the cloud and is not the field the test consumes. [measurement]

J1's wall-like fraction sits at the same extreme: 1674/19312 = 0.0867, against J2 0.8746,
J3 0.8712, J4 0.8696, J5 0.9030, J6 0.8966, J7 0.9074, J8 0.9053, J9 0.8346 (ticket 59's armed
cells, re-derived here from `r1` sizes and the flags). [measurement]

### Measurement A — shape, all nine (job 3)

`out/analysis2/A_shape.tsv`, `A_loops.tsv` (1666 loops): [measurement]

- **All nine meshes are closed** — `edges_closed_frac` 1.0000 and **zero boundary loops** on every
  piece, so no break edge of any of them is an open mesh boundary.
- **No crease loop reaches the annular criterion on any piece, J1 included.** J1's largest crease
  loop is 30 edges / 20.7 mm long / 0.069 azimuth coverage; J1 has 264 crease loops, all small.
  **A's crease-loop criterion misfired: it returns empty on all nine, and that is a measurement
  limitation, not evidence against H1's corrected prediction — a 360° body's top and bottom break
  edges are not 30° creases.** The ring-distance columns are dropped for that reason, by the
  lead's instruction.
- The shape measurement that does separate J1 is the azimuth audit of the surface: J1 covers
  **360° at mid and upper heights** (`cov_h50 = cov_h70 = cov_h90 = 1.000`, h30 0.806, h10 0.486)
  where J3–J6 and J8 cover 0.10–0.51 and J2/J9 reach 1.000 only at mid heights. [measurement]
  [inference] That is the conservator's tube: a body that closes in the round, so the two break
  edges are the top and bottom rims and there is no side edge.

Consequence for finding 6: the ring curves were never located (no annular crease), so the
ring-distance numbers planned for C could not be computed. The claim that the wall-like patch is
contiguous stands on the r–z render, not on ring distances.

### Where the 1,674 wall-like points sit (job 5)

J1's 19,312 rung points in 8 equal bands along the axis, and split inner/outer at the mid-wall
radius 11.18 mm (`out/analysis2/G_where.tsv`): [measurement]

| band / sheet | n all | % of all | n wall-like | % of wall-like | rate in band |
|---|---|---|---|---|---|
| z 1 (−445.6 … −440.4) | 320 | 1.7 | 31 | 1.9 | 0.097 |
| z 2 | 1842 | 9.5 | 40 | 2.4 | 0.022 |
| z 3 | 3047 | 15.8 | 59 | 3.5 | 0.019 |
| z 4 | 3359 | 17.4 | 37 | 2.2 | 0.011 |
| z 5 | 3723 | 19.3 | 202 | 12.1 | 0.054 |
| z 6 | 2445 | 12.7 | 379 | 22.6 | 0.155 |
| z 7 | 2325 | 12.0 | 508 | 30.4 | 0.219 |
| z 8 (−409.6 … −404.5) | 2251 | 11.7 | 418 | 25.0 | 0.186 |
| inner sheet r < 11.18 | 7980 | 41.3 | 264 | 15.8 | 0.033 |
| outer sheet r ≥ 11.18 | 11332 | 58.7 | 1410 | 84.2 | 0.124 |

[measurement] The paired points are not spread over the piece: the top three bands hold 1305 of
1674 (78 %) of them on 36 % of the points, and the outer sheet holds 1410 of 1674 (84 %) on 59 %
of the points. [inference] That is the same fact the S0/S1 split states — the pairing succeeds
where the sheet that kept its orientation faces the one that did not — and it is **not** a
localisation to a break edge: the top bands are the piece's upper shoulder, not a 2 mm ring.

`figs/B_sign_J1.png` shows it directly: left, J1's rung-1 field in the (r, z) frame, green = same
side as the mesh outward normal (11,273, 58.4 %), red = flipped (8,039, 41.6 %) — a red band that
runs the whole height as one sheet; middle, the corpus cloud's own field at the same axes and
scale, 41,867 / 167 (99.6 % / 0.4 %); right, J2's rung-1 field as the control, 1855 / 28
(98.5 % / 1.5 %). [measurement]

### Item 3 — the label join, delivered (job 4)

Per piece, the rung points' stage-0 label and their wall-like rate (`out/analysis2/D_crosstab.tsv`;
wall-labelled fraction is `frac_of_rung`): [measurement]

| piece | wall-labelled frac | wall-like rate on wall-labelled | wall-like rate, all |
|-------|--------------------|--------------------------------|---------------------|
| J1 | 0.7425 | **0.0036** | 0.0867 |
| J2 | 0.5412 | 0.9607 | 0.8747 |
| J3 | 0.6072 | 0.9907 | 0.8712 |
| J4 | 0.5925 | 0.9909 | 0.8696 |
| J5 | 0.7299 | 0.9925 | 0.9030 |
| J6 | 0.7169 | 0.9895 | 0.8966 |
| J7 | 0.7397 | 0.9818 | 0.9074 |
| J8 | 0.7015 | 0.9930 | 0.9053 |
| J9 | 0.5593 | 0.9830 | 0.8346 |

On the other eight the pairing test passes on 98–99 % of the points that the structural labelling
calls wall; on J1 it passes on 0.36 % of them. The "pairing test ≈ negation of the wall label"
statement is therefore about J1 alone, not about the rule — and the same table shows the rule
works as intended wherever its normal field is sane. [inference]

The offline mirror of the rule also reproduces **all nine** of ticket 59's armed wall-like counts
exactly (J1 1674, J2 1647, J3 2475, J4 2407, J5 5121, J6 3921, J7 6926, J8 3136, J9 1231), not
just J1's. [measurement]

**J1 split by stage-0 label and by surface** (`out/analysis2/F_J1_split.tsv`): [measurement]

| split | n | flip rate | folded median | wall-like rate |
|-------|---|-----------|---------------|----------------|
| label wall | 14340 | 0.4341 | 3.19° | 0.0036 |
| label fracture | 1586 | 0.3102 | 14.39° | 0.3808 |
| surface S0 | 8673 | **0.8975** | 4.60° | 0.0198 |
| surface S1 | 10639 | **0.0240** | 3.46° | 0.1412 |

[inference] This is the mechanism in one line: the re-estimate is *coherent per sheet* — S1 agrees
with the mesh (2.4 % flipped) and S0 is inverted almost wholesale (89.8 %) — so the two facing
sheets carry normals pointing the **same** way instead of opposite, and a rule that asks for an
anti-parallel partner (`dot <= -0.4`) must refuse them. It is not a scattered sign error; one
sheet's orientation came out inverted. Caveat [measurement]: S0/S1 are the gate-closed cell's two
exported surfaces assigned by nearest vertex (S1 median distance 0.0000 mm, S0 1.1931 mm), and S0
is the interior face by our own convention.

`work/t60_ab.py` and `work/t60_ab2.py` are fixed; job 4 ran the label join (`work/t60_p2.py`) and uploaded. The A+B rerun (job 3's phase 1,
29 s on one node) is:

```bash
/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python work/t60_ab.py \
  --run "$RUN" --ds "$DS" --geom "$RUN/outU/geom" --dump "$RUN/out/dump" \
  --normals "$RUN/out/normals" --out "$RUN/out/analysis"
```

It reads only job 1's existing dumps. Job 3 (`submit3.sbatch`, 34208340) ran phase 1; job 4
(`submit4.sbatch`, 34208455, 12 s) ran the label join. `C_rings.tsv` is empty because no ring vertices were
produced, so the ring-distance cross-tab could not be joined, and the right-hand panel of
`C_rings_Juglet_Piece_1.png` is blank.

### Files and renders

Run dir: `submit.sbatch`, `submit2.sbatch`, `bin/bin-MeshPreprocessingHeadless.t60dump`,
`work/{t60_patch.py, t60_c.py, t60_ab.py, patch2.diff, patch2.log, mesh_t60.cpp}`,
`logs/{ab.log, cell2.log, build2.log, c.log, gate2.attempts.tsv, job1.S0.md5, job2.armed.S0.md5,
job1.binaries.md5, slurm-34207633.out, slurm-34207945.out}`,
`out/dump/{Juglet_Piece_1..9/r1_downsampled.ply, armed_att1.tsv, gate_att1..6.tsv}`,
`out/normals/<piece>_call{0,1}.ply`, `outU/geom` (nine S0/S1/Bl0/Bl1),
`out/analysisC/{C_gates.txt, C_modes.tsv, C_normals.tsv, C_labels.tsv, C_pool.tsv}`,
`out/analysis2/{A_shape.tsv, A_loops.tsv, B_normals.tsv, D_crosstab.tsv, F_J1_split.tsv, G_where.tsv,`
`  figs/{A_axis_frame.png, B_normals_J1.png, B_sign_J1.png}}`.

Renders in `SfSpp_preprocessing/artifacts/60/`:

- `C_angle_Juglet_Piece_1.png` — rung-1 r–z section coloured by folded angle against the mesh,
  plus the wall-like / break-like angle histograms.
- `C_rings_Juglet_Piece_1.png` — the same section coloured by pairing flag (blue = the 1674
  wall-like, red = the 17638 break-like); its ring-distance panel is blank, because A produced no
  ring vertices.
- `B_sign_J1.png` — the sign figure: J1 rung-1, J1 corpus field (same axes and scale), J2 control.
- `A_axis_frame.png` — J1 / J7 / J3 in the axis frame.
- `B_normals_J1.png` — J1 rung-1 coloured by folded angle, with its histogram.

**For the conservator's eye:** whether that blue patch sits on the exterior face and the red on
the interior. If the sign split follows the two faces of the sherd, the stop rule is being driven
by which face the MST happened to orient, not by whether the point is on a break.

### Lead verification (2026-11-02)

Checked by the coordinating session before closing. Each line is a rerun or a re-read, not a
restatement of the Results.

- `awk -F'\t' '$1=="FLAG"' out/dump/armed_att1.tsv | wc -l` -> **19312**; each of
  `gate_att1..6.tsv` is **212432** rows. [gate 1 count]
- `md5sum outG1/att{1..6}/geom/Juglet_Piece_1.S0 outU/geom/Juglet_Piece_1.S0` ->
  **453661ae36dfce04287d29da9255e01f** seven times; passA's `outA/geom/Juglet_Piece_1.S0` ->
  **ff97481e9229201407d182bacd91fd8c**. [gate 2, and instrument inertness: closed == unpatched]
- Binaries and inputs: `bin-MeshPreprocessingHeadless` **736ff95c976486d17f7c00b3af402040**
  (1612840 B) and `bin-EdgeLineExtractionHeadless` **cbf747dc3172fe0bbd188822df14092a**, equal
  line for line to passA's `binaries.md5`; staged inputs equal too — axis **e0ba64c4**,
  mesh **b447066c**, cloud **a2686a8f**.
- `diff` of the two runs' J1 `mesh.log`: only the instrument's dump lines differ; the numeric
  lines agree (`[NORMAL-24] ... n=19312 k=19`, `[WORNESS-54] ... theta=6.42511`). So the
  cross-session divergence is downstream of the mesh stage, as recorded.
- `out/analysis2/B_normals.tsv`: J1 rung-1 flip **0.4163**, J1 corpus **0.0040**; the other
  eight rung-1 **0.0018-0.0170**. Read from the file.
- `F_J1_split.tsv`: S0 **0.8975** flipped (wall_rate 0.0198), S1 **0.0240** (0.1412).
- `D_crosstab.tsv`: J1 wall-labelled 14340 (0.7425) with wall_rate **0.0036**; the other eight's
  wall-labelled rows carry wall_rate **0.96-0.99**.
- `B_sign_J1.png` legends read back: 11273/8039 (58.4/41.6), 41867/167 (99.6/0.4), 1855/28
  (98.5/1.5).
- G_where arithmetic: z-bands 6-8 hold 1305 of 1674 wall-like points (**78.0 %**) on 7021 of
  19312 (**36.4 %**); the outer sheet holds 1410 of 1674 (**84.2 %**) on 58.7 % of the points.

Corrections made at verification:

1. The gate text above names run `20261102-1144_638504b_t59-breakstop-stage0` as the passA
   source; that run holds no S0 file. The reference actually used is run
   `20261102-1155_638504b_t59-control-gateclosed`. The worker flagged this; confirmed here.
2. "H1 not supported as a spatial localisation ... not on a ring" is **not** what the data
   shows. The annular-crease criterion found no ring on any piece, so no point can be placed
   "on" or "off" a ring. What is measured is that the wall-like points concentrate in the top
   three z-bands and on the outer sheet. Whether that band *is* the top break edge is precisely
   what the failed criterion was meant to answer: **H1's corrected prediction stays untested**,
   and nothing here is evidence against the conservator's reading of the piece.
3. The 8 m 24 s total is six jobs, not the two the budget allowed. Jobs 3-6 (37 s, 12 s, 12 s,
   15 s) ran on the lead's explicit go-ahead after the worker stopped at the budget.

**Verdict:** H2 ruled in — the stop's failure on J1 is orientation, not reach; H3 refuted;
H1 untested in its corrected form. Nothing merged; the instrumented file and its patch stay in
the run directory as provenance.

