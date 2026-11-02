# 63 — Why the orientation pass flips one whole sheet past a patch-size threshold

**What to build:** the measured mechanism for the sheet flip ticket 62 located (sound at
k <= 12 / radius <= 1.0 mm, ~42 % flipped at k = 19 / radius 1.4 mm, on J1 only), and the
answer to whether the safe patch size must adapt to any physical attribute of the sherd or
pot. Analysis only: no tracked source changes, no default changes, nothing adopted. The
adopt-or-park decision on radius 1.0 mm is the conservator's and is NOT part of this ticket.

**Answers:** U19, E1

**Blocked by:** 62 (its Stage-1 replica and run directories are this ticket's instrument and
baseline)

**Status:** resolved
**Working in:** chat on Thinkbook16 (2026-11-03)
**Branch:** 63-orientation-flip-mechanism, in /c/PR/worktrees/sfs/63
**Worker:** cursor_code session t63 (grok-4.7), phases 1-5, 2026-11-03

## Spec

### Given (measured facts this stands on)

1. Ticket 62 Stage 1 located the fault: a sharp threshold **inside the orientation pass**,
   not in the plane fit and not wall bridging. On J1 (replica, agrees with the pipeline at
   k=19: 41.88 % vs 41.63 %, S0 93.33 % vs 93.23 %): flipped 0.24/0.24/0.22/0.19 % at
   k=6/8/10/12, **41.88 % at k=19**; radius 0.8 mm 0.25 %, 1.0 mm 0.21 %, **1.4 mm 42.06 %**
   (bare) / 41.56 % (with the shipped 5..20 clamp). J2 and J7 are flat 0.26-0.85 % at every
   setting. Cause NOT measured — that is this ticket.
2. The default path: `CGAL pca_estimate_normals` with `nb_neighbors = max(5, min(20, n/1000))`
   (`mesh_processing_headless.cpp:680`), then `CGAL::mst_orient_normals` at `n24orientK`
   (`:806-809`). J1's growth call has n=19312, so k=19 — just past the cliff.
3. Wall bridging is refuted: 0 % of points on J1/J2/J7 have a k-th neighbour beyond the wall
   at any k (J1 k=19 max 1.63 mm against a 1.876 mm wall); J1's crossing fraction 0.26-0.55 %
   is LOWER than J2 (0.93-1.42 %) and J7 (0.42-1.00 %).
4. The flip is one connected sheet decided once: the graph is one component at every scale
   except the bare 0.6 mm ball (1024 components); J1's flipped points form 9-13 groups with
   99.61-99.69 % in the largest; within S0, 2-4 groups with 99.96-99.99 % in the largest.
5. Only J1 flips. Walls: J1 1.876, J2 2.178, J7 2.839 mm — the cliff (between 1.0 and 1.4 mm)
   is not a fixed fraction of any of them, and J2/J7 never flip at any size.
6. Instruments and baselines already on Spartan:
   - t62 Stage 1: `/data/gpfs/projects/punim2657/SfSpp/runs/20261103-0028_ca520fe_t62-normalfix`
     — `work/stage1_bridging.py` (the replica to instrument: PCA patch fit + MST orientation,
     edge weights 1-|ni·nj|, seed at max-z oriented toward +z, as CGAL does), `out/stage1_bridging.tsv` /
     `.json`, figure `out/stage1_bridging.png` (md5 f6ab510257612c96a8dc62d94a21018f).
   - t61: `runs/20261102-1744_f1e876d_t61-soundfield` — `outU/normals/<piece>_call1.ply`, the
     k=19 field the stop consumed.
   - t62 Stage 2: `runs/20261103-0035_ca520fe_t62-normalfix-s2` — outF/outFA normals at radius
     1.0 mm (the sound field).
   - Meshes: the same `Dataset/Mesh/<pot>` paths the t62 scoring job used (exact strings in
     its `submit.sbatch` / logs). J1 mesh md5 b447066c29181fe7ba987439c22c5d9c.

### Build (three stages, in order)

**Stage 1 — instrument the orientation walk (J1, J2/J7 as controls).** Extend the Stage-1
replica into a recording walk: same graph, same weights, same MST, same seed; record for
every MST step the edge taken, its weight, both endpoints' arrows against the mesh (dot
products), and the running flipped share. **Calibrate first:** the instrument must reproduce
J1 ≈ 41.9 % flipped at k=19 (within 2 points) and soundness at k=12 and radius 1.0 mm, and
flat J2/J7, before any conclusion is drawn. Then answer, with numbers:

