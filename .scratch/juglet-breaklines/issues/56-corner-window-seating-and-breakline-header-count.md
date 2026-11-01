# 56 — The corner-detection window, and why the Juglet breakline headers over-count

**What to build:** a written answer, in this ticket, to the conservator's two questions
(2026-11-01), each claim carrying the file and line it rests on. **No source change, no job
needed** — this is a read-the-code ticket. Its value is that the answers decide whether two
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

**Answers:** U19 (does the pipeline put the Juglet back together), E1 (do our breaklines let
SfS find joins)

**Blocked by:** None (can start immediately; ticket 55's run of record supplies the files)

**Status:** ready-for-agent

**Worker:** unassigned

## Spec

Two questions, one answer document. Read code; do not run the pipeline.

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

### Landmarks (orientation only — verify each before citing it)

`C:\PR\SfSpp_preprocessing\edgeline_extraction_headless.cpp`: the Vote247 walk and its
comment near :540-560; `RESAMPLE_D_MM` :556; `W` :816; threshold :828; peak test :830-845;
the lane selector :1330-1345; the segment splitter `detectSeparateLineSegments` :1914; the
breakline PCD writer :1643-1712; the cloud-building loop :3440-3484; the rim test :3476-3509.
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
- [ ] Every claim carries `file:line`; the ticket is written so the conservator can read
      the plain-language answer first and the citations after.
- [ ] No source change, no Slurm job, no corpus write. Nothing merged.

## Out of scope

- Applying either fix. This ticket establishes what is true and what the fix is; the change
  itself is a separate code ticket, written after the conservator has read the answer.
- Any assembly run or seating claim (step 5).
- Re-running the edge stage: the t55 files and logs are the evidence.

## Results (worker write-back)

_To be filled by the worker._
