# 02: Compare rim criteria head-to-head instead of asserting one

**Answers:** E1

**Blocked by:** nothing — laptop measurement on data already on disk

**Status:** ready-for-agent

**Needs-eye:** none — a comparison table, not a geometry claim. A render
enters only if the table disagrees with the gate and the disagreement needs
judging by eye.

## Why this ticket exists

Paper (§IV-B1, Rim detection): height/radius std ≤1.0mm, gradual change
≤0.1mm between adjacent points, ≥20 points; most-stable section wins.
Ours: plane-fit curvature error (>0.12) plus axis-distance deviation <50%
of mean (`isBreaklineSegARim`, axis override `:3289-3309`). Ticket 16 gap 5.
Nobody has run both on the same rims. The paper's test may be better, ours
may be better, or they may agree everywhere that matters — currently
unknown, and "the paper says so" is not evidence either way.

## Research spike (do first — this ticket may END here)

1. Implement the paper's rim test as a laptop script over the existing
   breakline files (Pot_A authors' rims + ours): per segment, height/radius
   std, adjacent-point variation, ≥20-point rule. Report per segment.
2. Run our test on the same segments (reimplement the stddev rule, or read
   the `is_seg_rim_` outcomes from a logged run).
3. Contingency table: segments where they agree / disagree, and for the
   disagreements, which test agrees with the gate outcome (does the segment
   participate in a passing pair?).

Lane decision from the table:
- Paper's test finds rim segments ours misses AND those segments matter at
  the gate → gate lane: implement in pipeline, score per pair.
- Tests agree everywhere that matters → close with the table as evidence;
  the deviation is cosmetic. Do not implement for compliance alone without
  a stated silent-failure reason (spec lane rules).
- Ours is better → close with the table; record that the paper's criterion
  was tested and lost on our material.

## Acceptance criteria

- [ ] Spike table: both criteria on the same segments, disagreements listed
- [ ] Lane declared with the numbers that decide it
- [ ] If gate lane: implemented, scored per pair from the current baseline,
      no regressions
- [ ] If closed without implementing: the table plus one line saying which
      condition above fired
- [ ] Authors' rims included as a comparison arm wherever a "correct" rim
      is needed