- **H1 (seed):** the seed's own arrow is wrong, or near-parallel to the surface (|dot| to
  mesh small), at large patches and right at small ones.
- **H2 (bridge):** between sound and flipped settings the MST GAINS edges connecting the two
  sheets (endpoints on opposite sheets by the S0/S1 labels; endpoint arrows near-perpendicular).
  Locate those edges on the sherd: distance to the fold/rim crease set and the dihedral across
  them (t59's stage-0 region labels and fold points are available in its run dir).
- **H3 (smoothing):** at larger patches the crease-region arrows rotate toward agreement
  BEFORE the flip appears — the crease becomes transparent to the walk with no new edges.

Distinguish H2 from H3 by diffing the MST edge sets and weights between a sound setting
(k=13 or radius 1.0 mm) and k=19: new edges ⇒ H2; same edges with rotated endpoint arrows ⇒ H3.

**Stage 2 — cross-pot field probe at shipped defaults.** Does any piece of another pot flip
at the default? Run the mesh stage with everything unset for **Pot A (all 8 pieces**,
full-res meshes, median spacing 0.286 mm**)** and **up to 8 Pot D pieces** (decimated,
0.39-0.59 mm — the other density class; pick pieces with released clouds), then count the
growth-call arrows' backwards share against each mesh (t61/t62's majority-sign method).
Report per piece. Any piece over 5 % is a second natural experiment: record it, and run the
Stage-1 instrument on it if budget allows.

**Stage 3 — verdict.** State which hypothesis held, or that none did and what was excluded;
state the cliff's physical meaning (what quantity, in mm or degrees, separates sound from
flipped); answer the adaptivity question: is there a measured physical predictor of the
cliff, or is the practical guard a per-pot arrow gate (field check before trusting the
chain)? No adoption recommendation.

### Gates

1. **Calibration:** instrument reproduces the replica's J1 flip at k=19 within 2 points and
   soundness at k=12 / radius 1.0; J2/J7 flat. On failure: stop and report — conclusions
   about the pipeline are not permitted from an uncalibrated instrument.
2. **Corpus read-only:** md5 of every mesh/cloud read, before and after; an empty diff file
   in the run dir proves it.
3. **No tracked source changes, no default changes.** Probe scripts live in `work/` in the
   run dirs. Any build is a read-only build of the unmodified tree.
4. Every sbatch polled to completion; final sacct State/ExitCode recorded in the ticket.
5. **Budget: <= 4 jobs, <= 3 h wall total.** If the instrument cannot be calibrated within
   2 jobs, stop and report — do not spend Stage 2's budget.
6. Claims from the instrument are labelled **replica**; only the cross-pot probe and quoted
   pipeline log lines are pipeline claims.

### Runs and traps

