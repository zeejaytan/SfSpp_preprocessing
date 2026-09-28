# 13: Locate where piece 2's rim is lost between surface and boundary cloud

**Answers:** E1

**Blocked by:** nothing — measurement only, no code changes

**Status:** ready-for-agent

**Needs-eye:** none — this ticket produces a per-stage coverage table, not a
geometry claim. A render is required only if the table points at a stage
whose output needs judging by eye.

## Why this ticket exists

Ticket 03 closed defect 2 as "boundary detection loses the rim" with the
evidence that Surface_0 covers 82% of the authors' rim while the boundary
clouds cover 10%/36%. But "boundary detection" is four stages, not one:

```
Surface_0.xyz (11,263 pts, 82% of ref)
  -> cleanSamples
  -> estimatePatchNormalsAndBreakLinesFromSimpleAlgo_BSplineSurface
     (writes Temp/Temp_edge/.../cloud_Surface_AllSamples_Cleaned.pcd)
  -> getInitialBoundary_UsingPCL_BoundaryAlgo
     (reads cloud_Surface_AllSamples_Cleaned.pcd, writes boundary.pcd)
  -> boundary improved + filtered (both discarded, line 974)
  -> getPointsInSequence (the walk)
```

The walk input (`Temp_edge/boundary.pcd`, the file reloaded at line 974)
is captured per piece already. What has never been captured is
`cloud_Surface_AllSamples_Cleaned.pcd` — the actual input to boundary
estimation. Without it, "the boundary detector loses the rim" and "the
B-spline stage never had it" are indistinguishable, and any fix targets the
wrong stage.

## What to do

1. Extend the piece-2 capture (`capture_piece2_boundary.sh`, which stages a
   piece-2-only tree) to snapshot **every** `Temp/Temp_edge/` intermediate,
   not just `boundary.pcd`: `cloud_Surface_AllSamples_Cleaned.pcd`,
   `boundaryImproved.pcd`, `cloud_Filtered.pcd`, `cloudForSpline.pcd`,
   `CompleteBreakline.pcd`. Poll with md5 dedupe per file; `Temp_edge/` is
   overwritten per surface, so without this only the last surface survives.
2. For each staged intermediate, measure **reference coverage**: fraction of
   the authors' piece-2 rim (169 pts, 303.5mm) within 2mm. Same reference,
   same threshold as tickets 03/10/11, so the numbers join the existing
   tables rather than starting a new vocabulary.
3. Report the per-stage coverage table. The stage where coverage collapses
   is the named target for ticket 14.

## FOUND 2026-09-28: the collapse is at boundary estimation

Same reference (169 pts), same 2mm threshold, every stage (`stage_coverage_table.py`):

| stage (S0 chain) | n | ref within 2mm |
|---|---|---|
| Surface_0.xyz | 11,263 | **82.2%** |
| cloud_Surface_AllSamples_Cleaned | 11,263 | **82.2%** (no loss) |
| boundary.pcd | 202 | **35.5%** ← COLLAPSE (82 → 36) |
| boundaryImproved | 202 | 43.2% |
| cloud_Filtered (NaN dropped) | 183 | 37.9% |
| cloudForSpline (dense surface) | 10,000 | 80.5% (surface, not rim) |
| CompleteBreakline | 200 | 9.5% (second collapse — see note) |

| stage (S1 chain) | n | ref within 2mm |
|---|---|---|
| Surface_1.xyz | 171 | 10.1% |
| cleaned | 171 | 10.1% (no loss) |
| boundary | 86 | 10.1% (nothing to lose) |

**The named stage is `getInitialBoundary_UsingPCL_BoundaryAlgo`**
(`edgeline_extraction_headless.cpp:817`): it receives 11,263 points covering
82% of the rim and returns 202 points covering 36%. The B-spline/cleaning
stage is exonerated (82→82). The walk is exonerated again (its input already
lacks the rim).

Note the CompleteBreakline second collapse (80.5%→9.5%): the dense surface
passes near the rim but the extracted 200-pt breakline does not. That
mapping needs care (segment selection sits between them), so it is recorded
as a second, unseparated collapse rather than a second finding. The emitted
baseline rim scores 30% within 2mm — between the two — consistent with
segment selection picking the better parts.

Also corrected here: ticket 03's boundary-cloud tables labeled the two
clouds backwards (appearance order in the exchanged run). The numbers were
valid; the wall attribution was wrong. S0's cloud is the 202-pt one (36%),
S1's is the 86-pt one (10%).

A side confirmation with teeth: `cloud_Filtered.pcd` carries NaN
placeholders (organized filter output) that crash a naive reader — the NaN
hazard ticket 05 predicted. Any consumer of that file must drop non-finite
rows first.

## Acceptance criteria (all met)

- [x] Per-stage coverage table for piece 2, one row per intermediate, all
      measured against the same 169-pt reference at 2mm
- [x] The collapse stage named explicitly: `getInitialBoundary_UsingPCL_BoundaryAlgo`
      (surface→cleaned holds 82%, cleaned→boundary falls to 36%)
- [x] The snapshot script kept in the repo (`capture_piece2_boundary.sh`
      watches six Temp_edge intermediates with per-file md5 dedupe)
- [x] No code changes to the pipeline in this ticket — confirmed: the walk
      input already lacks the rim, closing ticket 03's question rather than
      reopening it

## Note

`Temp_edge/` is overwritten per surface AND per piece, so a full-pot run
keeps only the last surface of the last piece. The piece-2-only tree exists
precisely because of this. Do not attempt this measurement on a full run.
