# 56 — The corner-detection window, the over-counting breakline headers, and why J1's lane left the surface

**What to build:** a written answer, in this ticket, to the conservator's three questions
(2026-11-01), each claim carrying the file and line it rests on. **No source change, no job
needed** — this is a read-the-code ticket. Its value is that the answers decide whether three
pieces of the edge-line stage need fixing before the Juglet goes to assembly (step 5):

- **A. The corner-detection window.** `getPointsInSequence_Vote247` scores every resampled
  point against a chord `W` points either side (`const int W = 8;`) and calls a peak a
  corner when its score clears `thr = std::max(2.0f, 3.0f * med)`. On the Juglet that
  window spans a large fraction of the loop. Question: **does it reach seating at all, and
  if so through which path?** Answer it by following the corner output to whatever consumes
  it, or by showing nothing does.
- **B. The header point count.** Every Juglet `Breakline_0.pcd` from the t55 run declares
  more points in its metadata header than the file holds, by exactly its segment count
  (J1 `# 2 30 0` over 28 dots, ... J9 `# 2 25 0` over 23). Pot A's eight files are
  self-consistent. Question: **why, how should it be fixed, and does it bite if a run ever
  marks segments as rim?**
- **C. Why J1's `Breakline_0` left the surface.** Ten of J1's 28 emitted dots run 3.9-5.2 mm
  off the mesh, in one straight 16.2 mm run that crosses a bay in the sherd. The lead measured
  the mechanism on 2026-11-01 and the conservator asked for it checked and carried here (the
  numbers are in *Given*, below). Question: **does the code bear the mechanism out, and what
  would a fix have to change?** No change is applied.

**Answers:** U19 (does the pipeline put the Juglet back together), E1 (do our breaklines let
SfS find joins)

**Blocked by:** None (can start immediately; ticket 55's run of record supplies the files)

**Status:** in-progress
**Working in:** chat on Thinkbook16 (2026-11-01)
**Branch:** 56-corner-window-seating-and-breakline-header-count, in /c/PR/worktrees/sfs/56

**Worker:** unassigned

## Spec

Three questions, one answer document. Read code; do not run the pipeline.

### A. Does the corner window change what the assembler seats?

1. Establish what the corner block actually does with its result: does a corner split the
   emitted lane, reorder it, or only get logged? Quote the comment that says which, and
   quote the code that acts on it. Follow the lane from the corner block to the
   `Breakline_0.pcd` that the assembler loads.
2. Establish whether the block fires at all on this data. The t55 per-piece logs
   (`out/pieces/Juglet_Piece_N/edge.log`, lines matching `[VOTE-247] resampled=`) carry
   the counts and thresholds for all 18 lanes; read them, do not re-run.
3. If the corner result is consumed somewhere, trace it into
   `C:\PR\structure-from-sherds-pp` and name every function that reads it, with the
   condition that gates each one.
4. Then answer the seating question in the only terms that survive step 1-3: name the
   mechanism (if any) by which lane geometry reaches a pose, and say what would have to
   change for the window to start mattering.
5. **Separately check the thing that does gate seating on lane length**: the assembler
   drops any piece whose breakline is short (`main.cpp` near line 86). Work out which
   Juglet pieces survive that gate at the t55 counts (J1 28, J2 32, J3 38, J4 32, J5 47,
   J6 46, J7 54, J8 41, J9 23) and state the consequence plainly. This is the part of the
   answer the conservator will act on, so it must be exact.

### B. Why the header over-counts, how to fix it, what it breaks

1. Find the writer that emits `# <nseg> <totalPts> <info_index>` plus the per-segment range
   lines, and the loop that builds the cloud it describes. Explain the discrepancy
   mechanically: what does the header count, what does the cloud hold, and why is the
   difference exactly the segment count? Name the commit that introduced the divergence if
   `git log -S` finds it cheaply.
2. Find the correct pattern already in this repo (the same writer in the GUI/legacy source
   and in `original_nurbs_preprocessing/` takes the caller's segment table instead of
   re-reading disk) and say precisely what the fix is, in terms of which existing table is
   already correct and just needs to be passed through.
3. Read the assembler's reader and say what it does with the declared total. If it is
   discarded, say so with the line — that is what makes the defect cosmetic today.
4. Answer the rim question honestly and completely: if a run wrote `info_index` 1 or 3
   (rim-flagged), which downstream loops would index with those ranges, would any read past
   the end of the point matrix, and what actually happens then — an assertion, or silent
   out-of-bounds? **Check the build flags**: this repo builds Release, and whether
   `NDEBUG` is defined decides between a clean abort and undefined behaviour. Say which.
5. State the order of operations: which change must land before which, so that the flag
   never goes live over wrong ranges.

### C. Why J1's `Breakline_0` left the surface — check the mechanism

The lead's measurements (2026-11-01, on the t55 run of record; every number below is a
measurement, not an inference) support this mechanism. **Verify it in the code and refute it
freely if the code says otherwise.** This part is a reading job: no new run, no new
measurement needed — cite the lines.