Run dirs `/data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t63-<tag>/` per the
repo convention (`run.json`, `submit.sbatch`, `logs/`, `out/`); append-only `index.tsv`
rows with `verdict` and `human_note` left EMPTY (the lead fills them). Spartan python:
`/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3`. Use **Windows ssh** for spartan
from Git Bash (Git Bash's own ssh has no key); poll jobs with `sacct` directly.

### Worker rules

Run the ticket end to end from this file. Append a `## Results` section to THIS file with
jobs/sacct/index rows, calibration numbers, the H1/H2/H3 verdict with measurements, the
cross-pot table, the propagation figure (one picture the conservator can read: J1 with the
wrong sign's entry point and crossing path coloured, sound vs flipped patch size side by
side), a not-measured list, and a per-piece + overall verdict with NO adoption
recommendation. Do not edit `Status:`, do not commit, do not touch other tickets.

### Verdict language

Name the claim type: a mechanism finding is a claim about the instrument unless reproduced
in the pipeline's own output; the cross-pot probe is a direct pipeline measurement. State
the weight: how many pieces, how many runs.

## Results

Worker write-back, 2026-11-03. Claim labels: **replica** = the t62/t63 re-implementation
(PCA plane + MST orientation); **pipeline** = arrows the shipped binary dumped, scored against
the mesh. Status, Given and gates above are untouched.

### Runs (2 of the 4-job budget; about 31.5 min of the 3 h wall budget)

| Run dir (`/data/gpfs/projects/punim2657/SfSpp/runs/`) | Job | sacct State / ExitCode | Elapsed | Node |
|---|---|---|---|---|
| `20261103-0211_249906a_t63-orientwalk` (Stage 1 instrument) | 34236606 | COMPLETED / 0:0 | 00:00:25 | spartan-bm023 (cascade) |
| `20261103-0228_249906a_t63-crosspot` (Stage 2 probe + radius rider) | 34236863 | COMPLETED / 0:0 | 00:31:00 | spartan-bm023 (cascade) |

```
JobID           JobName  Partition      State ExitCode    Elapsed        NodeList
34236606          t63S1    cascade  COMPLETED      0:0   00:00:25   spartan-bm023
34236863          t63S2    cascade  COMPLETED      0:0   00:31:00   spartan-bm023
```

- Both jobs were polled to completion. Both index rows were appended with `verdict` and `human_note`
  empty.
- `inputs.diff` is empty in both runs. Stage 1 hashed 15 inputs; Stage 2 hashed 63 (16 meshes, 16
  clouds, 16 axes, plus the Juglet meshes, t61 dumps/surfaces and t59 labels).
- No tracked source changed. Stage 2 built the unmodified tree at `249906a` (binary md5
  `52d8ae89f3ed00c066b80cdfdaf55ad1`). Every `SFS_*` dial was unset; only `POT_NAME`, `SFS_AXIS_FILE`
  and `SFS_STATUS_FILE` were set, as t55 sets them, plus the instrument-only `SFS_NORMAL_DUMP_DIR`.
- Pieces were staged by symlink with `scripts/stage_piece.sh`. All 16 passed the corpus-manifest
  check; Pot D clouds are the released ones, about 1,000,000 points each. Stages and the build
  tree were deleted in-job.

### Calibration gate: PASSED (replica)

The Stage-1 instrument reproduces the t62 replica (`20261103-0028_ca520fe_t62-normalfix`,
`out/stage1_bridging.tsv`) to all six decimals.

| Check | Setting | t63 flipped share | t62 replica | Criterion | Result |
|---|---|---|---|---|---|
| J1 reproduces the flip | k=19 | 0.418755 | 0.418755 | within 0.02 | PASS |
| J1 sound | k=12 | 0.001916 | 0.001916 | < 0.01 | PASS |
| J1 sound | k=13 | 0.002330 | (not run) | < 0.01 | PASS |
| J1 sound | radius 1.0 clamped | 0.002071 | 0.002071 | < 0.01 | PASS |
| J2 flat | k=19 | 0.005311 | 0.005311 | < 0.01 | PASS |
| J7 flat | k=19 | 0.003013 | 0.003013 | < 0.01 | PASS |

The Stage-2 rider repeats the replica exactly:
- bare radius 1.0 = 0.002071 and bare radius 1.4 = 0.420619 (both equal to t62);
- clamped radius 1.4 = 0.415648 in both t63 jobs (determinism check).

The Stage-2 scorer, t61's `field_metrics` copied verbatim, reproduces t61 `fields.tsv` cell U
exactly on J1 / J2 / J7: 0.416270 / 0.015932 / 0.002620.

### Mechanism: H2, a single through-wall edge plus a sign-blind cost (replica)

**H1 (seed) is refuted.** On J1 the seed is the same point (11629, surface S1, 0.21 mm from the
fold band) at every setting. Its fitted arrow agrees with the mesh at all of them: dot 0.9988 /
0.9982 / 0.9987 / 0.9946 / 0.9990 at k=12 / k=13 / k=19 / radius 1.0 / radius 1.4 clamped. It is
never flipped and never near-perpendicular. J2's seed sits on a crease (|dot| 0.75-0.96) and J2
never flips.

**H2 holds, though not as the ticket framed it.** At k=19 the wrong sign enters through one
tree edge, **9123-18574**, at **step 7393** of the walk (S1 to S0):
- **Geometry.** Length **1.470 mm**. The endpoints' mesh normals have dot **-0.996**, so they sit
  on opposite faces.
- **Why the edge is cheap.** Both fitted arrows are clean against their own mesh (-0.999 and
  +0.997) and parallel to each other. The edge cost `1-|ni.nj|` ignores sign, so the edge costs
  **0.0017**, against about 0.0005 for a typical tree edge. The walk keeps the arrow and the whole
  opposite face inherits the wrong sign.
- **Location.** It sits on flat wall, **6.7 mm from the t59 fold/fracture band**, with a 9.7 deg
  neighbourhood angle. It is not at the crease.
- **Wall under it.** t59's ray-cast thickness within 1 mm of the edge is **1.456-1.482 mm**
  (median 1.482). That is J1's 1st-percentile wall (1.463 mm over wall faces), against a median
  of 1.967 mm.
- **Why only k=19.** The k=19 reach (distance to the 19th neighbour) has a 95th percentile of
  1.370 mm and a maximum of **1.627 mm**, so it can span 1.47 mm. The k=12 median reach is
  0.987 mm. The edge is absent even from the k=13 *graph*.
- **One wrong decision.** 8,079 points hang below this edge, which is **41.8 %** of 19,312.
  8,058 of them end up backwards (99.7 %) and only 29 backwards points lie outside it. So 99.6 %
  of the 8,087 flipped points come from this single step.
- **No sudden jump in the running count.** The running flipped share is 0.15 % at step 7393, then
  climbs as the walk visits that region: 2 % at step 8149, 10 % at 10065, 40 % at 18708, ending at
  41.88 %.
- **Tree differences between k=13 and k=19.** 10,182 of 19,311 tree edges differ, which is
  re-selection among near-equal tiny weights. These changes are not concentrated at the crease:
  47.5 % lie within 2 mm of the band, against 42.7 % of all points. Only 2 of the new edges link
  opposite faces: 1.470 and 1.514 mm long, 4.7-6.7 mm from the band. Neither exists in the k=13
  graph.

**H3 (smoothing) is refuted.** Crease arrows (8,241 points within 2 mm of the band) do not rotate:
- median |dot| to the mesh is 0.9944 at k=13 and 0.9934 at k=19;
- the near-perpendicular share (|dot| < 0.5) is 0.79 % and 0.93 %.

They go from 0.55 % to 39.9 % backwards only because they lie in the region hanging off the wall
edge.

**Radius 1.4 mm: same mechanism, other crossings.** Neither radius variant reuses edge
9123-18574.

| Setting | Entry edge | Length | Weight | Mesh-normal dot | Points below / backwards inside (share of all flipped) | Where | Wall under it |
|---|---|---|---|---|---|---|---|
| k=19 | 9123-18574, step 7393 | 1.470 mm | 0.0017 | -0.996 | 8079 / 8058 (99.6 %) | flat wall, 6.7 mm from band | 1.456-1.482 mm |
| bare radius 1.4 | **19145-17587, step 9118** | **1.385 mm** | 0.00118 | -0.997 | 8106 / 8095 (99.7 %) | flat wall, 4.4 mm from band, 9.4 deg | **1.390-1.405 mm** (min / median within 1 mm) |
| clamped radius 1.4 (5-20 neighbours) | 9193 (child 15067, parent 19190) | 1.290 mm | 0.0085 | -0.63 | 8026 / 8004 (99.7 %) | beside the rim: 0.28 / 1.24 mm from band, 54 deg | median 1.60 / 1.58 mm, minimum about 1.14 mm |

- **Bare radius 1.4.** The ball is 1.4 mm and the wall is 1.39-1.41 mm, so the edge spans the
  local wall almost exactly. Its midpoint is 14.8 mm from edge 9123-18574.
- **Clamped radius 1.4.** The clamp does not stretch the ball here; 1.29 mm is inside 1.4 mm.
  This edge crosses near the rim instead, where the wall tapers.
- **Bare 1.4 also has two short opposite-face edges at the fold** (0.519 and 0.766 mm) that carry
  1-2 points. They are legitimate turns around the rim, not crossings.

**Cross-check on the pipeline's own points (replica on pipeline input, not the pipeline's walk).**
Stage 2 ran the replica at the pipeline's own k on the exact points the pipeline dumped.
- Its flipped share matches the pipeline's:
  - J2 0.015932 against 0.015932 (pipeline k=5);
  - J7 0.002620 against 0.002620 (k=7);
  - J1 0.4186 against 0.41627 (k=19). J1's replica figure differs from Stage 1's 0.418755 only
    because the mesh-normal reference differs: exact nearest triangle and majority sign, against
    12 nearest centroids.
