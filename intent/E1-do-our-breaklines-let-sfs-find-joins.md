# E1 — Do the breaklines we extract let SfS++ find any join?

**Status:** open · **Blocked by:** none · **Effort:** a measurement on existing scans, then
a change to `edgeline_extraction.cpp`

**2026-09-26, checked against the paper and the original code: this is a
real deviation, not a phantom, and it is upstream's.** `int K = 50` in
the edge-line ordering is byte-identical in `DominicoRyu/SfSpp_preprocessing`
— our fork only added empty-input guards — so nothing here was broken by
us. **But the released code does not implement what the paper specifies**
(§IV-B1, "Edge line extraction and segmentation"), in four ways:

1. The paper takes the edge line from the **interior** surface, selected
   as one of the **two largest clusters** and then classified by the
   ray-axis test. The code selected the two largest clusters correctly
   (`mesh_processing_headless.cpp:1799-1800`) but **skipped the
   classification entirely** — no interior/exterior test — and emitted an
   edge line for both surfaces. (An earlier version of this file said the
   code "takes the largest cluster where the paper takes the interior
   surface." That was wrong — see ticket 16. The paper does exactly the
   largest-two selection; the missing step was classification only.) On the
   authors' thin thrown pots the unclassified order probably keeps the same
   physical face first on every sherd, so their results are unaffected. On
   the Juglet, where inner and outer areas are nearly equal, the file order
   lands on **different faces for different sherds** — which is the
   arbitrary face assignment, and why 10 of 18 true mates end up
   inner-vs-outer and invisible to the 2 mm gate. Ticket 04 now classifies
   per sherd; Pot_A went 7/15 → 11/15 on that step.
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
not contain. And whether the authors' own 142 fragments always classify
the same way ours do cannot be checked from here — if they do, the Juglet
exposes a robustness gap rather than an error in their reported results.
(Corrected 2026-09-29 per ticket 16: the old wording here, "largest cluster
= interior", misdescribed both sides — the paper selects the two largest
and then classifies, and so do we now.)

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

## Where it stands

Our break-line tracing passes all 15 checks on the reference pot (Pot A). On the Juglet,
none of the 5 touching pairs that can be measured passes, and 5 more cannot be measured.
Sherds 3 and 9 produce no usable break surfaces at all, and loosening the settings did
not bring them back. This looks like the tracing failing on this pot, not SfS++.

Weight: one reference pot passing, one real pot failing.
Next: the end-to-end run (ticket 07), then why sherds 3 and 9 give nothing.

**2026-10-15 — untouched-upstream check (lead-run, task-1–3): the released
preprocessing does not regenerate the authors' own Pot A inputs.**
Unmodified upstream (DominicoRyu @ `d5ee6865`, fresh headless container,
zero source shims) on the authors' Pot A scans: piece 1 correct (0.52 mm),
pieces 2–8 shifted +1.8–3.5 mm upward in Z with matching point counts; the
shift is already in the fresh surfaces, so edge tracing is faithful to bad
input. Two blockers: fresh edge files lack the `#` segment headers the
untouched reader requires (0 of 8 load; only our fork writes headers), and
the MATLAB axis program is incomplete as released (missing loader,
Windows-only paths, a dimension error on current MATLAB, a 59-line
refinement file existing only in our fork — axes leg closed as a
documented gap). Fresh-vs-authors gate 6/15; untouched assembly on the
fresh bundle places nothing while the ORIG arm in the same job scores
8/8 + 15/15. This is the method genuinely failing (case 1), not the ruler
or the reference. Consequence for this question: no bundle from any code
we can honestly call the authors' passes the acceptance gate — the
acceptance test below remains open, and the "Pot_A is not regressed"
criterion now cuts the other way (our patched pipeline reached 15/15 on
11–15 pairs; the released code reaches 0 loadable edges). Evidence:
`artifacts/untouched_pota_verify_20261015/` (`TASK3_EVIDENCE.md`,
`SHIM_CHANGES.md`, `HANDOFF_TASK3.md`); staged view
`structure-from-sherds-pp/artifacts/visual-qa/task3_fresh_vs_orig/`.

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

- **face selection** — the two surfaces were emitted unclassified (the
  two-largest selection itself matches the paper; the missing
  classification did not — ticket 16), and 10 of 18 true mates are
  inner-vs-outer (item 1 at the top of this file, and ticket 04);
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

> **Corrected 2026-09-27.** The paragraph above is wrong about piece 1, and
> the correction matters more than the original claim. Comparing our curve
> against **the authors' curve for the same sherd in the same frame** — the
> comparison this project had never made — shows piece 1 is the **best**
> piece we produce: 0.69 mm median from the reference, 100% of its points
> inside the 2 mm gate tolerance, 98% of the reference's traced length. Its
> 9.1 mm centroid offset is 5% of its own 174 mm diagonal, which is better
> than most; piece 2 is proportionally worse. Piece 1's six failures are
> caused by its *partners*.
>
> **The dominant defect is a systematic ~3.5 mm displacement.** Six of eight
> of our curves sit 2.99–3.77 mm from the reference, displaced in *both*
> directions, with traced lengths matching to 2–9%. A tight, near-constant
> displacement at unchanged length is the same curve on a **parallel surface
> about 3.5 mm away** — not a truncated walk. Against a 2 mm gate that fails
> every comparison it touches, and a pair survives only when two sherds'
> offsets happen to cancel. This is consistent with the interior/exterior
> wall question already recorded in this file, and it points at ticket 04
> rather than at the ordering work.
>
> Piece 2 alone carries the ordering defect: 46% of the reference's traced
> length, reverse distance to 80 mm. So the walk accounts for roughly one
> sherd of eight here, not eight of fifteen lost joins.
>
> **Not yet tested:** whether the 3.5 mm displacement runs along the surface
> normal. That is the discriminating measurement between "the other wall
> face" and "a different feature", and it decides whether ticket 04 is the
> fix.

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

## 2026-09-27 — the denominators measured, and Pot_A's losses are ours

Placed each true pair at ground truth and measured the **real
surface-to-surface gap, no breakline involved**
(`structure-from-sherds-pp/artifacts/juglet_run1/real_gap_at_truth.py`):

| | true pairs | genuinely touch | median gap | our score | honest denominator |
|---|---|---|---|---|---|
| Juglet | 18 | **10** | 0.34 mm | 0/18 | **0/10** |
| Pot_A | 15 | **15** | 0.06 mm | 7/15 | **7/15** |

**The Juglet's honest denominator is 10.** Eight pairs stand off by
**3.5–19 mm of empty space** (1-5, 1-6, 3-7, 4-5, 4-6, 5-9, 7-8, 8-9). No
extraction can pass a 2 mm gate on them, because there is nothing there to
trace. On an eroded surface that is a material limit rather than a method
failure — and the conservator's judgement that eroded sherds do not touch
and may have sizeable gaps is what predicted it.

**And the "Pot_A 15/15 control" is gone for good, in the other direction.**
Our own output has never scored 15/15. It scores **7/15**, and because all
15 of Pot_A's pairs genuinely touch, at 0.02–0.12 mm, **all 8 of those
losses are ours.** Pot_A is the clean target: the gate is fair for every
pair and there is no material excuse. Any claim of "no regression against
Pot_A at 15/15" was measuring the authors' data — twice over.

**Located, on Pot_A, and it is neither the walk nor the face choice.**
Comparing our curve with the authors' for the same sherd in the same frame:
six of eight sit **2.99–3.77 mm off**, displaced **tangentially** — not
along the surface normal, so not the other wall — with the same loop size
(radius ratio 1.03) and the same traced length, the offset running the whole
way round. Rendered and inspected: piece 1 (0.69 mm) shows the curves
overdrawing around the entire rim; piece 3 shows two distinct parallel
curves 3.5–5.6 mm apart. The ordering walk is implicated on one sherd of
eight (piece 2, 46% of the reference length) and is not the main damage.

So the open question is now specific and falsifiable: **what puts the rim
about 3.5 mm to one side of the reference, consistently, on six of eight
sherds?** That is where effort belongs — not the ordering rewrite
(ticket 03, demoted) and not the face selection (ticket 04, whose premise
this contradicts on Pot_A).

## 2026-09-28 — ticket 04 resolved: the pipeline selects per sherd, 7/15 → 11/15

Implemented the paper's ray-vs-axis interior/exterior test as a
dependency-free unit (`surface_classify.{h,cpp}`) with 5 passing CTest
entries, wired into the edgeline loop: when `Surface_1` wins the vote the
two inputs are exchanged so `Breakline_0` comes from the interior wall.
No axis file → warns and keeps historic order.

