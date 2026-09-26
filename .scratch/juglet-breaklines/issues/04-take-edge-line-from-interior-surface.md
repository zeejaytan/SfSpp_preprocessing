# 04: Take the edge line from the interior surface only

**What to build:** the two surfaces of a sherd are classified as interior
and exterior, and the edge line is taken from the **interior** one — as
the paper specifies. Today the code takes whichever surface cluster is
*larger*, with no interior/exterior test at all, and emits an edge line
for both.

**This is the largest measured cause of the Juglet failure.** On thin
wheel-thrown pots the larger surface is probably the same physical face
on every sherd, so nothing looks wrong and the authors' results are
unaffected. On the Juglet, where inside and outside are nearly equal in
area, "larger" lands on **different faces for different sherds**:
measured, sherds 1, 5 and 9 trace one face and 2, 3, 4, 6, 7, 8 the
other, which puts **10 of the 18 true joins** in an inner-versus-outer
configuration that a 2 mm agreeing-normal test can never see.

**Answers:** E1

**Blocked by:** 03 (the edge line must be a well-ordered loop before it
is worth choosing which surface it comes from)

**Status:** ready-for-agent

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
- [ ] For the Juglet, the per-sherd interior/exterior assignment is
      reported so it can be checked against the vessel's wall
- [ ] The acceptance probe improves on the face-mismatch count, and the
      count of true mates still in an inner-versus-outer configuration is
      quoted before and after
- [ ] Pot_A's gate result is reported alongside, as the no-regression
      guard

## Note

If the authors' own 142 fragments also rely on "larger = interior", this
change may alter their results too — we cannot check that from here, and
the spec records it as a robustness gap rather than an error in their
reported work. Say so in any write-up rather than implying their method
is wrong on their data.