- The replica tree on J1 contains the same 2 through-wall edges (lengths [1.47, 1.514], largest
  region below one = 8079). All 18 other pieces have **zero**.
- This is strong agreement on the flip share and on where the flip lies. CGAL's own tree was not
  dumped, so the *edge identity* is still a replica claim (see "Still unproven").

### Why J2 and J7 stay safe

1. **Replica at a uniform k: no edge to cross on.** J2 has zero through-wall tree edges at every
   setting (k=12/13/19, radius 1.0/1.4 clamped). J7 has none except one 0.768 mm edge at k=12
   that carries 2 points. With nothing linking the faces, nothing can carry a wrong sign across.
   Their thinnest smooth wall is also thicker than their k=19 reach:
   - J2: 1st-percentile wall 1.585 mm against a reach maximum of 1.553 mm, a margin of only
     **+0.03 mm**;
   - J7: 1.980 mm against 1.761 mm, a margin of +0.22 mm.
2. **The pipeline never uses k=19 on them.** The shipped rule is
   `nb_neighbors = max(5, min(20, n/1000))`, and their growth clouds are small (J2 n=1883, J7
   n=7633). So the pipeline used **k=5 on J2 and k=7 on J7** (`[NORMAL-24]` log lines in t61 cell
   U), with reach maxima of **0.946 mm and 1.261 mm**. The count rule already shrinks the ball on
   sparse growth clouds, and the replica's uniform k=19 is the worst case they never meet. J1's
   growth cloud is the only Juglet one large enough (19,312 points) to reach k=19.

