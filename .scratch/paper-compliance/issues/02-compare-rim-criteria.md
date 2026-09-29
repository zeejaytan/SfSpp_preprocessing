# 02: Compare rim criteria head-to-head instead of asserting one

**Answers:** E1

**Blocked by:** nothing — laptop measurement on data already on disk

**Status:** resolved 2026-09-29 — cosmetic, with the table

## Spike result: agree 60, disagree 5 — all five on the authors' files

Paper test implemented per segment over authors' rims + ours (height/radius
vs axis, std ≤1.0, adjacent variation ≤0.1, ≥20 pts), compared against the
recorded rim flags in the same files:

- Our files: **zero disagreements.** Every segment our flag calls rim
  passes the paper test, and vice versa.
- Authors' files: 5 segments flagged rim fail the paper test (on
  gradualness — their std_h/std_r pass at 0.15–2.39/0.4–0.74, so the ≤0.1mm
  adjacent-variation rule is what bites). Their bundle still scores 15/15,
  so no gate consequence either.

Caveat recorded: the paper picks ONE most-stable rim section per sherd
while files carry per-segment flags, so this compares threshold-vs-flag
rather than selection-vs-selection. Within that limit, there is nothing to
implement — our criterion coincides with the paper's test everywhere on our
data, and the only deviations found are in the authors' own files against
their own test. Lane decision: close cosmetic.

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
