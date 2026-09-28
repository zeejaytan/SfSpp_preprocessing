# 14: Fix the stage that loses piece 2's rim

**Answers:** E1

**Blocked by:** 13 (the stage must be named by measurement before it is
changed — ticket 03 is the record of what happens when the wrong stage is
fixed eight times in a row)

**Status:** blocked — do not start until ticket 13 names the stage

**Needs-eye:** required before closing. Any change to where a rim is traced
is a geometry claim; stage the before/after rims against the authors'
reference in `visual-qa/` as a single look per affected sherd.

## Scope as currently understood (to be replaced by ticket 13's finding)

Candidates, in pipeline order, with what would confirm each:

1. **`cleanSamples` / B-spline surface stage.** If
   `cloud_Surface_AllSamples_Cleaned.pcd` already lacks the rim zone that
   Surface_0 has, the loss is here. Suspect: resampling or smoothing that
   drops the fracture strip.
2. **Boundary estimation** (`getInitialBoundary_UsingPCL_BoundaryAlgo`).
   If the cleaned cloud covers the rim but `boundary.pcd` does not, the
   detector (radius 7.78mm adaptive, angle 108°) misses this sherd's edge.
   Note ticket 11 eliminated the radius *globally* — the gate was flat
   across 3–9mm — so a radius fix here would have to be piece-specific to
   avoid contradicting that finding.
3. **The walk input selection** (line 974 reload). If `boundaryImproved.pcd`
   or `cloud_Filtered.pcd` covers the rim while `boundary.pcd` does not,
   the fix is to stop discarding the computed improvement. Ticket 03 tested
   the improved cloud's walkability (coverage stayed 0.68/0.27, <45% near
   reference) — so this candidate is already weak, but the measurement
   belongs to this ticket if ticket 13 contradicts it.

## Constraints from earlier tickets (do not re-litigate)

- The fix must move the **gate** (11/15 → up), not just a per-sherd offset.
  Ticket 10 is the record of a 5× proxy improvement that changed no joins.
- The fix must keep piece 1 correct (0.69mm, 100% inside tolerance) and must
  not regress the six currently-passing pairs. Report per pair, from 11/15.
- The authors' arm rides along in every comparison (ticket 11's rule).
- If the fix touches the surface split, it must not undo ticket 04's 11/15:
  re-run the guard audit (`KEPT`/`EXCHANGED` per piece by `cmp`) as part of
  acceptance, not just the gate number.

## Acceptance criteria

- [ ] The stage named by ticket 13 is the stage changed — no other stage
- [ ] Piece-2 rim coverage of the 169-pt reference reported before/after
- [ ] Gate re-measured per pair from 11/15; Juglet re-measured against its
      honest denominator of 10
- [ ] Guard audit re-run (ticket 04's per-piece decisions unchanged or
      changed-with-reason)
- [ ] Witnessed look of the fixed rim against the reference
- [ ] If the change alters shared code paths (not piece-2-only), the full
      Pot_A + Juglet boundary coverage distributions re-measured (ticket 08's
      method), so a local fix with global side effects cannot hide
