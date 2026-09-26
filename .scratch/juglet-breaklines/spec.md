# Spec — Edge-line extraction that matches SfS++ §IV-B1

**Answers:** E1

**Status:** spec for slicing into tickets; nothing implemented yet

## Problem Statement

SFS++ cannot find a single join on the Juglet — a handmade, thick-walled
Palestinian vessel — and the cause has been traced into our
preprocessing, not the assembler.

The paper specifies how a sherd's broken edge ("edge line") is produced
(§IV-B1, *Edge line extraction and segmentation*). The released code does
not do what the paper specifies, in four ways:

1. **The edge line is taken from the wrong surface.** The paper takes it
   from the **interior** surface. The code takes whichever surface
   cluster is **larger**, with no interior/exterior test, and emits an
   edge line for both surfaces. On thin thrown pots the larger surface is
   probably the same physical face on every sherd, so nothing looks
   wrong. On the Juglet — where inside and outside are nearly equal in
   area — "larger" lands on **different faces for different sherds**.
   Ten of the Juglet's eighteen true joins end up comparing the inside
   of one sherd to the outside of its neighbour, and the assembler's 2 mm
   / agreeing-normal test can never see them.
2. **The ordering step the paper names is not implemented.** The paper
   reorders the edge-line points "counter-clockwise using their normals
   and a voting algorithm". The code instead walks the points with a
   nearest-neighbour chain that takes the first unused point among 50
   candidates. On duplicate-dominated boundary clouds this walk stalls or
   derails, producing **disconnected fragments**: traced length 0.27–2.15×
   the rim it should cover, with internal jumps of 10–24 mm against a
   0.3 mm median step, and one sherd reduced to a 3.6 mm stub.
3. **The noise filter the paper specifies is dead code.** It is computed,
   written to disk, and its size printed — then a reload of the
   *unfiltered* cloud discards it before sequencing.
4. **The resampling the paper specifies is replaced by padding.** The
   paper resamples to equidistant points at 1.9 mm. The code pads to a
   fixed 200 points, so point count carries no information about trace
   quality — which is how a 3.6 mm fragment passed every file-count check
   for a week.

A conservator reading the output sees breaklines that are numerically
well-formed (200 points, plausible extent) and geometrically wrong.

**Whose bug this is, checked and settled.** The non-local walk is
byte-identical in `DominicoRyu/SfSpp_preprocessing` (`int K = 50;`); our
fork only added empty-input guards. This is not a regression we
introduced. It is a gap between the paper and the released code, which
the Juglet exposes and the authors' own thin-walled dataset does not.

**Why it matters beyond this ticket.** The assembler matches sherds by
running a longest-common-subsequence over the edge-line points *in
order*. Ordering is not cosmetic: it is the input the matcher consumes.

## Solution

Make the edge-line stage do what §IV-B1 specifies, and prove each part
against a test that can fail.

Four changes, in dependency order:

1. **Classify the two surfaces as interior/exterior** by the paper's
   ray-normal sign test, and take the edge line from the **interior**
   surface.
2. **Order the edge-line points** by a traversal that follows the rim
   (see Implementation Decisions for the reconstruction of the paper's
   underspecified "voting algorithm"), resolving the global
   counter-clockwise sense by an aggregate vote over per-point normals.
3. **Wire in the noise filter** the paper specifies, so it is applied
   rather than discarded.
4. **Resample to equidistant spacing** as specified, and report the
   traced length beside the point count so a fragment can never again
   look like a full breakline.

## User Stories

1. As a conservator, I want the broken edges drawn on my pot to be
   visible as one continuous line, so that I can see whether the
   software is following the join at all.
2. As a conservator, I want to see a correct placement beside the
   machine's attempt, so that I can judge a claimed join with my own
   eyes rather than a number.
3. As a conservator, I want to be told honestly when a join is still
   not found, so that a null result is not dressed up as progress.
