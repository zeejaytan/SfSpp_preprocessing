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
