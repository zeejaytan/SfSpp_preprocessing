# E1 — Do the breaklines we extract let SfS++ find any join?

**Status:** open · **Blocked by:** none · **Effort:** a measurement on
existing scans, then a change to `edgeline_extraction.cpp`

## Why it matters

SfS++ (the assembler, `../structure-from-sherds-pp`) decides two sherds
join by asking: is a point on one sherd's breakline within ~2 mm of a
point on its neighbour's, with the two surface normals agreeing (dot
> 0.85)? On the sample it was developed on, that question has a
satisfying answer: **15 of 15 true joins pass** it.

On the Juglet — a handmade, 1.8 mm-walled Palestinian juglet — it passes
**0 of 18**. The assembler was handed the *exact* ground-truth placement
of a genuinely-touching pair and still discarded the join with zero
matching points, while the same harness accepted a true pair on the
control pot (`artifacts/juglet_run1/gate_probe_b0.py` and ticket 06 in
the assembly repo).

That result was measured, not assumed, but **it is not this repo's
verdict to draw**. It could be the extractor's fault, or the assembler's
assumptions, or something about the object. The difference is decided
here, by what we hand over: a breakline that a 2 mm / agreeing-normal
test cannot fail is a breakline nobody can assemble from.

## The two candidate causes, separated

At ground truth, the Juglet's true mates fail the gate for two different
reasons, and they need different fixes:

1. **Opposite wall faces.** The wall is ~1.8 mm thick. The extractor
   appears to trace the *inner* face on one sherd and the *outer* face on
   its neighbour: 1.7 mm apart, normals **67–129° opposed**. The gate
   compares them as if they were the same surface. Candidate cause: the
   segmentation assigns a fracture-boundary rim to whichever surface
   cluster it finds first, rather than to both, or the inner/outer
   assignment is not being made at all.
2. **The trace misses the seam.** Even where the faces are close, sampled
   segments run 0.2–30 mm away from where mating edges actually touch
   (0.02 mm at ground truth). On eroded, rounded breaks the extracted
   fragment often excludes the seam entirely. This one *is* erosion.

## Done when

- [ ] **Measured, not guessed:** for each of the Juglet's 9 sherds, which
      surface face (inner / outer / both) does each extracted breakline
      segment come from, and does the segment span the actual seam? A
      per-segment table, in millimetres, with the GT contact point
      marked
- [ ] **One variable changed, one hypothesis tested.** E.g. "make
      segmentation emit both wall faces" — then re-measure. Not a bundle
      of changes, because then we learn nothing about which one worked
- [ ] **The acceptance test passes:** a new bundle where true mates
      clear the gate at ground truth, i.e.
      `python ../structure-from-sherds-pp/artifacts/juglet_run1/gate_probe_b0.py <bundle>`
      reports a materially non-zero pass rate. **This is the definition
      of done** — not "the breaklines look better in a render"
- [ ] **Pot_A is not regressed.** The working sample must still pass
      15/15 on that same gate, or the change is labelled Juglet-only.
      A change that helps one and breaks the other is not a fix
- [ ] **Rendered, not just counted:** the extracted breakline on both
      sides of a real seam, staged correct-vs-attempt in `visual-qa/`.
      A pass-rate number can pass while the curve is in the wrong place
- [ ] **Honest remainder recorded:** which true mates still fail, and
      whether the cause is wear, wall thickness, or both. Do not report a
      partial fix as a solved gate

## Gate

**This question is about our extraction, not about SfS++.** If a
re-extracted breakline passes the gate at ground truth and the assembler
still finds nothing, the fault has moved downstream and belongs to
`../structure-from-sherds-pp` — say so and hand it back. If the breakline
still fails the gate, no amount of assembler tuning is worth attempting,
and the honest report is that *this material's* breaks are outside what
the method's gate assumes.

**Do not restate the assembly-side result as a preprocessing verdict, and
do not restate a preprocessing result as a capability claim about
SfS++.** The two repos have been confusing each other all week; the
distinction is the whole point of this question.

## Source

Assembly ticket 06 and `intent/S1` in `../structure-from-sherds-pp`
(2026-09-26, oracle-init proof + Pot_A control). Extractor:
`edgeline_extraction.cpp` (segment finding ~line 1632, segmentation
`clusteringOnNormals` ~line 2118, writer `writeBreaklinePCDWithSegments`
~line 1042). Juglet patches already in `patches/juglet_*.patch`.
