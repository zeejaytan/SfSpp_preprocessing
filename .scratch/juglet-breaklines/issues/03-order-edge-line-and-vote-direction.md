# 03: Order the edge line along the rim, and vote for the direction

**What to build:** the edge line comes out as a single closed loop that
follows the rim, traversed in a consistent direction, instead of being
assembled by a non-local nearest-neighbour walk.

The paper (§IV-B1) states the edge-line points are "reordered
counter-clockwise using their normals and a voting algorithm". That step
is **not implemented in the released code** at all. The paper names the
voting but does not describe it, and a sweep of all 22 papers in
`papers/text/` found the word "voting" exactly once — in that sentence —
with no paper describing an edge-point ordering method. What follows is
therefore a **reconstruction, not the authors' algorithm**, and is
labelled as such in code and in the ticket.

- *Sequencing*: walk the rim, taking at each step the unused point that
  best continues the local tangent, subject to a maximum step. This
  replaces "first unused point among the 50 nearest", which is non-local
  and truncates on **roughly half the sherd faces of both pots** (8/18
  Juglet faces fully covered, 7/16 Pot_A faces — Pot_A being the control
  that assembles 15/15 correctly). See `08-is-the-defect-juglet-specific.md`.

## BLOCKED as the Juglet's fix — 2026-09-26

This ticket was going to be justified as *"the walk is why the Juglet
proposes no joins."* **Ticket 08 refuted that.** Pot_A suffers the same
truncation and still assembles perfectly, so the truncation does not
discriminate between the pot that works and the pot that doesn't, and
cannot be its cause.

**Keep the ticket; change the claim.** The work is still worth doing — the
walk discards 15–75% of an edge on half of all faces, which is a real
quality defect in its own right, and the paper's ordering step genuinely is
missing from the code. But it must be:

- described as **an independent defect, not the Juglet's cause**;
- judged by whether it improves the coverage *distribution* across all 18
  Juglet and 16 Pot_A faces — not by whether the Juglet's gate score moves,
  since there is no reason it should;
- **not credited in advance with fixing the Juglet.**

Before starting, read the face-selection hypothesis in ticket 08: the
leading candidate for the Juglet's zero joins is that `Surface_0` is the
largest cluster with no interior/exterior test, so 10 of 18 true mates are
inner-vs-outer. That is a face-*selection* problem, in ticket 04's
territory, and is the more likely explanation. This ticket should not be
sequenced as though it were the Juglet's remedy.

## A number in this ticket that does not belong to it

An earlier version carried *"traced length 0.27–2.15× the rim; internal
jumps of 10–24 mm against a 0.3 mm median step"* as evidence of the walk's
failure. **Those were measured on the emitted breakline files**, after
B-spline resampling and 200-point padding — a later stage. They say nothing
about the walk. The walk's own failure is truncation, measured as coverage
(ticket 01). Removed rather than left in place to mislead.
- *Voting*: ordering a closed curve has a one-bit ambiguity — which of
  the two senses of travel is "counter-clockwise". Each point votes on
  the sign of its fracture normal, defined by the paper as the cross
  product of the point's surface normal with its local tangent; the
  aggregate decides.

**Answers:** E1

**Blocked by:** 02 (dedupe first — sequencing on a duplicate-laden cloud
cannot be judged)

**Status:** resolved as characterized-but-unfixed, 2026-09-28 — see below

## Scope correction: dedupe eliminated, rewrite required

Piece 2's two boundary clouds diagnosed on the verified Python
transcription (ticket 01: matches the C++ exactly):

| cloud | n | K | exact dupes | coverage as-is | coverage after dedupe (exact, 1e-6, 1e-4, 1e-3 mm) |
|---|---|---|---|---|---|
| Surface_0 (86 pts) | 86 | 8 | 30 | 0.634 | **0.634 at every level** |
| Surface_1 (202 pts) | 202 | 20 | 26 | 0.265 | **0.265 at every level** |

Dedupe at four thresholds changes **nothing**. Ticket 02 is eliminated as
the fix for this sherd. The stall structure is the ticket-01 mechanism
exactly (18 of 20 K-window candidates already visited on the 202-point
cloud) — the rule itself, not its input. So this ticket is back in scope,
narrowed: replace the non-local rule with tangent continuation, judged by
piece 2's rim going from 46%/27% to full and the gate moving 11/15 → 15/15.
The general-coverage criteria below still apply as regression guards.

**Needs-eye:** none yet; the witnessed render is in 07.

- [ ] A clean synthetic circle is ordered as one closed loop visiting
      each point once
- [ ] A circle carrying near-duplicates and a gross outlier still yields
      one loop; the outlier is not swallowed into the traversal
- [ ] The traversal direction is the one the vote selects, and reversing
      the input normals reverses it — both asserted
- [ ] No internal step in the result exceeds the maximum step by more
      than a stated factor
- [ ] The reconstruction is marked as such in a code comment, so nobody
      later mistakes it for the authors' algorithm
- [ ] Acceptance probe run before and after, both numbers recorded

## CLOSED 2026-09-28: piece 2's input does not contain a traceable rim

Everything tried against piece 2's two boundary clouds (86 and 202 points),
each measured, each failing for a recorded reason:

| intervention | result on piece 2 | verdict |
|---|---|---|
| tangent-continuation rewrite (this ticket's plan) | validated in Python first: coverage **0.116 / 0.035**, worse than the old rule's 0.570 / 0.252 | **not built** — the port failed before any C++ was written, which is the TDD loop working |
| dedupe at exact/1e-6/1e-4/1e-3 mm | coverage **unchanged** at every level (0.634 / 0.265) | eliminated (ticket 02 for this sherd) |
| paper's noise filter (ticket 05) | removes almost nothing (86→86, 202→199): the thicket is dense, not isolated | eliminated |
| angular sort around centroid | 12/85 steps >3× median, max 9.9mm; S1 max 28.6mm | eliminated |
| concave-hull traversal | fragments: longest loop 54% of reference; 2D projection folds the 3D rim | eliminated |
| MST diameter path | 163/202 pts but weaves, median 3.32mm from reference, 26% within 2mm | eliminated |
| leaf-pruning + walk | overlap stays ~27%: the rim points are not in the cloud to begin with | eliminated |
| boundary radius 1–9mm | lengths 0.25–1.52× reference, offsets 2.4–14.8mm; nothing approaches it | eliminated |

The overlap map is the decisive measurement: S0's cloud touches the
reference along **one 17-point arc** (10% of the rim), S1's in scattered runs
of 10/7/6/6/4/4. Ref coverage: **10% and 36%**. No ordering, pruning,
filtering, or hull of these clouds can emit the authors' 303mm rim, because
~65–90% of it has no nearby cloud points.

And where curves do meet, normals oppose for real reasons: pair 1-2 sits at
**0.45mm** with max dot **0.488 over the whole rim**, while the t04 piece-2
normals agree with its own mesh at **+0.997**. No sign flip fixes it; the
walls face 62° apart at the seam.

**What this means.** Piece 2's boundary *detection* — not its ordering —
fails to return the rim. The cloud is a thicket (52 components at 2×
spacing, 30 MST leaves) that no tested traversal converts to the reference.
The authors extracted a clean 303mm rim from presumably similar input, so
their boundary stage differs somewhere upstream of anything measured here.
That difference is unlocated, and locating it is a boundary-detection
investigation this ticket's ordering scope does not cover.

**The four piece-2 pairs (1-2, 2-4, 2-5, 2-8) are therefore not recoverable
by any measured intervention.** The pipeline stands at **11/15** on Pot_A
with ticket 04's fix. The C++ replacement walk written for this ticket was
validated in Python, failed there, and was never built — recorded so the
work is not repeated, and so the TDD discipline that caught it is visible.

## REFINEMENT 2026-09-28: the loss is between surface and boundary cloud

One more measurement locates defect 2 precisely, and it is NOT the walk.
Same reference, same 2mm threshold, three stages:

| stage (piece 2) | ref rim within 2mm |
|---|---|
| Surface_0 (11,263 pts) | **82%** |
| boundary cloud S0-path (86 pts) | **10%**, one 17-pt arc |
| boundary cloud S1-path (202 pts) | **36%**, scattered runs |
| unclustered (1,428 pts) | 100% at 0.53mm |

The rim zone exists in the surface (82%) and is gone by the boundary cloud
(10–36%). **The walk cannot lose what it was never given.** Defect 2 is a
boundary-*detection* failure on this sherd — somewhere in
`cleanSamples` → `estimatePatchNormalsAndBreakLinesFromSimpleAlgo_BSplineSurface`
→ sphere-marching → boundary estimation — not an ordering failure. This
ticket's ordering scope never covered it, which is why eight interventions
at the wrong stage all failed.

Also tested and eliminated here: using the discarded `boundaryImproved`
cloud (boundary + nearby unclustered, the dead code at line 974) — coverage
stays 0.68/0.27 with <45% near the reference. Un-discarding it is not the
fix either.

What remains is mapping the surface→boundary stages for piece 2: new work,
not a continuation. Scripts: `improved_cloud_test.py`, `overlap_map.py`,
`where_is_the_excess.py`, `which_way_is_the_offset.py`.

## ADDENDUM 2026-09-28: the surfaces, not just the clouds

The closure above blames boundary *detection* (clouds missing the rim).
Surface-level measurement refines that without reopening it:

- Piece 2's Surface_1 (171 pts, 45mm from the rim) is a scrap the vote
  wrongly picked; ticket 04 now guards against exactly this.
- Piece 2's **unclustered points cover 100% of the reference at 0.53mm
  median** — better than either named surface. The fracture zone sits in
  the points region-growing refused to cluster.
- 30/169 ref points (18%) are covered ONLY by unclustered, not S0.

So a future boundary-detection investigation starts with a concrete lead:
the rim zone for this sherd is in S0 (82%) + unclustered (the rest), never
in S1. Any fix that does not consult the unclustered points cannot cover
the full rim. Scripts: `surfaces_cover_rim.py`, `unclustered_covers_rim.py`,
`overlap_map.py` (all in `structure-from-sherds-pp/artifacts/juglet_run1/`).

## Note

The paper reports the axis-direction sign ambiguity is handled at
*matching* time, by inverting one descriptor and matching twice. This
ticket is not required to solve it, and must not try to.
