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

## Axes (refined 2026-09-29: they exist, including for the Juglet)

`Dataset/Axes/` is produced by MATLAB (`AxisExtraction/*.m`, PotSAC
references in scripts), not by the C++ pipeline. The paper's axis comes
from its modified PotSAC on the inner surface. Whether our MATLAB matches
that method was not checked — it is the one input our vote depends on that
has never been audited. If the vote ever misbehaves on a new pot, look
here first.

Update: the Juglet axes DO exist — all 9 in `Juglet_Dataset_20260916/`,
single-candidate, same format — and are now staged at
`Dataset/Axes/Juglet/`. An early shallow `find` reported 4/9 and was wrong.
What remains unaudited is the MATLAB *method*, not the Juglet *files*.
(The assembler also carries its own C++ axis code — `ComputePottmannAxis`,
`ComputePotSACAxis`, `RefineAxis` — called from the ranking path, while the
mains load the files. File-vs-computed precedence there was not traced.)

## ADDENDUM 2026-09-29: second pass — the assembler side, plus three new gaps

A sidekick mapped the assembly repo's inputs (verified below by reading the
cited lines, not taken on trust). Three findings change the audit, one of
them correcting this ticket:

### Correction: descriptors ARE computed — downstream, differently

Ticket 16 item 1 said no axis-based descriptors are produced. Too broad.
`class/filter.cpp:161-219` (`CalculateFeatureAxisless`) computes per-point
Dist/Height/Theta/Thickness with `LanczosDiffLow` diffs and a `Gaussian`
smoothing pass, and `GetThickness` (`:221-260`) measures thickness against
`sur_out_`. What the paper specifies is finite differences +
**Savitzky-Golay** + Gaussian (kernel 7, σ=2.0); no Savitzky-Golay exists
repo-wide, and the Gaussian call differs in parameters. So the step EXISTS
in the assembly repo with different smoothing — the gap is a smoothing
mismatch, not an absence. Item 1 is corrected to that.

### New gap A: `is_seg_base_` is compiled out everywhere

`#define NO_BASE_INFO` sits in `main.cpp:34`, `main_headless.cpp:32`, and
`main_headless_correct.cpp:52` (with `NO_RIM_INFO` commented out in all
three). So `is_seg_base_` is forced false in every binary, and the
base-pair logic (the `sane&&seg_base` skips in `FeatureComp`, the base-only
paths in `ExclusivelyPickEdge`) never executes. The paper's rim/base
machinery runs on rim flags alone here. Verified in all three mains, not
inferred.

### New gap B: `Surface_F` is expected by name and never produced

`data_path.h` points `surface_fr[i]` at `Surfaces/<piece>_Surface_F.pcd`;
`main_headless_correct.cpp:187` and `main.cpp:95` always call the 3-arg
`LoadSurface` (only `main_headless.cpp:88-93` falls back). Zero such files
exist in either the Juglet archive or the Pot_A dataset (measured).
`reconstruction.cpp:701/749` runs the fractional-surface correspondence
(`sur_frac_.BuildTree`, `MakeCorWOBuildTree`) on the resulting empty
clouds. The paper segments three surfaces — interior, exterior, fractured —
and our mesh stage emits two named walls while the fracture zone sits
inside `unclustered.ply`, which no `Surface_F` filename ever points at.
This is the same fracture zone ticket 14's patch rims are mined from, seen
from the assembler's side: the data exists, the filename it is read by does
not.

### Wiring fact (operational, not a gap)

The JUGLET assembly paths point at the archive
(`JUGLET_BASE .../Juglet_Dataset_20260916/SfS_pp/`), not at fresh output.
Re-extracted Juglet breaklines do not reach the assembler until staged
there. Any Juglet rerun that stops at `Dataset/Breaklines/` has not
actually fed the matcher.

### Method note for this audit

Steps 1–4 above were mapped by a sidekick and each load-bearing claim
re-checked by reading the cited lines. Unverified and therefore NOT
claimed: the exact semantics of the rim-flag reads in `BuildTree`/`LCS`
(flag logic is subtle; cited but not interpreted here), and the MATLAB
PotSAC-vs-paper comparison (still open, as before).

## Acceptance criteria

- [ ] The "largest cluster" correction above propagated to E1 and ticket 04
      (search for the phrase; fix each occurrence rather than appending)
- [ ] Each numbered deviation either names its fix ticket or records why it
      is accepted (1: CORRECTED 2026-09-29 — descriptors exist downstream
      with different smoothing; remaining question is Savitzky-Golay vs
      Lanczos, assembly-repo scope. New gaps A/B above need tickets or
      recorded acceptance: A = base machinery compiled out; B = Surface_F
      never produced while reconstruction reads it)
- [ ] Nothing in this ticket re-argues settled measurements — it cites
      ticket + line and moves on
