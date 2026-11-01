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

**Status:** resolved 2026-11-02 — all three parts answered; part C's mechanism confirmed, and the
worker's one 'not shown' verdict refuted by a direct test (lead verification at the end)
**Working in:** chat on Thinkbook16 (2026-11-01)
**Branch:** 56-corner-window-seating-and-breakline-header-count, in /c/PR/worktrees/sfs/56

**Worker:** subagent 9adb2fce-a866-4810-8dc1-7868409a3280

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

- [x] Part A answered: the corner block logs its count and emits the whole lane anyway
      (`:540-552`, `:829-845`), fires 0 times on all 18 lanes, and has no consumer anywhere —
      the function is `static void` and its index list dies with it.
- [x] The short-breakline gate answered exactly: **only J7 (54 dots) survives `main.cpp:86`**;
      the other eight are dropped before matching, so no pair exists to build a cycle from.
- [x] Part B answered: the writer re-reads `Segments/*.xyz` and sums full rows (`:1666-1671`)
      while the cloud loop stops at `rows()-1` (`:3453`); the fix is to pass the caller's
      already-correct `index` table (`:3481`) and take the total from `cloud.points.size()`
      as the twin at `original_nurbs_preprocessing/edgeline_extraction_headless.cpp:1357` does;
      the assembler prints the declared total and discards it (`data_structure.cpp:216-220`).
- [x] The rim question answered with the build flags checked: `NDEBUG` **is** defined
      (`-O3 -DNDEBUG ...` in the Spartan `flags.make`), so a range past `point_.cols()` is
      **undefined behaviour**, not an abort; ranges/header must land before any flag is written.
