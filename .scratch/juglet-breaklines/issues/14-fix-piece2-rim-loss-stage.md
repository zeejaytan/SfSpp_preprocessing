# 14: Fix the stage that loses piece 2's rim

**Answers:** E1

**Blocked by:** 15 (ticket 13 named boundary estimation; deeper measurement
moved the target upstream to surface construction — split vs sample vs fit
unseparated. Ticket 03 is the record of what happens when the wrong stage
is fixed eight times in a row)

**Status:** ready-for-agent — attributed to the split (ticket 15); the fix
is routing, not recomputation (below)

**Needs-eye:** required before closing. Any change to where a rim is traced
is a geometry claim; stage the before/after rims against the authors'
reference in `visual-qa/` as a single look per affected sherd.

## REFINEMENT 2026-09-28: the surface is short, not just the boundary cloud

Ticket 13 named boundary estimation (82% → 36%). Deeper measurement moves
the target upstream again — the surface itself is under-grown:

- Piece-2 Surface_0's 30 uncovered reference points are **scattered** (runs
  of 6/3/3/2/2/… and singles) at **2.0–2.8mm**, just over the threshold.
  Not a missing region: the surface ends ~2mm inside the authors' rim
  along scattered stretches. (`overlap` reasoning; scripts below.)
- Stored normals are fine (rim-zone |dot| vs tight PCA normals: 0.993 vs
  1.000 off-rim), so the surface is well-formed but short — not corrupt.
- Downsampling (`downsamplePointCloud`, uniform sampling targeting
  8000–12000 pts) and the B-spline fitting stage
  (`improveSurfaceBoundaryByFittingBSplineSurface`) are the unexamined
  candidates for the 2mm inset. Neither has been measured yet.

And the unclustered points cover **100% of the reference at 0.53mm median**,
with 18% covered ONLY there. So the fracture-edge strip this surface lacks
exists in the intermediates — split into unclustered by region growing.

Eliminated along the way (each with numbers, none re-tried):
radius × angle sweep (no cell isolates the rim; small radius flags wall
texture 1029+ pts), noise filter (removes almost nothing — dense thicket),
angular sort (28mm jumps), concave hull (fragments at 54%; 2D projection
folds the 3D rim), MST diameter (weaves 3.3mm off, 26% within 2mm),
leaf-pruning (overlap stays ~27%), tangent-walk rewrite (port covered
0.116/0.035 — worse; never built), discarded `boundaryImproved` cloud
(coverage stays 0.68/0.27, <45% near ref).

## EXPERIMENT RUN 2026-09-28: union breaks the fit, not the detector — NEGATIVE

Fed boundary detection S0 + nearby-unclustered (D=3: +1389 pts, D=5:
+1427 pts), no axis staged so Breakline_0 comes from the S0 path in all
arms, existing binary, no rebuild:

| arm | rim length | len/ref | med off | gate pairs |
|---|---|---|---|---|
| control (S0) | 138.3mm | 0.456 | 2.82 | baseline |
| D3 | **10.8mm** | 0.036 | 2.57 | none pass |
| D5 | **10.8mm** | 0.036 | 2.57 | none pass |

The union collapses the rim to a padded 10.8mm stub (ticket 06's pattern:
padding hiding a fragment). Ruled out as cause: unclustered normals are
fine (median 0.979 vs tight PCA).

**The byte-level finding that locates it:** all three `boundary.pcd`
files are BYTE-IDENTICAL (`78572793`). The union changed nothing about
boundary detection output — consistent with the downsampler normalizing to
its 8000–12000 target budget before detection. But the Breakline_0 files
differ. Identical boundary in, different rim out means the union poisoned
something DOWNSTREAM that also reads Surface_0.xyz: the B-spline surface
fit. Dumping 1400 rough fracture points into the fitted surface distorts
the fit the rim is projected onto.

So naive concatenation is out, and the experiment's value is the
elimination plus the location: the remaining candidates are (a) S0's ~2mm
shortfall at surface *construction* (mesh stage / split — the strip sits
in unclustered), and (b) a fit-robust way to include the fracture strip
that does not poison the spline. Neither is an edgeline-side change, which
is why every edgeline-side intervention in ticket 03 failed.

