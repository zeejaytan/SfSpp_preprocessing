# 16: Paper-compliance audit — where our code still differs from §IV-B1

**Answers:** E1

**Blocked by:** nothing — audit only; each gap below names its own fix ticket
where one exists

**Status:** ready-for-agent

**Needs-eye:** none — source-vs-text comparison, no geometry claim

## What this ticket is

A 2026-09-29 audit of our preprocessing against SfS++ §IV-B1 (plus the
axis section), done because the chain kept describing deviations loosely
and one of those descriptions was wrong. Each item was verified against
both the paper text (`papers/text/sfspp-2502.13986v1.md`) and the code, not
carried over from earlier tickets. Anything here that later work touches
should cite the line numbers, not the summary.

## A correction to our own record (read first)

E1 and ticket 04 describe "`Surface_0` = the largest cluster" as the
deviation from the paper. **It is not.** The paper says "we select the two
largest clusters, representing the inner and outer surfaces." Our code does
exactly that (`mesh_processing_headless.cpp:1799-1800`, sort descending
`:1769`). The deviation was only ever the missing *classification* step —
deciding which of the two is interior — and ticket 04 implements it. Any
write-up that says "the code took the largest cluster where the paper takes
the interior surface" is wrong and should be corrected to "the code took
the largest clusters without classifying them."

## Matches (structure and content)

- Two-largest selection (above).
- Classification test: ray along the normal to the symmetry axis, sign of
  the scalar coefficient, both configurations tried, max satisfying points
  wins — implemented per spec in `surface_classify.{h,cpp}`. Caveats that
  are OURS, not the paper's: the 5mm near-intersection tolerance, and the
  ticket-04 guards (winner ≥10% of sibling size, margin ≥2.0).
- Region-growing shape: min-curvature start, neighbor + curvature + angle
  expansion. Parameters differ (below).
- Cluster merging with the paper's ingredients: kNN close pairs, patch
  normal similarity (0.95), boundary-curvature comparison (0.1), second
  verification pass (0.75/0.25).
- PCL BoundaryEstimation for the edge line; B-spline refinement; corner
  segmentation from distance-from-chord scores with peak detection.

## Deviations, load-bearing first

1. **No axis-based descriptors.** The paper's FE output — height, radius,
   angle, thickness per edge point, Savitzky-Golay smoothing plus Gaussian
   (kernel 7, σ=2.0) — is not produced anywhere in this stage: no such
   fields, no such filters in `edgeline_extraction_headless.cpp`. Whatever
   the assembler matches on, it does not come from here. (Whether matching
   computes its own is an assembly-repo question, not answered here.)
2. **No counter-clockwise ordering vote.** Nearest-neighbour walk instead
   (`edge_line_ordering.cpp:51`). Ticket 03 closed unimplemented; Pot_A
   reaches 15/15 without it, so it is not currently load-bearing for the
   gate — but it remains the plainest unimplemented sentence in §IV-B1.
3. **Noise filter dead.** Computed (`:949-972`: radius from boundary radius,
   min-neighbors 3/6) then discarded by the `boundary.pcd` reload (`:974`).
   Ticket 05. Measured harmless on piece 2 (dense thicket, removes almost
   nothing) — which is evidence about that sherd, not a reason to leave
   specified code dead.
4. **Resampling is 2.0mm-to-200-cap, not 1.9mm equidistant**
   (`adaptiveDensifyBreakline`, default 2.0, called `:715`; target count
   clamped `[30, 200]`). Ticket 06. The cap plus downstream padding is what
   let a 3.6mm fragment pass as a full breakline.
5. **Rim criterion differs.** Paper: height/radius std ≤1.0mm, gradual
   change ≤0.1mm, ≥20 points. Ours: plane-fit curvature error (>0.12) plus
   axis-distance deviation <50% of mean (`:2861`, `:3296-3300`). Different
   test entirely; never compared head-to-head.
6. **Region-growing parameters differ.** Paper: τθ=4, τκ=1, nb=10. Ours:
   4.5°/1.5, 15–40 neighbors, adaptive cluster sizes (`:1717-1727`,
   defaults `:2174`). Ticket 12 showed the default optimal and both
   directions hurt or crash — so these values are measured-good on Pot_A,
   but they are not the paper's values and should not be cited as such.
7. **Merging does not iterate to convergence.** Paper: repeat until no
   merges possible. Ours: single pass over pairs; the outer loop retries on
   *count* < 2 instead (`:1647-1660`), which is a different condition.
   Unmeasured effect.

## Ours with no paper basis (measured necessary, not compliant)

- Per-sherd vote guards (ticket 04): provisional thresholds on 8 sherds.
- Patch-rim appending (ticket 14): no paper step emits fracture-zone rims
  into the breakline. Demonstrated +4 pairs (11→15/15); still ours.
- Euclidean decorative path, adaptive K/radius/clamps, 50-point drop guard.
  Each has a measurement behind it (see its ticket); none should be
  described as "what the paper specifies."

## Axes (flagged, not judged)

`Dataset/Axes/` is produced by MATLAB (`AxisExtraction/*.m`, PotSAC
references in scripts), not by the C++ pipeline. The paper's axis comes
from its modified PotSAC on the inner surface. Whether our MATLAB matches
that method was not checked — it is the one input our vote depends on that
has never been audited. If the vote ever misbehaves on a new pot, look
here first.

## Acceptance criteria

- [ ] The "largest cluster" correction above propagated to E1 and ticket 04
      (search for the phrase; fix each occurrence rather than appending)
- [ ] Each numbered deviation either names its fix ticket or records why it
      is accepted (1: assembly-repo question filed or answered; 2–4: tickets
      03/05/06 updated, not duplicated; 5, 7: measured or explicitly deferred)
- [ ] Nothing in this ticket re-argues settled measurements — it cites
      ticket + line and moves on