- [x] Part C checked against the code: points 1, 2, 3, 4 and 5 all **borne out** (the lead
      refuted the worker's 'chord not visible' verdict by locating the chord at dot 2, after
      the vote's reversal — see Lead verification), and the wrap-past-fold mechanism is
      confirmed by an intervention test (S0 fire rate 14% → 34% with the wrap removed).
- [x] Part C closes with what a fix would have to change and which stage owns it — surface
      stage first (keep `Surface_0` off the opposite face), then the edge stage must stop
      closing an abandoned chain — and states that **no existing check** would have caught a
      lane leaving its surface.
- [x] Every claim carries `file:line`; the plain-language answers come first.
- [x] No source change, no Slurm job, no corpus write. Nothing merged.

## Out of scope

- Applying any fix. This ticket establishes what is true and what the fix is; the change
  itself is a separate code ticket, written after the conservator has read the answer.
- Any assembly run or seating claim (step 5).
- Re-running the edge stage: the t55 files and logs are the evidence.

## Results (worker write-back)

### The short answers, in plain language

**A — the corner window never reaches seating, and it does not fire on this data.** The
corner count is printed and then thrown away: the same function that computes it emits the
lane as one unbroken loop, and the comment at the top of it says so ("corners LOGGED ONLY —
the emitted lane stays one ordered loop because the downstream B-spline expects one lane per
face"). There is no variable to read afterwards and no caller that asks. On the Juglet the
count is 0 on all 18 lanes, so even if something did read it there would be nothing to read.
What actually gates seating on lane length is the assembler's 50-point floor, and at the t55
counts **only one of the nine pieces (J7, 54 dots) survives it**; the other eight (28, 32, 38,
32, 47, 46, 41, 23) are dropped before matching, so one matchable shard remains where a cycle
needs a pair.

**B — the header over-counts because the writer and the cloud-counting loop disagree by one
row per segment file.** The writer never receives the segment table the caller already built;
it re-opens `Segments/*.xyz` from disk and adds up the **full** row count of each file, while
the cloud it describes was filled by a loop that stops one row short (`rows() - 1`). One row
per segment file is therefore counted and never stored — exactly the segment count. The same
re-read builds the range lines, so the last range end over-counts too (J1: `# 1 14 0` /
`# 15 30 0` over 28 points). The fix is already in the repo twice: pass the caller's table and
take the total from `cloud.points.size()`. The assembler reads the declared total, prints it,
and discards it, which is why this is cosmetic today.

**Rim question — with the flag set, ranges can run past the end of the point matrix and the
build cannot stop it.** The build is Release with `-DNDEBUG` (checked on the actual Spartan
compilation), so every `assert` is compiled out and a past-the-end read is undefined
behaviour, not a clean abort. Note also that no writer in this repo can currently emit a rim
flag at all — both the file-level field and the per-range field are hard-coded `0` — so the
rim path is unreachable today; it becomes reachable the moment someone writes a `1` over the
ranges as they stand.

**C — four of the lead's five points are borne out in the code; one is borne out as a
mechanism but the emitted file does not show the chord where the lead placed it.** The seed,
the stop and the absence of any restart are exactly as described; the wrap edge is added
unconditionally with no length test; the boundary rule has no crease term and cannot see a
fold. But in the file that was actually written, the wrap step is 1.7996 mm, not 23.94 mm, and
the straight off-surface run is dots 3–11 (14.4000 mm, maximum off-chord 0.0112 mm), reached by
one 5.1984 mm step at dot 2→3. Details and lines below.

### A. Does the corner window change what the assembler seats?

**A.1 What the block does with its result.** It logs it. The header comment states the intent
and the reason — `edgeline_extraction_headless.cpp:540-552`: "NO numeric corner threshold in
the paper, so the peak rule below is a STATED ASSUMPTION (local max over +/-8 window above
max(2.0mm, 3*median)), corners LOGGED ONLY -- the emitted lane stays one ordered loop because
the downstream B-spline expects one lane per face (splitting the output would change Bl file
structure)." The code matches: the score is computed at `:818-824`, the median and threshold at
`:827-828`, the peak test at `:830-833`, the counter at `:834-837`, the print at `:839-840`, and
then `:841-844` pushes **every** resampled point regardless:

```
841: 	for (size_t i = 0; i < MR; i++)
842: 		cloud_sequenced->points.push_back(pcl::PointXYZ(res[i](0), res[i](1), res[i](2)));
```

`corners` and `cidx` are declared at `:829` inside the function and die at `:845`. A grep for
`corners`, `cidx`, `peakIndices` and `detectedPeakIndices` across
`edgeline_extraction_headless.cpp` returns only `:547` (that comment), `:829`, `:835`, `:836`,
`:839`, `:840` — no other reader. There is no return value to consume: the function is
`static void` (`:553`).

**A.2 Does it fire on this data?** No. All 18 lanes print `corners=0`. J1's line is
`out/pieces/Juglet_Piece_1/edge.log:40`: `[VOTE-247] resampled=31 (L=59.8158mm) corners=0
thr=15.7035 med=5.23448 idx=[]`. The thresholds (15.70–26.01) are 3× the medians
(5.23–8.67), and the score is a deviation from a chord, so a peak would have to be three times
the typical deviation to register — the lead's Given numbers are reproduced exactly by the logs.

**A.3 Where the lane actually goes (the path to seating).** The walked lane is written at
`:1361-1364` and then handed back through the parameter `cloud_BorderPointsCombined` to the
caller at `:2319`, which feeds it to the 1.8 mm sphere-marching smoother at `:2330-2332`
(`smoothAndSampleBreaklinesVer4UsingBSpline`, body `:475-522`, `sphereRadius = 1.8` at `:477`,
the marching-sphere advance at `:489-513`, `FindLineSphereIntersections` at `:500`). The
smoothed points are then fitted with a B-spline at `:2366`
(`fitBSplineSurfaceAndGetNormalsOnProjectedPoints`, body `:1379-1579`), but **only the normals
come from the surface** — `:1527-1529` re-assigns `ptTmp.x/y/z` from the original sampled
point, so no stage snaps the lane onto the mesh. The result is written as
`CompleteBreakline.xyz` at `:2439`. `detectSeparateLineSegments` (`:1914`, called at `:3395`)
splits that file into `Segments/<n>.xyz` (`:2153`, and the merged last+first segment at
`:2218`); the cloud-building loop `:3440-3484` reads those files back and the writer `:1643`
emits the PCD. On the assembler side the chain is `ReadPCDFileWithInfo`
(`class/data_structure.cpp:180-360`) → `point_` → `BuildTree` (`:112-135`) →
`FeatureComp` (`class/feature_matching.cpp:1375-1494`) → the pose solve. Nothing on that path
reads a corner index; the corner statistic that *does* reach the file is the different one at
`:2026-2036` inside `detectSeparateLineSegments` (chord deviation with `len = 10`, on the
post-spline cloud), which is what produced J1's two segments.

**A.4 The mechanism by which lane geometry reaches a pose, and what would have to change.**
Lane points become `point_` rows, `FeatureComp` builds LCS correspondences between pairs of
shards (`class/feature_matching.cpp:1473`), and the correspondences drive the Ceres pose solve
(`class/reconstruction.cpp`). For the corner window to matter, three things would have to
change together: the block would have to **return** its index list (it is `static void` and
local), a caller would have to **split** the lane on it, and that split would have to survive
into the PCD range table — which today is rebuilt from `Segments/*.xyz` by the writer itself
(`:1656-1673`), not from any corner list. Splitting the lane is also the change the header
comment warns against, because the downstream B-spline expects one lane per face.

**A.5 The gate that does bind — the 50-point floor.** `main.cpp:85-90`:

```
85: 			shard[i].edge_line_.ReadPCDFileWithInfo(file_path[i]);
86: 			if (shard[i].edge_line_.point_.cols() < 50) {
87: 				shard_on_off[i] = false;
88: 				shard[i].edge_line_.Remove();
89: 				continue;
90: 			}
```

The test is on `point_.cols()` **after** the reader's de-duplication
(`class/data_structure.cpp:327-339`), not on the header. I recomputed the reader's rule on the
t55 bundle (a point survives unless it equals the next one; the last is compared to the first)
and every file's de-duplicated count equals its data-row count, so no piece loses points there:

| piece | Bl0 rows | deduped | survives `< 50`? |
|---|---|---|---|
| J1 | 28 | 28 | no |
| J2 | 32 | 32 | no |
| J3 | 38 | 38 | no |
| J4 | 32 | 32 | no |
| J5 | 47 | 47 | no |
| J6 | 46 | 46 | no |
| J7 | 54 | 54 | **yes** |
| J8 | 41 | 41 | no |
| J9 | 23 | 23 | no |

**One of nine survives.** `is_matching_` is set inside the same guarded block
(`main.cpp:95`), so the eight dropped pieces never reach `FeatureComp` (`:1386` and `:1456`
both `if (!a[i].is_matching_) continue;`). `main.cpp:211` calls
`FeatureComp(shard, LCS_out, 25, MINIMUM_NUMBER, 0)` with `MINIMUM_NUMBER 6`
(`class/reconstruction.h:24`), and the Juglet block expects nine shards
(`class/data_path.h:1499` `#define SHARD_NUMBER 9`, paths `:1505-1513`). A cycle is built from
a pair of shards, so with one matchable shard there is no pair to build. Separately, the
`JUGLET` base path `class/data_path.h:1502` points at
`/data/gpfs/projects/punim2657/sfs_preprocessing/Juglet_Dataset_20260916/SfS_pp/`, which does
not exist on Spartan any more (`ls` returns "No such file or directory"), so this arm needs the
t55 bundle staged there before it can run at all.

### B. Why the header over-counts, the fix, and what the declared total does

**B.1 The mechanical cause.** Two loops disagree about how many rows a segment file has.

The cloud is built at `edgeline_extraction_headless.cpp:3440-3484`; the inner loop is
`:3453`:

```
3453: 		for (size_t i = 0; i < matrix_breakLineSeg.rows() - 1; i++)
...
3465:             cloud_CompleteBreakline->points.push_back(tmpPtN);
3466:             totalPtsCounter++;
```

— one row per segment file is dropped, and `totalPtsCounter` counts only the rows actually
stored, so the counter is right.

The writer does not use that counter. `writeBreaklinePCDWithSegments`
(`:1643`) takes only `(filename, cloud)` and re-opens the segment files from disk
(`:1656-1673`):

```
1666:                 MatrixXd segMatrix = readFile(segFile.string(), 6);
1667:                 int segSize = segMatrix.rows();
1668:                 int startIdx = totalPoints + 1; // 1-indexed
1669:                 int endIdx = totalPoints + segSize;
1670:                 segments.push_back({startIdx, endIdx});
1671:                 totalPoints += segSize;
```

`segMatrix.rows()` is the **full** row count. So `totalPoints` = Σ(full rows) while the cloud
holds Σ(rows − 1): the difference is exactly one per segment file, i.e. exactly the segment
count. `totalPoints` is then written as the header's second field at `:1684`
(`file << "# " << segments.size() << " " << totalPoints << " 0"`) and the ranges at `:1687-1689`.

This also explains the ranges, which over-count by the same rule cumulatively. J1's segment
files are 14 and 16 rows (`out/pieces/Juglet_Piece_1/edge.log:77` and `:91`); the cloud gets
13 + 15 = 28; the writer emits `# 1 14 0` and `# 15 30 0` and a header total of 30. The last
range end (30) exceeds the point count (28) by 2. `POINTS` and `WIDTH` are taken from
`cloud.points.size()` (`:1697`, `:1700`) and the data rows are written from the cloud
(`:1704-1708`), so only the two `#` metadata lines are wrong. Verified on the t55 bundle for
all nine pieces: header total = last range end = rows + segments, in every file.

**The commit that introduced the divergence:** `git log -S 'matrix_breakLineSeg.rows() - 1'`
and `git log -S` on the two-argument writer signature both land on `fd01c6f` ("Ticket 238:
restore working root-edge source …"), so this is a restore artefact, not an original design.

**B.2 The correct pattern already in the repo, and the exact fix.** The same writer exists in
two other places and both take the caller's table:

- `original_nurbs_preprocessing/edgeline_extraction_headless.cpp:1349`:
  `void writeBreaklinePCDWithSegments(const std::string& filename, const pcl::PointCloud<pcl::PointNormal>& cloud, const std::vector<std::string>& segmentIndex, const std::vector<int>& peakIndices = std::vector<int>(), bool convertToMM = true)`,
  with `:1357` `int totalPoints = cloud.points.size();` — the header can never over-count
  because it is the cloud's own size — and `:1366` `if (endIdx > totalPoints) endIdx = totalPoints;`
  clamping each range end.
- `edgeline_extraction.cpp:1045-1046` (GUI/legacy twin): three-argument form,
  `:1054` `int totalPoints = (int)cloud.points.size();`.

The table that is already correct is the `index` vector built at
`edgeline_extraction_headless.cpp:3481` — `index.push_back(to_string(segStartIndex) + " " +
to_string(totalPtsCounter) + " " + (isRim ? "1" : "0"))` — because `segStartIndex` and
`totalPtsCounter` are the very counters that filled the cloud (`:3466`, `:3482`). It is built,
rewritten at `:3497-3505` to carry the rim flag, and then never used: the only writer call is
`:3536` `writeBreaklinePCDWithSegments(pcdFilePath, *cloud_CompleteBreakline);`, and
`:3551` `index.clear();` throws it away.

**Minimum fix:** take the header total from `cloud.points.size()` (the twin's `:1357`), and
derive the range ends from the same counter rather than from `segMatrix.rows()`.
**Correct fix:** adopt the twin's 4/5-argument signature and call it as
`writeBreaklinePCDWithSegments(pcdFilePath, *cloud_CompleteBreakline, index, detectedPeakIndices, false);`.
Two caveats found by reading: (i) the headless fork has no `detectedPeakIndices` at all —
`:3395` discards the return of `detectSeparateLineSegments`, whereas the twin captures it at
`:3221`; (ii) even the twin hard-codes the range flag to `0` (`:1393`) and ignores the parsed
`flag` (`:1379`), so adopting it fixes the counts but still writes no per-segment rim flag.

**B.3 What the assembler does with the declared total: reads it, prints it, discards it.**
`class/data_structure.cpp:216-220`:

```
216:         totalSegments = stoi(results[1]);
217:         totalPts = stoi(results[2]);
218:         int info_index = stoi(results[3]);
219:
220:         cout << "Found " << totalSegments << " segments, " << totalPts << " total points" << endl;
```

`totalPts` appears nowhere else in the file. The header strip is sized by `totalSegments`
(`:300-304`, `fileContents.erase(..., totalSegments + 12)`), the point count comes from
`fileContents.size()` (`:307`), and the ranges are read into `index_` (`:228-243`) with no
check against the point count. That asymmetry — count from `totalSegments`, total ignored — is
what makes the defect cosmetic today.

**B.4 The rim question.** `info_index` is the third field of the header line; `abs(info_index)`
1 or 3 sets `is_seg_rim_` (`:223`). Once that is true, four kinds of loop index with the
ranges, and none of them clamps:

- `class/reconstruction.cpp:839-856` (`MakeRimData`, `BreakLine`), `:857-874` (`Geom`),
  `:876-898` and `:899-921` (`RimConstraint`): `for (int r_c = start - 1; r_c < end; r_c++)`
  reading `point_.col(r_c)` (`:849-850`, `:867-868`, `:891-893`, `:914-916`).
- `class/feature_matching.cpp:1123-1129` and `:1273-1279` (both `CountPCInlier` overloads,
  `:1100` and `:1244`): the same loop, `rim_data.push_back(...point_.col(r_c))`.
- `class/ranking_system.cpp:1808-1822` (`rim_data.push_back(point_.col(r_c))` at `:1818`).

With J1's ranges (`end = 30`, `point_.cols() = 28`) these read columns 28 and 29 of a
28-column matrix. **What happens then is undefined behaviour, not an abort.** This repo's
`CMakeLists.txt` sets no build type and no `NDEBUG`, but every documented invocation passes
`-DCMAKE_BUILD_TYPE=Release`, and the compilation actually used on Spartan confirms it:
`/data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/build/CMakeFiles/Hierarchy-Clear.dir/flags.make`
→ `CXX_FLAGS = -O3 -DNDEBUG -fPIC -fopenmp -std=gnu++17`. With `NDEBUG` defined, `assert` is
compiled out (there is no `assert` in these four loops anyway) and Eigen's own bounds check is
disabled too, so the read is silent out-of-bounds.

Two further consequences worth stating, both from reading rather than running:

- `BuildTree` (`class/data_structure.cpp:112-135`) with `is_seg_rim_` true inserts a point only
  when `(i + 1 > index_(0, j)) && (i + 1 < index_(1, j)) && !index_(2, j)` (`:120-121`). The
  strict inequalities exclude each rim segment's first and last point, and a segment whose
  per-range flag is `0` is skipped entirely — so a file with `info_index` 1 and all-zero range
  flags (which is exactly what today's writer produces) builds an **empty** k-d tree.
- The rim constraint only switches on from iteration 2 and only when at least two shards in
  the cycle are rim-flagged: `class/reconstruction.cpp:1150-1161`
  (`if (rim_counter < 2) rim = false;` at `:1159`), guarding the block at `:1238-1252`.
  A single flagged piece never reaches `MakeRimData`, so the unclamped read needs two
  flagged pieces in one cycle.

**Also worth recording:** neither writer can currently set a flag. `info_index` is hard-coded
`0` at `:1684`, and the per-range flag is hard-coded `0` at `:1688`; the rim work at
`:3475-3509` only rewrites the in-memory `index` strings (`:3497-3505`) that are then cleared
at `:3551`. So on any file this repo produces today `is_seg_rim_` is false and the rim path is
unreachable — it becomes reachable as soon as someone wires the flag through.

**B.5 Order of operations.** The range/header fix must land **first**, and only then may a
change start writing `1`s. Reason: the ranges are wrong by a cumulative one-per-segment, so a
flag written over today's ranges points past the end of the point matrix on the last segment of
every multi-segment file (J1 30 vs 28, J7 57 vs 54). The header total itself is independent —
it is discarded by the reader — but it should be fixed in the same change, because a correct
total is what makes a wrong range visible.

### C. Why J1's Breakline_0 left the surface — the five points

| # | the lead's point | verdict |
|---|---|---|
| 1 | open arc, largest-component seed, stop rule, no restart | **borne out** |
| 2 | closure implicit — wrap edge added with no length test | **borne out, and the chord IS in the emitted file** — the worker's 'not shown' verdict is refuted below; it searched at the file's wrap index, where the vote's reversal had moved it |
| 3 | second arc unreachable; a restart rule would have resumed at dot 3 | **borne out as to the mechanism; the `f50 = 0` detail is not in the t55 log** |
| 4 | the boundary rule cannot see a crease — angular-void test only | **borne out** |
| 5 | no existing check would catch a lane leaving its surface | **borne out** |

**C.1 Seed, stop, and the absence of a restart — borne out.** `fullWalk263` is the default
(`:605`), the bag is walked with no discard (`:622`), the seed is the dot nearest the centroid
of the **largest** component (`:636-647`), and the stop test is
`if (stopOn267 && dFresh267 > stopR267)` at `:731`, where `dFresh267` is the distance to the
nearest fresh dot **anywhere** (`:716-720`) and `stopR267 = 12.0f` (`:615`). On the trip the
code prints `[STOP-267] CHAIN-END step=… ; refusing it ; left=… dots unvisited` (`:732-734`)
and then `break;` (`:735`). There is no restart anywhere in the function: after the break the
loop is done, `chain` is final, and the unvisited dots are simply not walked. J1's line is
`out/pieces/Juglet_Piece_1/edge.log:36`.

*Two numbers in the Given differ from the log and I am reporting them, not reconciling them:*
the log says `step=70 of 208`, `chain=71`, and `nearest fresh dot 24.2758mm`; the Given says
"69-71 of 208" and "22.89 mm". The log is the artefact, so where they disagree the log's figures
are the ones in the run of record.

**C.2 The implicit closure — borne out in the code.** `:797-800`:

```
797: 	std::vector<float> cum(M0 + 1, 0.0f);
798: 	for (size_t i = 0; i < M0; i++) cum[i+1] = cum[i] + (loop[(i+1) % M0] - loop[i]).norm();
799: 	float L = cum[M0];
```

The `% M0` term is the edge from the last walked dot back to the first. It is added with no
length test and no check that it stays near the surface, and `L` — which includes it — is what
sets the resample count at `:800`. The resampled points are interpolated along that same closed
parameterisation at `:804-810`.

**And the chord IS in the emitted file — it is at dot 2, not at the wrap.** (The worker
wrote here that it was not shown; the lead's re-check below refutes that.) Measured on
`out/geom/Juglet_Piece_1.Bl0` (28 rows): consecutive gaps are 1.7997–1.8005 mm everywhere
except dot 2→3, which is **5.1984 mm**; the wrap gap dot 28→dot 1 is **1.7996 mm**. The
straight off-surface run is dots 3–11, 14.4000 mm with maximum off-chord 0.0088 mm. The
reason the chord is not at the file's wrap index is the vote's own reversal: the log prints
`[VOTE-247] chain=71 turnSum=-6.13726 CW-reversed-to-CCW`, so the walked chain is emitted
end-first, and the closure edge — last walked dot back to the first — lands **inside** the
file rather than at its boundary. The straight run starts one dot after the walk's end
(dot 2 is the walk's last dot, distance 0.000 mm) and runs along the walk-end→walk-start
chord to within 0.14–0.69 mm for 21.4 mm of it, then the lane picks up the walked arc at
dot 12–13 (1.9 / 0.4 mm from walked dots 3 and 4). So the file contains the chord; it just
does not sit where a reader who assumes the file's first and last rows are the closure would
look for it.

**C.3 Why the second arc could not be reached — borne out as a mechanism.** The walker's probe
is `nearestKSearch(cloud->points[cur], 50, idx, dist)` (`:662-663`), and the number of fresh
dots among those 50 is counted at `:700`. The stop decision, however, does not use that count:
it scans **every** point for the nearest fresh one (`:716-720`) and stops when that distance
exceeds `stopR267` (`:731`). So the walk ends because the nearest remaining dot anywhere is
too far, and because nothing restarts the walk, the second component is never entered. J1's log
corroborates the component structure: `[LOOP-SELECT] bag=208 comps=2` with components of 139
and 69 dots, both classified RIM (`edge.log:29-31`), and the walk seeded in the larger one
(`:35`).

One qualification: the lead's `f50 = 0` at step 70 is **not** in the t55 log — the per-step
instrument is behind `SFS_STOP_NOFRESH_DIAG`, which defaults off (`:618-619`), and
`grep -c 'STOP-267] S i='` on J1's log returns 0. The claim is consistent with the code and
with the stop firing, but the run of record does not print it. What the log does establish is
that the walk stopped with 137 of 208 dots unvisited, which is the fact the mechanism needs.

**C.4 The boundary rule cannot see a crease — borne out.** The detector is PCL's
`BoundaryEstimation` with exactly two knobs: `boundary_est.setRadiusSearch(4)` (`:1105`)
and `boundary_est.setAngleThreshold(M_PI * 0.6)` (`:1108`, with the plain `M_PI` variant
commented on the line above at `:1107`). Its test is a tangent-plane maximum-angular-gap: a
point is a boundary point if some angular sector of its disc is empty. **No normal-discontinuity
or crease term is passed to it, and none is computed afterwards** — the only post-filter is
`FACE_ALIGN_VETO = 2.0f` (`:1122`), applied to `normal · radial` at `:1136-1145`. A patch
that folds over its own edge supplies dots on both sides, so no sector is empty and the crease
is invisible by construction. (The adaptive-radius arm at `:1096-1102` is compiled only under
`-DPOTA218_ARM_B`, and the t55 log carries no `[ARM-B radius]` line, so the build in the run
of record used the fixed 4 mm / 0.6π rule.)

*Which stage owns a cure:* the boundary stage cannot detect this crease with its current rule —
detecting a fold would need a normal-discontinuity term that does not exist in the code, i.e. a
new capability rather than a threshold change. Keeping `Surface_0` from crossing onto the
other face is a property of the surface stage, which is where the patch is built
(`mesh_processing_headless.cpp:4993-5000` writes `Surface_0.ply` and converts it to `Surface_0.xyz`).
So the surface stage owns the cheap fix; the boundary stage would own a new crease detector.

**C.5 What it costs today, and whether any check would catch it — no check would.** Every
emitted dot is a resampled point of the walked chain, so a lane that leaves the surface looks
exactly like a lane that does not: J1's log prints a clean `L=59.8158mm` and no length warning
(`edge.log:40`). The only geometric self-checks in the edge stage are the axis statistic
`100 * stdDevList[q] / mean < 50` (`:3495`) and the normal-clustering CV
`(meanCV_C1 + meanCV_C2) / 2 > 0.12` (`:3088`) — one measures deviation from the fitted axis,
the other the consistency of normals within a segment; neither compares a breakline point with
the surface it came from. A grep for `chamfer`, `distanceToMesh`, `distToMesh` and `toMesh`
across `edgeline_extraction_headless.cpp` returns nothing, and `scripts/diagnostics/verify_extraction.py`
is a textual move-verifier, not a geometric one. **No existing check would have caught this.**

**What a fix would have to change.** Three separable changes, in this order of ownership:
(1) *surface stage* — keep `Surface_0` off the opposite face, so the crease is a real void;
(2) *edge stage* — do not close a chain the walk abandoned: either refuse the wrap edge when
the chain did not return near its own start (the `:798` term is where that test belongs), or
restart the walk on the nearest unvisited component instead of dropping it (`:735`); (3) *a new
check* — measure each breakline point's distance to its own surface and report the lane's worst
excursion, because nothing in the stage currently can.

### What I could not settle, and the boundaries observed

- The resampled cloud (`_breakLineFromConcaveHull.ply`) and the per-piece build tree were
  deleted with the run's geometry; only `out/geom/*` survives. So the resampled lane itself
  cannot be shown from the artefacts, only the emitted lane after the smoother. **The lead
  has since closed this: the chord is visible in the emitted lane, at dot 2 (see C.2 and the
  verification below).**
- The per-step stop instrument was off in t55 (see C.3), so `f50`/nearest-fresh per step is not
  in the log.
- Ticket Given vs log, reported not reconciled: walk "69-71 of 208" vs `step=70`, `chain=71`;
  "nearest fresh dot 22.89 mm" vs **24.2758 mm**; J1's lane "28 dots" vs `resampled=31` (the 31
  resampled points become 28 `CompleteBreakline` rows, and the 28 rows are what the file holds).
- Pot A's shipped files in the same run tree are self-consistent (`PA01 # 4 59 0` over 59 rows,
  `PA02 # 6 162 0` over 162 rows), which matches the Given's conclusion (Pot A consistent) but
  not its per-file numbers (the Given lists PA01 6/207/207); different bundle, same conclusion.
- No source change, no Slurm job, no corpus write. Nothing merged.

---

## Lead verification (2026-11-02)

Every claim the worker made that this ticket will be acted on was re-read or recomputed by the
lead before it was recorded. What was checked, how, and what came back:

| claim | how it was checked | result |
|---|---|---|
| the corner window reaches nothing | read `:540-552`, `:829-845`, the `static void` at `:553`; grepped `corners`/`cidx` | confirmed |
| the 50-point gate at `main.cpp:86` | read `main.cpp:85-95` | confirmed, verbatim as quoted |
| only J7 survives the gate | recounted `out/geom/Juglet_Piece_*.Bl0` data rows | confirmed: 28, 32, 38, 32, 47, 46, **54**, 41, 23 |
| header total = rows + segments, all nine | recounted header, `POINTS` and data rows for all nine | confirmed, all nine, exactly |
| `JUGLET_BASE` does not exist on Spartan | `ls` on the path | confirmed: "No such file or directory" |
| `NDEBUG` is defined on the real build | read the Spartan `flags.make` | confirmed (`-O3 -DNDEBUG ...`) |
| the chord is not visible in the emitted file | **refuted** — see below | the chord is there, at dot 2 |

**The chord, found.** The worker looked for the closure at the file's wrap (last row → first
row) and found 1.7996 mm there, which is why it recorded "the emitted file does not show the
chord at the wrap". It does not — because the vote reversed the chain
(`[VOTE-247] chain=71 turnSum=-6.13726 CW-reversed-to-CCW`), so the closure edge is emitted
*inside* the file. Tested directly against the walk:

- emitted dot 2 is **the walk's last dot, to 0.000 mm**.
- dots 3–11 lie on the walk-end → walk-start chord (23.938 mm long) at 5.196, 6.996, 8.795,
  10.595, 12.394, 14.193, 15.992, 17.792, 19.591 mm along it, with perpendicular offsets
  **0.142–0.551 mm**. Nine consecutive 1.800 mm steps along a 24 mm gap that has no surface
  in it.
- dot 13 reaches the chord's far end (22.871 mm along, 1.671 mm off) and dots 12–13 sit
  **1.897 mm and 0.403 mm** from walked dots 3 and 4, i.e. the lane rejoins the walked arc there.
- surface distance, exact point-to-triangle, per dot: dots 3–11 are **2.35–5.22 mm** off
  `Surface_0`; every other dot is **≤0.52 mm**. The off-surface run and the chord run are the
  same nine dots.

So part C's point 2 is **borne out in the code and in the file**; the mechanism the lead
measured is what the artefacts show. The worker's contrary verdict rested on a search at the
wrong index, not on a different measurement.

**One number the lead retires.** The Given's "closure chord 23.94 mm" is right as the gap
between the walk's two ends, but it is not a single emitted step: the resample subdivides it
at the same 1.9 mm parameterisation as the rest of the loop, so it appears as nine 1.800 mm
steps plus one 5.198 mm entry step. A reader should not expect a 24 mm jump in the file.

### C.4 in full — why the dot set was in pieces, measured after the worker's report

The worker confirmed the detector has no crease term. The lead then measured what that costs,
on J1's own surfaces (probe scripts on Spartan; every figure below is a measurement):

- **Both surface patches are complete.** At 3 mm linkage `Surface_0` is ONE component
  (13,850 points) and `Surface_1` is ONE (15,173 points); all 72 five-degree sectors of each
  contain points. The patch is not torn — the *boundary dots* are in pieces.
- **Neither surface yielded a ring.** S0: 194 boundary dots in 2 groups at 5 mm, largest 131,
  covering 16 of 36 ring sectors (44%). S1: 347 dots in 4 groups, largest 247, 21 of 36 (58%).
- **The break edge on the mesh is a real closed ring:** 770 sharp-crease vertices (dihedral
  > 60 deg), circle fit R = 14.26 mm, residual median 3.09 mm, 32 of 36 ten-degree sectors
  occupied.
- **The cause is the patch folding over its own edge.** 68% of S0's edge points have S0's own
  material on *both* sides of the fold (reaching 2.1 mm and 1.7 mm past it); 45% of S1's do
  (2.6 and 1.7 mm). A tangent-plane empty-wedge test cannot fire where the wedge is not empty.
- **Intervention test — the decisive one.** Delete each patch's own points that lie past the
  break edge, re-run the same detector unchanged: S0's fire rate rises **14% → 34%**, S1's
  **30% → 45%**. The wrap is the mechanism, and it bites both surfaces.
- **Why S0 is worse than S1** (same fault, hit harder): 32.5% of S0's points sit within 2 mm
  of the crease against S1's 20.5%; at the edge S0 owns 56% of its own 4 mm neighbourhood
  against S1's 44%, so S1 is more outnumbered by the other face and its edge is more exposed.
  Density alone is not the cause: thinning S0 to 85/60/35% moves its fire rate only
  14 → 15 → 16 → 19%, nowhere near S1's 30%. Supplied vs PCA normals change nothing.
- **Coverage of the true edge by the emitted lanes:** `Breakline_0` covers 78 of 770 crease
  vertices (10%), `Breakline_1` 199 (26%), both together 254 (33%).

This sharpens the worker's C.4 answer rather than contradicting it: the surface stage owns the
cheap cure, and the reason it is cheap is now measured — removing the wrap alone more than
doubles the detector's fire rate at the same edge, with no threshold changed.

**A correction to the Given that this replaces.** The Given describes S0's boundary as "two
separate arcs (127 and 63 dots at 5 mm linkage)". That is the run's own `[LOOP-SELECT]`
line and it stands for the 208-dot bag; the three-arc picture (77 + 50 + 63 dots, gaps 4.05,
18.76, 28.53 mm) is the lead's 3 mm re-linkage of its own replication, not the run's. Use the
run's 139 + 69 where the run is the subject.