Pot_A, verified by `cmp` per piece (the first version of the exchange
logged success while copying each file onto itself — caught by
byte-comparison, fixed with post-write verification): piece 1 kept on
`Surface_0` (820 vs 225), pieces 2–8 exchanged with large margins except
piece 2 (403 vs 280, weak — the ambiguous sherd).

Gate: **11/15**. The five piece-1 pairs recovered at 0.16–1.24 mm. All four
remaining failures contain piece 2, whose rim is 46% of the reference —
the ordering defect, now the only thing between us and 15/15 on this pot.

Two defects, one fixed, one characterized: wall selection (5 pairs, done —
pipeline at 11/15) and piece 2 (4 pairs). Ticket 03 investigated piece 2
fully and closed it as unfixable by any measured intervention: its boundary
clouds touch the reference along one 17-point arc (S0) and in scattered
runs (S1, ref coverage 36%), so no ordering/pruning/filter/hull/radius
recovers the 303mm rim — eight interventions tried, each with its failing
numbers on record. Where its curves do meet the neighbours (1-2 at 0.45mm),
normals oppose at max 0.488 over the whole rim while agreeing with its own
mesh at +0.997: real geometry, no sign flip available. The four piece-2
pairs are not recoverable without a boundary-detection investigation this
chain did not open.

## 2026-09-28 — vote guards, and piece 2's surfaces measured

The vote picked a **171-point scrap 45mm from the fracture** over an
11,263-point surface covering 82% of the reference (piece 2, margin 403 vs
280 — weakest of the eight). Ticket 04 now guards: an S1 win stands only
with ≥10% of S0's size and margin ≥2.0 (separations 0.015 vs 0.80–0.96 and
1.44 vs ~3.6–30; both provisional). Prediction on record: pipeline
reproduces the mixed 11/15.

Deeper: piece 2's **unclustered points cover 100% of the reference at
0.53mm median**, and 18% of it is covered ONLY there, not by S0. The
fracture zone sits in the points region-growing refused. So the future fix
for piece 2 starts with S0 + unclustered as the rim source — never S1, and
never S0 alone. Ticket 03 carries the pointer; ticket 12 carries the
smoothness context (default optimal, both directions hurt or crash).

Ticket 04's guard (an S1 win stands only with ≥10% of S0's size and margin
≥2.0) ran in the pipeline: audit by `cmp` shows 01 KEPT, 02 KEPT via guard
rejection, 03–08 EXCHANGED. Gate (`t04_interior` arm): **11/15**, failing
exactly **1-2, 2-4, 2-5, 2-8** — the set predicted before the run. The five
piece-1 pairs recovered at 0.16–1.24 mm.

Defect 1 is implemented, not demonstrated. Defect 2 (piece 2) refined by
ticket 03: its boundary clouds cover 10%/36% of the reference while its
Surface_0 covers 82% — so the rim is lost between surface and boundary
cloud, i.e. a boundary-*detection* failure on this sherd, not an ordering
one. The four piece-2 pairs are not recoverable without mapping those
stages, which is new work outside this chain's ordering scope.

## 2026-09-28 — pipeline 15/15: defect 1 implemented, defect 2 routed

Our preprocessing now scores **15/15** on Pot_A from the pipeline itself
(`t14_patches` arm — mesh with tol-1.5 + persist, edgeline with vote +
guards + patch appends, no hand assembly). Per-pair movement: 1-2
22.94→0.20mm, 2-4 18.78→0.81, 2-5 14.43→0.31, 2-8 38.20→0.20. All eleven
previously-passing pairs still pass.

Caveats on record in ticket 14: 1-2 passes thin (2 strict inliers — the
most fragile join, first place to look on any regression); 2-8 rides on
piece 8's wall rim which emitted no patch rims. The Juglet (0/10 honest,
8 pairs standing 3.5–19mm apart) is unchanged: material limit, not method.

## 2026-09-28 — decorative rim routed by hand: 12/15, 1-2 recovers

Persisted piece 2's decorative rim (110 pts, previously computed and
dropped), enriched with mesh normals as the assembler does, scored through
the probe with t04 partners fixed: **1-2 passes, 13 strict inliers at
0.56mm**. Overall **12/15**, failing only 2-4/2-5/2-8 on distance. The
pipeline routing change (persist + wire into the breakline) is demonstrated
worthwhile (+1 measured) but not yet implemented — ticket 14.

## 2026-09-29 — paper-compliance write-up pass closed two tickets

Ticket 02 (rim criteria): paper test vs recorded flags agree 60–5, all
five disagreements on the authors' own files — cosmetic, nothing to
implement. Ticket 04 (region params): accepted with justification, no code
change — the ticket-12 sweep shows the default optimal. Neither moves any
gate number; both stop the next audit from re-reporting them.

## 2026-09-28 — tickets brought current with the 15/15 result

Status sweep, no new measurements: 01 resolved (seam delivered; ordering
code restored byte-identical after the reverted experiment); 09 resolved
(control passes on our output); 10 resolved (offset exonerated); 11 closed
as withdrawn (circular measure); 12 closed (premise wrong; tolerance
changed under 14 for separate measured reason); 13 resolved (collapse
named); 15 resolved (split loses, fit preserves, sample stable); 04 and 14
resolved (pipeline 15/15); 07 in-progress (Pot_A half met genuinely,
Juglet half untouched). Tickets 02/05/06 stay open as paper-compliance
work, explicitly not gate remedies.

## 2026-09-29 — Juglet axes found and staged; vote can fire there now

All 9 Juglet axes existed in `Juglet_Dataset_20260916/` (an early shallow
`find` wrongly reported 4/9) and are now staged at `Dataset/Axes/Juglet/`.
Ticket 04/07/16 updated; the MATLAB *method* remains unaudited, and the
assembler's file-vs-computed axis precedence untraced. Next: run the Juglet
with the vote live.

## 2026-09-30 — ticket 17: the Juglet gate was measured on corrupted data; re-measured clean

The first Juglet vote run crashed partway (SIGABRT, exit 134) and, worse,
silently corrupted: pieces 3 and 9 carried pieces 2 and 8's surfaces
**byte-identically** (`cmp`/md5) through surfaces into breaklines. Mechanism,
read from the code: `tmpSurfaceCluster_*.ply` are fixed filenames in the
shared intermediate dir; the single-cluster branch `break`s out of the
retry loop writing nothing, and the per-piece exists-check copy then
inherits the previous piece's files. Alphabetical order picked exactly the
observed pairs. The old 0/10 honest score is **retracted, not compared**.

Fix (three small changes, one bug): stale temps deleted per piece (inherit
→ loud missing), premature `break` removed (retry loop loosens to 45° as
evidently intended), missing surfaces skip loudly in both stages instead of
aborting/asserting. Verified: 7 genuine + 2 loud skips, zero copies, both
stages complete.

Outcome against hope: loosening did NOT recover pieces 3 and 9 (one cluster
after 30 retries each) — they skip, and 5 touching pairs are unmeasurable
until someone decides what a single-cluster sherd should produce. Clean
Juglet state: **0 of 5 scorable touching pairs pass, 5 unmeasurable**.
Pot_A re-measured per pair IDENTICAL to the 15/15 baseline (header line
excepted); authors' arm still 15/15; vote/guard pattern unchanged. The
question stays open; the ruler is now clean.

## 2026-09-30 — paper-compliance 03 closed: merging converges trivially

`mergeClusters` now iterates to convergence (cap 10, per-pass log).
Second pass merges nothing on any segmentation attempt of either pot (13
Juglet attempts, all `pass 1: 0 merges`; Pot_A gate per-pair identical at
15/15; Juglet 0/5 scorable unchanged). Single-pass ≡ convergence on all
observed data. Cosmetic-close with counts; the loop stays as the paper's
stated behavior.

## 2026-09-30 — paper-compliance 05 closed: the noise filter is live

The dead reload is deleted; the filter output is what gets ordered
(shared seam, unit test 6/6). Pot_A 15/15 with per-pair inliers moved but
all passing; Juglet 0/5 scorable unchanged. As the ticket predicted, no
gate movement — the value is that the code now does what the method says,
under test.

## 2026-09-30 — paper-compliance 06 closed: 1.9mm resampling live, 15/15 held

Clamp fiction gone (files carry 8–32 honest points on the Juglet);
Pot_A holds 15/15; Juglet 0/5 unmoved. The change exposed a hardcoded
K=20 loop that segfaulted on 12-point rims — bounded by found count,
confirmed by a completing rerun. Short rims (2: 9pts, 7: 8pts) now sit
below the assembler's 50-point threshold, where they fail loudly instead
of passing silently.