| Piece | Thinnest wall: wall-face 1st / 5th percentile, median (t59) | Point-by-point wall 1st / 5th percentile, median (Stage 2) | k=19 reach 95th percentile / max | Pipeline k / reach max | Points with reach >= wall at pipeline k (share) | Point margin (min wall minus reach) | Through-wall tree edges (k=19 replica / pipeline-k replica) | Pipeline flip |
|---|---|---|---|---|---|---|---|---|
| J1 | 1.463 / 1.523, 1.967 | 1.401 / 1.500, 1.993 | 1.370 / 1.627 | 19 / 1.627 | 111 (0.57 %) | -1.350 | 2 (8079) / 2 (8079) | **0.416270** |
| J2 | 1.585 / 1.827, 2.341 | 0.083 / 1.902, 2.364 | 1.356 / 1.553 | 5 / 0.946 | 27 (1.43 %) | -0.700 | 0 / 0 | 0.015932 |
| J7 | 1.980 / 2.193, 3.113 | 0.922 / 2.128, 3.164 | 1.377 / 1.761 | 7 / 1.261 | 50 (0.66 %) | -0.869 | 0 / 0 | 0.002620 |

### Reconciliation with t62 Stage 1

t62 found that no point's k-th neighbour reaches *beyond the wall*, measured against J1's
**median** wall of 1.876 mm. That is true: the longest k=19 reach is 1.627 mm. The flip needs
something else: **one** graph edge that *spans the wall where it is locally thin*. Edge 9123-18574
is 1.470 mm long, across a 1.456-1.482 mm patch at about the 1st percentile of J1's wall. Such
patches are a few percent of the sherd, so a per-point fraction stays near zero, and the
sign-blind cost then makes that single edge as cheap as any edge on one face. Both statements are
true. t62's test ruled out wall-wide bridging; it was blind to one local crossing, and one
crossing is enough because the minimum spanning tree commits the whole far face through it.

### Cross-pot field probe at shipped defaults (pipeline)

These are the growth-call arrows (call 1; call 0 is identical on every piece) against each mesh.
- `raw_neg` = share pointing against the mesh's outward normal.
- `flip_rate` = min(raw_neg, 1-raw_neg), the majority-sign method.
- Predictor columns are from Stage 2's point-by-point ray cast and the replica at the pipeline k.

