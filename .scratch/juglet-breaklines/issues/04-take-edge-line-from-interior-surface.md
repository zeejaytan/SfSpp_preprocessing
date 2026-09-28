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
the paper specifies. The paper selects the two largest clusters and then
classifies them; the code did the first half (largest → `Surface_0`) with
no interior/exterior test at all, and emitted an edge line for both.
(Corrected per ticket 16: "largest" was never the deviation — only the
missing classification was.)

The rule is **inconsistently correct**, which is the finding. On seven of
eight Pot_A sherds a single cluster holds 100% of the points, so "largest"
makes no choice at all and both walls pass forward as one surface. Piece 1
is the only sherd where it chooses (31 clusters, largest holding 18.6%) and
the only one whose rim already matches. So the rule is right by coincidence
on some sherds, not systematically.

**Answers:** E1

**Blocked by:** 03 (the edge line must be a well-ordered loop before it
is worth choosing which surface it comes from)

**Status:** resolved 2026-09-28 — pipeline reproduces the 11/15 demonstration,
then 15/15 with patch rims (ticket 14)

## RESOLUTION: the pipeline now selects per sherd, 7/15 → 11/15

Classifier (`surface_classify.{h,cpp}`, dependency-free) + 5 unit tests
(passing) + wiring that exchanges the two Surface inputs when `Surface_1`
wins the vote, so `Breakline_0` always comes from the interior wall.

Pot_A run with axes staged, verified by `cmp` on disk per piece (not by log
lines — the first version of the exchange logged success while copying each
file onto itself, caught only by byte-comparison):

| piece | vote | action | audit |
|---|---|---|---|
| 1 | S0 wins 820 vs 225 | kept | KEPT confirmed |
| 2 | S1 wins 403 vs 280 | exchanged | EXCHANGED confirmed |
| 3–8 | S1 wins by ~950 vs ~50 | exchanged | EXCHANGED confirmed |

Piece 2's margin (403 vs 280) is notably weaker than the rest — consistent
with piece 2 being the ambiguous truncated sherd.

Gate (`t04_interior` arm): **11/15**. Passing: 1-3, 1-4, 1-5, 1-6, 1-7, 3-5,
3-6, 4-6, 4-7, 4-8, 6-7. Failing: **1-2, 2-4, 2-5, 2-8 — all contain
piece 2**, whose rim is 46% of the reference length. The five piece-1 pairs
recovered at 0.16–1.24 mm.

Piece 2's exchanged rim now reaches piece 1 at 0.45 mm (was 22.94 mm) but
with opposing normals, so 1-2 still fails — on normals, not distance. That
is a thread for the ordering work, not this ticket.

**Open remainder, stated not buried:** the Juglet per-sherd assignment has
not run — there are no Juglet axis files (`Dataset/Axes/` holds Pot_A
only), so the vote cannot fire there. And the witnessed render (Needs-eye)
is still owed; the matplotlib offset render exists but is not a staged
`visual-qa` look.

## GUARDS 2026-09-28: the vote picks a scrap on piece 2, so the vote gets guards

Measured on piece 2's intermediates (`surfaces_cover_rim.py`):

| source | points | authors' rim within 2mm | median |
|---|---|---|---|
| Surface_0 | 11,263 | 82% | 1.26mm |
| Surface_1 | **171** | 10% | **45mm** |
| unclustered | 1,428 | **100%** | **0.53mm** |

**Surface_1 is a 171-point scrap sitting 45mm from the fracture**, and the
vote picked it (margin 403 vs 280 — the weakest of all eight by far).
Worse, the unclustered points — the fracture zone region-growing refused —
cover the whole reference rim at half a millimetre. So the vote erred AND
the best rim source for this sherd is neither named surface.

The guard, implemented in `ticket04_interior_first.cpp`: an S1 win stands
only if S1 holds **≥10% of S0's points** AND the margin ratio is **≥2.0**.
Separations on current data: size 0.015 vs 0.80–0.96, margin 1.44 vs
~3.6–30. Either guard firing keeps historic order with the reason logged.
Both thresholds provisional (8 sherds, one pot) and recorded as such.

**Prediction, on record before the run:** piece 2 keeps Surface_0 and the
pipeline reproduces the hand-built mixed bundle at **11/15**, failing
exactly 1-2, 2-4, 2-5, 2-8. Run `run_ticket04_pota.sh` in flight; audit
table plus gate score together, audit first.

## CONFIRMED 2026-09-28: pipeline scores 11/15 with the guard live

Audit (by `cmp`, per piece): 01 KEPT, 02 KEPT via guard rejection, 03–08
EXCHANGED. Piece 1's file is byte-identical to baseline; piece 2's differs
byte-wise (fresh mesh run colliding with the known run-to-run variation)
while its pairs behave as predicted.

Gate (`t04_interior` arm): **11/15**, failing exactly **1-2, 2-4, 2-5, 2-8**
— the predicted set. The five piece-1 pairs recovered at 0.16–1.24 mm.

Defect 1 is implemented, not demonstrated: per-sherd interior selection
with scrap-guards, 7/15 → 11/15 from the pipeline itself.

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

If the authors' own 142 fragments classify the same way ours now do, this
change is behaviour-neutral on their data — we cannot check that from here.
(Corrected per ticket 16: both sides select the two largest; the old wording
here, "largest = interior", misdescribed the comparison.) Say so in any
write-up rather than implying their method is wrong on their data.