## 2026-09-30 — paper-compliance 01 closed as removal, not emission

The spike proved populating `Surface_F` would change zero executed
instructions (sole consumer `IcpFine` has no callers), so the ticket
converted to dead-expectation removal, implemented assembly-side: both
unconditional 3-arg loads now 2-arg, `IcpFine` refuses empty frac loudly,
in-container rebuild clean. No such files exist in either dataset; nothing
that runs changes. Emission would have been pure cost.

## 2026-09-30 — audit inputs closed: MATLAB axis method matches; ordering vote explicitly declined

- The MATLAB axis extraction is paper-plausible end to end (6-pt Pottmann
  solver, biaxial Cao error, LM refinement, multi-candidate dedup). It
  uses both unclassified file-order surfaces where line 149 says inner —
  immaterial given the sign-robust metric. The Juglet's near-tie votes are
  material indeterminacy, not a broken axis. Last unaudited vote input
  closed (ticket 16 addendum, md5-pinned).
- The paper's ordering vote stays unimplemented by explicit decision: the
  algorithm is unspecified in the corpus, Pot_A is 15/15 without it, and
  implementing it would be invention risking the working pot. Reopen
  conditions recorded in ticket 16.

## 2026-10-01 — `pota_12` witnessed: thinnest pass genuine, plus new finding

Pair 1-2 confirmed belonging together by the eye; red on seam with gaps
as measured. New: piece 2's `Breakline_0` carries a 38mm face-crossing
trace (seg 24-44, ≤0.93mm on mesh, up to 15.9mm off the wall rim) —
likely appended decorative content, invisible to the gate, filed as
ticket 18. The only known false-positive surface in a passing bundle.

## 2026-10-02 — ticket 18 refuted: the lines are true 2-8 seams, look was context-limited

Piece 2's small segments sit below the 30-pt append floor (not appends)
and 0.07–0.13mm from piece 8's mesh (true seam traces). Lesson: single-pair
looks hide other-seam content — future looks state which seams are out of
frame. Agent's append-inference retracted in the ticket.

## 2026-09-28 — ticket 11 withdrawn: there is no 1.2 mm outward offset in our rims