| Piece | n (growth) | k | raw_neg = flip_rate | Ray hits (share) | Wall 1st / 5th percentile / median (mm) | Reach max at k (mm) | Points reach >= wall (share) | Point margin (mm) | Through-wall tree edges | Largest opposite-normal subtree |
|---|---|---|---|---|---|---|---|---|---|---|
| Pot A 01 | 85136 | 20 | 0.000035 | 0.077 | 3.959 / 4.028 / 4.455 | 1.740 | 23 (0.027 %) | -0.882 | 0 | 2 |
| Pot A 02 | 49528 | 20 | 0.000363 | 0.858 | 3.250 / 3.305 / 3.619 | 1.743 | 46 (0.093 %) | -1.430 | 0 | 27 |
| Pot A 03 | 46784 | 20 | 0.000299 | 0.898 | 3.240 / 3.347 / 3.668 | 1.786 | 26 (0.056 %) | -1.252 | 0 | 8 |
| Pot A 04 | 38901 | 20 | 0.000026 | 0.907 | 3.302 / 3.378 / 3.669 | 1.650 | 2 (0.005 %) | -0.298 | 0 | 0 |
| Pot A 05 | 38074 | 20 | 0.000000 | 0.872 | 3.324 / 3.413 / 3.765 | 1.839 | 7 (0.018 %) | -0.636 | 0 | 0 |
| Pot A 06 | 27944 | 20 | 0.000000 | 0.902 | 3.208 / 3.259 / 3.569 | 1.789 | 10 (0.036 %) | -0.882 | 0 | 0 |
| Pot A 07 | 8598 | 8 | 0.000233 | 0.770 | 2.504 / 3.446 / 3.948 | 1.150 | 6 (0.070 %) | -0.676 | 0 | 1 |
| Pot A 08 | 7682 | 7 | 0.000260 | 0.821 | 3.248 / 3.382 / 3.632 | 1.029 | 0 | +0.131 | 0 | 7681 (rim turn; flip 0.026 %) |
| Pot D 01 | 144448 | 20 | 0.000000 | 0.001 | 1.464 / 1.778 / 3.603 | 1.740 | 0 | +0.002 | 0 | 0 |
| Pot D 02 | 129391 | 20 | 0.000000 | 0.002 | 0.677 / 1.195 / 2.475 | 1.755 | 19 (0.015 %) | -0.921 | 0 | 0 |
| Pot D 03 | 158221 | 20 | 0.000006 | 0.060 | 2.257 / 2.470 / 3.711 | 1.728 | 10 (0.006 %) | -1.390 | 0 | 0 |
| Pot D 04 | 123402 | 20 | 0.000008 | 0.012 | 1.203 / 1.883 / 4.389 | 1.696 | 19 (0.015 %) | -1.319 | 0 | 7 |
| Pot D 05 | 114186 | 20 | 0.000000 | 0.003 | 0.580 / 0.977 / 3.392 | 1.725 | 36 (0.032 %) | -0.957 | 0 | 0 |
| Pot D 06 | 101429 | 20 | 0.000000 | 0.002 | 1.099 / 1.583 / 3.735 | 1.746 | 5 (0.005 %) | -1.309 | 0 | 0 |
| Pot D 07 | 83088 | 20 | 0.000012 | 0.006 | 0.741 / 1.016 / 2.794 | 1.719 | 52 (0.063 %) | -0.729 | 0 | 2 |
| Pot D 08 | 85721 | 20 | 0.000012 | 0.001 | 0.798 / 1.138 / 3.264 | 1.655 | 6 (0.007 %) | -0.633 | 0 | 12 |

**Which pieces flip.**
- **None of the 16 Pot A / Pot D pieces.** The largest is Pot A 02 at 0.036 %; the other 15 are
  at or below 0.03 %, and six are exactly 0.
- Adding t61 cell U (`fields.tsv`), which scores the nine Juglet pieces at the shipped normal
  default (SFS_WORNESS=0.7), **J1 at 41.63 % is the only piece over 5 % among the 25 pieces with
  a pipeline field.** Next highest: J4 1.70 %, J2 1.59 %, J3 1.34 %, J8 1.30 %.
- J6's raw_neg is 0.998, a whole-piece inversion that the majority sign absorbs. That is a
  different event (a global sign), recorded by t61, not a partial-sheet flip.
- No second natural experiment exists, so the instrument was not run on another flipper.

**Does the point-by-point predictor separate flippers? No.** I could not settle this one in the
ticket's favour.
- Points with reach >= the wall under them exist on 17 of the 19 pieces scored (J1, J2, J7 and
  the 16). The point margin is negative on all but Pot A 08 and Pot D 01, and J2's danger share
  (1.43 %) is *higher* than J1's (0.57 %).
- Those points sit where the ray cast legitimately finds thin material: tapering rims, fracture
  lips, mesh artefacts. A label-free, point-by-point "reach >= local thickness" flags every pot.
- What does separate J1 from all 18 others is the **through-wall tree edge**: an edge between
  opposite surfaces, opposite normals, low weight. J1 has 2; every other piece has 0.
