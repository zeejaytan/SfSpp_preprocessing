# E1 — Do the breaklines we extract let SfS++ find any join?

**Status:** open · **Blocked by:** none · **Effort:** a measurement on
existing scans, then a change to `edgeline_extraction.cpp`

**2026-09-26, ticket 02 groundwork — and the question has moved.** Three
measurements re-pointed the work, none of them needing C++:

1. **The extractor already emits both wall faces** (`Breakline_0` and
   `Breakline_1`, both genuine surface traces). There is no missing-face
   bug in *our* code. The assembler reads only `Breakline_0` — an
   assembly-side limitation, and recording it as our defect would have
   been wrong.
2. **Reading both makes the gate worse** (1/18 true vs 4/18 false, against
   0/18 vs 1/18 today), because pooling lets opposite wall faces match at
   0.17 mm. All four face-pairing conventions were tested; only 1/18
   passes under any. Face pairing is not the lever.
3. **Coverage is the real problem.** 22 of 36 directed true contacts sit
   2.8–29.5 mm from the nearest breakline point. The breaklines are
   well-formed closed loops — they simply do not pass through the seam.
   On 5 of 9 sherds the traced loop's radial band sits *inside* its own
   surface's extent, which is what a loop closed on the wrong feature
   looks like.

**So the question narrows to: does our rim trace follow the true outer
boundary of the surface, or an interior curvature ring?** That is a
preprocessing question with a falsifiable test, and it is now the only
one left on this side of the fence.

**Two corrections to what was written earlier here:**
- The "one face per sherd, arbitrarily" finding was an artifact of
  comparing which surface file each `Breakline_0` sat on. All nine sit on
  `Surface_0`. Whether that is the inner or outer wall varies — but that
  is a property of the *segmentation's* file ordering, not a choice the
  rim tracer makes, and it is not something this ticket should have
  reported as a face-confusion defect.
- The "opposed normals" reading stays withdrawn: on same-face pairs the
  normals agree at 0.92–1.00.

- **10 of 18 true mates are inner-vs-outer**, so a 2 mm
  agreeing-normal comparison cannot see them at all. The assignment is
  also *uninformative*: 10/18 non-mate pairs are same-face too, so face
  agreement predicts nothing about a pair being real.
- **But fixing the face would not be enough.** Of the 8 same-face mates,
  only 1 (pair 6-7) has traces within 2 mm at ground truth; the rest sit
  5–30 mm from the 0.02 mm truth. On those same-face pairs the normals
  agree at **0.92–1.00 (6–23°)**, which passes the gate easily.

**This corrects an earlier reading.** The "normals are opposed 67–129°"
figure came from pair 2-9, which is an *opposite-face* pair — the opposed
normals are the signature of tracing two different wall faces, not a
separate defect in the normals themselves. The real headline is that the
extracted segment **does not span the seam**. Fix order: coverage first,
then both-faces. Both are required; neither alone suffices.

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

- [x] **Measured, not guessed:** for each of the Juglet's 9 sherds, which
      surface face (inner / outer / both) does each extracted breakline
      segment come from, and does the segment span the actual seam? A
      per-segment table, in millimetres, with the GT contact point
      marked. **Done 2026-09-26** (ticket 01): one face per sherd,
      arbitrary; 10/18 true mates opposite-face; 34.7% of points
      ambiguous; only 1/8 same-face mates within 2 mm at GT. Scripts and
      output in `../structure-from-sherds-pp/artifacts/juglet_run1/`
      (`breakline_face_*.py`, `sameface_gt_geometry.py`)
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