Ticket 11 claimed our traced rims sit about 1.2 mm further out than the authors' on six
of eight Pot A sherds. That was the ruler, not the rims: each rim's radius was measured
from its own centroid, which is circular. Measured directly against the mesh, both sit on
it (ours 0.02 mm, the authors' 0.00 mm). It rules nothing in or out for E1; it only
removes a defect that never existed. `.scratch/juglet-breaklines/issues/11-the-1p2mm-outward-bias.md`

## 2026-10-15 — pota-repro 13: piece 2's rim recovered, gate 15/15, reassembly 7/8

Piece 2's missing rim was a truncated walk, not missing geometry: the
greedy ordering walk stalls at the first boundary component (183 input
points → 45 sequenced, 141 mm of a ~300 mm rim), and the assembler's
silent 50-point minimum drops the 48-point stub with no log line. Fix
(SFS-T13, `original_nurbs_preprocessing/edge_line_ordering.cpp`): when
sequenced/input coverage falls below 0.40, keep walking with jumps to the
nearest unvisited input. The threshold fires on exactly 1 of 16 Pot_A
wall surfaces; the other 7 pieces' rims are byte-identical. Render
checked by the lead: the fixed rim follows the authors' reference loop
at the same millimetre scale (179 pts, 450 mm traced incl. 4 jump chords
vs authors' 169 pts / 302 mm).

Numbers (same-binary authors' arm alongside, all jobs clean): piece 2
loads; gate **15/15** on the patched arm; end-to-end best **7/8 + 11/15**
— pieces 1, 3–8 seat perfectly, piece 2 seats 120° off or unseated, and
any patch content poisons the search (forest 441 vs 257). True piece-2
matches exist at the gate (4–21 strict inliers) but the beam will not
take them. Verdict class: the measurement is now right and the remaining
failure is the method's search, not our rims — the blocker moved from
rims to search, with piece 2's mesh-stage exterior wall (a 171-point
scrap vs the authors' ~12k-point wall) as the last known-missing input.
Ticket: `.scratch/pota-repro/issues/13-piece2-rim-fix.md`.

Weight: one pot, eight sherds, single runs — the direction (rims now
sufficient, search now the limit) is solid; sizes of any claimed fix
need more pots before they conclude anything.

## 2026-10-16 — pota-repro 10: the finder generalises partially, 117/155 across B–J

The frozen GM-refine axle finder ran unmodified over pots B–J (155
pieces, 12 compute jobs, all clean): **117 of 155 pieces (75%) point
within 5° of the shipped reference axles, with zero tuning.**
Single-axle wall pieces pass nearly everywhere (pot G 7/7, pot D's
first 16 pieces 16/16, pot I's first 15 pieces 15/15). The misses fall
in the two failure families Pot A already taught us (multi-axle pieces
where the peel seats too few modes; pockets where the cost landscape
prefers a wrong axle) plus one new family: **pot H collapses at 1/11**
— small fragments carrying up to 6 axles each, where the finder often
returns nothing at all. Verdict class: the method genuinely works on
single-axle walls across nine new pots and genuinely fails on small
multi-axle fragments — the next work is per-family repair (H first),
not the end-to-end gate yet. Ticket:
`.scratch/pota-repro/issues/10-axle-generalise.md`.

Weight: nine pots, 155 pieces, single runs — the 75% direction is solid
as a direction; per-family rates need repeat runs before they conclude
anything.

## 2026-10-16 — pota-repro 17: Pot H diagnosed — base caps under the support floor

Pot H is not "too small": its biggest piece dwarfs passing fragments
elsewhere. Its collapse is three proven effects stacked: four pieces
are base-cap geometry (surface normals facing along the axle, fragments
touching it — a shape the wall-tuned vote cannot see, with hundreds of
singular-math warnings as the symptom); every true axle in the pot owns
only 6–17% of its fragment's points, under the finder's 10% support
floor (even a perfect oracle proposing the truth gets rejected); and on
multi-axle pieces the vote splits and the pruning kills the survivors.
The passing piece survived by 8 thousandths of support share — luck, not
margin. Deliverable: an admission test, not a fix — the finder refuses
a fragment when its own vote cost runs hot AND its round-1 winner owns
under a fifth of the points (both observable without the answer key).
Thresholds provisional, confirmed on all nine pots by the follow-up.
Ticket: `.scratch/pota-repro/issues/17-poth-diagnosis.md`.

Weight: one pot (11 pieces) for the mechanism, nine pots for the
threshold calibration to come — the stack is solid; the gate numbers
await the follow-up.

## 2026-10-16 — pota-repro 18: refusal gate shipped, H3 eye-confirmed

The admission test is in and frozen: the finder refuses a fragment
when its own best vote costs more than 1.40 per point AND its round-1
winner owns under 22% of the points — both visible without the answer
key. The one allowed threshold move (share 0.20 → 0.22) bought one more
caught failure at zero new false refusals; the matrix after: all 11
H pieces refused, 3 passing pieces wrongly refused out of 117, and the
remaining failures (tails, counts, landscapes) proven unreachable on
these two statistics — they show healthy round-1 support, so they need
a different signal, not a looser gate. The lead looked at all four base
renders: foot-ring arcs, a domed cap, flat plates, each pierced straight
through by the shipped axis — base caps, claim closed. Ticket:
`.scratch/pota-repro/issues/18-refusal-gate.md`.

Weight: 155 pieces across nine pots for the gate; four renders for the
geometry. The 75% that passes plus the refusals are now the admitted
set the end-to-end proof runs on.

## 2026-10-16 — pota-repro 19: end-to-end 7/8 + 11/15, piece 2 the last one standing

Our rims plus our axles through the untouched assembly program: seven
of eight pieces seat within a degree and a few millimetres of the
authors' own seatings, and the authors' arm alongside reproduced its
perfect score exactly, so the run counts. The eighth piece flings
itself 103° off — visible on the render as one orange arc escaping an
otherwise closed ring — and the second-chance rim repair changes
nothing about it except poisoning the search further (measured three
times now, so that repair stays out of the seating path). The refusal
gate admits all eight, correctly: it judges axles, and this piece's
axle is fine — its rim is short, which the gate cannot see. One
suspect order for the follow-up: the wall the mesh stage builds for
this piece, then the search's taste for the wrong seating. Ticket:
`.scratch/pota-repro/issues/19-admitted-e2e.md`.

Weight: one full assembly job with both arms inside it, plus the
render the lead checked. Pot A is one piece away from perfect.

## 2026-10-16 — pota-repro 20: the search is innocent, our wall is missing

The swap test acquitted the search: the authors' piece-2 rim dropped
into our bundle seats perfectly four times out of four, while our own
rim never seats strictly in five attempts. Point by point, the input
meshes are byte-identical — yet where the authors have a wall, we
have a 171-point scrap floating 3mm off, and our rim walk follows the
scrap instead of the wall. The wall is lost downstream of the mesh,
upstream of the rim walk; the two existing leads point at the surface
labelling. A measurement lesson came free: the loose scoreboard
reports "perfect" with the piece visibly 10° adrift, so from here the
strict bar is the only acceptance. Ticket:
`.scratch/pota-repro/issues/20-piece2-endgame.md`.

Weight: two multi-arm assembly jobs with valid controls, plus the
three-panel render the lead checked — closed vessel, escaped piece,
seated swap.

## 2026-10-16 — pota-repro 21: wall recovered and committed; the search is the remaining fight

The missing wall is back: where one file held two fused sheets, each
wall now has its own file — the cross-section render shows it cleanly
— and the rim gate reads 15/15 with the authors' control valid beside
it. That fix is committed. But the seating run refused to follow:
whether the piece offers a stub, a patched rim, or the full true
wall, the search parks it at the same wrong pose and drags four
neighbours with it as a rigid block. More truth in, worse out — so
the fault changed address from the extraction stage to the search,
and the earlier acquittal is narrowed to what it actually tested (the
authors' rim, not ours). Two hazards were found along the way and left
untouched for their own tickets: a filename bug that silently wipes
multi-pass pieces, and a mesh stage that rolls dice run to run. Ticket:
`.scratch/pota-repro/issues/21-piece2-wall-recovery.md`.

Weight: gate plus control for the fix; a three-way controlled
comparison for the search verdict; the lead checked the slice render.

## 2026-10-16 — pota-repro 22: the beam wants the truth; three gates won't let it

The search-side diagnosis is complete and honest about its limit:
reproduced inside a single bundle, the beam's own scoring prefers the
true seating by a wide margin — but three gates veto true candidates
before selection. Two were relaxed with the authors' control holding
perfect throughout (one even seated an extra piece correctly on clean
rims). The third gate checks the fragment's profile shape, and it
stands on rim content: our rim still follows the old merged wall, so
the gate is right to object and gutting it would be destroying the
test instead of passing it. The cure is prescribed, not guessed: a
rim that follows the recovered wall, run through the two validated
relaxations. The other worker's hazard fixes were found mid-flight in
the shared files and left strictly alone for its own landing. Ticket:
`.scratch/pota-repro/issues/22-beam-attractor.md`.

Weight: four assembly jobs with valid controls, rim-centroid
instrumentation proving the binding gate, identical-pose reproduction
from different rim content.

## 2026-10-16 — pota-repro 23: two hazards defused, the pipeline rolls no dice

Both traps are closed. The filename bug that silently wiped multi-pass
pieces is gone — the trigger case now stages its surfaces, zero
strays. And the run-to-run dice roll is over: three unseeded random
draws fixed, plus a family of uninitialized curvature values found by
bisection (live scoring noise through the assembler's curvature check,
now computing the same formula as the wall path) — the final proof is
full-tree byte-identity across reruns, all sixteen rims identical.
Nothing regressed: the authors' control holds perfect, the gate holds
15/15, the seating numbers sit exactly in the known shortfall band the
search-side ticket owns. The diffs were reviewed line by line before
landing. Ticket:
`.scratch/pota-repro/issues/23-pipeline-landmines.md`.

Weight: trigger-plus-fix proofs per hazard, byte-identity reruns, two
valid controls. Every future bundle comparison now measures signal.

## 2026-10-16 — pota-repro 24: the attractor cured, two pieces left

The cure test moved the seating from three pieces to six — and, more
importantly, the wrong pose is gone: the piece sits 1.85° from the
authors' seating. The surprise was where the poison lived: the rim
walk itself was good all along (matching the authors' wall point for
point); the damage came from 575 decorative-groove points stapled on
afterwards with jumps up to 107mm. Skipping that append for the piece
fixed the rim. What remains is one unplaced piece and one flipped
nearly backwards, both held by the profile-shape gate — and the open
question is whether the true seatings are vetoed or merely outscored,
which needs finer instrumentation before anyone touches the gate. Per
the ticket's own rules, with the bar unmet, nothing lands yet: the rim
fix and both relaxations wait for the veto fix as one set. The lead
checked the render: six in the ring, one gap, one flung. Ticket:
`.scratch/pota-repro/issues/24-clean-rim-rerun.md`.

Weight: one cure job with a valid control, composition checks proving
the walk innocent and the append guilty, veto evidence with scores.

## 2026-10-16 — pota-repro 25: starved, not vetoed — and the gate stays

The instrumentation answered the open question decisively: neither
remaining piece is vetoed — no true seating ever reaches the judging
stage at all. Loosening the profile gate would have seated a
higher-scoring wrong answer, so the gate stays authoritative and the
veto-fix line of attack is closed. The hunt moves one stage earlier,
to where pairs of edges first propose candidates: one pair shows the
same support as the authors' run but its true candidates die on the
axis test, and the other piece joins through pairs nobody
instrumented. A past record was corrected along the way — the
"vetoed fully-true assembly" was never fully true. The lead checked
the render: closed vessel beside a ring with a gap and a flung piece.
Ticket: `.scratch/pota-repro/issues/25-remaining-vetoes.md`.

Weight: all-piece centroid instrumentation with a validated
systematic, same-job control, corrected record.

## 2026-10-16 — pota-repro 26: the points are right; their order is scrambled

The pairwise hunt ended back where the rims are made. The candidate
stage is exonerated — true edges survive it. What kills them is an
overlap test deleting 323 of ours against 5 of the authors', and the
port proves why: at the true seating our overlap areas run 30–250×
the authors'. The points agree to under a millimetre — it is their
order along the loop that is scrambled, with jumps up to 93mm where
the authors never exceed 5. The render shows it at a glance: our loop
stitched with red leaps, theirs a clean closed ring. No search
threshold can separate true areas that large from false, so forcing
the gate would repeat the earlier trap in reverse — the fix belongs
in the rim walk, piece by piece, the same pattern that cured the last
one. The staged set waits: four fixes, one strict pass. Ticket:
`.scratch/pota-repro/issues/26-rp-starvation.md`.

Weight: two jobs with valid controls, a faithful port of the overlap
check, the teleport render the lead checked.

## 2026-10-16 — pota-repro 27: the cure — 8/8 + 15/15, and the frame question settled

The seating is complete: all eight pieces, all fifteen joins, on every
bar the arc agreed — the gate 15/15, the binary board 8/8 + 15/15, and
all fifteen joins within tolerance. The fix was the same pattern as
the last one: the walk innocent, the decorative append guilty, now for
three pieces at once. The one dissenting gauge read zero because the
whole vessel sits turned 91° in its frame — and the overlay proves it
is only the frame: one rigid motion brings all eight pieces onto the
authors' seating within two-thirds of a millimetre, and all but one
non-scoring pair agree independently of any frame. The lead accepts
this: a reassembly with no absolute anchor may choose its frame; what
must match is the shape, and the shape matches. The fixes live in
experiment copies, so the results land now and the sources follow
through a port-and-reproduce ticket before anything is called done.
Ticket: `.scratch/pota-repro/issues/27-rim-ordering.md`.

Weight: one cure job with a valid control, teleport counts to zero on
all four pieces, three renders the lead checked.

## 2026-10-17 — pota-repro 43: the beam's math, and two rulers that lied

The beam was opened up and its scoring written down exactly: each
candidate is ranked by outline length times matched points, and our
piece-2 collapses on both — eight candidate joins instead of
nineteen, each three times weaker, and its most important join has
no candidates at all. Widening the beam and reseating piece-2 first
change nothing; a length-normalized ranking moved things once and
never again. Piece-2 starves in ten runs out of ten — deterministic.
Two measuring instruments also lied and are now corrected: the
printed join count truncates (three real joins printed as two), and
identical runs can split on last-bit arithmetic noise (suspected
uninitialized memory — hunt open, half a day). The beam rewards
only genuine overlap content, so the next attempt grows piece-2's
true outline from the wall face (ticket 44); a scoring change is
held in reserve.

Weight: nine sacct-verified runs, controls green throughout, the
noise proven on identical binaries.

## 2026-10-17 — pota-repro 44: piece-2 seated — and why the win comes with an asterisk

Giving piece-2 back its missing lower outline seats it on all three
true joins, three runs out of three, with every control green — Pot B
fresh now scores full marks alongside the authors' data, the first
pot to do so. An honest failure came first: walking the wall face
for the lip diverged up to 34 mm — the face is surface, not outline.
But the winning outline was traced from the authors' own reference
piece, not discovered in our data — so this proves the beam seats
piece-2 *given* the outline (sufficiency), not that our chain finds
it. Landing it as proof, with the asterisk on the record; the real
fix — finding that outline without the reference — is ticket 45.

Weight: three identical same-binary runs, all controls green,
render eye-checked; the asterisk is the finding, not a footnote.

## 2026-10-17 — pota-repro 46: the author's recipe, read off their data

Comparing the authors' finished outlines against ours, piece by
piece across all pots, revealed their recipe: evenly spaced points
every 1.8 mm, no jumps, no decoration — and one flag our chain
never sets, which marks mouth and base arcs so the matcher ignores
them. Without that flag our outlines feed the matcher ten times
the candidates on some pots, drowning the true joins. That single
missing flag is now the prime suspect for every pot at once, and
emitting it is ticket 47. The same comparison exonerated our
surfaces for piece-2: its missing outline points are sitting in our
data — the outline walk drops them, which is ticket 45's hunt.

Weight: 620-row fingerprint table, laptop-side analysis, no code
touched; the flag mechanism verified in the assembler's own code.

## 2026-10-17 — pota-repro 45: the lip was ours all along — but geometry isn't agreement

Piece-2's missing outline was sitting in our own data, filed in a
second outline the assembler never reads. Recovering it honestly —
no reference points — lifted the outline-to-outline scores most of
the way to the reference-traced version. Yet the assembly still
refuses piece-2, three runs out of three. The measured reason: the
matcher compares smoothed derivative runs, not raw shapes, and our
honest outline's strongest agreement scores half what the beam's
frontier demands. Right shape, wrong signature. Closing that last
gap — the same shape in a signature the matcher accepts — is
ticket 48.

Weight: five sacct-verified jobs, full controls green throughout,
render eye-checked; the negative end-to-end honestly recorded.

## 2026-10-17 — pota-repro 47: the missing labels were the lever

Stamping our outlines with the authors' mouth-and-base marks the
paper's own way — steady height and radius, gentle change,
twenty points minimum — lifted Pot B from four sherds to seven,
three identical runs, every control green. The forest of false
candidates thinned by a quarter. Recall is honestly short: eight of
our outlines hold no arc steady enough to earn the mark, including
three near-misses the rule keeps unmarked. Both renders eye-checked:
our marked arc sits on the mouth where the authors' does, and the
seated ring tracks the true ring with two sherds off. Chasing the
rest — a forgiving threshold, named identities, cleaner outline
content — is ticket 49.

Weight: three identical same-binary runs, paper-recipe flagger
validated 17/18 against the authors' own marks, full controls.

## 2026-10-17 — pota-repro 48: walking the right way, still too quiet

Smoothing our honest piece-2 outline to the authors' even pace
changed nothing — the pace was never the problem. But walking it in
the authors' direction, mirroring how they travel the surface,
coaxed out the first genuine piece-2-to-1 match ever, identical on
three runs. It is real and far too weak: one thin match where the
authors' data brings five strong ones, so the beam still starves.
Both renders eye-checked: the new branches ride the mating outlines
with a clean step, no leaps. What remains is the walk itself — the
descending branch is eleven lonely points, detached — so ticket 50
re-walks the real surface.

Weight: six sacct-verified jobs, zero author points anywhere,
controls green in every run, renders eye-checked.

## 2026-10-17 — pota-repro 49: eight of nine, with names

Loosening the authors' twenty-point minimum to ten recovered three
true mouth arcs — verified point-for-point against the authors' own
data — and the seventh sherd clicked into the ring along the
contacts they enabled. Eight of nine seated, twice in three runs,
every control green, both renders eye-checked: the baseline shows
the seventh sherd adrift across the interior, the relaxed run seats
it on the true rim with only the eighth still floating. The losers
taught as much: re-smoothing our outlines to the authors' even pace
wrecked the score — the matcher reads the raw sampling itself, so
the pace is signal, not noise. The last miss is a contact with no
measurable grip at the true seating; blaming or saving it is
ticket 51's job, matcher-side.

Weight: six sacct-verified jobs, identities extracted per run,
resample rejection measured not asserted.

## 2026-10-17 — pota-repro 50: the surface has no more to give

Re-walking our whole piece-2 surface ridge by ridge found nothing
more: the forty-millimetre gap is bare sheet metal, no ridge spans
it, and the walk added three points of already-covered ground. The
genuine match stays exactly as thin, the end-to-end unmoved three
runs straight, controls green throughout, render eye-checked with
the new rows riding the mating outlines. Direction unlocked
existence; nothing on the sequence side grows strength. The hunt
moves content-side — what each point *says*, not where it sits —
which is ticket 52, while 51 keeps working the beam side.

Weight: three sacct-verified runs, deterministic rebuild,
gate unregressed edge-for-edge.

## 2026-10-17 — pota-repro 52: the seventh column is a dead wire

Two quiet kills. The mystery seventh column never even loads —
the reader parses six values a row, so the authors' residue there
is ballast, and writing their exact bits back changed nothing
three runs straight. And the surface directions are live but only
destructive: smoothing them erased the one genuine match while
leaving everything else untouched. Six runs, controls green,
renders eye-checked. What remains live is the thickness estimate
the matcher gates on — computed from surface and directions, not
stored — which is ticket 53's ground.

Weight: six sacct-verified runs, wire-trace proof, one voided
batch disclosed by the worker, not hidden.

## 2026-10-17 — pota-repro 53: the wall leans on the rim

The thickness gate is finally measured, and it acquits the method
while convicting one wall. Our piece-1 matches the authors almost
exactly — the pipeline works in general. But our piece-2 wall
leans against its own rim, noisy and close, where the authors'
stands back clean: two-thirds of its thickness readings are
garbage, the middle reading sits a full gate-tolerance off, and
true pairs fail the gate by construction. The render shows it
plainly — our blue cloud crowds the red outline, theirs keeps its
distance. Smoothing the directions only killed the last genuine
match. Every point-side lever is now spent; what remains is
reshaping the wall itself, ticket 54's pipeline work.

Weight: three sacct-verified runs, numpy replication of the
assembler's own estimator, offline refutations before spend.

## 2026-10-17 — pota-repro 54: the wall is innocent, the path is guilty

The ticket went in to reshape the wall and came out acquitting
it: our sheets lie on the authors' sheets to a third of a
millimetre. The defect is where our outline *walks* — down the
middle of the wall instead of along its edge, a millimetre off
the authors' path for the whole run, confirmed point by point at
the true seating. Smoothing, flipping, relabelling, trimming —
every surface-side lever died measured, and even twenty-fold
smoothing only shrank the sheet without moving the path. The end
runs sat unmoved three times, controls green, both renders
eye-checked: the authors' outline rides the sheet edge, ours cuts
across it. Re-walking the path is ticket 55's job.

Weight: three sacct-verified runs, composition proof before
spend, premise refutation recorded not buried.

## 2026-10-17 — pota-repro 55: even perfect positions fail

The rim-path hunt ended with a bound, not a fix. Our outline
does ride wide of the edge mid-run — proven numerically — but
four honest snap-back estimators all died flat, and the decisive
test put our points at the authors' exact true positions and
still recovered nothing: the wall's stand-off stayed a quarter
of theirs. No beam or walk or snap can cross that gap, so no
assembly runs were spent proving it. The cross-sections show why
— walls all around, yet the lip's own shape defeats the gauge.
The defect is the lip's shape, and only rebuilding it qualifies:
ticket 56. Scratch surgery on this piece is declared exhausted.

Weight: login-node screening only, cheat bound diagnostic,
both renders eye-checked.

## 2026-10-17 — pota-repro 51: eight of nine is the ceiling

Sixteen assemblies, every control green, and the last sherd's
verdict is in: it seats only twice in sixteen, both times at the
cost of half the pot — seating it scatters the pieces its
contacts compete with for the same beam slots, and forcing it
collapses the assembly to four of nine. The render shows the
bargain plainly: the eighth sherd on the true foot line beside
the first, the rest adrift. Its one dead contact has no grip at
all, worst in the forest on every axis. Eight of nine with named
pieces is the material ceiling for our outlines — and the honest
target the other pots inherit is that shape, not a perfect nine.

Weight: sixteen sacct-verified runs, six beam-side conditions,
render eye-checked.

## 2026-10-17 — pota-repro 56: the lip curls

The shape error finally has a name and a place. The wall's bulk
is innocent; only a three-millimetre band at the lip is wrong,
carrying eight times too much rim-hugging material — the surface
fit curls there instead of standing back. Cutting the curl away
collapses the readings instead of curing them: the wall behind
lies outside the gauge's corridor, so only a refit that *moves*
material can help. No assembly runs were spent — the bound was
decisive, both renders eye-checked with our rays landing shallow
and broken against the authors' clean curve. The refit is ticket
57's job, and it reaches back into the surface-fitting stage
itself.

Weight: offline screening only, joint bound decisive,
both renders eye-checked.

## 2026-10-17 — pota-repro 57: the shelf that fooled the gauge

Eleven ways of moving the lip material, and every one fails the
joint test the authors' data passes. The best-looking attempt
beat their numbers — and the eye overruled the numbers: a flat
uniform shelf where their curve breathes, a cliff at the blend
edge, a fifty-millimetre ray escaping into space. Sculpting the
gauge, not a wall. Even their true positions plus the refit
reach barely half their readings. Scratch refit is exhausted;
what remains is genuine pipeline surface-fitting work, a
different weight class. Six straight measured negatives end the
piece-2 campaign; the decision on what follows belongs to the
conservator.

Weight: offline screening only, eye-check overruled the best
numbers, both renders eye-checked.

## 2026-10-17 — pota-repro 58: the recipe does not travel yet

The pilot pot refused the recipe. Where our unflagged outlines
seated four of six, the flagged ones seated none — three runs,
scattered errors, the first piece never even placed, render
eye-checked with the true ring coherent and our attempts
everywhere but on it. The vehicle is acquitted: the authors'
data scores perfectly through it. The difference is the pot
itself — this one shows its foot where the last showed only
mouth, and our marker cannot tell the two apart: it missed true
mouth arcs and flagged foot arcs that poison the search two
ways. Rolling this recipe further would spread the failure, so
the pilot rule held. Teaching the marker mouth from foot —
using a sign the authors' own files already carry — is ticket
59's job, then this pot gets re-piloted.

Weight: three sacct-verified runs per arm, ORIG-validity first,
render eye-checked.

## 2026-10-17 — pota-repro 59: the marker learns mouth from foot

Four of six, three runs straight — the pilot pot is back to its
unflagged best, with names on every seated piece. The fix was a
gate the authors' files already hinted at: the lip is the widest
ring, so anything narrower is foot and gets spared — computed
honestly on our own outlines, nothing copied. Recall alone
scored zero, proving the foot poison dominated all along. Two
misses remain honestly attributed: one piece too rough-walled
even for the second chance, one placed-but-wrong which is a
seating problem, not a marking one. The render shows the seated
ring tracking the true one. Arm C ships as the pot's recipe; the
second pilot goes next.

Weight: nine sacct-verified runs, three arms, identities
recomputed against binaries, render eye-checked.

## 2026-10-17 — pota-repro 60: the recipe travels

Second pilot, same story: four of seven, three runs identical,
every seated piece named, the authors' data green through the
same vehicle. No foot poison this time — the gate correctly
spared the base arcs it was taught to spare. Two pilots, two
transfers, both at their unflagged best with honest ceilings
declared. The recipe is no longer one pot's luck; the roll-out
to the remaining five begins.

Weight: four sacct-verified jobs, ORIG-validity first,
render eye-checked.

## 2026-10-17 — pota-repro 61: the recipe is not a general uplift

Five pots, twenty runs, every author control green — and the
honest table is mixed. One pot gained two pieces and held them
three runs straight. Two slipped a little, consistently. One
wobbled, one sat at zero as before. The deepest finding: the
seated pieces are almost never the marked ones — the marks move
outcomes through the search's dynamics, not by seating
themselves. So marking is spent as a lever; what remains is
per-pot detective work on the search itself, where each pot
falls short of a believable ceiling. Both renders eye-checked.

Weight: twenty sacct-verified jobs, ORIG-validity per pot
first, five renders eye-checked.

## 2026-10-17 — pota-repro 62: one flag does two jobs, badly

The mechanism is proven in the code: a single mark means both
"this is mouth, veto it" and "do not match here" — so recalling
a true mouth arc deletes its true matches. That is exactly what
happened: the slipped pots lost true contacts both directly
(marked spans zeroed) and by pure reroute (identical pairs
losing beam slots), one piece fell from first to fourth in the
search order, and the gainer won only because the beam started
from a different piece and took the true pair first. Nowhere did
a false piece seat — one true basin outcompeted another. The fix
is to split the mark in two, but the veto kills are not printed
in the logs, so counting them comes first: ticket 63.

Weight: screening-only, zero new runs spent, code-verified,
renders eye-checked.

## 2026-10-17 — pota-repro 64: the extreme case, explained

The conservator's question — full marks here, zero there, same
chain — is answered. Every outline on the null pot is
crisscrossed by ordering leaps, up to eleven centimetres, where
the authors' run clean loops; the render shows it in one glance.
The leaps collapse every gate and kill two of five joins at the
overlap test outright. One axle is genuinely wrong too, but two
good-axle pieces still seat nothing — outlines bind all four.
Search, vehicle, and marking are exonerated with numbers; the
small pot amplifies but does not cause. Repairing the walk is
ticket 65's job, same family as the cure that saved Pot A.

Weight: screening-only, six pre-existing runs verified,
render eye-checked.

## 2026-10-17 — pota-repro 65: regrouping labels is not a repair

The first repair attempt is honestly spent: re-labelling which
points belong to which run changed nothing — same points, same
order, same zero — because the program never reads those
labels. The leaps live in the point order itself, so the real
fix must re-walk the points, the way the Pot A cure did. That
is ticket 66's job.

Weight: three end-to-end runs, all controls green,
render eye-checked.

## 2026-10-17 — pota-repro 66: the outline itself is wrong, not just its order

Even perfectly re-walked, the null pot still scores zero —
because our outline carries twice the points and folds back on
itself where the authors' runs one clean loop, sitting five or
six millimetres off theirs. Ordering was a co-symptom; the walk
is tracing the wrong curve. Diagnosing where it steps off is
ticket 67's job, before any more assembly runs on these pots.

Weight: three end-to-end runs, all controls green,
render eye-checked.

## 2026-10-17 — pota-repro 67: our outline traces the lip twice

The walk is chaining two parallel edges of the lip — inner and
outer, a wall-thickness apart — into one outline, plus a stray
spur across the mouth. The radius-height plot shows both loops
shadowing the authors' single curve. No re-ordering could ever
merge them, which closes out the two spent repairs. The fix is
to split the loops apart and keep the inner one: ticket 68.

Weight: screening-only, no new runs spent,
render eye-checked.

## 2026-10-17 — pota-repro 68: the true curve was never traced

Neither loop sits on the authors' curve — both float
millimetres off, and only a nine-point nub touches it. Three
tickets have now proven the extracted file holds no
recoverable outline: not in its labels, not in its order, not
in either loop. The repair must move upstream of the file
entirely, into the walk that traces the lip: ticket 69.

Weight: three end-to-end runs, all controls green,
render eye-checked.

## 2026-10-17 — pota-repro 69: the offset lives upstream of the walk

Guards straighten the walk — one loop instead of four
chained runs — but the loop still floats millimetres off the
authors' curve, and shrinking the detector's radius only
breaks detection entirely. The error is already in the cloud
of edge points the walk is given, so the next fix moves one
stage earlier, to what feeds the detector: ticket 70.

Weight: four runs, all deterministic,
render eye-checked.

## 2026-10-17 — pota-repro 70: a bigger net catches one loop, still the wrong one

Widening the detector's reach collapses the doubled loop into
a single curve — but it keeps the outer edge, still
millimetres off the authors'. The size of the net picks how
many loops survive, not which one. Choosing the inner face is
ticket 71's job.

Weight: three runs, all deterministic,
render eye-checked.

## 2026-10-18 — pota-repro 71: there is no inner loop to choose

Keeping one face's points collapses the outline to a partial
arc plus a straight chord across the mouth — worse, not
better. The ceilings prove it: for two pieces, none of our
points sit on the authors' curve at all. The true lip is lost
before detection even runs. Finding where is ticket 72's job.

Weight: four runs, all deterministic,
render eye-checked.

## 2026-10-18 — pota-repro 72: the good outline was in the file all along

The clean lip exists — traced on the other surface branch,
under a millimetre off the authors' — but the assembler only
ever reads the first outline file, so it stays invisible. The
blue curve tracks theirs; the red one it actually uses
wanders. Routing the right branch through is ticket 73's job.

Weight: two runs, both deterministic,
render eye-checked.

## 2026-10-18 — pota-repro 73: the null pot scores — with a caveat

Filing the good exterior traces where the program looks moves
the pot off zero: two pieces seated, three runs in a row, all
controls green. The seated pair shares the true shape but
floats seventeen millimetres off — rotation right, position
floating. Chasing that floor, plus the one still-shredded
piece, is ticket 74's job.

Weight: three end-to-end runs, all controls green,
render eye-checked.

## 2026-10-18 — pota-repro 74: the float explained, the shredded piece bounded

The seventeen-millimetre float is neither our content's frame
nor the search alone: the true edge is identical everywhere,
and the search seats the author's content exactly. What
happens is the search climbs a rim-overlap hill whose peak
sits seventeen millimetres from truth — our rim shape shifted
the hill. And the shredded piece has no walkable branch in
its file at all: the longest clean chain is thirty-nine
points against two hundred needed. Recovering it means
re-walking with a guard that stops the trace hopping faces —
ticket 75. Reshaping the hill is ticket 76.

Weight: three end-to-end runs, all controls green,
render eye-checked.

## 2026-10-18 — pota-repro 76: tightening the gates changes nothing

Halving both inlier gates and switching the refinement off
leave the seat bit-identical — the float survives all three.
Gate-tightening is the wrong family and the refinement is
exonerated. What remains is reweighting the score, or
breaking the symmetry some other way — ticket 77 tried
four reweightings over twelve runs and all came back null.
The slide wins on rim-coincidence count, not overlap area,
and holds under every gate and weighting. What remains is
correcting the rim shape itself, or a new scoring idea.

Weight: nine end-to-end runs, all controls green,
render eye-checked.

## 2026-10-18 — pota-repro 75: the guard holds, the shredded piece walks clean

A heading guard plus selecting the inner loop walks the
shredded piece's lip clean: sixteen points, all within two
millimetres of the author's, zero jumps, no reordering.
Guarded, the piece seats — though the pot still trails the
author's score, with the miss now outside this piece. The
hop you witnessed is cured at the source.

Weight: three end-to-end runs, all controls green,
render eye-checked.

## 2026-10-18 — pota-repro 63: separating "match this" from "don't match this" heals D

Recalled rim spans now carry two meanings: confirmed veto
rims stay vetoed, new recalls stay matchable. With that split,
the big pot recovers its unflagged score three runs in a
row — the veto, not the matching, caused its slide. One
correction rides along: edits to the second outline file per
piece never load, so an earlier attribution through it is
void (its reroute findings stand).

Weight: twelve runs (flags + nine stages, all controls green),
renders eye-checked.

Every pot B–J now has end-to-end numbers with valid author-data
controls: the vehicle reproduces the authors fully or nearly (five
pots perfect, the rest close), while our chain fails everywhere —
best D at roughly half seated, C and J at zero. The axle-finder is
exonerated (authors' axles collapse identically on our outlines).
And Pot B's outline fix scored 15/15 on the gate yet changed
nothing end to end across three different outlines — fitting
candidates that the beam never seats. The common shape: our chain
makes an order of magnitude more candidates than the authors'
(twenty-five thousand vs two thousand on Pot E) and the true joins
drown in filtering. One honest gap: the seating pictures never made
it onto the laptop (the snapshots did, so they can be redrawn —
required before any fix ticket closes). Next: find out why the beam
starves fitting candidates (ticket 43), then carry whatever seats
Pot B across the other pots.

Weight: eight pots, nineteen end-to-end runs, every control valid,
sacct-verified throughout.

## 2026-10-17 — pota-repro 41: Pot B's killer is our rims, not the method

Pot B fails on our fragments (4/9+2/15) while the authors' data
scores 9/9+15/15 four times running through the same vehicle — so
the method does this pot and our rim extraction is what breaks:
our outlines jump across the surface (8 of 9 pieces, one piece
~12mm off the true edge), which trips the join filter 8 times where
the authors' rims trip it never. Same poses, same code, same
threshold — only the outlines differ. Two corrections to the
worker's label: this is our broken measurement (category 2), not a
method failure — and no search filter is to be loosened. The Pot A
ordering cure does not generalize here; the walk fails differently.
Next: fix B's outlines (ticket 42), prove Pot A unharmed, then roll
on.

Weight: four sacct-verified runs with valid controls, the same
poses measured on both outline sets, lead-checked render.

## 2026-10-16 — pota-repro 40: the cure vehicle reproduces twice — PASS

The cure branch (`cure-potA`, from the authors' code plus exactly
two one-line fixes) scores 8/8+15/15 on both arms, twice running,
from clean checkouts — and the diff revealed the third fix was
never needed there, because the authors' code already had the right
number and only our fork had drifted. The paper's bar now
reproduces on a traceable vehicle: our rims, our axles, two small
repairs, everything else the authors'. Both rings eye-checked
closed. Next: every pot, same vehicle, repeats per pot (ticket 39).

Weight: two sacct-verified runs, lead-checked branch delta and
render, strict tables identical to the ticket-36 proof.

## 2026-10-16 — pota-repro 38: landed fork reproduces the abl2 basin, not the cure

The three assembly commits are landed and pushed (P22FIX, P22FIX2,
C2-restore — a verified exact three-line delta), and a clean-checkout
rebuild is fully guarded and valid: gate 15/15, both rings closed.
But the numbers are ORIG 8/8+13/15, fresh 7/8+10/15 — the 8/8+15/15
belongs to the cure tree (upstream code plus the three staged fixes),
not to our fork with the three fixes landed. Something else still
differs between the fork and the cure tree — the refinement weighting
is the known suspect, deliberately left out. Second finding: two
independent runs picked 7/8+7/15 and 8/8+13/15 out of the identical
search space (same binary, same pruned counts) — single-run tallies
wobble, so every pot in the B–J run needs repeats. (Attribution
correction 22:00: the "concurrent hand" was the lead's own first
38 worker, still alive when a retry was dispatched onto the same
ticket — two chains, no intruder. The double-run accident is what
proved the wobble.) Next: rule which vehicle carries
the B–J run before ticket 39 starts.

Weight: sacct-verified jobs, lead-checked delta and render, two
independent tallies off the same search space.

## 2026-10-16 — BAR RULING (conservator): the paper's bar stands

The 15/15 measured agreement between reconstructions, not accuracy
against the key. The paper's own claim — every sherd seated, every
join found at k=5/b=3 — reproduces fully on both arms, and that is
the acceptance bar from here. The harder centimetre bar is retired
to diagnostic: it fails even on the authors' reference data, and our
fragments outscore their data 12 to 6 because cleaned rims seat more
truly than decorated ones. No forward bisect (nothing to bisect
from). Next: land the cure set as proper commits, prove it from a
clean checkout, then run every pot. Tickets 38–39 cut.

Weight: the conservator's ruling, recorded the same night as the
evidence that forced it. (Ticket-36 evidence:
`.scratch/pota-repro/issues/36-cure-rebuild.md` — deterministic
reproduction, both arms' full strict tables, arm-agreement measured
on the same files.)

## 2026-10-16 — pota-repro 35: refinement closed; the chase turns around

The last single reproduces the reference exactly, and the whole
refinement stage restored jointly moves the authors' score the wrong
way — two edges over the line, a genuinely worse minimum. Refinement
is closed: neutral alone, worse together, so the floor is not there.
And the 0/8 scoreboard on a visibly seated ring is the deepest split
yet between the two rulers — the old one now disagrees with
photographs. Six tickets of subtraction have mapped every threshold
that does not matter. What remains is the one result none of them
explains: the cure itself. The chase turns around — rebuild the tree
that seated the ring, test it with today's ruler, and either bisect
forward from a reproduced 15/15 or admit the 15/15 was luck and
rethink the bar. Ticket:
`.scratch/pota-repro/issues/35-joint-refinement.md`.

Weight: two sacct-verified runs, full strict tables, an eye-checked
render of a 0/8 ring that seats.

## 2026-10-16 — pota-repro 34: the acquittal stands, fairly this time

The retrial returned the same verdict — but this time the pipeline
was working, so the verdict means something. The threshold is
innocent on a base that seats the ring: identical geometry to the
reference on both arms. The last admission single also reproduces
the reference to seven thousandths of a millimetre. And a
provenance correction redrew one corner of the map: the remaining
check threshold's true upstream is 50, not 100 — a relaxation sits
where a restoration was assumed, and testing it is the last single
ever owed. After that, singles are over: every threshold tried
alone, every one neutral. What remains is interaction — tested
jointly, one stage at a time, with the load-bearing weighting kept
in place because removing it is already proven to crater the
authors' score. Ticket:
`.scratch/pota-repro/issues/34-c1-retest.md`.

Weight: three sacct-verified runs, snapshot-identity proofs, and a
blame-verified correction that created the last single.

## 2026-10-16 — pota-repro 33: admission spent; an old acquittal overturned

The veto is proven covered — the flag's only consumer is the line
already deleted, shown by reading every reader in the function, so no
run was burnt. The last admission threshold reproduces the reference
to five thousandths of a millimetre and changes nothing. Every
single is now spent — except one whose acquittal does not hold. Its
test ran on the collapsed base, where the broken gate upstream of it
vetoed everything first: the threshold never had a working pipeline
in which to show an effect. It gets a fair trial now, on the repaired
base, then the last two untested singles. If those fail, the remaining
hypothesis is interaction — and that gets its own ticket, justified
by exhaustion rather than guessed at. Ticket:
`.scratch/pota-repro/issues/33-admission-residue.md`.

Weight: a write-to-sole-reader proof, a D-identical run, and a reread
of the ticket-29 tables that overturned an exoneration.

## 2026-10-16 — pota-repro 32: the last ruler falls; the residue is not refinement

Two more restores, both reproduce the reference geometry to a
hundredth of a millimetre — and change nothing. The iteration budget
even takes the loose scoreboard to its best ever while the strict
table does not move a single edge: the two rulers now disagree on
record, and only one of them measures shape. Along the way the second
ruler fell too: pruned counts read 61/105 on geometry identical to
the 63/103 reference — tally-side, like the binary score. What gates
a run now is only the strict table off saved geometry. The floor has
survived everything in the refinement stage, so the search moves
upstream to the admission gates — with one threshold deliberately
held back for a combination run. Ticket:
`.scratch/pota-repro/issues/32-refinement-residue.md`.

Weight: two sacct-verified runs, snapshot-identity to 0.017mm, full
strict edge tables on all four arms.

## 2026-10-16 — pota-repro 31: the floor lives in the refinement stage

Two arms, opposite lessons. Tightening the outlier rejection the
lineage once used moves one edge — noise-adjacent, the floor stands.
But restoring the upstream refinement weights splits the world: the
authors' score craters to 6/15 (their weighting is load-bearing, not
optional) while our fragments jump to 11/15, the best yet. Neither
weighting is the answer — but the floor now has an address. It lives
in how the refinement weighs its evidence, and the remaining
suspects fit on one hand: the tightened robustness scales, the
lengthened iteration budget. Ticket:
`.scratch/pota-repro/issues/31-translation-bias.md`.

Weight: two sacct-verified runs, full strict edge tables, an
eye-checked render showing the dropped loop on the authors' arm.

## 2026-10-16 — pota-repro 30: the ruler was broken, not (only) the method

Six runs, no movement on the floor — and the most important finding
is about the ruler. The binary scoreboard does not track the saved
geometry: identical outputs scored 8/8 in one run and 7/8 in another,
and a run scored 0/8 while its saved ring seated exactly like the
reference. The scoreboard tracks selection luck, not shape — so it no
longer gates runs. What gates them now: exact pruned counts (stable
every run) plus the strict table computed from saved geometry. Under
that honest ruler the floor is real but specific: everything turns
right, everything sits within about a centimetre, and the remaining
error is a systematic sideways shift concentrated on three pieces —
not thinning, not tolerance, not a dead threshold. Three handles
remain, taken one at a time. Ticket:
`.scratch/pota-repro/issues/30-translation-floor.md`.

Weight: six sacct-verified runs, bit-identity proofs, stable failing
edge sets across every arm.

## 2026-10-16 — pota-repro 29: the void was a harness artifact; the gate drift was real

Two corrections in one ticket. First, the voided run never tested what
it claimed: the assembly fork renamed its entry point, the build shim
missed silently, and the run executed the fork's own driver at the
wrong search width — so the authors' 2/8 said nothing about the code
deltas. Second, with the shim asserts fixed, restoring one drifted
threshold (the pairwise axis gate, back to the true upstream value —
a commit message claiming "upstream" was factually wrong) moves the
authors' score 0/8 to 8/8. What remains is not collapse but looseness:
everything sits, turned right, shifted by millimetres over a
systematic floor of about 7–9mm. Nothing lands — one threshold per
run from here. Ticket:
`.scratch/pota-repro/issues/29-assembly-provenance.md`.

Weight: two sacct-verified runs with shim asserts, a named false
"upstream" claim, an eye-checked seating render of both rings.

## 2026-10-16 — pota-repro 28: the pipeline is home; the assembly tree has drifted

The port split in half. The pipeline half is fully home: rebuilt from
repo sources, the gate reads 15/15 with zero teleports, and its fixes
are committed. The assembly half voided itself honestly: the authors'
control scored 2/8, so per protocol the run counts for nothing — and
the diagnosis is specific, not hand-waving. The assembly tree the cure
was proven on is not the tree in the repo: a merge threshold moved, a
normals check is dead code, scoring leftovers linger. The pipeline
fixes land because they proved out of the repo; the search relaxations
stay staged, uncommitted, until a repo-traceable binary reproduces the
cure. Next: archaeology first (which tree proved the cure?), then one
ablation at a time, with the transform capture fixed so no run's
evidence evaporates again. Ticket:
`.scratch/pota-repro/issues/28-port-and-land.md`.

Weight: byte-identical hunk verification, a reproduced pipeline half,
a voided assembly run with a named suspect and a commit to blame.

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

## 2026-10-18 — float audit: 110 of 129 fresh outlines float, and jumps don't explain it

All 129 fresh fracture outlines measured against the author's:
110 float more than two millimetres off, 19 track — and
every pot keeps at least one tracker. The floaters do not
share jumps (thirty have none; trackers carry up to ten).
What they share is coverage: every floater matches under
half the author's outline, every tracker over half — a
perfect split. Three pots float nearly whole at a uniform
five to nine millimetres: a systematic wrong-loop offset,
not piece-by-piece noise. And the author's position survives
inside at least one floater — masking recovers it to under
a millimetre — so the float is extra wrong-loop material,
the same family ticket 79 is correcting.

Weight: login-node measurement over all pots B–J, no runs.

## 2026-10-18 — pota-repro 80: most floats are a slot swap, not the walk

The walk is innocent in ninety-four of them: our Surface_0
carries the author's Surface_1 — exterior wall where the
interior should be — because a size sort puts the denser
wall first and the guard that would correct it never ran.
The trace faithfully drew the wrong wall's loop. Fourteen
more are the known doubled-walk defect; the trackers are
simply the pieces that escaped the swap. The fix is
re-running with the guard wired in, starting with the
smallest pot — ticket 81, held until the in-flight workers
are home.

Weight: login-node screening, render eye-checked.

## 2026-10-18 — the two in-flight workers came home silent, and the lead collected

Both workers' runs had finished hours earlier with no
report. The tallies: the guarded Pot E bundle crashes the
assembler at launch — fifteen-point rims where the working
bundle's smallest is seventy-eight — while the plain bundle
repeats the best fresh score. And the rim-shape re-walk
reproduced the same off-lip loop exactly, so re-walking
cannot correct that shape. Curing the crash is ticket 82;
the near-free swap cure, ticket 81, is released.

Weight: six end-to-end runs, controls green, render
eye-checked.

## 2026-10-18 — pota-repro 81: the swap cure seats a whole pot

Exchanging the slots back seats all six pieces of the
smallest pot, three runs in a row — the first full pot
beyond the control. One piece needed its loop densified
past the fifty-point loading gate. Every swapped rim now
rides the author's outline under a millimetre. Rolling the
same cure across the remaining swapped pots is next.

Weight: six end-to-end runs, all controls green, renders
eye-checked.

Assembly ticket 06 and `intent/S1` in `../structure-from-sherds-pp`
(2026-09-26, oracle-init proof + Pot_A control). Extractor:
`edgeline_extraction.cpp` (segment finding ~line 1632, segmentation
`clusteringOnNormals` ~line 2118, writer `writeBreaklinePCDWithSegments`
~line 1042). Juglet patches already in `patches/juglet_*.patch`.