1. **The lane is built from an open arc, then closed.** J1's `Surface_0` boundary is two
   separate arcs (127 and 63 dots at 5 mm linkage, closest approach 18.76 mm), not one rim.
   The walk seeds inside the largest component, walks 69-71 of 208 dots and stops. Confirm
   the seed rule (largest-component centroid-nearest) and the stop rule
   (`dFresh267 > stopR267`) at the lines named in *Landmarks*, and confirm that when the walk
   ends early nothing restarts it — the remaining dots are dropped, not walked.
2. **The closure is implicit.** Confirm that the resample treats the walked chain as a
   *closed* loop: `cum[M0] = cum[0] + (loop[0] - loop[M0-1]).norm()`, i.e. the wrap edge is
   added with no length test and no check that it stays near the surface. Quote the line.
   That wrap is the 23.94 mm chord the ten off-surface dots sit on (perpendicular distance to
   the chord 0.14-0.69 mm; the chord itself is 3.9-5.4 mm off the mesh at its middle).
3. **Why the second arc could not be reached.** After 69 dots the walker's 50-dot probe
   (`nearestKSearch(..., 50, ...)`) is entirely its own trail (f50 = 0) and the nearest fresh
   dot anywhere is 22.89 mm away, past R = 12 mm. The leftover arm of the *same* component
   attaches to the walked arc only 0.31 mm from it, at walked dot 3 of 69 — so a restart
   rule ("if dots remain and some are within R of any walked dot, resume there") would have
   picked it up; only 11 of the 121 unvisited dots are within 12 mm of the walked arc, and
   those 11 are exactly that arm. Say what a restart rule would and would not have fixed.
4. **Why the boundary detector never saw the real crease.** The mesh's own sharp rim is 753
   edges with dihedral > 60 deg, 770 vertices. Of the 358 that belong to `Surface_0` (nearest
   to S0), 356 have an S0 dot within 1 mm — so the data is there — but only 80 are within 1 mm
   of a detected boundary dot, and the median detected dot sits 7.17 mm from the crease. The
   S0 dots beside the crease have a median max-angular-gap of 9-10 deg against a 108 deg
   threshold, at search radii 2, 3, 4 and 6 mm alike, and the boundary set is line-like
   (planarity 0.98 over a 3 mm neighbourhood). **The cause is the face patch wrapping past the
   fold:** S0 carries dots on both sides of the crease (1,712 dots within 1 mm of it), so from
   an S0 dot the crease is not a void. Check this in the code: `setRadiusSearch(4)` and
   `setAngleThreshold(M_PI * 0.6)` — is the rule purely a tangent-plane angular-void test
   with no normal-discontinuity term, so that a patch that folds over its own edge cannot be
   detected? Name the line and say plainly whether a cure belongs to the surface stage (keep
   S0 off the other face) or to the boundary stage.
5. **What this costs today.** Every emitted dot is a resampled point of the chain, so the
   closure chord is invisible in the logs (J1's log shows a clean `L=59.8158mm`, no
   over-length warning). State whether any existing check would catch a lane that leaves its
   surface, and if not, say so — that is the finding the conservator will act on.

### Given, not to be re-derived

The measurements below were taken by the lead on the t55 run of record
(`20261101-2004_05be12c_t55-worness07-breaklines`, job 34165367) and on Pot A's shipped
files. Use them; verify any you rely on, and **refute the inference freely if the code says
otherwise**.

- Header vs POINTS vs data rows, all nine Juglet Bl0: J1 2 segs 30/28/28; J2 2/34/32/32;
  J3 2/40/38/38; J4 2/34/32/32; J5 2/49/47/47; J6 3/49/46/46; J7 3/57/54/54;
  J8 2/43/41/41; J9 2/25/23/23. Every third field (info_index) is `0`.
- Pot A, all eight consistent: PA01 6/207/207/207, PA02 4/295/295/295, PA03 5/160/160/160,
  PA04 5/231/231/231, PA05 5/153/153/153, PA06 3/160/160/160, PA07 4/76/76/76,
  PA08 4/62/62/62. All info_index `0`.
- `[VOTE-247]` corner counts are **0 on all 18 lanes**, with thresholds 15.70-26.01 and
  medians 5.23-8.67 (a threshold that is 3x the median cannot be cleared by a peak whose
  score is a deviation from a chord).
- A lead-side replication of the corner block on the emitted lanes: at `W=8` no corners
  anywhere; `W=4` finds one only on J1; `W=2` finds 1-3 on seven of nine pieces; `W=1`
  finds none, because the 2.0 mm absolute floor in the threshold then dominates. So the
  window and the floor bind together — shrinking the window alone does not revive the rule.
