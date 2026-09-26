# E1 — Do the breaklines we extract let SfS++ find any join?

**Status:** open · **Blocked by:** none · **Effort:** a measurement on existing scans, then
a change to `edgeline_extraction.cpp`

**2026-09-26, checked against the paper and the original code: this is a
real deviation, not a phantom, and it is upstream's.** `int K = 50` in
the edge-line ordering is byte-identical in `DominicoRyu/SfSpp_preprocessing`
— our fork only added empty-input guards — so nothing here was broken by
us. **But the released code does not implement what the paper specifies**
(§IV-B1, "Edge line extraction and segmentation"), in four ways:

1. The paper takes the edge line from the **interior** surface. The code
   takes `Surface_0` = the **largest cluster** with no interior/exterior
   test, and emits an edge line for both surfaces. On the authors' thin
   thrown pots "largest" probably lands on the same physical face for
   every sherd, so their results are unaffected. On the Juglet, where
   inner and outer areas are nearly equal, it lands on **different faces
   for different sherds** — which is the arbitrary face assignment, and
   why 10 of 18 true mates end up inner-vs-outer and invisible to the
   2 mm gate.
2. The paper orders edge-line points "**using their normals and a voting
   algorithm**". The code uses a nearest-neighbour chain. **That step is
   not implemented at all** — and it is precisely the step whose absence
   produces the disconnected fragments. My K=2 attempt was trying to
   repair a substitute for a method step that does not exist in the code.
3. The paper's noise/outlier filter is specified; in the code it runs and
   is then **discarded** (dead reload).
4. The paper's equidistant 1.9 mm resampling is replaced by padding to a
   fixed 200 points, which is how a 3.6 mm fragment passed as a
   full-size breakline.

**So the fix is to implement the paper's method, not to retune a
constant.** That is a better-defined and more defensible target than
"make the walk local".

**Limits, stated honestly:** the paper names the voting algorithm but
does not specify it, pointing to supplementary material this corpus does
not contain. And whether "largest cluster = interior" holds on the
authors' own 142 fragments cannot be checked from here — if it does,
this is a robustness gap exposed by the Juglet rather than an error in
their reported results.

**2026-09-26, ticket 02 patch 1 — the obvious fix was wrong, and the
wrongness is informative.** Making the rim walk local (K=2) was tested
and **refuted**: it collapsed the trace to a sub-millimetre blob
(sherd 4: 10×13×14 mm → 0.09×0.19×0.22 mm; traced length 1–15% of the
rim; closest true contact 0.17 mm → 11.74 mm). The adaptive K it replaced
was **load-bearing**: with a small K the walk's nearest unused neighbour
is almost always another member of the same tight cluster, so it crawls
and never leaves the cluster.

So the defect is not the walk's *step size* but its **input**: the
boundary cloud from `pcl::BoundaryEstimation` is duplicate-dominated,
and a nearest-neighbour chain has no notion of stepping *along* a curve.
The fix is to **cluster/dedupe the boundary cloud and then order it** (or
replace the chain with a minimum spanning tree / principal curve — which
is what the function name `_breakLineFromConcaveHull` suggests it was
meant to be), not to retune K.

> **2026-09-26 — the duplicate-domination claim above is NOT SUPPORTED and is
> withdrawn as an explanation.** Ticket 08 measured the boundary clouds of
> both pots. Every Pot_A cloud contains exact duplicates (26–124 points,
> median 54 per cloud); most Juglet clouds contain **none**. Pot_A is the pot
> that assembles 15/15 correctly. Duplicates are therefore *more* abundant in
> the working pot and cannot be what distinguishes the failing one. The
> "dedupe then order" plan (ticket 02) has lost its justification; dedupe
> remains defensible as hygiene, not as the fix.

This also confirms the trace is the binding constraint: a *worse* trace
measurably pushed the nearest true contact from 0.17 mm to 11.74 mm, so
the gate is sensitive to precisely this quantity.

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

## 2026-09-26, ticket 08 — the walk is NOT the Juglet's problem

Measured every sherd face of both pots, not one sherd: **18 Juglet faces**
(9 sherds × 2 walls) and **16 Pot_A faces** (8 × 2), by running the
pipeline in isolated trees and snapshotting `boundary.pcd` per face before
it is overwritten. Metric: **coverage** — what fraction of the boundary
points the ordering walk actually emits.

| | Juglet | Pot_A (the 15/15 control) |
|---|---|---|
| fully covered (≥0.9) | **8 / 18** | **7 / 16** |
| median coverage | 0.866 | 0.883 |
| worst coverage | 0.143 | 0.252 |

**The two pots are indistinguishable, and Pot_A assembles perfectly
anyway.** So the walk's truncation is real, general, and **not the cause of
the Juglet's zero joins** — a defect present in the pot that works cannot
explain the pot that doesn't.