4. As the pipeline operator, I want the edge line taken from the
   interior surface, so that two sherds which meet are compared on the
   same physical face.
5. As the pipeline operator, I want each edge line to be a single
   closed loop that visits every boundary point once, so that the
   longest-common-subsequence matcher receives a coherent sequence.
6. As the pipeline operator, I want the traversal direction chosen
   consistently, so that two edge lines that meet are traversed the same
   way round and their descriptors align.
7. As the pipeline operator, I want duplicate and clustered boundary
   points not to derail the traversal, so that eroded sherds still yield
   a continuous trace.
8. As the pipeline operator, I want the specified noise filter actually
   applied, so that spec and behaviour agree.
9. As the pipeline operator, I want points spaced as specified rather
   than padded to a fixed count, so that point count stops being
   meaningless.
10. As the pipeline operator, I want each breakline file to report its
    traced length, so that a fragment is visible as a fragment.
11. As the pipeline operator, I want a run whose patch did not apply to
    abort loudly, so that I never score unpatched code.
12. As the pipeline operator, I want the working sample to be unaffected,
    so that a Juglet fix cannot silently damage the material the method
    already handles.
13. As a researcher, I want the ordering algorithm unit-tested on
    synthetic curves, so that a regression is caught without a cluster
    run.
14. As a researcher, I want an end-to-end acceptance test that can fail,
    so that "the numbers improved" is never the only evidence.
15. As a researcher, I want the reconstruction of the paper's
    underspecified voting step written down and marked as such, so that
    nobody later mistakes it for the authors' algorithm.
16. As a researcher, I want the Pot_A control reported alongside every
    Juglet number, so that a Juglet-only change is visible as one.
17. As a researcher, I want the segment-boundary non-determinism
    resolved, so that two runs of the same input are comparable.
18. As the maintainer, I want the source verifiable from the laptop, so
    that a patch can be checked before a job is submitted.

## Implementation Decisions

