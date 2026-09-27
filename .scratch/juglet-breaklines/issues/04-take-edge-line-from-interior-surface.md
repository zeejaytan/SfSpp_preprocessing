# 04: Take the edge line from the interior surface only

**What to build:** the two surfaces of a sherd are classified as interior
and exterior, and the edge line is taken from the **interior** one — as
the paper specifies. Today the code takes whichever surface cluster is
*larger*, with no interior/exterior test at all, and emits an edge line
for both.

**Originally written as "the largest measured cause of the Juglet failure".
That claim is now DOUBTED, on Pot_A evidence — see the correction below.
Do not start this ticket on the strength of the original claim.**

On thin wheel-thrown pots the larger surface is probably the same physical
face on every sherd, so nothing looks wrong and the authors' results are
unaffected. On the Juglet, where inside and outside are nearly equal in
area, "larger" was measured to land on **different faces for different
sherds**: sherds 1, 5 and 9 one face and 2, 3, 4, 6, 7, 8 the other, which
puts **10 of 18 true joins** in an inner-versus-outer configuration that a
2 mm agreeing-normal test cannot see.

**Answers:** E1

**Blocked by:** 03 (the edge line must be a well-ordered loop before it
is worth choosing which surface it comes from)

**Status:** needs-info — the premise is contradicted by measurement; see below

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

## CORRECTION (2026-09-27) — the premise is contradicted, hold this ticket

Ticket 09 produced the first measurement of **our own** preprocessing
against the gate, on Pot_A, where the answer is unambiguous. Comparing our
curve against **the authors' curve for the same sherd in the same frame**:

| piece | our→authors (median) | within 2 mm | offset along the surface normal | length vs theirs |
|---|---|---|---|---|
| 1 | **0.69 mm** | **100%** | — | 98% |
| 3 | 3.49 mm | 0% | **|cos| 0.255 — tangential, not normal** | 102% |
| 4 | 3.59 mm | 0% | — | 100% |
| 8 | 3.52 mm | 0% | — | 109% |

**If we were tracing the wrong wall, the offset would run along the surface
normal. It does not** — 59.5% of piece 3's offsets are tangential and only
11.5% normal-aligned. The offset runs *sideways*, around the same face.

Also measured and refuted on the way:

- **not displaced inward** — radius ratio 1.029, area ratio 1.054 against the
  reference, so our loop is the same size and very slightly *outward*;
- **not an over-permissive boundary detector** — rendered and inspected:
  piece 1's sherd has obvious interior ring features and our curve walks
  past all of them to the true outer edge, and piece 3's offset is a clean
  parallel displacement rather than a loop hopping between features.

So the face-selection question is **real for the Juglet** (10/18 inner vs
outer is measured) but it is **not** the cause of the Pot_A shortfall, and
Pot_A is where the gate is fair for every pair. If this ticket is done, it
should be justified on the Juglet's face evidence — not presented as the
fix for our 7/15.

## Note

If the authors' own 142 fragments also rely on "larger = interior", this
change may alter their results too — we cannot check that from here, and
the spec records it as a robustness gap rather than an error in their
reported work. Say so in any write-up rather than implying their method
is wrong on their data.