This is a fourth thing, distinct from the three failure classes: **a real
defect that is not the cause of the observed failure.** The defect is real
— it discards 15–75% of an edge on half of all faces, and the paper's
ordering step genuinely is missing from the code — but the causal story
attached to it was wrong.

**What this rules out as the discriminator:** spacing variation (the
highest-spread Juglet face, 8.1×, was covered *perfectly*; the worst face
has low spread, 2.7×) and exact duplicates (more abundant in Pot_A, which
works). **We do not currently know which input property decides which faces
truncate.**

**Consequence for the plan.** Implementing the paper's ordering step
(ticket 03) stays worth doing, as an independent quality improvement, but
must **not** be credited in advance with fixing the Juglet, and must be
judged on the coverage *distribution* over all 34 faces rather than on the
Juglet's gate score.

**Where that leaves the question.** The candidates that remain for the
Juglet's zero joins are the ones already recorded here and *not* in the
ordering chain:

- **face selection** — `Surface_0` is the largest cluster with no
  interior/exterior test, and 10 of 18 true mates are inner-vs-outer
  (item 1 at the top of this file, and ticket 04);
- **the trace missing the seam** — 22 of 36 directed true contacts sit
  2.8–29.5 mm from the nearest breakline point, so the loops are
  well-formed but do not pass through the join.

The ordering work was a real defect worth fixing, and it was also a red
herring for this question. Both are true, and only one of them was assumed.

## 2026-09-26, ticket 09 — there is NO valid control on our own output

The "Pot_A 15/15" control has been the **SfS++ authors' released sample**
all along, not our pipeline's output. `data_path.h` carries two Pot_A
datasets — `POT_A` (our `NURBS_Dataset_20251103/`) and `POT_A_ORIG`
(`sfs_main/original_samples/`) — and the 15/15 came from the second.

Our own Pot_A output scores 0/15 — **and that number is unusable too.** Both
Pot_A ground-truth files are byte-identical, but our breakline bundle sits
**1881 mm away in z** from the authors', and the probe's "gaps" of
2466–3305 mm are that offset rather than any property of the curves.

**So no valid measurement of our own preprocessing existed on any pot it
should handle.** This question — *is the Juglet's 0/18 our fault or the
material's?* — therefore **could not be answered**, and the earlier
reasoning in this file that leaned on a Pot_A control was leaning on the
authors' data.

## 2026-09-26, ticket 09 resolved — the control now exists, and it fails

Re-ran the current code on Pot_A and added a `pota_fresh` arm to the gate
probe, pairing our fresh breaklines with the **authors'** ground truth —
legitimate because the fresh output is in the scan frame (breakline
centroids 0.7–2.5 mm from the mesh centroids on 6 of 8, the frame the
authors' own breaklines occupy to ~1 mm).

| arm | whose breaklines | strict pass at truth |
|---|---|---|
| `pota_orig` | authors' released sample | **15/15** |
| **`pota_fresh`** | **our current code** | **7/15** |
| `juglet` | our current code, Juglet | 0/18 |

**Our preprocessing loses 8 of 15 true joins on the pot SfS++ was developed
on.** Passing pairs sit at 0.26–1.67 mm, so this is not a frame artifact.

And the losses are not spread evenly: **all six of piece 1's pairs fail**,
plus 2-4 and 2-5. Piece 1 is the largest sherd (100 064 vertices, ~63 mm)
and the only one whose breakline centroid sits materially off its mesh
(9.1 mm). One bad sherd accounts for three quarters of the damage — a far
better target than "the method fails on this material".

**The old `pota` 0/15 is retracted as void.** Its Nov-2025 bundle has its
pieces arranged 4.5× too far apart, and the current code does not reproduce
that. It measured a stale artifact.

Consequences, stated carefully:

- The Juglet's 0/18 is *worse* than 7/15, so the Juglet is harder material
  **and** our pipeline is already substantially broken on good material.
  Two problems; do not conflate them again.
- The paper-vs-code gaps (interior-surface selection, the missing ordering
  step, the dead noise filter, padding instead of 1.9 mm resampling) are
  live work, not a theory about one pot.
- The still-open cheap fix: `main_headless.cpp:64` silently drops any sherd
  with fewer than 50 breakline points.

A second, independent defect surfaced on the way:
`main_headless.cpp:64` in the assembly repo **silently drops any sherd whose
breakline has fewer than 50 points** — no warning — and our Pot_A bundle
already has two (pieces 6 and 8, 30 points each). On Pot_A the assembler
would quietly assemble from 6 of 8 sherds.

Priority order is therefore inverted from what this file assumed: establish
the frame convention and get a control that *can* fail, before improving
anything. See ticket 09.

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