## TARGET ATTRIBUTED 2026-09-28 (ticket 15): route, don't recompute

The split assigns piece 2's fracture strip to unclustered points; the fit
preserves whatever it is given (80.5→82.2%); sampling is stable. And
`getBreakLineForDecorativeParts` (`mesh_processing_headless.cpp:1032`)
already extracts an ordered rim from those unclustered points — then drops
it (`cloud_sequenced` local, `:1128-1135`, no save). Third dead end in this
pipeline (line-974 reload, dead outlier filter, now this).

So the fix is ROUTING, not a new computation: persist that rim beside the
wall breaklines instead of discarding it. Constraints (all from measured
failures, none invented):
- scored per pair from 11/15 with the authors' arm riding along;
- must keep piece 1 correct and the six passing pairs passing;
- must not undo ticket 04 (guard audit re-run);
- the rim comes from unclustered points, so it needs the NaN/validity
  discipline ticket 13 recorded for filter outputs;
- if the change touches shared paths, re-measure the full Pot_A + Juglet
  coverage distributions (ticket 08's method).

## The experiment this was set up for (now run, above)

Feed piece 2's boundary detection the union of Surface_0 + unclustered
points near the surface edge, instead of Surface_0 alone. Predicts a full
rim near the reference because the union covers 100% of it at sub-mm.
Requires pipeline modification (merge before boundary estimation) plus the
NaN guard from ticket 13 for any filter output. One variable, one run,
scored per pair from 11/15 — the shape that settled every earlier question
in this chain.

Candidates, in pipeline order, with what would confirm each:

1. **`cleanSamples` / B-spline surface stage.** If
   `cloud_Surface_AllSamples_Cleaned.pcd` already lacks the rim zone that
   Surface_0 has, the loss is here. Suspect: resampling or smoothing that
   drops the fracture strip.
2. **Boundary estimation** (`getInitialBoundary_UsingPCL_BoundaryAlgo`).
   If the cleaned cloud covers the rim but `boundary.pcd` does not, the
   detector (radius 7.78mm adaptive, angle 108°) misses this sherd's edge.
   Note ticket 11 eliminated the radius *globally* — the gate was flat
   across 3–9mm — so a radius fix here would have to be piece-specific to
   avoid contradicting that finding.
3. **The walk input selection** (line 974 reload). If `boundaryImproved.pcd`
   or `cloud_Filtered.pcd` covers the rim while `boundary.pcd` does not,
   the fix is to stop discarding the computed improvement. Ticket 03 tested
   the improved cloud's walkability (coverage stayed 0.68/0.27, <45% near
   reference) — so this candidate is already weak, but the measurement
   belongs to this ticket if ticket 13 contradicts it.

## Constraints from earlier tickets (do not re-litigate)

- The fix must move the **gate** (11/15 → up), not just a per-sherd offset.
  Ticket 10 is the record of a 5× proxy improvement that changed no joins.
- The fix must keep piece 1 correct (0.69mm, 100% inside tolerance) and must
  not regress the six currently-passing pairs. Report per pair, from 11/15.
- The authors' arm rides along in every comparison (ticket 11's rule).
- If the fix touches the surface split, it must not undo ticket 04's 11/15:
  re-run the guard audit (`KEPT`/`EXCHANGED` per piece by `cmp`) as part of
  acceptance, not just the gate number.

## Acceptance criteria

- [ ] The stage named by ticket 13 is the stage changed — no other stage
- [ ] Piece-2 rim coverage of the 169-pt reference reported before/after
- [ ] Gate re-measured per pair from 11/15; Juglet re-measured against its
      honest denominator of 10
- [ ] Guard audit re-run (ticket 04's per-piece decisions unchanged or
      changed-with-reason)
- [ ] Witnessed look of the fixed rim against the reference
- [ ] If the change alters shared code paths (not piece-2-only), the full
      Pot_A + Juglet boundary coverage distributions re-measured (ticket 08's
      method), so a local fix with global side effects cannot hide