- An opposite-normal edge alone is not enough. Pot A 08 has one carrying 7,681 points with a flip
  of 0.026 %, because there the walk turns round a rim and the arrows rotate with the surface.
  The danger is specifically a *cheap* opposite-face edge.

**Pot D caveat.**
- **Thickness is weak evidence.** The ray cast found an opposing face for only 0.1-6.0 % of Pot D
  points (Pot A 01: 7.7 %; the other Pot A pieces 77-91 %; Juglet 78-86 %). The cause is not
  measured: a mesh winding the opposing-face test rejects, open or one-sided decimated meshes, or
  walls over 5 mm. Pot D's wall columns describe a small, unrepresentative subset and should not
  be used.
- **The flip measurements are direct.** Every point was scored against its nearest triangle,
  median distance a few microns, majority sign, so Pot D's flip_rate is as good as Pot A's.

### Stage 3 verdict

**Hypothesis.** H2 holds in its "bridge" form (replica, J1, one run per setting, deterministic). H1
and H3 are refuted. The flip is caused by a single minimum-spanning-tree edge that joins the two
faces of the wall at a locally thin spot. The arrows at the two ends are well fitted and parallel,
because the faces are parallel. The orientation cost `1-|ni.nj|` cannot tell "same face, same
direction" from "opposite faces, opposite directions", so the edge is cheap and the walk carries
one sign across it. Everything on the far face then inherits the wrong sign, which is one decision
for 99.6 % of the flip. Three settings (k=19, bare radius 1.4, clamped radius 1.4) produce three
different entry edges with the same signature.

**The cliff's physical meaning.** The quantity separating sound from flipped is **the neighbour
reach measured against the thinnest *smooth* wall of the piece**: whether some point's patch
reaches the far face across the wall.
- **J1, k=19:** the reach maximum is 1.627 mm and the crossing edge is 1.470 mm long, across a
  1.46-1.48 mm wall.
- **J1, bare radius 1.4:** the ball is 1.4 mm; the crossing edge is 1.385 mm, across a 1.39-1.41 mm
  wall.
- **J1, sound settings:** k=12 (reach maximum 1.326 mm, from t62) and radius 1.0 mm have no
  crossing edge, and nor does k=13. The flip stays at 0.19-0.23 %.

The cliff therefore sits between about 1.0 and about 1.4 mm on J1 because J1's thinnest smooth
wall is about 1.39-1.46 mm. It is not a fixed fraction of the *median* wall, which is why
Given 5 found no ratio.

**Adaptivity: is there a measured physical predictor, or is the guard a per-pot arrow gate?**
- **The physical rule explains the cliff but did not work as a standalone detector here.**
  - With t59's *wall-face* labels (smooth, paired faces only), "max reach >= 1st-percentile
    wall" separates J1 (1.627 against 1.463) from J2 and J7. But J2's margin in the worst case
    (uniform k=19) is only **+0.03 mm** (1.553 against 1.585).
  - Those labels exist only for the Juglet. Without them, the label-free point-by-point version
    flags 17 of 19 pieces because of rims, so it does not separate.
  - On Pot D the thickness coverage is too thin to judge.
- **The test that did separate 1 flipper from 18 sound pieces** is the count of through-wall tree
  edges from the replica at the pipeline's own k. That is effectively running the orientation
  walk.
- **The direct per-pot arrow check is the only measurement here that needs no proxy.** It is the
  pipeline's growth-call arrows against the mesh, majority sign, about 20 s per piece. In this
  corpus it separates J1 (41.63 %) from all 24 other pieces (at most 1.70 %).
- **Size dependence.** The shipped count rule makes the reach depend on growth-cloud size
  (k = n/1000, clamped 5-20). Fourteen of the 16 Pot A / Pot D growth clouds reach k=20, with
  reach maxima of 1.650-1.839 mm; Pot A 07 and 08 run at k=8 and k=7 (1.150 / 1.029 mm).
  Pot A's 1st-percentile point-by-point walls are 2.504-3.959 mm, so its margin is at least
  1.35 mm. A pot with walls near 1.5 mm and growth clouds over about 19,000 points would be
  exposed the way J1 is.
- **No adoption recommendation.** Per the ticket, this section recommends nothing: whether radius
  1.0 mm is adopted, and whether an arrow gate is installed, are the conservator's decisions.