- Every lane's `PercentDev` is 75.7-139.5 against a rim bar of `< 50`, so **no segment on
  any of the 18 lanes is flagged rim**, whatever the window does.

Part C, the J1 lane (measured by the lead on 2026-11-01, t55 run of record, J1 only):

- The emitted lane's 28 dots: dots 2-11 lie 3.9-5.2 mm off the mesh; the other 18 are
  0.00-0.52 mm off. They form nine steps of exactly 1.800 mm with 0.00-0.08 mm perpendicular
  wander — a resampled straight line.
- The closure chord (walk end -> walk start) is 23.94 mm. The closed loop measures 53.798 mm
  against the log's `L=59.8158mm`; the 6.02 mm difference is the chord the wrap cut across.
- `Surface_0` and `Surface_1` lie on the mesh (median 0.0001 mm, max 0.0004 mm), so the
  surface is not displaced. The lane leaves it; the faces do not.
- The input cloud is present along the chord (6,446 points in the window; every chord station
  is inside the cloud's own alpha-shape at 1.0-3.0 mm), so this is not missing data.
- Boundary components: S0 127 + 63 dots (5 mm linkage), closest approach 18.76 mm; S1 splits
  into four (222, 33, 8, 59). Only J1 among the nine has `comps=2` on `Breakline_0` plus a
  `CHAIN-END` line; the other eight walk one component to completion (kept == chain,
  142-294 dots, maxjump 1.61-4.16 mm). J1's `Breakline_1` also chain-ends (at 14.3006 mm)
  yet closes harmlessly — a chain-end is not automatically fatal; it is fatal when the chord
  it closes over crosses material.
- `Surface_0` carries 13,850 points but only 8,283 distinct positions (5,567 doubled); the
  duplication does not change the boundary count materially (206 raw vs 174 deduped, against
  the run's 208), so it is a footnote, not the cause.

### Landmarks (orientation only — verify each before citing it)

`C:\PR\SfSpp_preprocessing\edgeline_extraction_headless.cpp`: the Vote247 walk and its
comment near :540-560; `RESAMPLE_D_MM` :556; `W` :816; threshold :828; peak test :830-845;
the lane selector :1330-1345; the segment splitter `detectSeparateLineSegments` :1914; the
breakline PCD writer :1643-1712; the cloud-building loop :3440-3484; the rim test :3476-3509.
Part C adds: the component split and `COMP_GAP_MM` :580-601; `fullWalk263` :605; the
largest-component seed :627-647; the K=50 heading-guarded pick :662-696; the stop test
:711-737; the wrap that closes the loop `cum[i+1] = cum[i] + (loop[(i+1) % M0] - loop[i]).norm()`
:796-811; the boundary estimator `setRadiusSearch(4)` :1105 and
`setAngleThreshold(M_PI * 0.6)` :1108.
`C:\PR\structure-from-sherds-pp\class\data_structure.cpp`: `ReadPCDFileWithInfo`
:185-304, `BuildTree` :112-135, `ChangeOrder` :423-449.
`C:\PR\structure-from-sherds-pp\main.cpp`: the short-breakline gate near :86.
`C:\PR\structure-from-sherds-pp\class\reconstruction.cpp`: `MakeRimData` :839-874,
`RimConstraint` :876-921.

## Acceptance

- [ ] Part A answered: what the corner block does with its output (with the code that proves
      it), whether it fires on this data, and — if it reaches the assembler at all — every
      consumer named with its gate. If it does not reach seating, that is stated as the
      answer, with the reason.
- [ ] The short-breakline gate answered exactly: which of the nine Juglet pieces survive it
      at the t55 counts, and what that means for a Juglet assembly run.
- [ ] Part B answered: the mechanical cause of the over-count, the exact fix and which
      already-correct table it uses, and what the assembler does with the declared total.
- [ ] The rim question answered with the build flags checked: assertion or undefined
      behaviour, and the order in which the header fix and any rim-flag change must land.
- [ ] Part C checked against the code: the seed and stop rules, the implicit wrap at the
      resample, the absence of any restart, and whether the boundary rule can see a crease at
      all. Each of the lead's five points marked **borne out** or **refuted**, with the line.
- [ ] Part C closes with what a fix would have to change and which stage owns it (surface or
      boundary), and whether any existing check would have caught a lane leaving its surface.
- [ ] Every claim carries `file:line`; the ticket is written so the conservator can read
      the plain-language answer first and the citations after.
- [ ] No source change, no Slurm job, no corpus write. Nothing merged.

## Out of scope

- Applying any fix. This ticket establishes what is true and what the fix is; the change
  itself is a separate code ticket, written after the conservator has read the answer.
- Any assembly run or seating claim (step 5).
- Re-running the edge stage: the t55 files and logs are the evidence.

## Results (worker write-back)

_To be filled by the worker._