**Surface classification (§IV-B1, "Interior and exterior surface
classification").** For each sampled point, project a ray along its
surface normal towards the axis of symmetry to the intersection point
p′. If p′ lies along the positive surface normal, the surface is
interior; if along the negative, exterior. Where the two surfaces are
ambiguous, the paper evaluates both configurations and takes the one
with the greater number of satisfying points. The edge line is taken
from the interior surface only.

**Ordering — the paper's "voting algorithm" is not specified and this is
a reconstruction.** The corpus was swept (22 papers): the phrase "voting"
occurs **exactly once**, in this sentence, and no paper in the collection
states, names or describes an edge-point ordering method. The paper
points to supplementary material that the collection does not contain.
The following is therefore our reconstruction, to be recorded as such in
the ticket and in code comments:

- *Sequencing.* Points are ordered by walking the rim, choosing at each
  step the unused point that best continues the local tangent, subject to
  a maximum step. This replaces the "first unused among 50 nearest"
  rule, which is non-local and is the direct cause of the stalled and
  derailed walks measured on the Juglet.
- *Voting.* Ordering a closed curve has a genuine one-bit ambiguity —
  which of the two senses of travel is "counter-clockwise". The paper
  resolves it "using their normals"; we resolve it by letting each point
  vote on the sign of its tangent-derived fracture normal, and taking the
  aggregate. The paper defines that fracture normal as the cross product
  of the point's surface normal with its tangent, which is what the vote
  is taken over.
- The paper separately reports that the ± axis-direction ambiguity is
  handled at matching time by inverting one descriptor and matching
  twice, so this stage is not required to fix it.

**The resampling value is a parameter, not a constant.** 1.9 mm is
quoted as "an empirically optimized value" for their data; it is exposed
as a parameter with that default rather than hard-coded, because our
vessels are an order of magnitude smaller than some of theirs.

**Padding is removed, not adjusted.** The fixed 200-point pad is deleted
rather than re-tuned, because it is what let a 3.6 mm fragment pass every
count-based check.

**No new dependency.** The ordering uses the existing PCL K-D tree and
Eigen linear algebra. No graph library is introduced.

**The point-count contract changes.** Breakline files keep their existing
header format (segment count, total points, per-segment ranges) so the
assembler needs no change; a traced-length line is added as a comment,
which the assembler already ignores.

## Testing Decisions

A good test here states a property of the *output geometry* and fails
loudly when it is violated. No test asserts on log text, on point counts
alone, or on the identity of an internal function.

**Seam 1 — ordering, as a C++ unit test run inside the build container.**
This seam does not exist and must be created; the repository has no
CTest wiring and no unit tests at all. It is the highest seam available
for the ordering itself, and it is necessarily on the cluster, because
the laptop cannot build this code (no PCL/Eigen).

Properties tested on synthetic inputs: a clean circle comes back as a
single closed loop visiting each point once; a circle carrying a clump
of near-duplicate points still comes back as one loop rather than
stalling; a circle with a gross outlier does not swallow the outlier into
the traversal; the returned traversal direction is the one the vote
selects, and reversing the input normals reverses it. Prior art: none in
this repository; the properties are stated as behaviour, not as a
template copied from elsewhere.

**Seam 2 — end-to-end acceptance, as the existing gate probe on the
laptop.** Already built, and it has already earned its place by
refuting a plausible fix. For the regenerated bundle: true mates must
pass the assembler's own 2 mm / agreeing-normal test at ground truth,
reported per pair, with **Pot_A held at 15/15** as the no-regression
guard. A run that scores better on the Juglet while Pot_A drops is
labelled Juglet-only, not a fix.

**The gate is not run inside the extracting job.** Scoring a re-extract
from within the process that produced it is how a broken input gets
certified by its own producer. It runs on the laptop, where it can fail
independently.

**Marker discipline applies to the build.** Every patch carries a marker,
the marker is grepped in the source before building and its effect
confirmed in the runtime log, and a run whose marker is absent is void
rather than a negative result.

## Out of Scope

- **Any change to the assembler.** Reading the second breakline, and the
  normal-direction convention in the join gate, are assembly-side and
  belong to `structure-from-sherds-pp`. If a correct edge line still
  gets rejected, that is a finding to hand back, not a fix here.
- **Axis extraction.** Already closed work.
- **The segment-boundary non-determinism** observed on piece 1. Recorded,
  and a candidate contributor to the assembly's run-to-run pairing
  instability, but a separate ticket: it must not be bundled into this
  change or it will be impossible to attribute.
- **Early Kurgan material** and any vessel without an answer key.
- **Reproducing the authors' results.** We are not claiming their method
  is wrong on their data; on thin thrown pots "larger surface" may be
  reliably the interior, in which case their reported results stand and
  this is a robustness gap the Juglet exposed.

## Further Notes

**An honest limit on the reconstruction.** The paper names a voting
algorithm and does not describe it, and the supplementary material is
not in our collection. If the authors' voting does something other than
resolve traversal orientation, our version will differ. The spec is
written so that this is a single, isolated, testable decision: if the
acceptance seam passes and the unit seam passes, we have an edge line
that behaves as specified, whatever the original algorithm was.

**The paper's own limitations section** (line 454) lists
"surface extraction, fracture line adjustment, and counterclockwise
alignment" as required preprocessing steps — confirming that this
ordering is a real, named stage of the method and not an implementation
detail. It also states that "some constraints require parameter
adjustments or data scaling when the dataset changes", which is the
failure the Juglet exhibits.

**Scale note for the 1.9 mm default.** The paper's dataset is described
as having an edge-line perimeter of approximately 9 cm per fragment
(line 329); at 1.9 mm that is roughly 47 points per edge line, against
the 200 our files carry. Our denser output is a deviation from the
specified spacing in the opposite direction to the padding problem, and
is corrected by the same change.
