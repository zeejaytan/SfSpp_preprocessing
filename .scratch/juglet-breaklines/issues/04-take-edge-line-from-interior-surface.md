# 04: Take the edge line from the interior surface only

> **STATUS: implementing. The remedy is now DEMONSTRATED per-sherd.**
>
> A blanket swap (ticket 10) fixed six of eight rims to 0.53–0.80 mm but
> moved the gate 7/15 → 6/15, because piece 1 was already right and the swap
> broke it. The per-sherd mix — pieces 1+2 from `Surface_0`, 3–8 from
> `Surface_1` — scores **11/15**, recovering all five piece-1 pairs, with
> every remaining failure containing piece 2. So the remedy is a per-sherd
> rule, which is exactly what the paper's interior/exterior test is. Full
> numbers in ticket 10.

**What to build:** the two surfaces of a sherd are classified as interior
and exterior, and the edge line is taken from the **interior** one — as
the paper specifies. Today the code takes whichever surface cluster is
*larger*, with no interior/exterior test at all, and emits an edge line
for both.

The rule is **inconsistently correct**, which is the finding. On seven of
eight Pot_A sherds a single cluster holds 100% of the points, so "largest"
makes no choice at all and both walls pass forward as one surface. Piece 1
is the only sherd where it chooses (31 clusters, largest holding 18.6%) and
the only one whose rim already matches. So the rule is right by coincidence
on some sherds, not systematically.

**Answers:** E1

**Blocked by:** 03 (the edge line must be a well-ordered loop before it
is worth choosing which surface it comes from)

**Status:** in-progress — classifier + tests written 2026-09-28, building next

**Needs-eye:** the conservator should be shown, for one true pair, which
face each sherd's edge line came from — on the render staged in 07.

- [ ] Interior/exterior is decided by the paper's test: for each sampled
      point, project a ray along its surface normal to the axis of
      symmetry; the sign of the scalar coefficient classifies the surface
- [ ] Where the two surfaces are ambiguous, both configurations are
      evaluated and the one with more satisfying points wins, as the
      paper describes
- [ ] The edge line is taken from the interior surface only; what the
      extractor writes for the other surface is a deliberate, recorded
      decision rather than a side effect of file naming
- [ ] The rule is **not** a blanket flip. Piece 1 is already correct on
      `Surface_0` and is broken by swapping, so any implementation must be
      shown to keep piece 1 correct and fix pieces 3–8. A rule that scores
      well by always taking the other surface has simply moved the error.
- [ ] For the Juglet, the per-sherd interior/exterior assignment is
      reported so it can be checked against the vessel's wall
- [ ] The acceptance probe is re-run and reported **per pair**, against
      movement in our own Pot_A score (7/15, not 15/15 — see ticket 09) and
      the Juglet's honest denominator of 10
- [ ] The result is reported as a **paper-compliance fix with no measured
      effect on the gate**, unless the per-pair numbers say otherwise. Do
      not let a real deviation be reported as a solved failure

## Two errors this ticket's history records, so they are not repeated

1. **The offset direction was measured against the wrong normal.** The 3.5 mm
   offset was found to be tangential to the *mesh* (|cos| 0.255) and this
   ticket was marked `needs-info` on the conclusion "not the other wall."
   But the two wall faces meet the mesh at an angle, so a wall-to-wall
   displacement *is* tangential to the mesh. The measurement was sound and
   the inference was not; testing the mesh's normal could not have detected
   this.
2. **A real improvement in a proxy was nearly reported as a fix.** The swap
   took the curves from 3.5 mm to 0.7 mm from the reference — a fivefold
   improvement — and the gate did not follow. The offset is real and is not
   the cause of the lost joins.

Both are the same shape: a sound measurement, a plausible inference, and no
intervention to test it. The fix is to always ask what the metric the
question is *scored on* says, not what the proxy says.

## Note

If the authors' own 142 fragments also rely on "largest = interior", this
change may alter their results too — we cannot check that from here, and
the spec records it as a robustness gap rather than an error in their
reported work. Say so in any write-up rather than implying their method
is wrong on their data.
