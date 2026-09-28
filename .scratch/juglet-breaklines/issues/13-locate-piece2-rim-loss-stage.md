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

## Acceptance criteria

- [ ] Per-stage coverage table for piece 2, one row per intermediate, all
      measured against the same 169-pt reference at 2mm
- [ ] The collapse stage named explicitly (surface→cleaned, cleaned→boundary,
      boundary→walk, or walk→emitted), with the before/after numbers
- [ ] The snapshot script kept in the repo so the same table can be produced
      for any other sherd without new work
- [ ] No code changes to the pipeline in this ticket — it is measurement.
      If the table says the walk input already lacks the rim, that confirms
      ticket 03's closure rather than reopening it

## Note

`Temp_edge/` is overwritten per surface AND per piece, so a full-pot run
keeps only the last surface of the last piece. The piece-2-only tree exists
precisely because of this. Do not attempt this measurement on a full run.