**Weight.**
- Mechanism: one flipping piece (J1), two Juglet controls, 8 settings, deterministic replica, two
  jobs.
- Cross-pot probe: 16 pieces, one pipeline run each, plus t61's nine Juglet fields.

### Still unproven, and not done

1. **The edge identity in CGAL's own walk.** The pipeline's flip share (41.63 %) and the replica's
   on the pipeline's own points (41.86 %) agree within 0.23 points, and J2 and J7 agree exactly.
   CGAL's minimum spanning tree was not dumped, so "edge 9123-18574 is the pipeline's entry" is a
   replica claim. A dump of `mst_orient_normals`' tree would settle it.
2. **One flipper.** The predictor and the mechanism rest on a single natural experiment. No Pot A
   or Pot D piece flips, so the cross-pot probe confirms soundness but cannot test the predictor's
   positive side.
3. **Whole-piece versus point-by-point.**
   - The wall-face 1st-percentile predictor uses t59 Juglet labels that do not exist for other pots.
   - The point-by-point version is confounded by rims.
   - A label-free *smooth-wall* thickness (excluding rim and fracture faces) was not built.
4. **Pot D thickness coverage (0.1-6.0 %) is unexplained.** Pot D's provenance itself is clean:
   the released clouds and `_DS` meshes passed the manifest check. The open question is why the
   opposing-face ray cast fails on those meshes.
5. **The decimated meshes were sampled on Pot D 01-08 only,** chosen as the first eight by number;
   this also avoids the defective D18/D29 axis files.
6. **Not produced:** the propagation figure the worker rules ask for (J1 with the wrong sign's
   entry point and crossing path, sound against flipped side by side). The entry edges, regions
   and coordinates needed for it are in
   `20261103-0211_249906a_t63-orientwalk/out/` and `20261103-0228_249906a_t63-crosspot/out/bare/`.
   Nothing has been rendered, so per the workspace rule no picture-based claim is made here.


## Lead verification (2026-11-03)

Every load-bearing number re-read from the runs' own artefacts before recording:

- verified: sacct 34236606 COMPLETED 0:0 00:00:25; 34236863 COMPLETED 0:0 00:31:00 -> both recorded above match.
- verified: out/inputs.diff 0 bytes in BOTH run dirs; index.tsv rows for both runs appended with empty verdict/human_note.
- verified: out/bare/walk_summary.json -> r1.0 flip 0.002071 (top entry subtree 20, no cross-sheet); r1.4 flip 0.420619 (entry step 9118, subtree 8106, weight 0.001176, cross_sheet=1, dih13 9.36 deg = flat wall, dband 4.386 mm); rc1.4 flip 0.415648 == the phase-3 clamped value (deterministic re-run).
- verified: index mapping of edge 9123-18574 into the t61 growth-call dump Juglet_Piece_1_call0.ply (19312 pts): |P[18574]-P[9123]| = 1.4695 mm vs walk table 1.470; ply endpoint normals dot +0.9983 (parallel arrows through the wall); walk k19 back share 0.4188. The replica ran on the pipeline's own points.
- verified: out/xpot_predictor.tsv -> mst_through = [] on ALL 16 cross-pot pieces; max pipeline_flip 0.000363 (Pot A 02); out/jug_predictor.tsv -> J1 mst_through [1.47, 1.514] maxsub 8079, J2/J7 zero.
- Worktree diff before commit: ticket file only, 291 insertions, 0 deletions; no tracked source changed anywhere.
- Lead figure rendered from the run's own data (point indices verified above): artifacts/63/t63_j1_through_wall_edge.png (left: the 41.8% backwards side in red, entry edge circled; right: the two faces and the 1.47 mm link through the 1.46-1.48 mm wall). This supplies the propagation view the worker rules ask for and the Results section deferred.

Verdict: the analysis the ticket set out to do is done. H1 refuted, H2 established at replica level and confirmed on the pipeline's own points (flip shares agree within 0.23 points on J1, exactly on J2/J7); the shipped count rule's ball spans the thinnest wall of a piece exactly when k = n/1000 rises with growth-cloud size; the physical thickness rule explains the cliff but fails as a standalone detector (rims are legitimately thin); the direct arrow check separates the one flipper from all 24 sound pieces measured. Nothing merged into defaults; adopt/park on radius-1.0 mm and whether to install an arrow gate stay with the conservator.
